# Quick Start Guide

## Local Testing (5 minutes)

### 1. Start Backend

```bash
# Terminal 1
cd backend
pip install -r requirements.txt
python app.py
```

Backend runs on `http://localhost:5000`

### 2. Start Frontend

```bash
# Terminal 2
cd frontend
npm install
npm start
```

Frontend runs on `http://localhost:3000`

### 3. Test

1. Open `http://localhost:3000`
2. Upload a video file
3. Select model and settings
4. Click "Generate Thumbnails"
5. Wait for results!

## File Structure

```
project/
├── backend/
│   ├── app.py              # Flask API server
│   └── requirements.txt   # Python dependencies
├── frontend/
│   ├── src/
│   │   └── App.jsx        # React frontend
│   └── package.json       # Node dependencies
├── hybrid_netflix_disney_system.py
├── run_netflix_system.py
├── disney_complete_system.py
└── requirements.txt       # Main Python dependencies
```

## Common Issues

**Backend won't start:**
- Make sure all Python model files are in project root
- Install dependencies: `pip install -r requirements.txt`

**Frontend won't start:**
- Install Node modules: `npm install`
- Check Node version: `node --version` (need 16+)

**Can't connect to backend:**
- Check backend is running on port 5000
- Check CORS is enabled in `app.py`

**Generation fails:**
- Check video file format (mp4, avi, mov, mkv, webm)
- Check file size (may need to increase limit)
- Check backend logs for errors

## Next Steps

- See `LOCAL_TESTING_GUIDE.md` for detailed testing
- See `DEPLOYMENT_GUIDE.md` for server deployment
- See `SSH_SETUP_GUIDE.md` for SSH key setup

