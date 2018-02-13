"""
Main configuration
"""

import logging
import os
import sys

from wheezy.html.ext.template import WidgetExtension
from wheezy.html.utils import html_escape
from wheezy.template.engine import Engine
from wheezy.template.ext.core import CoreExtension
from wheezy.template.loader import FileLoader
from wheezy.web.templates import WheezyTemplate


APPDIR = os.path.join(os.path.dirname(os.path.realpath(__file__)), '..')


def app_path(path):
    return os.path.join(APPDIR, path)


DEBUG = True
TPL_PATH = [app_path('templates')]
engine = Engine(
    loader=FileLoader(TPL_PATH),
    extensions=[
        CoreExtension(),
        WidgetExtension(),
    ])
engine.global_vars.update({'h': html_escape})


# cache = NullCache() if DEBUG else MemoryCache()
# cached = Cached(cache, time=16*60)


options = {}
options.update({
    'render_template': WheezyTemplate(engine),
})

log = logging.getLogger('rust_vending_search')
_log_handler = logging.StreamHandler(sys.stdout)
_log_handler.setFormatter(logging.Formatter(
    '[%(asctime)s] [%(name)s] %(levelname)s: %(message)s',
    '%Y-%m-%d %H:%M:%S'))
log.addHandler(_log_handler)
log.setLevel(logging.DEBUG if DEBUG else logging.INFO)
