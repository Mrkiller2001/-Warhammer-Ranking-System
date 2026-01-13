# Vercel Configuration Documentation
# See: https://vercel.com/docs/project-configuration

# This project uses a monorepo structure with separate frontend and backend.
# Use this file for frontend deployment.
# For backend deployment, see vercel-backend.json or use Railway/Render.

## Frontend Deployment (This Config)

### Deploy Frontend:
```bash
vercel --prod
```

### Environment Variables (Set in Vercel Dashboard):
- `VITE_API_URL` - Your backend API URL

## Backend Deployment Options

### Option 1: Vercel Serverless (vercel-backend.json)
- Deploy: `vercel --prod --config vercel-backend.json`
- Limitations: Cold starts, 15MB limit
- Good for: Low-traffic applications

### Option 2: Railway/Render (Recommended)
- Always-on server
- Better performance
- No cold starts
- See: QUICKSTART_DEPLOYMENT.md

## Environment Variables

### Frontend (.env files):
- `.env.development` - Local development (auto-loaded)
- `.env.production` - Production build
- Set `VITE_API_URL` in Vercel Dashboard for production

### Backend (.env files):
- `backend/.env` - Local development
- Set in Vercel/Railway dashboard for production:
  - FIREBASE_PROJECT_ID
  - FIREBASE_CREDENTIALS (base64) or FIREBASE_CREDENTIALS_PATH
  - SECRET_KEY
  - CORS_ORIGINS

## Local Development

See LOCAL_DEVELOPMENT.md for setup instructions.

Quick start:
```bash
./start-dev-firebase.sh
```
