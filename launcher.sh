#!/bin/sh

cd /
cd home/pi/mqtt_client

# Activate the virtual environment
. .venv/bin/activate

# Check if the virtual environment is activated
if [ -z "$VIRTUAL_ENV" ]; then
  echo "Virtual environment failed to activate."
  exit 1
fi

# Verify that the Python interpreter is the one from the virtual environment
if [ "$(which python)" != "$(pwd)/.venv/bin/python" ]; then
  echo "Python interpreter is not from the virtual environment."
  exit 1
fi

echo "Virtual environment activated successfully."

# Run your Python script
python reloadable.py mqtt_client.py

# Return to the root directory
cd /
