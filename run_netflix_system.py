"""
Simplified Netflix System - Works with available models
Avoids heavy model downloads that can crash
"""

import cv2
import numpy as np
from pathlib import Path
from typing import List, Dict, Optional
from dataclasses import dataclass, asdict
from collections import defaultdict
import json
from datetime import datetime

# Core - these should already be installed
from ultralytics import YOLO
import torch

print("="*80)
print("NETFLIX-STYLE SYSTEM (Simplified)")
print("="*80)

class NetflixSimplifiedSystem:
    """Simplified Netflix system using only YOLO (reliable model)"""
    
    def __init__(self, genre='action', title='Untitled', num_variants=8):
        self.genre = genre.lower()
        self.title = title
        self.num_variants = num_variants
        
        print(f"\nTitle: {self.title}")
        print(f"Genre: {self.genre}")
        print(f"Variants: {num_variants}")
        
        # Load YOLO (this works well)
        print("\nLoading YOLO model...")
        self.yolo = YOLO('yolov8n.pt')
        print("✓ Loaded")
        
        self.analyses = []
    
    def analyze_frame(self, frame, timestamp, frame_number):
        """Analyze single frame"""
        
        result = self.yolo(frame, verbose=False)
        
        people = []
        objects = []
        
        if result and len(result) > 0 and result[0].boxes:
            for box in result[0].boxes:
                class_id = int(box.cls)
                class_name = self.yolo.names[class_id]
                confidence = float(box.conf)
                
                if class_name == 'person':
                    bbox = box.xyxy[0].cpu().numpy()
                    people.append({
                        'bbox': bbox.tolist(),
                        'confidence': confidence
                    })
                else:
                    objects.append({
                        'name': class_name,
                        'confidence': confidence
                    })
        
        # Visual quality
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        lab = cv2.cvtColor(frame, cv2.COLOR_BGR2LAB)
        
        quality = {
            'brightness': 1 - abs(np.mean(lab[:,:,0]) - 50) / 50,
            'contrast': min(np.std(gray) / 50, 1.0),
            'sharpness': min(cv2.Laplacian(gray, cv2.CV_64F).var() / 300, 1.0),
        }
        
        quality['overall'] = np.mean(list(quality.values()))
        
        # Composition
        composition = self._get_composition(frame, people)
        
        # Scene type
        scene_type = self._classify_scene(people, objects)
        
        # Score
        score = quality['overall'] * 0.6 + len(people) * 0.2 + len(objects) * 0.1
        
        analysis = {
            'timestamp': timestamp,
            'frame_number': frame_number,
            'people_count': len(people),
            'objects_count': len(objects),
            'quality': quality,
            'composition': composition,
            'scene_type': scene_type,
            'overall_score': score,
            'description': f"{scene_type} with {len(people)} people",
            'frame': frame
        }
        
        return analysis
    
    def _get_composition(self, frame, people):
        """Get shot composition"""
        if not people:
            return 'wide'
        
        largest = max(people, key=lambda x: (x['bbox'][2]-x['bbox'][0])*(x['bbox'][3]-x['bbox'][1]))
        bbox = largest['bbox']
        
        prominence = ((bbox[2]-bbox[0])*(bbox[3]-bbox[1])) / (frame.shape[0]*frame.shape[1])
        
        if prominence > 0.25:
            return 'closeup'
        elif prominence > 0.10:
            return 'mid'
        else:
            return 'wide'
    
    def _classify_scene(self, people, objects):
        """Classify scene type"""
        people_count = len(people)
        object_names = [obj['name'] for obj in objects]
        
        if self.genre == 'action':
            action_items = ['car', 'motorcycle', 'truck', 'bus', 'airplane']
            has_action = any(item in object_names for item in action_items)
            
            if people_count == 1:
                return 'hero_action' if has_action else 'hero_solo'
            elif people_count >= 3:
                return 'ensemble_action' if has_action else 'ensemble'
            elif people_count == 2:
                return 'duo_scene'
            else:
                return 'background'
        
        elif self.genre == 'romance':
            if people_count == 1:
                return 'solo_emotional'
            elif people_count == 2:
                return 'romantic_couple'
            else:
                return 'group_romance'
        
        else:
            if people_count == 0:
                return 'background'
            elif people_count == 1:
                return 'character_focus'
            elif people_count == 2:
                return 'duo_scene'
            else:
                return 'ensemble'
    
    def process(self, video_path, output_dir):
        """Process video"""
        print(f"\n📹 Processing: {Path(video_path).name}")
        
        cap = cv2.VideoCapture(video_path)
        fps = cap.get(cv2.CAP_PROP_FPS)
        
        analyses = []
        frame_number = 0
        
        print("\n🔍 Analyzing frames...")
        
        while True:
            ret, frame = cap.read()
            if not ret:
                break
            
            if frame_number % 15 == 0:
                timestamp = frame_number / fps
                analysis = self.analyze_frame(frame, timestamp, frame_number)
                analyses.append(analysis)
            
            frame_number += 1
            
            if len(analyses) % 50 == 0:
                print(f"   Analyzed {len(analyses)} frames...")
        
        cap.release()
        
        print(f"✓ Complete: {len(analyses)} frames")
        
        # Select variants
        by_scene = defaultdict(list)
        for a in analyses:
            by_scene[a['scene_type']].append(a)
        
        selected = []
        priorities = ['hero_action', 'hero_solo', 'ensemble', 'romantic_couple', 'duo_scene']
        
        for scene_type in priorities:
            if scene_type in by_scene:
                items = sorted(by_scene[scene_type], key=lambda x: x['overall_score'], reverse=True)
                selected.extend(items[:2])
                if len(selected) >= self.num_variants:
                    break
        
        if len(selected) < self.num_variants:
            remaining = sorted([a for a in analyses if a not in selected], 
                             key=lambda x: x['overall_score'], reverse=True)
            selected.extend(remaining[:self.num_variants - len(selected)])
        
        selected.sort(key=lambda x: x['timestamp'])
        selected = selected[:self.num_variants]
        
        # Extract
        self._extract(cap, selected, output_dir, fps, video_path)
        
        # Save metadata
        self._save_metadata(selected, output_dir)
        
        return selected
    
    def _extract(self, cap, analyses, output_dir, fps, video_path):
        """Extract thumbnails"""
        Path(output_dir).mkdir(parents=True, exist_ok=True)
        cap = cv2.VideoCapture(video_path)
        
        print(f"\n📸 Extracting {len(analyses)} thumbnails...")
        
        for i, analysis in enumerate(analyses, 1):
            cap.set(cv2.CAP_PROP_POS_FRAMES, analysis['frame_number'])
            ret, frame = cap.read()
            
            if ret:
                timestamp_str = f"{int(analysis['timestamp']//60):02d}_{int(analysis['timestamp']%60):02d}"
                filename = f"thumb_{i:02d}_{analysis['scene_type']}_t{timestamp_str}.jpg"
                filepath = Path(output_dir) / filename
                
                h, w = frame.shape[:2]
                if w > 1920:
                    scale = 1920 / w
                    frame = cv2.resize(frame, (int(w*scale), int(h*scale)))
                
                cv2.imwrite(str(filepath), frame, [cv2.IMWRITE_JPEG_QUALITY, 95])
                
                print(f"   ✓ {filename}")
                print(f"      Score: {analysis['overall_score']:.2f}")
        
        cap.release()
    
    def _save_metadata(self, variants, output_dir):
        """Save metadata"""
        metadata = {
            'title': self.title,
            'genre': self.genre,
            'timestamp': datetime.now().isoformat(),
            'variants': []
        }
        
        for i, analysis in enumerate(variants, 1):
            metadata['variants'].append({
                'id': i,
                'timestamp': analysis['timestamp'],
                'scene_type': analysis['scene_type'],
                'composition': analysis['composition'],
                'people_count': analysis['people_count'],
                'score': analysis['overall_score'],
                'description': analysis['description']
            })
        
        metadata_path = Path(output_dir) / 'metadata.json'
        with open(metadata_path, 'w') as f:
            json.dump(metadata, f, indent=2, default=str)
        
        print(f"\n✓ Metadata saved: {metadata_path}")


def main():
    """Main entry"""
    import sys
    
    if len(sys.argv) < 2:
        print("\nUsage: python run_netflix_system.py <video> [genre] [num_variants]")
        print("Example: python run_netflix_system.py 3.mp4 action 10")
        sys.exit(1)
    
    video_path = sys.argv[1]
    genre = sys.argv[2] if len(sys.argv) > 2 else 'action'
    num_variants = int(sys.argv[3]) if len(sys.argv) > 3 else 8
    
    title = Path(video_path).stem
    
    system = NetflixSimplifiedSystem(genre=genre, title=title, num_variants=num_variants)
    output_dir = f"{Path(video_path).stem}_final"
    
    system.process(video_path, output_dir)
    
    print("\n" + "="*80)
    print("✓ COMPLETE!")
    print(f"✓ Location: {Path(output_dir).absolute()}")
    print("="*80)


if __name__ == '__main__':
    main()











