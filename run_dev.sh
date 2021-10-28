#!/usr/bin/env bash

# Activate virtual environment
this_dir="$(dirname "$0")"
source "$this_dir/venv/bin/activate"

export FLASK_APP="$this_dir/app.py"
export FLASK_ENV="development"
export PORT=7777
flask run --port="$PORT"