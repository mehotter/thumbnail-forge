# Setup Instructions for AI Thumbnail Extractor

## Quick Start (5 minutes)

1. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

2. **Test with your video:**
   ```bash
   python quick_test.py your_video.mp4
   ```

That's it! The system will extract 10 diverse thumbnails automatically.

## Cloud AI APIs Setup (Optional, Better Results!)

### Google Cloud Vision API

1. **Enable API:**
   - Go to [Google Cloud Console](https://console.cloud.google.com/)
   - Enable "Cloud Vision API"

2. **Create credentials:**
   - Create Service Account
   - Download JSON key file

3. **Use it:**
   ```bash
   python thumbnail_extractor.py video.mp4 --cloud --google-creds path/to/credentials.json -g action
   ```

### AWS Rekognition

1. **Get credentials:**
   - Create AWS account
   - Get Access Key ID and Secret Key from IAM

2. **Use it:**
   ```bash
   python thumbnail_extractor.py video.mp4 --cloud --aws-key YOUR_KEY --aws-secret YOUR_SECRET -g action
   ```

### Azure Computer Vision

1. **Create resource:**
   - Go to Azure Portal
   - Create "Computer Vision" resource
   - Get endpoint and key

2. **Use it:**
   ```bash
   python thumbnail_extractor.py video.mp4 --cloud --azure-endpoint YOUR_ENDPOINT --azure-key YOUR_KEY -g action
   ```

## Features

### Local Models (No API needed)
- ✅ Works offline
- ✅ Fast processing
- ✅ No costs
- ✅ Uses YOLO + MediaPipe

### Cloud APIs (Better semantic understanding)
- ✅ Superior scene understanding
- ✅ Better label detection
- ✅ Celebrity recognition
- ✅ Emotion detection
- ✅ More accurate genre matching

## Performance Comparison

| Feature | Local Models | Cloud APIs |
|---------|-------------|------------|
| Object Detection | ✅ Good | ✅✅ Excellent |
| Scene Understanding | ✅ Good | ✅✅ Excellent |
| Genre Relevance | ✅ Good | ✅✅ Excellent |
| Processing Speed | ✅✅✅ Fast | ✅ Medium |
| Cost | ✅ Free | ⚠️ Pay per use |
| Offline | ✅✅✅ Yes | ❌ No |

## Recommended Settings

### For Best Quality
```bash
python thumbnail_extractor.py video.mp4 --cloud --google-creds credentials.json -g action -n 15
```

### For Fast Processing
```bash
python quick_test.py video.mp4 action 10
```

### For Maximum Diversity
```bash
python thumbnail_extractor.py video.mp4 -g action -n 20 -r 15
```

## Troubleshooting

**Issue: CUDA errors**
- Solution: System auto-falls back to CPU. No action needed.

**Issue: Out of memory**
- Solution: Use larger frame sampling rate: `-r 60`

**Issue: API errors**
- Solution: Check credentials and ensure API is enabled. System falls back to local models.

**Issue: Slow processing**
- Solution: Use smaller frame rate (higher number): `-r 60`

