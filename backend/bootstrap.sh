#!/bin/bash
export FLASK_APP=./src/warskald_app.py
source $(pipenv --venv)/bin/activate
flask --debug run -h 0.0.0.0 