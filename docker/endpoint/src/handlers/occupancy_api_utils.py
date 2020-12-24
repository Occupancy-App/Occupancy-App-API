import uuid
import json
import logging
import redis
import datetime


def get_redis_hash_by_id( db_handle, space_id ):
    # Make sure the space ID string is a legit UUID
    space_uuid = uuid.UUID( "urn:uuid:{0}".format(space_id) )

    retrieved_data = db_handle.hgetall( str(space_uuid) )
    if retrieved_data is not None:
        json_obj = {}
        for key in retrieved_data:
            json_obj[ key.decode() ] = retrieved_data[key].decode()
        logging.debug("Successful retrieval of hash for space {0}".format(str(space_uuid)) )
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

    return "Created new space {0}".format(space_redis_key) 


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

