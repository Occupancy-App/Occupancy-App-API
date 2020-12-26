import tornado.web
import uuid
import logging
import redis
import json
from . import occupancy_api_utils 


class GetSpaceHandler(tornado.web.RequestHandler):

    # Note -- should not override __init__, per 
    #       https://www.tornadoweb.org/en/stable/web.html#tornado.web.RequestHandler
    def initialize(self):
        self._db_handle = redis.Redis( host='redis' )


    def set_default_headers(self):
        self.set_header("Access-Control-Allow-Origin",      "*")
        self.set_header("Access-Control-Allow-Headers",     "x-requested-with")
        self.set_header('Access-Control-Allow-Methods',     "GET, OPTIONS")

 
    def options(self, current_occupancy, max_occupancy ):
        self.set_status(204)
        self.finish()


    def get(self, space_id): 
        try:
            space_uuid = uuid.UUID( "urn:uuid:{0}".format(space_id) )
        except:
            self.set_status( 400 )
            self.write( { "error": "{0} is not in valid GUID format".format(space_id) } )
            self.finish()
            return

        retrieved_hash = occupancy_api_utils.get_redis_hash_by_id( self._db_handle, str(space_uuid) )
        if retrieved_hash is not None:
            self.write( "{0}\n".format( 
                occupancy_api_utils.convert_redis_hash_to_api_response(retrieved_hash)) )
        else:
            self.set_status( 404, "No space found with ID {0}".format(space_id) )
            self.write( { "error": "No space found with requested ID {0}".format(space_id) } )
            self.finish()
