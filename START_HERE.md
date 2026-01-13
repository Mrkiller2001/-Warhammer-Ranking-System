# 🎯 Start Here - Quick Setup Guide

## Overview
Your Warhammer Ranking System is configured for **Vercel** (hosting) and **Firebase Firestore** (database). This guide gets you up and running in 10 minutes.

## ⚡ 3-Step Setup

### Step 1: Firebase Setup (5 minutes)

1. **Create Firebase Project**
   - Go to https://console.firebase.google.com
   - Click "Add Project" → Name it → Create
   
2. **Enable Firestore**
   - In left sidebar: Build → Firestore Database
   - Click "Create Database"
   - Choose "Start in production mode"
   - Select location (closest to you)

3. **Get Service Account Key**
   - Project Settings (⚙️ icon) → Service Accounts
   - Click "Generate New Private Key"
   - Save file as `backend/firebase-credentials.json`

4. **Configure Backend**
   ```bash
   cd backend
   cp .env.example .env
   # Edit .env and set FIREBASE_PROJECT_ID=your-project-id
   ```

### Step 2: Install Dependencies (3 minutes)

```bash
# Frontend
cd frontend
npm install

# Backend
cd ../backend
pip install -r requirements.txt
```

### Step 3: Start Development (1 minute)

```bash
# From project root
chmod +x start-dev-firebase.sh
./start-dev-firebase.sh
```

**Access your app:**
- Frontend: http://localhost:5173
- Backend API: http://localhost:8000
- API Docs: http://localhost:8000/docs

## ✅ Verify It Works

1. Open http://localhost:5173
2. Try registering a test player
3. Record a test match
4. Check Firebase Console → Firestore Database to see the data

## 📚 Documentation

- **Having issues?** → [LOCAL_DEVELOPMENT.md](LOCAL_DEVELOPMENT.md)
- **Ready to deploy?** → [VERCEL_CONFIG.md](VERCEL_CONFIG.md)
- **What changed?** → [MIGRATION_SUMMARY.md](MIGRATION_SUMMARY.md)
- **Known issues?** → [KNOWN_ISSUES.md](KNOWN_ISSUES.md)

## 🚨 Common Issues

### "Cannot find firebase-credentials.json"
- Download it from Firebase Console (Step 1.3 above)
- Save it as `backend/firebase-credentials.json`
- Ensure it's listed in `.gitignore` (already configured)

### "Module not found: firebase-admin"
```bash
cd backend && pip install -r requirements.txt
```

### "VITE_API_URL is not defined"
- File `frontend/.env.development` should exist (already created)
- Contains: `VITE_API_URL=http://localhost:8000/api`

### "Permission denied" errors in Firebase
```bash
firebase deploy --only firestore:rules
```

## 🚀 What's Next?

### For Local Development
You're done! Just run `./start-dev-firebase.sh` whenever you want to develop.

### For Deployment
1. Deploy frontend to Vercel: `cd frontend && vercel --prod`
2. Deploy backend (choose one):
   - Vercel: `vercel --prod --config=vercel-backend.json`
   - Railway: https://railway.app (recommended)
   - Render: https://render.com
3. See [VERCEL_CONFIG.md](VERCEL_CONFIG.md) for details

## 🎮 Features Available

### ✅ Working Now
- Player registration
- Match recording (1v1, FFA, teams)
- Glicko-2 ratings
- Rankings & statistics
- 3D solar system visualization

### ⚠️ Needs Testing
- Campaign narrative features
- See [KNOWN_ISSUES.md](KNOWN_ISSUES.md)

## 📁 Key Files

```
Important Configuration Files:
├── backend/
│   ├── .env.example          # Copy to .env and configure
│   ├── firebase-credentials.json  # Download from Firebase
│   └── src/services/
│       └── firestore_service.py   # Main database service
├── frontend/
│   ├── .env.development      # Auto-loaded by Vite (already configured)
│   └── src/api/client.ts     # API client (uses VITE_API_URL)
├── firebase.json              # Firebase config
├── firestore.rules            # Security rules
├── vercel.json                # Frontend deployment
└── start-dev-firebase.sh      # Startup script
```

## 🆘 Still Stuck?

1. Check [LOCAL_DEVELOPMENT.md](LOCAL_DEVELOPMENT.md) for detailed setup
2. Check [KNOWN_ISSUES.md](KNOWN_ISSUES.md) for known problems
3. Verify Firebase credentials are correct
4. Check that ports 5173 and 8000 are not in use
5. Try restarting the servers

## 🎉 Success!

Once you see:
```
Frontend running on http://localhost:5173
Backend running on http://localhost:8000
```

You're ready to develop! 

**Happy coding! ⚔️**

---

**Tech Stack**: React + TypeScript + Vite + FastAPI + Firebase Firestore  
**Status**: ✅ Ready for Development  
**Estimated Setup Time**: 10 minutes  
**Deployment**: Vercel (frontend) + Railway/Vercel (backend)
