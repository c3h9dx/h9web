import os
import logging
import tornado.web
import tornado.ioloop

from tornado.options import options
from tornado.ioloop import PeriodicCallback
from h9web import h9d
from h9web.LoginHandler import LoginHandler
from h9web.cli import CliWSHandler
from h9web.event import Event
from h9web.settings import get_ssl_context, get_server_settings
from h9web.stats import Stats
from h9web.frames import Frames
from h9web.nodes import Nodes, NodesDiscovery
from h9web.node import GetNodeInfo, NodeRegister, NodeReset
from h9web.dev import Dev
from h9web.dashboard import Dashboard

class Application(tornado.web.Application):
    def __init__(self, options, h9d_int, loop):
        vue_path = os.path.join(os.path.dirname(__file__), '../web/dist')
        handlers = [
            (r'/api/login', LoginHandler),
            (r'/api/logout', LoginHandler),
            (r'/api/stats', Stats),
            (r'/api/cli', CliWSHandler, dict(loop=loop)),
            (r'/api/events', Event),
            (r'/api/frames', Frames, dict(h9d_int=h9d_int)),
            (r'/api/nodes', Nodes, dict(h9d_int=h9d_int)),
            (r'/api/nodes/discover', NodesDiscovery, dict(h9d_int=h9d_int)),
            (r'/api/node/([0-9]+)', GetNodeInfo, dict(h9d_int=h9d_int)),
            (r'/api/node/([0-9]+)/reset', NodeReset, dict(h9d_int=h9d_int)),
            (r'/api/node/([0-9]+)/reg/([0-9]+)', NodeRegister, dict(h9d_int=h9d_int)),
            (r'/api/dev/([A-Za-z0-9_]+)/([A-Za-z0-9_]+)', Dev, dict(h9d_int=h9d_int)),
            (r'/api/dashboard', Dashboard, dict(h9d_int=h9d_int)),
            (r"/dashboard", tornado.web.RedirectHandler, {"url": "/dashboard/"}),
            (r"/nodes", tornado.web.RedirectHandler, {"url": "/nodes/"}),
            (r"/rawframe", tornado.web.RedirectHandler, {"url": "/rawframe/"}),
            (r"/stats", tornado.web.RedirectHandler, {"url": "/stats/"}),
            (r"/settings", tornado.web.RedirectHandler, {"url": "/settings/"}),
            (r"/dashboard/(.*)", tornado.web.StaticFileHandler, {"path": vue_path, "default_filename": "index.html"}),
            (r"/nodes/(.*)", tornado.web.StaticFileHandler, {"path": vue_path, "default_filename": "index.html"}),
            (r"/rawframe/(.*)", tornado.web.StaticFileHandler, {"path": vue_path, "default_filename": "index.html"}),
            (r"/stats/(.*)", tornado.web.StaticFileHandler, {"path": vue_path, "default_filename": "index.html"}),
            (r"/settings/(.*)", tornado.web.StaticFileHandler, {"path": vue_path, "default_filename": "index.html"}),
            (r"/(.*)", tornado.web.StaticFileHandler, {"path": vue_path, "default_filename": "index.html"}),
        ]
        settings = dict(
            template_path=os.path.join(os.path.dirname(__file__), 'templates'),
            static_path=vue_path,
            login_url='/login',
            cookie_secret='__TODO:_GENERATE_YOUR_OWN_RANDOM_VALUE_HERE__',
            websocket_ping_interval=options.wpintvl,
            xsrf_cookies=(options.xsrf and not options.dev),
            dev_mode=options.dev,
            debug=options.debug,
            sslport=options.sslport,
            redirect=options.redirect,
            cli=options.cli,
            h9d_address=options.h9daddress,
            h9d_port=options.h9dport
        )
        super(Application, self).__init__(handlers, **settings)

        if settings["dev_mode"]:
            logging.warning("Enable CORS (cross-origin resource sharing)")
        if not settings["xsrf_cookies"]:
            logging.warning("Disable CSRF protection")


def main():
    options.parse_command_line()
    loop = tornado.ioloop.IOLoop.current()

    h9d_int = h9d.H9d(options.h9daddress, options.h9dport)

    app = Application(options, h9d_int, loop)

    ssl_ctx = get_ssl_context(options)
    server_settings = get_server_settings(options)

    app.listen(options.port, options.address, **server_settings)
    logging.info('Listening on {}:{} (http)'.format(options.port, options.address))
    if ssl_ctx:
        server_settings.update(ssl_options=ssl_ctx)
        app.listen(options.sslport, options.ssladdress, **server_settings)
        logging.info('Listening on {}:{} (https)'.format(options.sslport, options.ssladdress))

    stat_refresh_period = 10000 #ms
    stat_refresh = PeriodicCallback(lambda: Stats.refresh_stats_and_calc_rate(h9d_int, stat_refresh_period), stat_refresh_period)
    stat_refresh.start()

    # loop.spawn_callback(h9bus_int.run)
    loop.spawn_callback(h9d_int.run)
    loop.start()


if __name__ == '__main__':
    main()
