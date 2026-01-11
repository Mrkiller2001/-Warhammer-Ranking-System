#!/bin/bash

# Full stack startup script

echo "🚀 Starting Full Warhammer Ranking System..."

# Start backend in background
echo "📡 Starting backend..."
./scripts/start-backend.sh &
BACKEND_PID=$!

# Wait a moment for backend to initialize
sleep 3

# Start frontend
echo "🎨 Starting frontend..."
./scripts/start-frontend.sh &
FRONTEND_PID=$!

echo ""
echo "✅ Application started!"
echo "📡 Backend API: http://localhost:8000"
echo "📚 API Docs: http://localhost:8000/docs"
echo "🎨 Frontend: http://localhost:3000"
echo ""
echo "Press Ctrl+C to stop all services"

# Wait for interrupt
trap "kill $BACKEND_PID $FRONTEND_PID; exit" INT
wait
