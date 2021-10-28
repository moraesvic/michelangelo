#!/usr/bin/env bash

export FLASK_APP="app.py"
export FLASK_ENV="development"
export PORT=7777
flask run --port="$PORT"