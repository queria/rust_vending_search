#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""My first wheezy.web app"""

# import csv
# import datetime
import locale
import logging
from operator import itemgetter
import requests
import socket
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
        val = self._r.query.get(field, [default])
        return val[0]

    def get(self):
        addr = ''
        # now try to parse/fetch addr
        server_info = ''
        offers = []
        vending_machines = []
        try:
            addr = self._arg('addr', '')

            if addr:
                self.validate_address(addr)
                # TODO(queria): caching of these responses for certain time
                # to not hit any server too often
                server_info = self.fetch_server_info(addr)
                offers, vending_machines = self.fetch_offers_and_machines(addr)

                # TODO(queria): advanced sorting
                # eg always item name + by price/currency/etc
                sort_by = self._arg('sortby', 'item')
                order = self._arg('order', 'asc')
                if offers and sort_by in offers[0].keys():
                    offers = sorted(offers,
                                    key=itemgetter(sort_by),
                                    reverse=(order == 'desc'))

            if not addr:
                addr = '217.182.199.20:28019'
            return self.render_response(
                'index.html',
                server_addr=addr,
                server_info=server_info,
                offers=offers,
                vending_machines=vending_machines)

        except InvalidServerAddress as e:
            return self.render_response(
                'bad_address.html',
                exc=e)
        except Exception as e:
            return self.render_response('exception.html',
                                        exc=traceback.format_exc(e))

    def fetch_offers_and_machines(self, addr):
        # TODO(queria): friendly handling of fetching/parsing issues
        monuments = requests.get(
            'http://%s/monuments.json' % addr, timeout=10).json()
        vending_machines_tmp = [m for m in monuments
                                if m['name'] == "vendingmachine.deployed"]
        offers = []
        vending_machines = {}
        for machine in vending_machines_tmp:
            offers_tmp = machine.pop('goods')
            vending_machines[id(machine)] = machine
            for offer in offers_tmp:
                offer['machineId'] = id(machine)
            offers += offers_tmp
        return (offers, vending_machines)

    def fetch_server_info(self, addr):
        try:
            status = requests.get('http://%s/status.json' % addr, timeout=10).json()
            return ('%s - %d/%d' % (
                status['hostname'],
                status['players'],
                status['maxplayers']))
        # TODO(queria): more friendly handling of fetching/parsing issues
        # when i know what kind of things can be wrong,
        # and make Exception catching more class specific
        # then use just:
        # except SomeExceptionLike404:
        #  server_name = ''
        # for cases which mean server does not support this extension
        except Exception as e:
            return str(e)

    def validate_address(self, addr):
        # TODO(queria): replace with more sofisticated check (ipv6 in rust?)
        LOG.debug('Validating user specified address %s', addr)
        parts = addr.split(':')
        try:
            socket.getaddrinfo(parts[0], parts[1])
        except (IndexError, socket.error, socket.herror, socket.gaierror,
                socket.timeout):
            raise InvalidServerAddress(addr)


class InvalidServerAddress(Exception):
    def __init__(self, addr):
        super(InvalidServerAddress, self).__init__(
            'Invalid address specified: %s' % addr)


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
