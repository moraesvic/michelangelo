#!/usr/bin/env bash

# Activate virtual environment
this_dir="$(dirname "$0")"
source "$this_dir/venv/bin/activate"

(cd "$this_dir/client" && npm run build) || exit 1
FLASK_APP="$this_dir/app.py"
export FLASK_ENV="production"
export PORT=7777
python3 "$FLASK_APP"