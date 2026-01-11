# Warhammer Ranking System

Modern full-stack application for tracking Warhammer game rankings and campaigns using the Glicko-2 rating system.

## Stack

- **Backend:** Python FastAPI (RESTful API)
- **Frontend:** React + TypeScript
- **Database:** SQLite

## Quick Start

```bash
# Start everything
./scripts/start-all.sh
```

**Or start separately:**

```bash
# Terminal 1 - Backend
cd backend
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
python main.py

# Terminal 2 - Frontend
cd frontend
npm install
npm run dev
```

## Access

- Frontend: http://localhost:3000
- Backend API: http://localhost:8000
- API Docs: http://localhost:8000/docs

## Project Structure

```
├── backend/           # FastAPI REST API
│   ├── src/
│   │   ├── api/      # API routes
│   │   └── services/ # Business logic
│   └── main.py
├── frontend/          # React + TypeScript
│   └── src/
│       ├── api/      # API client
│       └── pages/    # React pages
└── scripts/          # Startup scripts
```

## Features

- Automatic Glicko-2 rating calculations
- Campaign management with requisition points
- Player rankings and statistics
- Match history tracking
- RESTful API with auto-generated docs

## API Examples

```bash
# Create a game
curl -X POST http://localhost:8000/api/v1/games \
  -H "Content-Type: application/json" \
  -d '{"name": "warhammer-40k", "display_name": "Warhammer 40,000"}'

# Record a match
curl -X POST http://localhost:8000/api/v1/matches \
  -H "Content-Type: application/json" \
  -d '{"game_id": 1, "winner_discord_id": "123", "loser_discord_id": "456"}'

# Get rankings
curl http://localhost:8000/api/v1/rankings/game/1
```

## Environment Setup

### Backend (.env)
```bash
DATABASE_URL=sqlite+aiosqlite:///./rankings.db
API_PORT=8000
CORS_ORIGINS=http://localhost:3000
```

### Frontend (.env)
```bash
VITE_API_BASE_URL=http://localhost:8000/api/v1
```
