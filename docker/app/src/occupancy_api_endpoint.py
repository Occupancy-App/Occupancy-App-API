import tornado.ioloop
import tornado.web
import logging
from handlers.newspacehandler                   import NewSpaceHandler 
from handlers.getspacehandler                   import GetSpaceHandler
from handlers.incrementspaceoccupancyhandler    import IncrementSpaceOccupancyHandler
from handlers.decrementspaceoccupancyhandler    import DecrementSpaceOccupancyHandler
from handlers.maxoccupancyhandler               import MaxOccupancyHandler


def _make_app():
    return tornado.web.Application(
        [
            (r"^\/space\/new\/occupancy\/current\/(\d+)\/max\/(\d+)(\/name\/([^\/]+))?",    NewSpaceHandler ),
            (r"^\/space/([^\/]+)",                                                          GetSpaceHandler ),
            (r"^\/space/([^\/]+)/increment\/?",                                             IncrementSpaceOccupancyHandler ),
            (r"^\/space/([^\/]+)/decrement\/?",                                             DecrementSpaceOccupancyHandler ),
            (r"^\/space/([^\/]+)/max\/(\d+)\/?",                                            MaxOccupancyHandler ),
        ],
        debug=True
    )
 

if __name__ == "__main__":

    logging.basicConfig(
        level=logging.DEBUG,
        format='%(asctime)s %(levelname)-8s %(message)s',
        datefmt='%Y-%m-%d %H:%M:%SZ' )

    application = _make_app()
    http_server = tornado.httpserver.HTTPServer( application ) 
    server_port = 80
    http_server.listen( server_port )
    logging.info( "Listening for connections on port {0}".format(server_port) )
    tornado.ioloop.IOLoop.current().start()
