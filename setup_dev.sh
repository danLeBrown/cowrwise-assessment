#!/bin/bash

# Setup admin API virtual environment
echo "Setting up admin API virtual environment..."
cd admin_api
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
deactivate
cd ..

# Setup frontend API virtual environment
echo "Setting up frontend API virtual environment..."
cd frontend_api
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
deactivate
cd ..

# Setup e2e test environment
echo "Setting up e2e test environment..."
cd tests
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
pip install -e ../admin_api
pip install -e ../frontend_api
deactivate
cd ..

echo "Setup complete! To activate the virtual environments:"
echo "Shared package: cd shared && source .venv/bin/activate"
echo "Admin API: cd admin_api && source .venv/bin/activate"
echo "Frontend API: cd frontend_api && source .venv/bin/activate"
echo "E2E Tests: cd tests && source .venv/bin/activate"
