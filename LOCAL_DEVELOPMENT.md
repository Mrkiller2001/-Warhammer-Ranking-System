# =============================================================================
# LOCAL DEVELOPMENT SETUP GUIDE
# =============================================================================

## Quick Start

1. **Backend Setup:**
   ```bash
   cd backend
   cp .env.example .env
   # Edit .env and set your Firebase project ID
   python3 -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   pip install -r requirements.txt
   ```

2. **Frontend Setup:**
   ```bash
   cd frontend
   npm install
   # .env.development is used automatically for local dev
   ```

3. **Firebase Setup:**
   - Go to https://console.firebase.google.com/
   - Create/select your project
   - Go to Project Settings > Service Accounts
   - Generate new private key
   - Save as `firebase-credentials.json` in project root

4. **Start Development:**
   ```bash
   # From project root:
   ./start-dev-firebase.sh
   
   # Or manually:
   # Terminal 1 - Backend
   cd backend && source venv/bin/activate && python main.py
   
   # Terminal 2 - Frontend
   cd frontend && npm run dev
   ```

5. **Access:**
   - Frontend: http://localhost:5173
   - Backend: http://localhost:8000
   - API Docs: http://localhost:8000/docs

## Environment Variables

### Backend (backend/.env)
- `FIREBASE_PROJECT_ID` - Your Firebase project ID
- `FIREBASE_CREDENTIALS_PATH` - Path to credentials JSON (default: ./firebase-credentials.json)
- `SECRET_KEY` - API secret key (generate with: `python -c "import secrets; print(secrets.token_urlsafe(32))"`)
- `CORS_ORIGINS` - Allowed origins (default: http://localhost:5173,http://localhost:3000)

### Frontend (frontend/.env.development - auto-loaded)
- `VITE_API_URL` - Backend API URL (default: http://localhost:8000/api)

## Troubleshooting

### "Firebase credentials not found"
- Make sure `firebase-credentials.json` exists in project root
- Check `FIREBASE_CREDENTIALS_PATH` in backend/.env

### "CORS error"
- Verify `CORS_ORIGINS` in backend/.env includes your frontend URL
- Make sure backend is running

### "Module not found"
- Backend: Make sure venv is activated and dependencies installed
- Frontend: Run `npm install` in frontend directory

### Port already in use
- Backend (8000): Check if another process is using it
- Frontend (5173): Vite will automatically try next port (5174, etc.)

## File Structure

```
Warhammer-Ranking-System/
├── backend/
│   ├── .env                    # Your local backend config (git-ignored)
│   ├── .env.example            # Template for backend/.env
│   └── ...
├── frontend/
│   ├── .env.development        # Local dev config (committed, safe defaults)
│   ├── .env.example            # Template (for reference)
│   └── ...
├── firebase-credentials.json   # Your Firebase credentials (git-ignored!)
├── .env.example                # Master template (for reference)
└── start-dev-firebase.sh       # Quick start script
```

## Notes

- Never commit `.env` files or `firebase-credentials.json`
- `.env.development` is safe to commit (contains only local URLs)
- For production deployment, see QUICKSTART_DEPLOYMENT.md
