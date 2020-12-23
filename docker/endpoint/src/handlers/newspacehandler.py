import tornado.web
import uuid
import time
import datetime


class NewSpaceHandler(tornado.web.RequestHandler):
    def set_default_headers(self):
        self.set_header("Access-Control-Allow-Origin",      "*")
        self.set_header("Access-Control-Allow-Headers",     "x-requested-with")
        self.set_header('Access-Control-Allow-Methods',     "GET, OPTIONS")
 
    def options(self, current_occupancy, max_occupancy ):
        self.set_status(204)
        self.finish()

    def _create_occupancy_response( self, space_id, space_name, current_occupancy, max_occupancy, 
            created_timestamp, last_updated_timestamp ):

        return {
            'space_id'      : str(space_id),
            'space_name'    : space_name,
            'occupancy'     : {
                'current'   : int( current_occupancy ),
                'maximum'   : int( max_occupancy )
            },
            'created'       : created_timestamp,
            'last_updated'  : last_updated_timestamp
        }


    def get( self, current_occupancy, max_occupancy ):

        current_occupancy = int( current_occupancy ) 
        max_occupancy = int( max_occupancy ) 

        # Sanity check occupancy
        if max_occupancy < 1 or max_occupancy > 100000:
            self.set_status( 400, 
                "Invalid occupancy value: {0}, passed value must be 1 <= max_occupancy <= 100000".format(
                    max_occupancy) )
            self.finish()
        else:
            if current_occupancy < 0:
                current_occupancy = 0

            new_space_id = uuid.uuid4()
            space_name = "placeholder"

            now_timestamp = "{0}Z".format(datetime.datetime.utcnow().isoformat())

            # TTL: 8 hours
            ttl_seconds = 60 * 60 * 8

            expiration_seconds_since_epoch = time.time() + ttl_seconds

            # Write new key to Redis

            self.write( self._create_occupancy_response( new_space_id, space_name, current_occupancy, 
                max_occupancy, now_timestamp, now_timestamp) )
