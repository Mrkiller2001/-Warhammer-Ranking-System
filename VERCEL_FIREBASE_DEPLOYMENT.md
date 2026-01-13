# Vercel + Firebase Deployment Guide

This guide walks you through deploying the Warhammer Ranking System to Vercel (frontend) and Firebase (database).

## Table of Contents
1. [Firebase Setup](#firebase-setup)
2. [Vercel Frontend Deployment](#vercel-frontend-deployment)
3. [Backend Deployment Options](#backend-deployment-options)
4. [Environment Configuration](#environment-configuration)
5. [Post-Deployment Steps](#post-deployment-steps)

---

## Firebase Setup

### 1. Create Firebase Project

1. Go to [Firebase Console](https://console.firebase.google.com/)
2. Click "Add project"
3. Enter project name (e.g., `warhammer-ranking-system`)
4. Disable Google Analytics (optional)
5. Click "Create project"

### 2. Set up Firestore Database

1. In Firebase Console, go to "Build" → "Firestore Database"
2. Click "Create database"
3. Choose "Start in production mode" (we have security rules configured)
4. Select your preferred location
5. Click "Enable"

### 3. Generate Service Account Credentials

1. Go to Project Settings (gear icon) → "Service accounts"
2. Click "Generate new private key"
3. Download the JSON file
4. **IMPORTANT**: Keep this file secure! Add it to `.gitignore`
5. Save it as `firebase-credentials.json` in your project root (for local dev)

### 4. Deploy Security Rules and Indexes

```bash
# Install Firebase CLI
npm install -g firebase-tools

# Login to Firebase
firebase login

# Initialize Firebase in your project
firebase init firestore

# Select your project
# Use existing firestore.rules and firestore.indexes.json

# Deploy rules and indexes
firebase deploy --only firestore:rules,firestore:indexes
```

### 5. Update Firebase Project ID

Update `.firebaserc` with your actual project ID:
```json
{
  "projects": {
    "default": "your-actual-firebase-project-id"
  }
}
```

---

## Vercel Frontend Deployment

### 1. Install Vercel CLI

```bash
npm install -g vercel
```

### 2. Login to Vercel

```bash
vercel login
```

### 3. Deploy Frontend

```bash
# Navigate to project root
cd /path/to/Warhammer-Ranking-System

# Deploy (first time)
vercel

# Follow prompts:
# - Setup and deploy? Yes
# - Which scope? Your account
# - Link to existing project? No
# - Project name: warhammer-ranking-frontend
# - Directory: frontend
# - Override settings? No

# Production deployment
vercel --prod
```

### 4. Configure Frontend Environment Variables

In Vercel Dashboard:
1. Go to your project → Settings → Environment Variables
2. Add:
   - `VITE_API_URL`: Your backend URL (see backend deployment section)

---

## Backend Deployment Options

You have two options for backend deployment:

### Option A: Vercel Serverless Functions (Recommended for smaller loads)

**Pros**: Simple, all in one place
**Cons**: Cold starts, Python support limitations

```bash
# Deploy backend to Vercel
cd backend
vercel --prod

# In Vercel Dashboard, configure:
# - Project name: warhammer-ranking-backend
# - Framework Preset: Other
```

**Environment Variables** (in Vercel Dashboard):
- `FIREBASE_PROJECT_ID`: Your Firebase project ID
- `FIREBASE_CREDENTIALS`: Base64 encoded Firebase credentials JSON
  ```bash
  # Encode credentials:
  cat firebase-credentials.json | base64 -w 0
  ```
- `SECRET_KEY`: Your API secret key
- `CORS_ORIGINS`: Your frontend URL (e.g., `https://your-frontend.vercel.app`)

### Option B: Railway/Render (Recommended for better performance)

**Pros**: Always-on, better for persistent backends
**Cons**: Separate service to manage

#### Railway Deployment:

1. Go to [Railway](https://railway.app/)
2. Connect your GitHub repo
3. Create new project from repo
4. Select `backend` as root directory
5. Add environment variables (see below)
6. Deploy!

#### Environment Variables for Railway/Render:
- `FIREBASE_PROJECT_ID`
- `FIREBASE_CREDENTIALS_PATH` (or upload credentials file)
- `SECRET_KEY`
- `CORS_ORIGINS`
- `API_HOST=0.0.0.0`
- `API_PORT=8000`

---

## Environment Configuration

### Local Development

Create `.env` file in project root:

```bash
cp .env.example .env
```

Edit `.env` with your values:
```env
# Firebase
FIREBASE_PROJECT_ID=your-firebase-project-id
FIREBASE_CREDENTIALS_PATH=./firebase-credentials.json

# API
SECRET_KEY=local-dev-secret-key
CORS_ORIGINS=http://localhost:5173

# Frontend
VITE_API_URL=http://localhost:8000/api
```

### Production Configuration

**Frontend** (Vercel Dashboard → Environment Variables):
- `VITE_API_URL`: `https://your-backend-url.com/api`

**Backend** (Vercel/Railway Dashboard → Environment Variables):
- `FIREBASE_PROJECT_ID`: Your Firebase project ID
- `FIREBASE_CREDENTIALS`: (Vercel) Base64 encoded JSON
- `FIREBASE_CREDENTIALS_PATH`: (Railway) Path to uploaded file
- `SECRET_KEY`: Strong random string
- `CORS_ORIGINS`: Your frontend URL
- `API_HOST`: `0.0.0.0`
- `API_PORT`: `8000` (or Vercel default)

---

## Post-Deployment Steps

### 1. Test the Deployment

```bash
# Test backend health
curl https://your-backend-url.com/api/health

# Test frontend
open https://your-frontend-url.vercel.app
```

### 2. Initialize Database

If starting fresh, you may need to create initial game entries through the API:

```bash
# Create a game
curl -X POST https://your-backend-url.com/api/games \
  -H "Content-Type: application/json" \
  -d '{
    "name": "warhammer40k",
    "display_name": "Warhammer 40,000"
  }'
```

### 3. Monitor Firebase Usage

1. Go to Firebase Console → Usage and Billing
2. Monitor:
   - Firestore reads/writes
   - Storage usage
   - Network egress

### 4. Set up Firebase Backup (Recommended)

1. Go to Firebase Console → Firestore Database → Data
2. Click "Import/Export"
3. Set up automated backups to Google Cloud Storage

---

## Data Migration from SQL to Firestore

If you have existing data in SQLite/PostgreSQL, you'll need to migrate:

### Migration Script

Create a migration script to:
1. Read from old database
2. Transform data structure
3. Write to Firestore

```python
# Example migration snippet
import asyncio
from src.services.database_service import DatabaseService
from src.services.firestore_service import FirestoreService

async def migrate_data():
    old_db = DatabaseService()
    new_db = FirestoreService()
    
    # Migrate games
    games = await old_db.get_all_games()
    for game in games:
        await new_db.create_game(
            name=game['name'],
            display_name=game['display_name']
        )
    
    # Migrate players, matches, campaigns, etc.
    # ... (implement based on your data structure)

if __name__ == "__main__":
    asyncio.run(migrate_data())
```

---

## Troubleshooting

### Firebase Connection Issues

- Verify `FIREBASE_PROJECT_ID` is correct
- Check Firebase credentials are properly encoded
- Ensure Firestore is enabled in Firebase Console

### CORS Errors

- Update `CORS_ORIGINS` in backend environment variables
- Include both `http://` and `https://` versions if needed

### Vercel Build Failures

- Check build logs in Vercel Dashboard
- Ensure all dependencies are in `package.json` or `requirements.txt`
- Verify `vercel-build` script exists in `package.json`

### Cold Starts (Vercel Serverless)

- Consider upgrading to Vercel Pro for faster cold starts
- Or switch to Railway/Render for always-on backend

---

## Cost Estimation

### Firebase (Free Tier includes):
- 50,000 document reads/day
- 20,000 document writes/day
- 1 GB storage
- **Enough for small-medium communities**

### Vercel (Hobby Tier - Free):
- 100 GB bandwidth/month
- Unlimited serverless function executions
- **Perfect for frontend hosting**

### Railway (Free Tier):
- $5 free credit/month
- ~500 hours of uptime
- **Great for backend hosting**

---

## Security Best Practices

1. ✅ Keep Firebase credentials out of Git
2. ✅ Use environment variables for all secrets
3. ✅ Enable Firestore security rules
4. ✅ Rotate `SECRET_KEY` regularly
5. ✅ Use HTTPS only in production
6. ✅ Monitor Firebase security alerts
7. ✅ Set up Firebase App Check (optional)

---

## Next Steps

1. Set up monitoring with Vercel Analytics
2. Configure custom domain
3. Set up CI/CD with GitHub Actions
4. Implement Firebase Authentication (if needed)
5. Add Firebase Cloud Functions for complex operations

---

## Support

For issues:
- Firebase: [Firebase Support](https://firebase.google.com/support)
- Vercel: [Vercel Support](https://vercel.com/support)
- Project Issues: GitHub Issues
