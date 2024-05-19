#!/bin/bash

# Ensure the script exits if any command fails
set -e

# Path to your main.py file
MAIN_PY_PATH="./main.py"
PORT=5002
# Extract the filename without the extension to use with gunicorn
FILENAME=$(basename -- "$MAIN_PY_PATH")
BASENAME="${FILENAME%.*}"
WORKERS=4
echo "Starting server on port ${PORT} with ${WORKERS} workers, through file at ${MAIN_PY_PATH}."
# Run the gunicorn command
gunicorn -w ${WORKERS} -b 0.0.0.0:${PORT} ${BASENAME}:app

