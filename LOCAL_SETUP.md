# Local Development Setup Guide

This guide will help you set up and run the Warhammer Ranking System on your local machine.

## Prerequisites

- **Python 3.10+** (for backend)
- **Node.js 18+** and **npm** (for frontend)
- **Git** (to clone the repository)

## Quick Start

The fastest way to get started is to use the provided startup script:

```bash
./scripts/start-all.sh
```

This will start both the backend and frontend automatically.

## Manual Setup

If you prefer to set up services individually or need more control:

### 1. Backend Setup

```bash
# Navigate to backend directory
cd backend

# Create a Python virtual environment
python3 -m venv venv

# Activate the virtual environment
# On Linux/Mac:
source venv/bin/activate
# On Windows:
# venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Copy the example environment file (if needed)
cp .env.example .env

# Start the backend server
python main.py
```

The backend API will be available at:
- **API**: http://localhost:8000
- **API Documentation**: http://localhost:8000/docs
- **Health Check**: http://localhost:8000/health

### 2. Frontend Setup

In a new terminal:

```bash
# Navigate to frontend directory
cd frontend

# Install dependencies
npm install

# Start the development server
npm run dev
```

The frontend will be available at:
- **Frontend**: http://localhost:3000

## Environment Variables

### Backend (.env)

The backend uses a local SQLite database by default. The `.env.example` file has been copied to `.env` with these defaults:

```env
# Database - SQLite for local development
DATABASE_URL=sqlite+aiosqlite:///./rankings.db

# API Configuration
API_HOST=0.0.0.0
API_PORT=8000
API_RELOAD=True

# Security
SECRET_KEY=dev-secret-key-change-in-production
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

# CORS - Allow local frontend
CORS_ORIGINS=http://localhost:3000,http://localhost:5173

# Environment
ENVIRONMENT=development

# Discord Bot (optional)
DISCORD_TOKEN=
DISCORD_GUILD_ID=
```

### Frontend (.env.local)

Create a `.env.local` file in the frontend directory:

```env
# API Base URL - Points to local backend
VITE_API_BASE_URL=http://localhost:8000/api/v1
```

## Database

The SQLite database (`rankings.db`) will be created automatically in the backend directory on first run. No manual setup is needed.

## Project Structure

```
├── backend/                 # FastAPI REST API
│   ├── src/
│   │   ├── api/            # API routes
│   │   ├── services/       # Business logic
│   │   ├── config.py       # Configuration
│   │   ├── models.py       # Data models
│   │   └── dependencies.py # Dependency injection
│   ├── main.py             # Application entry point
│   ├── requirements.txt    # Python dependencies
│   └── .env                # Local environment variables
├── frontend/               # React + TypeScript
│   ├── src/
│   │   ├── api/           # API client
│   │   ├── components/    # React components
│   │   ├── pages/         # Page components
│   │   └── types/         # TypeScript types
│   ├── package.json       # Node dependencies
│   └── .env.local         # Local environment variables
└── scripts/               # Utility scripts
    └── start-all.sh       # Start both services
```

## Development Workflow

### Running Tests

Backend tests:
```bash
cd backend
pytest
```

Frontend linting:
```bash
cd frontend
npm run lint
```

### Making Changes

1. **Backend Changes**: The server will automatically reload when you save Python files (hot reload is enabled)
2. **Frontend Changes**: The Vite dev server automatically refreshes the browser

### API Development

- **OpenAPI Docs**: http://localhost:8000/docs (interactive Swagger UI)
- **ReDoc**: http://localhost:8000/redoc (alternative documentation)
- **OpenAPI JSON**: http://localhost:8000/openapi.json (raw specification)

## Common Issues

### Port Already in Use

If port 8000 or 3000 is already in use:

**Backend**: Change `API_PORT` in `.env`
**Frontend**: Change the port in `vite.config.ts` or use:
```bash
npm run dev -- --port 3001
```

### Database Locked

If you get a "database is locked" error:
```bash
# Stop the backend
# Delete the database file
rm backend/rankings.db
# Restart the backend - it will recreate the database
```

### Module Not Found

**Backend**:
```bash
cd backend
pip install -r requirements.txt
```

**Frontend**:
```bash
cd frontend
npm install
```

### CORS Errors

Make sure `CORS_ORIGINS` in backend `.env` includes your frontend URL:
```env
CORS_ORIGINS=http://localhost:3000,http://localhost:5173
```

## Using Individual Scripts

You can also use the individual startup scripts:

```bash
# Start only backend
./scripts/start-backend.sh

# Start only frontend (in a separate terminal)
./scripts/start-frontend.sh
```

## Discord Bot Integration (Optional)

To enable Discord bot features:

1. Create a Discord bot at https://discord.com/developers/applications
2. Get your bot token and guild (server) ID
3. Update your backend `.env`:
   ```env
   DISCORD_TOKEN=your_bot_token_here
   DISCORD_GUILD_ID=your_guild_id_here
   ```

## Next Steps

- Review the API documentation at http://localhost:8000/docs
- Check out the frontend at http://localhost:3000
- Try creating a game, adding players, and recording matches
- Explore the campaign system with the solar system visualization

## Production Deployment

When you're ready to deploy to production, see [DEPLOYMENT.md](DEPLOYMENT.md) for instructions on deploying to Render.
