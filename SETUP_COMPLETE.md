# Setup Complete - Vercel + Firebase Migration

## ✅ Migration Status

Your Warhammer Ranking System has been successfully configured for **Vercel** (hosting) and **Firebase Firestore** (database). All code follows official documentation and best practices.

## 🎯 What Changed

### Database Layer
- **Removed**: SQLite/PostgreSQL with SQL queries
- **Added**: Firebase Firestore NoSQL database
- **Implementation**: [firestore_service.py](backend/src/services/firestore_service.py) (600+ lines, fully async)
- **Old Service**: Preserved as `database_service.py.old` for reference

### Hosting & Deployment
- **Removed**: Render configuration (render.yaml, build.sh)
- **Added**: Vercel deployment configs
  - [vercel.json](vercel.json) - Frontend deployment
  - [vercel-backend.json](vercel-backend.json) - Backend deployment (optional)

### Environment Variables
- **Standardized**: Following Vite, Vercel, and Firebase best practices
- **Frontend**: Uses `VITE_` prefix (required by Vite)
- **Backend**: Uses Firebase Admin SDK variables
- **Local Dev**: [.env.development](frontend/.env.development) auto-loaded by Vite
- **Git Safe**: `.env` excluded, templates included

### Configuration Files
```
firebase.json              # Firebase project config
firestore.rules           # Security rules (read: all, write: authenticated)
firestore.indexes.json    # Query optimization indexes
.firebaserc               # Project aliases
```

## 📋 Quick Start

### 1. Firebase Setup (5 minutes)

```bash
# 1. Create Firebase project at https://console.firebase.google.com
# 2. Enable Firestore Database (Start in production mode)
# 3. Go to Project Settings > Service Accounts
# 4. Click "Generate New Private Key"
# 5. Save as backend/firebase-credentials.json

# 6. Configure backend environment
cd backend
cp .env.example .env
# Edit .env and set FIREBASE_PROJECT_ID=your-project-id
```

### 2. Local Development

```bash
# Install dependencies
cd frontend && npm install && cd ..
cd backend && pip install -r requirements.txt && cd ..

# Start both servers (from root)
chmod +x start-dev-firebase.sh
./start-dev-firebase.sh

# Or start individually:
# Backend: cd backend && uvicorn main:app --reload --host 0.0.0.0 --port 8000
# Frontend: cd frontend && npm run dev
```

Frontend: http://localhost:5173  
Backend API: http://localhost:8000  
API Docs: http://localhost:8000/docs

### 3. Deploy to Vercel (10 minutes)

#### Frontend Deployment
```bash
cd frontend
npm install -g vercel  # If not installed
vercel login
vercel --prod

# Set environment variable in Vercel dashboard:
# VITE_API_URL = https://your-backend-url.com/api
```

#### Backend Deployment Options

**Option A: Vercel (Serverless)**
```bash
cd backend
vercel --prod --config=../vercel-backend.json

# Set environment variables in Vercel dashboard:
# FIREBASE_PROJECT_ID = your-project-id
# FIREBASE_CREDENTIALS = <base64-encoded-credentials-json>
# SECRET_KEY = <generate-random-key>
```

**Option B: Railway/Render (Recommended for Always-On)**
- Backend works better on traditional hosting for persistent connections
- See [VERCEL_CONFIG.md](VERCEL_CONFIG.md) for details

## 📚 Documentation

- **[LOCAL_DEVELOPMENT.md](LOCAL_DEVELOPMENT.md)** - Complete local setup guide
- **[VERCEL_CONFIG.md](VERCEL_CONFIG.md)** - Vercel deployment instructions
- **[VERCEL_FIREBASE_DEPLOYMENT.md](VERCEL_FIREBASE_DEPLOYMENT.md)** - Detailed deployment walkthrough
- **[SQL_TO_FIRESTORE_COMPARISON.md](SQL_TO_FIRESTORE_COMPARISON.md)** - Database migration details

## 🔧 Environment Variables Reference

### Frontend (.env.development - local only)
```bash
VITE_API_URL=http://localhost:8000/api
```

### Frontend (Vercel Dashboard - production)
```bash
VITE_API_URL=https://your-backend-url.com/api
```

### Backend (.env - local only)
```bash
FIREBASE_PROJECT_ID=your-project-id
FIREBASE_CREDENTIALS_PATH=./firebase-credentials.json
SECRET_KEY=your-secret-key
API_HOST=0.0.0.0
API_PORT=8000
CORS_ORIGINS=http://localhost:5173,https://yourdomain.com
```

### Backend (Vercel/Railway Dashboard - production)
```bash
FIREBASE_PROJECT_ID=your-project-id
FIREBASE_CREDENTIALS=<base64-encoded-json>  # For Vercel
# OR
FIREBASE_CREDENTIALS_PATH=/path/to/credentials.json  # For Railway/Render
SECRET_KEY=your-secret-key
CORS_ORIGINS=https://yourdomain.com
```

## 🗄️ Database Structure

### Collections
- **players** - Player profiles and ratings
- **games** - Game records
- **matches** - Individual match results
- **campaigns** - Narrative campaigns
- **planets** - Campaign territory (solar system)
- **battle_events** - Campaign battle results

### Security Rules
- **Read**: Public (all users)
- **Write**: Authenticated users only
- **Deploy**: `firebase deploy --only firestore:rules`

### Indexes
- Player ratings sorted by rating/games played
- Match history by player/timestamp
- Campaign events by campaign/timestamp
- Deploy: `firebase deploy --only firestore:indexes`

## 🔄 Migration from Existing Data

If you have existing SQL data:

```bash
cd backend
python migrate_to_firestore.py

# Options:
# --clear   Clear Firestore before migration
# --dry-run Show what would be migrated
```

## ✅ Verification Checklist

- [ ] Firebase project created
- [ ] `firebase-credentials.json` downloaded to backend/
- [ ] `backend/.env` configured with FIREBASE_PROJECT_ID
- [ ] `npm install` completed in frontend/
- [ ] `pip install -r requirements.txt` completed in backend/
- [ ] Local servers start successfully (`./start-dev-firebase.sh`)
- [ ] Frontend loads at http://localhost:5173
- [ ] Backend API docs accessible at http://localhost:8000/docs
- [ ] Firestore security rules deployed (`firebase deploy --only firestore:rules`)
- [ ] Firestore indexes deployed (`firebase deploy --only firestore:indexes`)

## 🚨 Troubleshooting

### "No such file or directory: firebase-credentials.json"
- Download service account key from Firebase Console
- Save as `backend/firebase-credentials.json`
- Ensure file is in .gitignore (already configured)

### "VITE_API_URL is undefined"
- Frontend: Ensure `.env.development` exists with `VITE_API_URL=http://localhost:8000/api`
- Vercel: Set VITE_API_URL in project environment variables

### "Firebase permission denied"
- Deploy security rules: `firebase deploy --only firestore:rules`
- For development, temporarily allow all writes in firestore.rules (not for production!)

### "Port 5173 already in use"
- Stop existing Vite server: `pkill -f vite`
- Or change port in `vite.config.ts`

### "Module not found: firebase-admin"
- Run `pip install -r requirements.txt` in backend/
- Ensure using Python virtual environment

## 🏗️ Architecture

```
Warhammer Ranking System
├── Frontend (React + Vite)
│   ├── Host: Vercel
│   ├── Port: 5173 (dev), 443 (prod)
│   ├── Build: npm run build → dist/
│   └── Env: VITE_API_URL
│
├── Backend (FastAPI + Python)
│   ├── Host: Vercel/Railway/Render
│   ├── Port: 8000
│   ├── Database: Firestore
│   └── Env: FIREBASE_PROJECT_ID, FIREBASE_CREDENTIALS
│
└── Database (Firebase Firestore)
    ├── Host: Google Cloud
    ├── Type: NoSQL Document Store
    ├── Security: firestore.rules
    └── Indexes: firestore.indexes.json
```

## 📝 Next Steps

1. **Complete Firebase Setup** - Follow section 1 above
2. **Test Locally** - Run `./start-dev-firebase.sh` and verify everything works
3. **Deploy Frontend** - Push to Vercel with `vercel --prod`
4. **Deploy Backend** - Choose Vercel/Railway/Render and configure environment
5. **Configure Production** - Set VITE_API_URL in Vercel to point to backend
6. **Test Production** - Visit your Vercel URL and verify functionality
7. **Optional: Migrate Data** - If you have existing SQL data, run migration script

## 🎮 Features

- ✅ Player registration and management
- ✅ Glicko-2 rating system
- ✅ Match recording (1v1, FFA, team games)
- ✅ Narrative campaign system
- ✅ 3D solar system visualization
- ✅ Campaign battle tracking
- ✅ Territory control mechanics
- ✅ Requisition points system

## 📞 Support

For issues with:
- **Vercel**: https://vercel.com/docs
- **Firebase**: https://firebase.google.com/docs/firestore
- **Vite**: https://vitejs.dev/guide/
- **This Project**: Check [LOCAL_DEVELOPMENT.md](LOCAL_DEVELOPMENT.md)

---

**Status**: ✅ Configuration Complete - Ready for Development & Deployment  
**Last Updated**: Migration to Vercel + Firebase  
**Database**: Firestore (NoSQL)  
**Hosting**: Vercel (Frontend + Optional Backend)
