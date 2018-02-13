#!/bin/bash
# vim: set et sw=4 ts=4:

set -o errexit

cd $(dirname $0)
if [[ ! -d .venv ]]; then
    virtualenv --no-site-packages .venv
fi
.venv/bin/pip install -U --upgrade-strategy only-if-needed -r requirements.txt
