import tornado.web

class NewSpaceHandler(tornado.web.RequestHandler):
    def set_default_headers(self):
        self.set_header("Access-Control-Allow-Origin",      "*")
        self.set_header("Access-Control-Allow-Headers",     "x-requested-with")
        self.set_header('Access-Control-Allow-Methods',     "GET, OPTIONS")
 
    def options(self):
        self.set_status(204)
        self.finish()

    def get( self, current_occupancy, max_occupancy ):
        self.write( 
            { 
                "status": "Not implemented yet"
            }
        )
