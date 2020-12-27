import tornado.web


class InvalidUrlHandler(tornado.web.RequestHandler):

    # Prepare will cover all HTTP methods
    def prepare(self):
        self.set_header("Access-Control-Allow-Origin",      "*")
        self.set_header("Access-Control-Allow-Headers",     "x-requested-with")
        self.set_header('Access-Control-Allow-Methods',     "GET, OPTIONS")

        self.set_status(404)
        self.write( { "error": "Invalid URL requested" } )
        self.finish()
