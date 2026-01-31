# AI Thumbnail Forge - Full Stack Application

Complete web application for generating video thumbnails using Netflix, Disney+, and Hybrid AI models.

## 🚀 Features

- **3 AI Models**: Hybrid (Netflix + Disney+), Netflix-only, Disney+-only
- **Video Upload**: Support for mp4, avi, mov, mkv, webm
- **Customizable**: Title, genre, number of variants
- **Real-time Processing**: Live status updates during generation
- **Download**: Individual thumbnail downloads
- **Modern UI**: React + Tailwind CSS

## 📁 Project Structure

```
project-root/
├── backend/
│   ├── app.py                 # Flask API server
│   ├── requirements.txt      # Backend Python dependencies
│   ├── uploads/              # Uploaded videos (auto-created)
│   └── outputs/              # Generated thumbnails (auto-created)
├── frontend/
│   ├── src/
│   │   ├── App.jsx           # Main React component
│   │   ├── index.js          # React entry point
│   │   └── index.css         # Tailwind CSS
│   ├── public/
│   │   └── index.html        # HTML template
│   ├── package.json          # Node dependencies
│   ├── tailwind.config.js    # Tailwind configuration
│   └── postcss.config.js     # PostCSS configuration
├── hybrid_netflix_disney_system.py
├── run_netflix_system.py
├── disney_complete_system.py
├── requirements.txt          # Main Python dependencies
├── QUICK_START.md            # Quick setup guide
├── LOCAL_TESTING_GUIDE.md    # Detailed local testing
├── DEPLOYMENT_GUIDE.md       # Server deployment guide
└── SSH_SETUP_GUIDE.md        # SSH key setup
```

## 🏃 Quick Start

### 1. Install Dependencies

**Backend:**
```bash
cd backend
pip install -r requirements.txt
```

**Frontend:**
```bash
cd frontend
npm install
```

### 2. Start Backend

```bash
cd backend
python app.py
```

Backend runs on `http://localhost:5000`

### 3. Start Frontend

```bash
cd frontend
npm start
```

Frontend runs on `http://localhost:3000`

### 4. Use the Application

1. Open `http://localhost:3000`
2. Upload a video file
3. Enter title and select genre
4. Choose AI model (Hybrid/Netflix/Disney+)
5. Set number of variants
6. Click "Generate Thumbnails"
7. Wait for processing
8. Download thumbnails

## 📚 Documentation

- **QUICK_START.md** - Get started in 5 minutes
- **LOCAL_TESTING_GUIDE.md** - Detailed local testing instructions
- **DEPLOYMENT_GUIDE.md** - Deploy to production server
- **SSH_SETUP_GUIDE.md** - SSH key generation and setup

## 🔧 API Endpoints

### `GET /api/health`
Health check endpoint

**Response:**
```json
{
  "status": "healthy",
  "message": "Thumbnail generation API is running"
}
```

### `POST /api/generate`
Generate thumbnails from video

**Request:**
- `video` (file): Video file to process
- `title` (string): Video title
- `genre` (string): Genre (drama, action, romance, etc.)
- `model` (string): Model type (hybrid, netflix, disney)
- `variants` (int): Number of thumbnails to generate

**Response:**
```json
{
  "success": true,
  "thumbnails": [
    {
      "id": 1,
      "url": "/api/thumbnail/abc123/thumb_01.jpg",
      "filename": "thumb_01.jpg",
      "scene_type": "ensemble",
      "score": 3.11
    }
  ],
  "request_id": "abc123"
}
```

### `GET /api/thumbnail/<request_id>/<filename>`
Get thumbnail image

### `GET /api/download/<request_id>/<filename>`
Download thumbnail file

## 🎨 Frontend Features

- **Video Upload**: Drag & drop or file picker
- **Model Selection**: Choose between 3 AI models
- **Real-time Status**: Loading indicators and progress
- **Thumbnail Gallery**: Grid view of generated thumbnails
- **Download**: Individual thumbnail downloads
- **Responsive Design**: Works on desktop and mobile

## 🖥️ Backend Features

- **Flask API**: RESTful API for thumbnail generation
- **File Upload**: Secure video file handling
- **Model Integration**: Connects to Python AI models
- **Error Handling**: Comprehensive error messages
- **CORS Support**: Cross-origin requests enabled

## 🚢 Deployment

See `DEPLOYMENT_GUIDE.md` for:
- Server setup
- Nginx configuration
- SSL/HTTPS setup
- Systemd service setup
- Production optimizations

## 🐛 Troubleshooting

### Backend Issues

**Port already in use:**
```bash
# Change port in backend/app.py
app.run(debug=True, host='0.0.0.0', port=5001)
```

**Module not found:**
- Ensure all Python model files are in project root
- Check Python path and virtual environment

### Frontend Issues

**Can't connect to backend:**
- Verify backend is running on port 5000
- Check CORS settings
- Update API URL in `App.jsx` if needed

**Build errors:**
```bash
# Clear cache and reinstall
rm -rf node_modules package-lock.json
npm install
```

## 📝 Requirements

- Python 3.8+
- Node.js 16+
- npm or yarn
- All Python dependencies (see `requirements.txt`)
- All Node dependencies (see `frontend/package.json`)

## 🔒 Security Notes

- File upload size limits configured
- File type validation
- Secure filename handling
- CORS properly configured
- Production: Use HTTPS, environment variables for secrets

## 📞 Support

For issues or questions:
1. Check `LOCAL_TESTING_GUIDE.md` for common issues
2. Check `DEPLOYMENT_GUIDE.md` for server issues
3. Review backend logs: `sudo journalctl -u thumbnail-api`
4. Review frontend console for errors

## 🎯 Next Steps

1. ✅ Test locally (see `QUICK_START.md`)
2. ✅ Deploy to server (see `DEPLOYMENT_GUIDE.md`)
3. ✅ Setup SSH keys (see `SSH_SETUP_GUIDE.md`)
4. ✅ Configure domain and SSL
5. ✅ Monitor and optimize

---

**Ready to generate thumbnails?** Start with `QUICK_START.md`!

