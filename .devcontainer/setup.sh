#!/bin/bash

set -e

echo "Setting up development environment..."

# Ensure proper permissions
sudo chown -R devuser:devuser /workspace

# Backend setup
cd /workspace/backend
if [ ! -d "venv" ]; then
    echo "Creating Python virtual environment..."
    python3 -m venv venv
fi

source venv/bin/activate
echo "Installing Python dependencies..."
pip install --upgrade pip
pip install -r requirements.txt

# Create .env file if .env.example exists
if [ -f ".env.example" ] && [ ! -f ".env" ]; then
    cp .env.example .env
    echo "Created .env file from .env.example"
elif [ ! -f ".env" ]; then
    echo "Creating empty .env file..."
    touch .env
fi

deactivate

# Frontend setup
cd /workspace/frontend
echo "Installing Node.js dependencies..."
npm install

echo "Setup complete!"
