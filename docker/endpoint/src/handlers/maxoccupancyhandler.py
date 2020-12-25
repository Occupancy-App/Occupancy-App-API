import tornado.web
import uuid
import time
import datetime
import logging
import redis
import json
from . import occupancy_api_utils


class MaxOccupancyHandler(tornado.web.RequestHandler):

    # Note -- should not override __init__, per 
    #       https://www.tornadoweb.org/en/stable/web.html#tornado.web.RequestHandler
    def initialize(self):
        self._db_handle = redis.Redis( host='redis' )


    def set_default_headers(self):
        self.set_header("Access-Control-Allow-Origin",      "*")
        self.set_header("Access-Control-Allow-Headers",     "x-requested-with")
        self.set_header('Access-Control-Allow-Methods',     "PUT, OPTIONS")

 
    def options(self, current_occupancy, max_occupancy ):
        self.set_status(204)
        self.finish()


    def put( self, space_id, new_max_occupancy ):

        # Make sure we have a valid space ID
        try:
            space_uuid = uuid.UUID( "urn:uuid:{0}".format(space_id) )
        except:
            logging.warn( "Invalid space ID, not a GUID: {0}".format(space_id) )
            self.set_status( 400, "Invalid space ID format {0}".format(space_id) )
            self.finish()
            return

        # If the space doesnsn't exist, bail
        if self._db_handle.exists( str(space_uuid) ) is False:
            self.set_status( 404, "Space {0} does not exist".format(str(space_uuid)) )
            self.finish()
            return

        new_max_occupancy = int( new_max_occupancy ) 

        # Sanity check occupancy
        if new_max_occupancy < 1 or new_max_occupancy > 100000:
            self.set_status( 400, 
                "Invalid occupancy value: {0}, passed value must be 1 <= max_occupancy <= 100000".format(
                    new_max_occupancy) )
            self.finish()
            return

        redis_key = str( space_uuid )

        # Transaction will lower max, lower current to max if needed, update last updated timestamp, 
        #   reset TTL
        with  self._db_handle.pipeline() as pipe:
            while True:
                try:
                    pipe.watch( redis_key ) 

                    new_values = { 
                        'occupancy_maximum'     : new_max_occupancy,
                        'last_updated'          : "{0}Z".format( datetime.datetime.utcnow().isoformat() )
                    }

                    # Back in immediate mode, read any values from database that are needed
                    curr_occupancy = int( pipe.hget( redis_key, 'occupancy_current' ).decode() )
                    if curr_occupancy > new_max_occupancy:
                        new_values['occupancy_current'] = new_max_occupancy

                    # Attomic commit group after this point
                    pipe.multi() 

                    pipe.hset( redis_key, mapping=new_values )
                    pipe.expire( redis_key, occupancy_api_utils.key_expire_value )

                    # Commit group is now done
                    pipe.execute()

                    # Done with this loop
                    break

                except redis.WatchError:
                    continue

        # Get updated value, return it
        self.write( occupancy_api_utils.convert_redis_hash_to_api_response(
            occupancy_api_utils.get_redis_hash_by_id(self._db_handle, redis_key)) )
