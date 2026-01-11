#!/bin/bash

# Frontend startup script

echo "🚀 Starting Warhammer Ranking System Frontend..."

# Change to frontend directory
cd "$(dirname "$0")/../frontend"

# Check if node_modules exists
if [ ! -d "node_modules" ]; then
    echo "📦 Installing dependencies..."
    npm install
fi

# Run the application
echo "✨ Starting Vite dev server..."
npm run dev
