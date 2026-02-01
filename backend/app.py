"""
Flask Backend API for Thumbnail Generation System
Connects frontend to Python AI models
"""

import os
import sys

# Set UTF-8 encoding for Windows compatibility
if sys.platform == 'win32':
    os.environ['PYTHONIOENCODING'] = 'utf-8'
    # Set console encoding to UTF-8
    if hasattr(sys.stdout, 'reconfigure'):
        sys.stdout.reconfigure(encoding='utf-8')
    if hasattr(sys.stderr, 'reconfigure'):
        sys.stderr.reconfigure(encoding='utf-8')

from flask import Flask, request, jsonify, send_file, send_from_directory
from flask_cors import CORS
import subprocess
import json
from pathlib import Path
import uuid
from werkzeug.utils import secure_filename
import time

app = Flask(__name__)
# Enable CORS for all origins (required for Vercel deployment)
# Enable CORS for all origins (required for Vercel deployment and direct calls)
CORS(app)


# Configuration
UPLOAD_FOLDER = 'uploads'
OUTPUT_FOLDER = 'outputs'
ALLOWED_EXTENSIONS = {'mp4', 'avi', 'mov', 'mkv', 'webm'}

# Create directories
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(OUTPUT_FOLDER, exist_ok=True)

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/', methods=['GET'])
def root():
    """Root endpoint - redirect to API info"""
    return jsonify({
        'message': 'Thumbnail Generation API',
        'status': 'running',
        'endpoints': {
            'health': '/api/health',
            'generate': '/api/generate (POST)',
            'thumbnail': '/api/thumbnail/<id>/<filename> (GET)',
            'test': '/api/test (GET)'
        },
        'note': 'This is the backend API. Use the React frontend to interact with the system.'
    })

@app.route('/api/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'message': 'Thumbnail generation API is running'
    })

@app.route('/api/test', methods=['GET'])
def test_endpoint():
    """Test endpoint to verify backend is working"""
    try:
        backend_dir = os.path.dirname(os.path.abspath(__file__))
        outputs_dir = os.path.join(backend_dir, OUTPUT_FOLDER)

        test_files = []
        if os.path.exists(outputs_dir):
            for item in os.listdir(outputs_dir):
                item_path = os.path.join(outputs_dir, item)
                if os.path.isdir(item_path):
                    for file in os.listdir(item_path):
                        if file.lower().endswith(('.jpg', '.jpeg', '.png', '.webp')):
                            test_files.append(os.path.join(item, file))
                            if len(test_files) >= 5:
                                break
                if len(test_files) >= 5:
                    break

        return jsonify({
            'success': True,
            'message': 'Backend is working',
            'outputs_dir': outputs_dir,
            'outputs_exists': os.path.exists(outputs_dir),
            'test_files_found': len(test_files),
            'sample_files': test_files[:3]
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/generate', methods=['POST'])
def generate_thumbnails():
    """Generate thumbnails from uploaded video"""
    print("\n" + "="*80)
    print("NEW GENERATION REQUEST RECEIVED")
    print("="*80)
    try:
        # Check if video file is present
        if 'video' not in request.files:
            return jsonify({'success': False, 'error': 'No video file provided'}), 400

        video_file = request.files['video']
        if video_file.filename == '':
            return jsonify({'success': False, 'error': 'No file selected'}), 400

        if not allowed_file(video_file.filename):
            return jsonify({'success': False, 'error': 'Invalid file type. Please upload a video file.'}), 400

        # Get parameters
        title = request.form.get('title', 'Video Title')
        genre = request.form.get('genre', 'drama')
        model = request.form.get('model', 'hybrid')
        variants = int(request.form.get('variants', 20))
        want_debug = request.args.get('debug') == '1'

        # Generate unique ID for this request
        request_id = str(uuid.uuid4())[:8]

        # Save uploaded file to absolute path
        filename = secure_filename(video_file.filename)
        uploads_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), UPLOAD_FOLDER)
        os.makedirs(uploads_dir, exist_ok=True)
        video_path = os.path.join(uploads_dir, f"{request_id}_{filename}")
        video_file.save(video_path)

        # Determine output directory (use absolute path)
        output_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), OUTPUT_FOLDER, f"{request_id}_{Path(filename).stem}")
        os.makedirs(output_dir, exist_ok=True)

        # Compute paths
        backend_dir = os.path.dirname(os.path.abspath(__file__))
        project_root = os.path.dirname(backend_dir)
        project_root = os.path.normpath(project_root)

        # Debug: Print paths
        print(f"DEBUG: Backend dir: {backend_dir}")
        print(f"DEBUG: Project root: {project_root}")
        print(f"DEBUG: Current working dir: {os.getcwd()}")
        print(f"DEBUG: Video path: {video_path}")
        print(f"DEBUG: Video exists: {os.path.exists(video_path)}")

        # Build command for model
        script_path = None
        if model == 'hybrid':
            script_path = os.path.join(project_root, 'hybrid_netflix_disney_system.py')
            script_path = os.path.normpath(script_path)
            cmd = [
                sys.executable, script_path,
                video_path,
                '--title', title,
                '--genre', genre,             # <-- removed stray 'family'
                '--variants', str(variants),
                '--output-dir', output_dir
            ]
        elif model == 'netflix':
            script_path = os.path.join(project_root, 'run_netflix_system.py')
            script_path = os.path.normpath(script_path)
            cmd = [
                sys.executable, script_path,
                video_path,
                genre,
                str(variants)
            ]
        elif model == 'disney':
            script_path = os.path.join(project_root, 'disney_complete_system.py')
            script_path = os.path.normpath(script_path)
            cmd = [
                sys.executable, script_path,
                video_path,
                '--title', title,
                '--genre', genre,             # <-- removed stray 'family'
                '--variants', str(variants),
                '--output-dir', output_dir
            ]
        else:
            return jsonify({'success': False, 'error': 'Invalid model selected'}), 400

        # If script path missing, try alternative locations
        if not os.path.exists(script_path):
            alt_paths = [
                os.path.join(os.getcwd(), os.path.basename(script_path)),
                script_path,
            ]
            found = False
            for alt_path in alt_paths:
                if os.path.exists(alt_path):
                    script_path = alt_path
                    cmd[1] = script_path
                    found = True
                    break
            if not found:
                return jsonify({
                    'success': False,
                    'error': f'Script not found: {script_path}. Project root: {project_root}, Current dir: {os.getcwd()}'
                }), 500

        # --- SAFE SUBPROCESS RUN (no len(None), optional debug tails) ---
        print(f"Running command: {' '.join(cmd)}")
        print(f"Working directory: {project_root}")
        print(f"Script path: {script_path}")
        print(f"Script exists: {os.path.exists(script_path)}")

        try:
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                encoding='utf-8',
                errors='replace',
                cwd=project_root,
                timeout=1800,
                check=False
            )
        except subprocess.TimeoutExpired:
            return jsonify({
                'success': False,
                'error': 'Generation timed out after 30 minutes'
            }), 500
        except Exception as e:
            import traceback
            print("ERROR running subprocess:", e)
            print(traceback.format_exc())
            return jsonify({
                'success': False,
                'error': f'Failed to run script: {e}'
            }), 500

        stdout = result.stdout or ""
        stderr = result.stderr or ""

        print(f"Return code: {result.returncode}")
        print(f"STDOUT preview ({len(stdout)} chars):\n{stdout[:2000]}")
        if len(stdout) > 2000:
            print(f"... (truncated, total {len(stdout)} chars)")
        print(f"STDERR preview ({len(stderr)} chars):\n{stderr[:2000]}")
        if len(stderr) > 2000:
            print(f"... (truncated, total {len(stderr)} chars)")

        if result.returncode != 0:
            msg = (stderr.strip() or stdout.strip() or f"Process exited with code {result.returncode}")[-4000:]
            payload = {
                'success': False,
                'error': f'Generation failed (code {result.returncode})',
                'details': msg
            }
            if want_debug:
                payload['stdout'] = stdout[-4000:]
                payload['stderr'] = stderr[-4000:]
            return jsonify(payload), 500

        print("✓ Script executed successfully")

        # Find generated thumbnails - COMPREHENSIVE SEARCH
        thumbnails = []
        thumbnail_files = []

        print(f"\n{'='*80}")
        print(f"SEARCHING FOR THUMBNAILS")
        print(f"{'='*80}")
        print(f"Request ID: {request_id}")
        print(f"Backend dir: {backend_dir}")
        print(f"Project root: {project_root}")

        # PRIMARY: outputs dir
        backend_outputs = Path(backend_dir) / OUTPUT_FOLDER
        print(f"\n1. Checking backend/outputs: {backend_outputs}")
        if backend_outputs.exists():
            for item in backend_outputs.iterdir():
                if item.is_dir() and request_id in item.name:
                    print(f"  ✓ Found output directory: {item.name}")
                    for ext in ['*.jpg', '*.jpeg', '*.png', '*.webp']:
                        found = list(item.glob(ext))
                        thumbnail_files.extend(found)
                        if found:
                            print(f"    Found {len(found)} {ext} files")

        # SECONDARY: explicit output_dir
        if not thumbnail_files:
            output_path = Path(output_dir)
            print(f"\n2. Checking output_path: {output_path}")
            if output_path.exists():
                for ext in ['*.jpg', '*.jpeg', '*.png', '*.webp']:
                    found = list(output_path.rglob(ext))
                    thumbnail_files.extend(found)
                    if found:
                        print(f"    Found {len(found)} {ext} files")

        # TERTIARY: Netflix-style: {video_stem}_final at project root
        if not thumbnail_files:
            video_stem = Path(video_path).stem
            netflix_output = Path(project_root) / f"{video_stem}_final"
            print(f"\n3. Checking Netflix-style output: {netflix_output}")
            if netflix_output.exists():
                print(f"  ✓ Found Netflix output directory")
                for ext in ['*.jpg', '*.jpeg', '*.png', '*.webp']:
                    found = list(netflix_output.glob(ext))
                    thumbnail_files.extend(found)
                    if found:
                        print(f"    Found {len(found)} {ext} files")

        # QUATERNARY: any directory containing request_id
        if not thumbnail_files:
            print(f"\n4. Searching project root for {request_id}...")
            for item in Path(project_root).iterdir():
                if item.is_dir() and request_id in item.name:
                    print(f"  ✓ Found directory: {item.name}")
                    for ext in ['*.jpg', '*.jpeg', '*.png', '*.webp']:
                        found = list(item.rglob(ext))
                        thumbnail_files.extend(found)
                        if found:
                            print(f"    Found {len(found)} {ext} files")

        # Remove duplicates and sort
        thumbnail_files = sorted(list(set(thumbnail_files)), key=lambda x: x.name)
        print(f"\n✓ Total unique thumbnail files: {len(thumbnail_files)}")
        if thumbnail_files:
            print(f"Sample files: {[f.name for f in thumbnail_files[:3]]}")
        print(f"{'='*80}\n")

        # Build response (URLs via /api/thumbnail/<id>/<filename>)
        print(f"\nCreating thumbnail data for {len(thumbnail_files)} files...")
        for idx, thumb_file in enumerate(thumbnail_files[:variants]):
            try:
                thumb_name = thumb_file.name

                # Try to read metadata but don't fail if missing
                scene_type = 'unknown'
                score = 0.0
                metadata_file = thumb_file.parent / 'disney_metadata.json'
                if not metadata_file.exists():
                    metadata_file = thumb_file.parent / 'hybrid_metadata.json'
                if not metadata_file.exists():
                    metadata_file = thumb_file.parent / 'metadata.json'
                if metadata_file.exists():
                    try:
                        with open(metadata_file, 'r', encoding='utf-8', errors='ignore') as f:
                            metadata = json.load(f)
                            variants_list = metadata.get('variants', [])
                            if idx < len(variants_list):
                                variant = variants_list[idx]
                                scene_type = variant.get('scene_type') or variant.get('type', 'unknown')
                                score = float(variant.get('score', 0.0))
                                if 'metadata' in variant:
                                    scene_type = variant['metadata'].get('scene_type', scene_type)
                    except Exception:
                        pass

                from urllib.parse import quote
                encoded_filename = quote(thumb_name)
                thumbnail_url = f'http://localhost:5000/api/thumbnail/{request_id}/{encoded_filename}'
                download_url = f'http://localhost:5000/api/download/{request_id}/{encoded_filename}'
                # Create static URL path relative to outputs directory if possible
                try:
                    outputs_abs = Path(backend_dir) / OUTPUT_FOLDER
                    rel_path = Path(thumb_file).resolve().relative_to(outputs_abs.resolve())
                    rel_url_path = quote(rel_path.as_posix())
                    static_url = f"http://localhost:5000/outputs/{rel_url_path}"
                except Exception:
                    static_url = ''

                thumbnails.append({
                    'id': idx + 1,
                    'url': thumbnail_url,
                    'static_url': static_url,
                    'download_url': download_url,
                    'filename': thumb_name,
                    'scene_type': scene_type,
                    'score': float(score)
                })

                print(f"  ✓ {idx+1}. {thumb_name}")
            except Exception as e:
                print(f"  ✗ Error processing {idx+1}: {e}")
                import traceback
                print(traceback.format_exc())
                continue

        if not thumbnails:
            error_msg = f'No thumbnails found. Request ID: {request_id}. Files found: {len(thumbnail_files)}'
            print(f"\n✗ {error_msg}")
            if thumbnail_files:
                print(f"Files that were found but not processed: {[f.name for f in thumbnail_files[:5]]}")
            return jsonify({
                'success': False,
                'error': error_msg
            }), 500

        print(f"\n✓ Successfully processed {len(thumbnails)} thumbnails")
        print(f"Returning response to frontend...\n")

        response_data = {
            'success': True,
            'thumbnails': [
                {
                    'id': int(t['id']),
                    'url': str(t['url']),
                    'static_url': str(t.get('static_url', '')),
                    'download_url': str(t.get('download_url', '')),
                    'filename': str(t['filename']),
                    'scene_type': str(t['scene_type']),
                    'score': float(t['score'])
                }
                for t in thumbnails
            ],
            'request_id': str(request_id),
            'message': f'Successfully generated {len(thumbnails)} thumbnails'
        }

        # If debug requested, include stdout/stderr tails
        if want_debug:
            response_data['stdout_tail'] = (stdout or "")[-2000:]
            response_data['stderr_tail'] = (stderr or "")[-2000:]

        print(f"Response size: {len(json.dumps(response_data))} bytes")
        return jsonify(response_data)

    except Exception as e:
        import traceback
        error_trace = traceback.format_exc()
        print("\n" + "="*80)
        print("ERROR IN GENERATE THUMBNAILS")
        print("="*80)
        print(f"ERROR: {str(e)}")
        print(f"ERROR TYPE: {type(e).__name__}")
        print(f"TRACEBACK:\n{error_trace}")
        print("="*80 + "\n")
        return jsonify({
            'success': False,
            'error': f'Server error: {str(e)}',
            'error_type': type(e).__name__
        }), 500

@app.route('/api/thumbnail/<request_id>/<path:filename>', methods=['GET'])
def get_thumbnail(request_id, filename):
    """Serve generated thumbnail images with proper headers"""
    try:
        from urllib.parse import unquote
        import glob
        from pathlib import Path as PathLib

        filename = unquote(filename)

        search_locations = []

        backend_dir = os.path.dirname(os.path.abspath(__file__))
        outputs_dir = os.path.join(backend_dir, OUTPUT_FOLDER)
        output_dir_pattern = os.path.join(outputs_dir, f"{request_id}_*")
        matching_dirs = glob.glob(output_dir_pattern)
        search_locations.extend(matching_dirs)

        project_root = os.path.dirname(backend_dir)
        project_pattern = os.path.join(project_root, f"*{request_id}*")
        project_dirs = glob.glob(project_pattern)
        for pd in project_dirs:
            if os.path.isdir(pd):
                search_locations.append(pd)

        if os.path.exists(project_root):
            for item in os.listdir(project_root):
                item_path = os.path.join(project_root, item)
                if os.path.isdir(item_path) and request_id in item:
                    search_locations.append(item_path)

        thumbnail_path = None
        for search_dir in search_locations:
            direct_path = os.path.join(search_dir, filename)
            if os.path.exists(direct_path):
                thumbnail_path = direct_path
                break
            for root, dirs, files in os.walk(search_dir):
                if filename in files:
                    thumbnail_path = os.path.join(root, filename)
                    break
            if thumbnail_path:
                break

        if not thumbnail_path or not os.path.exists(thumbnail_path):
            return jsonify({
                'error': f'Thumbnail file not found: {filename}',
                'request_id': request_id
            }), 404

        mime_type = 'image/jpeg'
        if filename.lower().endswith('.png'):
            mime_type = 'image/png'
        elif filename.lower().endswith('.gif'):
            mime_type = 'image/gif'
        elif filename.lower().endswith('.webp'):
            mime_type = 'image/webp'

        response = send_file(thumbnail_path, mimetype=mime_type)
        response.headers['Cache-Control'] = 'public, max-age=3600'
        response.headers['Access-Control-Allow-Origin'] = '*'
        return response

    except Exception as e:
        import traceback
        print(f"Error serving thumbnail: {e}")
        print(traceback.format_exc())
        return jsonify({
            'error': str(e)
        }), 500

@app.route('/api/download/<request_id>/<path:filename>', methods=['GET'])
def download_thumbnail(request_id, filename):
    """Download thumbnail file"""
    try:
        from urllib.parse import unquote
        import glob
        from pathlib import Path as PathLib

        filename = unquote(filename)

        # Search locations mirror get_thumbnail logic
        search_locations = []

        backend_dir = os.path.dirname(os.path.abspath(__file__))
        outputs_dir = os.path.join(backend_dir, OUTPUT_FOLDER)
        output_dir_pattern = os.path.join(outputs_dir, f"{request_id}_*")
        matching_dirs = glob.glob(output_dir_pattern)
        search_locations.extend(matching_dirs)

        project_root = os.path.dirname(backend_dir)
        project_pattern = os.path.join(project_root, f"*{request_id}*")
        project_dirs = glob.glob(project_pattern)
        for pd in project_dirs:
            if os.path.isdir(pd):
                search_locations.append(pd)

        if os.path.exists(project_root):
            for item in os.listdir(project_root):
                item_path = os.path.join(project_root, item)
                if os.path.isdir(item_path) and request_id in item:
                    search_locations.append(item_path)

        thumbnail_path = None
        for search_dir in search_locations:
            direct_path = os.path.join(search_dir, filename)
            if os.path.exists(direct_path):
                thumbnail_path = direct_path
                break
            for root, dirs, files in os.walk(search_dir):
                if filename in files:
                    thumbnail_path = os.path.join(root, filename)
                    break
            if thumbnail_path:
                break

        if not thumbnail_path or not os.path.exists(thumbnail_path):
            return jsonify({'error': 'Thumbnail file not found'}), 404

        download_name = PathLib(thumbnail_path).name
        resp = send_file(thumbnail_path, as_attachment=True, download_name=download_name)
        resp.headers['Access-Control-Expose-Headers'] = 'Content-Disposition'
        resp.headers['Access-Control-Allow-Origin'] = '*'
        return resp

    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/outputs/<path:filename>', methods=['GET'])
def serve_outputs(filename):
    """Serve files directly from the outputs directory (static access)."""
    try:
        backend_dir = os.path.dirname(os.path.abspath(__file__))
        outputs_dir = os.path.join(backend_dir, OUTPUT_FOLDER)
        return send_from_directory(outputs_dir, filename)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    import logging
    logging.basicConfig(level=logging.DEBUG)

    # Get port from environment variable (Hugging Face uses PORT=7860)
    port = int(os.environ.get('PORT', 7860))
    
    print("="*80)
    print("Thumbnail Generation API Server")
    print("="*80)
    print(f"Starting server on http://0.0.0.0:{port}")
    print("API Endpoints:")
    print("  - GET  /api/health - Health check")
    print("  - POST /api/generate - Generate thumbnails")
    print("  - GET  /api/thumbnail/<id>/<filename> - Get thumbnail image")
    print("="*80)
    print("DEBUG MODE: ON - All errors will be logged")
    print("="*80)

    app.logger.setLevel(logging.DEBUG)
    app.run(debug=True, host='0.0.0.0', port=port, use_reloader=False)
