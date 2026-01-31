# Local Testing Guide

## Prerequisites

1. **Python 3.8+** installed
2. **Node.js 16+** and npm installed
3. All Python dependencies installed (from main `requirements.txt`)

## Step 1: Setup Backend

### 1.1 Install Backend Dependencies

```bash
cd backend
pip install -r requirements.txt
```

### 1.2 Ensure Python Models are Available

Make sure these files are in the project root (same level as `backend/`):
- `hybrid_netflix_disney_system.py`
- `run_netflix_system.py`
- `disney_complete_system.py`
- All other required Python files

### 1.3 Start Backend Server

```bash
cd backend
python app.py
```

The server will start on `http://localhost:5000`

## Step 2: Setup Frontend

### 2.1 Install Frontend Dependencies

```bash
cd frontend
npm install
```

### 2.2 Start Frontend Development Server

```bash
npm start
```

The frontend will start on `http://localhost:3000`

## Step 3: Test the Application

1. Open browser to `http://localhost:3000`
2. Upload a video file (test1.mp4, test2.mp4, etc.)
3. Enter title and select genre
4. Choose model (Hybrid, Netflix, or Disney+)
5. Set number of variants
6. Click "Generate Thumbnails"
7. Wait for processing (may take 2-10 minutes depending on video length)
8. View generated thumbnails
9. Download individual thumbnails

## Troubleshooting

### Backend Issues

**Problem: Module not found errors**
```bash
# Make sure you're in the project root when running backend
# The backend needs access to the Python model files
cd /path/to/project/root
python backend/app.py
```

**Problem: Port 5000 already in use**
```bash
# Change port in backend/app.py
app.run(debug=True, host='0.0.0.0', port=5001)  # Use different port
```

**Problem: CORS errors**
- Make sure `flask-cors` is installed
- Check that `CORS(app)` is in `app.py`

### Frontend Issues

**Problem: npm install fails**
```bash
# Clear cache and try again
npm cache clean --force
npm install
```

**Problem: Can't connect to backend**
- Check backend is running on port 5000
- Update API URL in `App.jsx` if using different port:
  ```javascript
  const response = await fetch('http://localhost:5001/api/generate', {
  ```

**Problem: Video upload fails**
- Check file size limits
- Ensure video format is supported (mp4, avi, mov, mkv, webm)

## Testing Checklist

- [ ] Backend starts without errors
- [ ] Frontend starts without errors
- [ ] Can upload video file
- [ ] Can select model and set parameters
- [ ] Generation starts when clicking button
- [ ] Loading indicator shows during processing
- [ ] Thumbnails appear after generation
- [ ] Can download thumbnails
- [ ] Error messages display correctly

## File Structure

```
project-root/
├── backend/
│   ├── app.py
│   ├── requirements.txt
│   ├── uploads/          (created automatically)
│   └── outputs/          (created automatically)
├── frontend/
│   ├── src/
│   │   └── App.jsx
│   ├── package.json
│   └── public/
├── hybrid_netflix_disney_system.py
├── run_netflix_system.py
├── disney_complete_system.py
└── requirements.txt
```

## Next Steps

Once local testing is successful:
1. Build frontend for production: `cd frontend && npm run build`
2. Deploy backend to server
3. Deploy frontend build to server or static hosting
4. Update API URLs for production

