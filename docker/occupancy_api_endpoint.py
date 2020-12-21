import tornado.ioloop
import tornado.web
import os
import tornado.tcpserver
import ssl
import logging
from handlers.newspacehandler import NewSpaceHandler 


def _make_app():
    return tornado.web.Application(
        [
            (r"^\/space\/new\/occupancy\/current\/(\d+)\/max\/(\d+).*?$", NewSpaceHandler )
        ],
        debug=True
    )
 

if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG)
    application = _make_app()
