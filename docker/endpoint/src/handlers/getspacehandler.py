import tornado.web
import uuid
import logging
import redis
import json


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
            # Make sure the space ID is a legit UUID
            space_uuid = uuid.UUID( "urn:uuid:{0}".format(space_id) )

            retrieved_data = self._db_handle.get( str(space_uuid) )
            if retrieved_data is not None:
                json_obj = json.loads( retrieved_data )
                logging.debug("Successful retrieval of JSON for space {0}".format(str(space_uuid)) )
                self.write( json_obj )
            else:
                self.set_status( 404, "No data found for space ID {0}".format(space_id) )
        except redis.RedisError as e:
            logging.warn("Exception thrown getting JSON for space {0}: {1}".format(space_id, e) )
            self.set_status( 500, "DB error thrown when requesting data for space ID {0}".format(space_id) )
