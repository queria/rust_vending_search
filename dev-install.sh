#!/bin/bash
# vim: set et sw=4 ts=4:

set -o errexit

cd $(dirname $0)
./install.sh
./venv/bin/pip install -U --upgrade-strategy only-if-needed -r dev-requirements.txt

