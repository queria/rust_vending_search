#!/bin/bash
# vim: set et sw=4 ts=4:

set -o errexit

cd $(dirname $0)
if [[ "$(readlink -f $(which pip))" != "$(readlink -f .venv/bin/pip)" ]]; then
    source .venv/bin/activate
fi
PORT=${PORT:-5000}
SPORT=${SPORT:-$(( $PORT + 5 ))}

OPTS=""
OPTS="${OPTS} --threads 4 --processes 1"
OPTS="${OPTS} --reload-on-exception "
OPTS="${OPTS} --http :${PORT} --stats :${SPORT}"
OPTS="${OPTS} --wsgi-file rust_vending_search/app.py"
if uwsgi --help|grep -q python-autoreload; then
    OPTS="$OPTS --python-autoreload 1"
fi
set -x
uwsgi $OPTS
