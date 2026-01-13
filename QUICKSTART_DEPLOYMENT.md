# Quick Start Guide: Vercel + Firebase Deployment

## Prerequisites
- Node.js installed
- Python 3.9+ installed
- Firebase account
- Vercel account
- Git repository

## Step 1: Firebase Setup (5 minutes)

1. **Create Firebase project**: https://console.firebase.google.com/
2. **Enable Firestore**: Build → Firestore Database → Create Database (Production mode)
3. **Download credentials**:
   - Project Settings → Service Accounts
   - Generate new private key
   - Save as `firebase-credentials.json` (DON'T commit to Git!)
4. **Update `.firebaserc`**: Replace `your-firebase-project-id` with your actual ID
5. **Deploy Firestore rules**:
   ```bash
   npm install -g firebase-tools
   firebase login
   firebase deploy --only firestore
   ```

## Step 2: Install Dependencies

```bash
# Backend
cd backend
pip install -r requirements.txt

# Frontend
cd ../frontend
npm install
```

## Step 3: Configure Environment Variables

**Backend** - Create `backend/.env`:
```env
FIREBASE_PROJECT_ID=your-firebase-project-id
FIREBASE_CREDENTIALS_PATH=../firebase-credentials.json
SECRET_KEY=your-random-secret-key
CORS_ORIGINS=http://localhost:5173
```

**Frontend** - Create `frontend/.env`:
```env
VITE_API_URL=http://localhost:8000/api
```

## Step 4: Test Locally

```bash
# Terminal 1 - Backend
cd backend
python main.py

# Terminal 2 - Frontend
cd frontend
npm run dev
```

Visit: http://localhost:5173

## Step 5: Deploy to Vercel

### Deploy Frontend:
```bash
cd frontend
vercel --prod

# Set environment variable in Vercel Dashboard:
# VITE_API_URL = (your backend URL)
```

### Deploy Backend - Option A (Vercel):
```bash
cd backend
vercel --prod

# In Vercel Dashboard, add:
# FIREBASE_PROJECT_ID = your-project-id
# FIREBASE_CREDENTIALS = (base64 encoded credentials)
# SECRET_KEY = your-secret-key
# CORS_ORIGINS = https://your-frontend.vercel.app
```

To encode credentials for Vercel:
```bash
cat firebase-credentials.json | base64 -w 0
```

### Deploy Backend - Option B (Railway - Recommended):
1. Go to https://railway.app/
2. Create new project from GitHub repo
3. Select `backend` directory
4. Add environment variables:
   - `FIREBASE_PROJECT_ID`
   - `FIREBASE_CREDENTIALS_PATH` (upload credentials file)
   - `SECRET_KEY`
   - `CORS_ORIGINS`
   - `API_PORT=8000`

## Step 6: Update Frontend API URL

In Vercel Dashboard (frontend project):
- Update `VITE_API_URL` to your backend URL
- Redeploy frontend

## Done! 🎉

Your app is now live:
- Frontend: `https://your-app.vercel.app`
- Backend: `https://your-backend.vercel.app` or `https://your-backend.railway.app`

## Troubleshooting

**CORS errors**: Update `CORS_ORIGINS` in backend environment variables
**Firebase errors**: Check credentials are correct and Firestore is enabled
**Build errors**: Check logs in Vercel/Railway dashboard

For detailed instructions, see: `VERCEL_FIREBASE_DEPLOYMENT.md`
