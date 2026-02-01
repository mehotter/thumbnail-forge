---
title: Thumbnail Forge Backend
emoji: 🎬
colorFrom: blue
colorTo: purple
sdk: docker
pinned: false
---

# Thumbnail Forge Backend

AI-powered thumbnail generation API using Netflix, Disney+, and Hybrid models.

## API Endpoints

- `GET /api/health` - Health check
- `POST /api/generate` - Generate thumbnails from video
- `GET /api/thumbnail/<id>/<filename>` - Retrieve generated thumbnail

## Tech Stack

- Flask API
- PyTorch (CPU)
- OpenCV
- YOLOv8
