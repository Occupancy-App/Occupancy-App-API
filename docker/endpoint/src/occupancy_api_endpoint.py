import tornado.ioloop
import tornado.web
import os
import tornado.tcpserver
import ssl
import logging
import sys
from handlers.newspacehandler                   import NewSpaceHandler 
from handlers.getspacehandler                   import GetSpaceHandler
from handlers.incrementspaceoccupancyhandler    import IncrementSpaceOccupancyHandler
from handlers.decrementspaceoccupancyhandler    import DecrementSpaceOccupancyHandler


def _make_ssl_ctx():
    ssl_ctx = ssl.create_default_context( ssl.Purpose.CLIENT_AUTH )
    crt_file = 'tls_cert/fullchain.pem'
    key_file = 'tls_cert/privkey.pem'

    logging.info( "TLS certificate and chain: {0}".format(crt_file) )
    logging.info( "          TLS private key: {0}".format(key_file) )

    # Set minimum TLS version to 1.2 to improve SSL Labs SSL score
    ssl_ctx.minimum_version = ssl.TLSVersion.TLSv1_2

    # Limiting cipher suites to the only two SSL labs approves of
    #       1. TLS_ECDHE_RSA_WITH_AES_256_GCM_SHA384
    #       2. TLS_ECDHE_RSA_WITH_AES_128_GCM_SHA256

    # https://docs.python.org/2/library/ssl.html#ssl.SSLContext.set_ciphers
    # IDs are colon-separated
    # Recommended list obtained from https://github.com/ssllabs/research/wiki/SSL-and-TLS-Deployment-Best-Practices

    acceptable_cipher_suites = [
        "ECDHE-ECDSA-AES128-GCM-SHA256",
        "ECDHE-ECDSA-AES256-GCM-SHA384",
        "ECDHE-RSA-AES128-GCM-SHA256",
        "ECDHE-RSA-AES256-GCM-SHA384",
        "DHE-RSA-AES128-GCM-SHA256",
        "DHE-RSA-AES256-GCM-SHA384",
    ]

    ssl_ctx.set_ciphers( ":".join(acceptable_cipher_suites) )
    ssl_ctx.load_cert_chain( crt_file, key_file )

    return ssl_ctx


def _make_app():
    return tornado.web.Application(
        [
            (r"^\/space\/new\/occupancy\/current\/(\d+)\/max\/(\d+)(\/name\/([^\/]+))?", NewSpaceHandler ),
            (r"^\/space/([^\/]+)", GetSpaceHandler ),
            (r"^\/space/([^\/]+)/increment\/?", IncrementSpaceOccupancyHandler ),
            (r"^\/space/([^\/]+)/decrement\/?", DecrementSpaceOccupancyHandler )
        ],
        debug=True
    )
 

if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG)
    application = _make_app()
    ssl_ctx = _make_ssl_ctx()
    http_server = tornado.httpserver.HTTPServer( application, ssl_options=ssl_ctx )
    server_port = 443
    http_server.listen( server_port )
    logging.info( "Listening for HTTPS connections on port {0}".format(server_port) )
    tornado.ioloop.IOLoop.current().start()
