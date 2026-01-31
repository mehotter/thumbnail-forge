# Quick Backend Test

To test if the backend is working, run this in a new terminal:

```bash
cd backend
python app.py
```

Then in another terminal, test the health endpoint:

```bash
curl http://localhost:5000/api/health
```

You should see: `{"status":"healthy","message":"Thumbnail generation API is running"}`

If you see errors, check:
1. Are all Python model files in the project root?
2. Is Flask installed? `pip install flask flask-cors`
3. Check the backend console for error messages






