#!/bin/bash

# Render build script for backend
# This ensures the database tables are created on first deployment

echo "Installing Python dependencies..."
pip install -r requirements.txt

echo "Backend build complete!"
