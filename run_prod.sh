#!/usr/bin/env bash

(cd client && npm run build) || exit 1
FLASK_APP="app.py"
export FLASK_ENV="production"
export PORT=7777
python3 "$FLASK_APP"