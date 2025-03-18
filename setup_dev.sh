#!/bin/bash

# Setup admin API virtual environment
echo "Setting up admin API virtual environment..."
cd admin_api
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
pip install -e ../shared
deactivate

# Setup frontend API virtual environment
echo "Setting up frontend API virtual environment..."
cd ../frontend_api
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
pip install -e ../shared
deactivate

echo "Setup complete! To activate the virtual environments:"
echo "Admin API: cd admin_api && source .venv/bin/activate"
echo "Frontend API: cd frontend_api && source .venv/bin/activate"
