#!/bin/sh
set -e

# optional: allow overriding the command, otherwise run gunicorn
DEFAULT_CMD="gunicorn -b 0.0.0.0:5000 wsgi:app"

echo ">> Running migrations (flask db upgrade)"
flask db upgrade

echo ">> Starting app"
exec ${CMD:-$DEFAULT_CMD}
