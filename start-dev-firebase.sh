#!/bin/bash

# Local development start script for Vercel + Firebase setup

set -e

echo "🚀 Starting Warhammer Ranking System (Local Development)"
echo "=========================================================="
echo ""

# Check if Firebase credentials exist
if [ ! -f "firebase-credentials.json" ]; then
    echo "❌ Error: firebase-credentials.json not found!"
    echo ""
    echo "Please follow these steps:"
    echo "1. Go to https://console.firebase.google.com/"
    echo "2. Select your project"
    echo "3. Go to Project Settings > Service Accounts"
    echo "4. Click 'Generate new private key'"
    echo "5. Save the file as 'firebase-credentials.json' in the project root"
    echo ""
    exit 1
fi

# Check if backend .env exists
if [ ! -f "backend/.env" ]; then
    echo "⚠️  Warning: backend/.env not found!"
    echo "Creating from backend/.env.example..."
    cp backend/.env.example backend/.env
    echo ""
    echo "✅ Created backend/.env"
    echo "⚠️  Please edit backend/.env and set your FIREBASE_PROJECT_ID"
    echo ""
    echo "Then run this script again."
    exit 1
fi

# Check if dependencies are installed
echo "📦 Checking dependencies..."
echo ""

# Backend dependencies
if [ ! -d "backend/venv" ]; then
    echo "Creating Python virtual environment..."
    cd backend
    python3 -m venv venv
    source venv/bin/activate
    pip install --upgrade pip
    pip install -r requirements.txt
    cd ..
    echo "✅ Backend dependencies installed"
else
    echo "✅ Backend virtual environment found"
fi

# Frontend dependencies
if [ ! -d "frontend/node_modules" ]; then
    echo "Installing frontend dependencies..."
    cd frontend
    npm install
    cd ..
    echo "✅ Frontend dependencies installed"
else
    echo "✅ Frontend node_modules found"
fi

echo ""
echo "=========================================================="
echo ""

# Start backend
echo "🔧 Starting backend server..."
cd backend
source venv/bin/activate
python main.py &
BACKEND_PID=$!
cd ..

# Wait for backend to start
echo "⏳ Waiting for backend to be ready..."
sleep 3

# Start frontend
echo "⚛️  Starting frontend development server..."
cd frontend
npm run dev &
FRONTEND_PID=$!
cd ..

echo ""
echo "=========================================================="
echo "✅ Application started successfully!"
echo ""
echo "📍 Frontend: http://localhost:5173"
echo "📍 Backend:  http://localhost:8000"
echo "📍 API Docs: http://localhost:8000/docs"
echo ""
echo "Press Ctrl+C to stop all servers"
echo "=========================================================="
echo ""

# Wait for user to stop
trap "echo ''; echo '🛑 Stopping servers...'; kill $BACKEND_PID $FRONTEND_PID 2>/dev/null; echo '✅ Servers stopped'; exit" INT TERM

wait
