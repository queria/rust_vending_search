#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""My first wheezy.web app"""

# import csv
# import datetime
import locale
import logging
import requests
import traceback

from rust_vending_search import config

from wheezy.http import WSGIApplication
from wheezy.routing import url
from wheezy.web import handlers
from wheezy.web.handlers import file_handler
from wheezy.web.middleware import bootstrap_defaults
from wheezy.web.middleware import path_routing_middleware_factory

# Only for modded servers, with Oxide support for map.playrust.io - vending
# machines have to be visible there.
#
# curl 'http://217.182.199.20:28019/monuments.json'
# cat /tmp/x1 | python -c 'import json; import sys; import pprint;
#   m=json.load(sys.stdin);
#   pprint.pprint([v for v in m if v["name"] == "vendingmachine.deployed"])'


LOG = logging.getLogger('rust_vending_search.app')


locale.setlocale(locale.LC_ALL, 'en_US.utf8')


class MainView(handlers.BaseHandler):

    def __init__(self, request):
        super(MainView, self).__init__(request)

        self._r = request

    def _arg(self, field, default=''):
        LOG.debug(self._r)
        val = self._r.query.get(field, [default])
        return val[0]

    def get(self):
        try:
            addr = self._arg('addr', '')
            # now try to parse/fetch addr
            server_name = ''
            vending_machines = []

            if addr:
                # TODO(queria): friendly handling of fetching/parsing issues
                status = requests.get('http://%s/status.json' % addr).json()
                monuments = requests.get(
                    'http://%s/monuments.json' % addr).json()
                # TODO(queria): caching of these responses for certain time
                # to not hit any server too often

                server_name = '%s - %d/%d' % (status['hostname'],
                                              status['players'],
                                              status['maxplayers'])
                vending_machines = [m for m in monuments
                                    if m['name'] == "vendingmachine.deployed"]
                # TODO(queria): sorting of offers
                # also convert from list of machines to list of individual
                # orders ... or split into two lists?

            if not addr:
                addr = '217.182.199.20:28019'
            return self.render_response(
                'index.html',
                server_addr=addr,
                server_name=server_name,
                vending_machines=vending_machines)

        except Exception as e:
            return self.render_response('exception.html',
                                        exc=traceback.format_exc(e))

url_map = [
    url('', MainView, name='index'),
    url('static/{path:any}',
        file_handler(root=config.app_path('static/')),
        name='static'),
]

application = WSGIApplication(
    middleware=[
        bootstrap_defaults(url_mapping=url_map),
        path_routing_middleware_factory
    ],
    options=config.options)

if __name__ == '__main__':
    from wsgiref.simple_server import make_server
    try:
        LOG.info('Launching on http://localhost:5000/ ...')
        make_server('', 5000, application).serve_forever()
    except KeyboardInterrupt:
        LOG.info('... exiting')
    LOG.info('\nThanks for trying me!')
