import uuid
import json
import logging
import redis
import datetime

# TTL = 8 hours
key_expire_value = 60 * 60 * 8



def get_redis_hash_by_id( db_handle, space_id ):
    # Make sure the space ID string is a legit UUID
    space_uuid = uuid.UUID( "urn:uuid:{0}".format(space_id) )

    retrieved_data = db_handle.hgetall( str(space_uuid) )
    
    # If no key matches the requested UUID, we get an empty hash back
    # Empty hashes evaluate to False. Not that None also evaluates to false, so 
    # it's a safe test for both
    if bool(retrieved_data) is True:
        json_obj = {}
        for key in retrieved_data:
            json_obj[ key.decode() ] = retrieved_data[key].decode()
        logging.debug("Successful retrieval of hash for space {0}".format(str(space_uuid)) )
        #logging.debug("Retrieved data:\n{0}".format(json.dumps(json_obj, indent=4, sort_keys=True)))

        # Refresh its TTL
        db_handle.expire( str(space_uuid), key_expire_value ) 

        return json_obj
    else:
        logging.debug( "No contents found for space ID {0}".format( str(space_uuid) ) ) 
        return None


def create_redis_hash( space_id, space_name, current_occupancy, max_occupancy, 
        created_timestamp, last_updated_timestamp ):

    if space_name is None:
        space_name = ""

    return {
        'space_id'              : str(space_id),
        'space_name'            : space_name,
        'occupancy_current'     : current_occupancy,
        'occupancy_maximum'     : max_occupancy,
        'created'               : created_timestamp,
        'last_updated'          : last_updated_timestamp
    } 


def write_new_space_to_db( db_handle, space_id, space_name, current_occupancy, max_occupancy ):

    now_timestamp = "{0}Z".format(datetime.datetime.utcnow().isoformat())

    space_redis_key = str( space_id )

    redis_hash = create_redis_hash( str(space_id), space_name, current_occupancy, max_occupancy,
        now_timestamp, now_timestamp )

    # hmset is deprecated.  Use hset with "mapping" field instead)
    hset_return = db_handle.hset( space_redis_key, mapping=redis_hash )

    logging.debug( "HSET return value: {0}".format(hset_return) )

    # Set TTL on the new key
    db_handle.expire( space_redis_key, key_expire_value )

    #return "Created new space {0}\n".format(space_redis_key) 
    return convert_redis_hash_to_api_response( redis_hash )


def convert_redis_hash_to_api_response( redis_hash ):
    if redis_hash[ 'space_name' ] == '':
        api_space_name = None
    else:
        api_space_name = redis_hash[ 'space_name' ]

    return {
        'space_id'      : redis_hash[ 'space_id' ],
        'space_name'    : api_space_name,
        'occupancy'     : {
            'current'   : int( redis_hash['occupancy_current'] ),
            'maximum'   : int( redis_hash['occupancy_maximum'] )
        },
        'created'       : redis_hash['created'],
        'last_updated'  : redis_hash['last_updated']
    }


def increment_occupancy( db_handle, space_id ):
    return _do_occupancy_change( db_handle, space_id, 1 )


def decrement_occupancy( db_handle, space_id ):
    return _do_occupancy_change( db_handle, space_id, -1 )


def _do_occupancy_change( db_handle, space_id, increment_amount ):
    redis_key = str(space_id)

    # No key by that name, nothing to do here
    exists_test = db_handle.exists( redis_key )
    if exists_test == 0:
        logging.warn("Tried an increment on space {0} which does not exist, bailing".format(
            redis_key) )
        return None
    else:
        logging.debug( "Space ID {0} passed a DB \"exists\" test, we think it's in the DB".format(
            redis_key) )

    # Pipelines are used for transactions
    with db_handle.pipeline() as pipe:

        increment_completed = False
        while increment_completed is False:
            try:
                # Put a watch on our key, so if anyone changes it, we detect it and retry
                pipe.watch ( redis_key )
            
                # After a watch we're in immediate execution mode again, which lets us get the two keys we care about

                # Get current and max
                (current_occupancy_bytes, max_occupancy_bytes) = pipe.hmget( 
                    redis_key, ('occupancy_current', 'occupancy_maximum') )

                current_occupancy   = int( current_occupancy_bytes.decode() )
                max_occupancy       = int( max_occupancy_bytes.decode() )

                # Sanity check the change
                computed_new_value = current_occupancy + increment_amount

                if computed_new_value >= 0 and computed_new_value <= max_occupancy:
                    logging.debug( "Key {0} okay to change by {1}, 0 <= new value {2} <= {3}".format(
                        redis_key, increment_amount, computed_new_value, max_occupancy) )

                    # Restart buffered behavior with MULTI. Once we're in multi, the writes will not happen if the 
                    #           WATCH is triggered
                    pipe.multi()
                    pipe.hincrby( redis_key, 'occupancy_current', increment_amount )

                    # Update last updated timestamp 
                    now_timestamp = "{0}Z".format(datetime.datetime.utcnow().isoformat())
                    pipe.hset( redis_key, 'last_updated', now_timestamp )

                    # Update the TTL
                    pipe.expire( redis_key, key_expire_value )

                    # Execute does the atomic commit for all the changes since we turned multi back on
                    pipe.execute()
                    increment_completed = True

                else:
                    # Doing the change would violate bounds, return original, unchanged value
                    break

            # Our element got changed underneath us, restart from scratch
            except redis.WatchError:
                # Just try again
                logging.debug( "Watch error tripped on increment for key {0}, retrying".format(redis_key) )

    # Get updated space entry and return it
    return convert_redis_hash_to_api_response( get_redis_hash_by_id(db_handle, redis_key) )
