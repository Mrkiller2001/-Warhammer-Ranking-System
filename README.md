# Warhammer Ranking System

Modern full-stack application for tracking Warhammer game rankings and campaigns using the Glicko-2 rating system with 3D solar system campaign visualization.

## 🎯 New Here?

**→ [START_HERE.md](START_HERE.md)** ← Follow this guide for 10-minute setup

## 🚀 Quick Start

```bash
# 1. Setup Firebase (one-time)
# - Create project at https://console.firebase.google.com
# - Download credentials to backend/firebase-credentials.json
# - Copy backend/.env.example to backend/.env and set FIREBASE_PROJECT_ID

# 2. Install dependencies
cd frontend && npm install && cd ..
cd backend && pip install -r requirements.txt && cd ..

# 3. Start development servers
./start-dev-firebase.sh
```

**Access:**
- Frontend: http://localhost:5173
- Backend API: http://localhost:8000
- API Docs: http://localhost:8000/docs

## 📚 Documentation

- **[START_HERE.md](START_HERE.md)** - 🎯 **Start here!** 10-minute setup guide
- **[MIGRATION_SUMMARY.md](MIGRATION_SUMMARY.md)** - ✅ What changed in the migration
- **[LOCAL_DEVELOPMENT.md](LOCAL_DEVELOPMENT.md)** - Complete local setup guide
- **[VERCEL_CONFIG.md](VERCEL_CONFIG.md)** - Vercel deployment instructions
- **[KNOWN_ISSUES.md](KNOWN_ISSUES.md)** - Known issues and workarounds

## 🛠️ Tech Stack

- **Frontend:** React 18 + TypeScript + Vite + Three.js (3D visualization)
- **Backend:** Python FastAPI (async REST API)
- **Database:** Firebase Firestore (NoSQL)
- **Hosting:** Vercel (frontend + optional backend)
- **Rating System:** Glicko-2 algorithm

## Project Structure

```
├── backend/           # FastAPI REST API
│   ├── src/
│   │   ├── api/      # API routes
│   │   └── services/ # Business logic
│   └── main.py
├── frontend/          # React + TypeScript
│   └── src/
│       ├── api/            # Axios API client
│       ├── components/    # React components (3D solar system, modals)
│       ├── pages/         # Page components
│       └── types/         # TypeScript type definitions
├── firebase.json          # Firebase configuration
├── firestore.rules        # Firestore security rules
└── start-dev-firebase.sh  # Development startup script
```

## 🎮 Features

### Core Functionality
- ✅ **Player Management** - Register and track players
- ✅ **Glicko-2 Rating System** - Automatic rating calculations with RD and volatility
- ✅ **Match Recording** - Support for 1v1, FFA, and team games
- ✅ **Rankings & Statistics** - Real-time leaderboards

### Campaign System
- ✅ **Narrative Campaigns** - Warhammer 40K Crusade-style progression
- ✅ **3D Solar System Visualization** - Interactive Three.js planet map
- ✅ **Territory Control** - Planetary battle tracking
- ✅ **Requisition Points** - Win/loss rewards for army upgrades
- ✅ **Supply Limits** - Progressive army size increases

## 🔥 Firebase Database Structure

### Collections
```
players/          # Player profiles, ratings, campaign stats
games/            # Game types (40K, Kill Team, etc.)
matches/          # Individual match results
campaigns/        # Campaign metadata
planets/          # Campaign territory (solar system)
battle_events/    # Campaign battle history
```

### Security
- **Read**: Public access (all users can view)
- **Write**: Authenticated users only
- **Rules**: Defined in [firestore.rules](firestore.rules)

## 📡 API Examples

### Player Management
```bash
# Register a player
curl -X POST http://localhost:8000/api/v1/players \
  -H "Content-Type: application/json" \
  -d '{"discord_id": "123456", "display_name": "PlayerOne"}'

# Get player rankings
curl http://localhost:8000/api/v1/rankings/game/warhammer-40k
```

### Match Recording
```bash
# Record 1v1 match
curl -X POST http://localhost:8000/api/v1/matches \
  -H "Content-Type: application/json" \
  -d '{
    "game_id": "warhammer-40k",
    "winner_discord_id": "123456",
    "loser_discord_id": "789012"
  }'

# Record FFA (Free-For-All)
curl -X POST http://localhost:8000/api/v1/matches/ffa \
  -H "Content-Type: application/json" \
  -d '{
    "game_id": "warhammer-40k",
    "placements": [
      {"discord_id": "player1", "placement": 1},
      {"discord_id": "player2", "placement": 2},
      {"discord_id": "player3", "placement": 3}
    ]
  }'
```

### Campaign Management
```bash
# Create campaign
curl -X POST http://localhost:8000/api/v1/campaigns \
  -H "Content-Type: application/json" \
  -d '{"name": "Crusade Alpha", "game_id": "warhammer-40k"}'

# Record campaign battle
curl -X POST http://localhost:8000/api/v1/campaigns/{campaign_id}/battles \
  -H "Content-Type: application/json" \
  -d '{
    "attacker_discord_id": "player1",
    "defender_discord_id": "player2",
    "planet_id": "terra",
    "attacker_points": 65,
    "defender_points": 45
  }'
```

## 🌐 Environment Configuration

### Local Development
```bash
# Backend (.env)
FIREBASE_PROJECT_ID=your-project-id
FIREBASE_CREDENTIALS_PATH=./firebase-credentials.json
API_HOST=0.0.0.0
API_PORT=8000

# Frontend (.env.development - auto-loaded by Vite)
VITE_API_URL=http://localhost:8000/api
```

### Production (Vercel)
```bash
# Frontend (Vercel Dashboard)
VITE_API_URL=https://your-backend-url.com/api

# Backend (Vercel/Railway Dashboard)
FIREBASE_PROJECT_ID=your-project-id
FIREBASE_CREDENTIALS=<base64-encoded-json>
SECRET_KEY=<random-secret>
CORS_ORIGINS=https://yourdomain.com
```

## 🚀 Deployment

### Frontend (Vercel)
```bash
cd frontend
vercel --prod
# Set VITE_API_URL in Vercel dashboard
```

### Backend Options

**Option A: Vercel (Serverless)**
```bash
vercel --prod --config=vercel-backend.json
```

**Option B: Railway/Render (Recommended)**
- Better for persistent connections
- See [VERCEL_CONFIG.md](VERCEL_CONFIG.md) for details

## 🧪 Testing

```bash
# Backend tests (if implemented)
cd backend
pytest

# Frontend tests
cd frontend
npm test
```

## 🔧 Development Commands

```bash
# Backend
cd backend
pip install -r requirements.txt       # Install dependencies
uvicorn main:app --reload            # Start dev server
python migrate_to_firestore.py       # Migrate SQL data (if needed)

# Frontend
cd frontend
npm install                          # Install dependencies
npm run dev                          # Start dev server (port 5173)
npm run build                        # Build for production
npm run preview                      # Preview production build

# Firebase
firebase deploy --only firestore:rules    # Deploy security rules
firebase deploy --only firestore:indexes  # Deploy query indexes
```

## 📊 Glicko-2 Rating System

- **Initial Rating**: 1500
- **Initial RD**: 350
- **Volatility**: 0.06
- **Tau**: 0.5
- **Epsilon**: 0.000001

Ratings update after each match based on:
- Opponent's rating
- Rating deviation (uncertainty)
- Volatility (consistency)
- Game outcome

## 📝 License

MIT License - See LICENSE file for details

---

**Status**: ✅ Ready for Development & Deployment  
**Database**: Firebase Firestore (NoSQL)  
**Hosting**: Vercel  
**Rating Algorithm**: Glicko-2
