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

        new_max_occupancy = int( new_max_occupancy ) 

        # Sanity check occupancy
        if new_max_occupancy < 1 or new_max_occupancy > 100000:
            self.set_status( 400, 
                "Invalid occupancy value: {0}, passed value must be 1 <= max_occupancy <= 100000".format(
                    new_max_occupancy) )
            self.finish()
            return

        now_timestamp = "{0}Z".format(datetime.datetime.utcnow().isoformat())

        self.write( "New max: {0}\n".format(new_max_occupancy) )
