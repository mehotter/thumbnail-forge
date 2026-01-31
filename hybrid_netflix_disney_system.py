"""
Hybrid Netflix + Disney+ Thumbnail Generation System
Combines the best of both systems for maximum diversity and quality
"""

import cv2
import json
from pathlib import Path
from typing import List, Dict, Any, Optional
from datetime import datetime
import argparse
import sys

# Import both systems
from run_netflix_system import NetflixSimplifiedSystem
from disney_complete_system import DisneyCompleteThumbnailSystem
from disney_metadata_spec import DisneyMetadataBuilder


class HybridThumbnailSystem:
    """Combines Netflix and Disney+ systems for optimal results"""
    
    def __init__(self):
        print("🚀 Initializing Hybrid Netflix + Disney+ System...")
        
        # Initialize both systems
        self.netflix_system = NetflixSimplifiedSystem(genre="action", title="Hybrid", num_variants=10)
        self.disney_system = DisneyCompleteThumbnailSystem()
        
        print("✓ Netflix System: Active")
        print("✓ Disney+ System: Active")
        print("✓ Hybrid Integration: Ready")
    
    def process_video(
        self,
        video_path: str,
        title: str,
        genre: List[str],
        characters: List[str],
        num_variants: int = 20,
        output_dir: Optional[str] = None
    ) -> Dict[str, Any]:
        """Process video with both systems and combine results"""
        
        print(f"\n{'='*80}")
        print(f"HYBRID NETFLIX + DISNEY+ PROCESSING")
        print(f"{'='*80}")
        print(f"Title: {title}")
        print(f"Genre: {', '.join(genre)}")
        print(f"Requested Variants: {num_variants}")
        
        content_id = Path(video_path).stem
        
        # 1. Run Netflix System
        print("\n1️⃣ Running Netflix System...")
        netflix_output_dir = f"{content_id}_netflix_hybrid"
        netflix_results = self.netflix_system.process(video_path, netflix_output_dir)
        
        # Netflix system returns a list, not dict
        netflix_variants = netflix_results if isinstance(netflix_results, list) else netflix_results.get('variants', [])
        print(f"✓ Netflix generated {len(netflix_variants)} thumbnails")
        
        # 2. Run Disney+ System
        print("\n2️⃣ Running Disney+ System...")
        disney_results = self.disney_system.process_content(
            video_path=video_path,
            title=title,
            genre=genre,
            characters=characters,
            num_variants=15,
            output_dir=f"{content_id}_disney_hybrid"
        )
        print(f"✓ Disney+ generated {len(disney_results.get('variants', {}).get('variants', []))} thumbnails")
        
        # 3. Combine and deduplicate results
        print("\n3️⃣ Combining Results...")
        combined_thumbnails = self._combine_results(netflix_variants, disney_results, video_path)
        print(f"✓ Combined {len(combined_thumbnails)} unique thumbnails")
        
        # 4. Select best diverse variants
        print("\n4️⃣ Selecting Best Variants...")
        final_variants = self._select_diverse_variants(combined_thumbnails, num_variants)
        print(f"✓ Selected {len(final_variants)} final variants")
        
        # 5. Save final results
        print("\n5️⃣ Saving Final Results...")
        if output_dir is None:
            output_dir = f"{content_id}_hybrid_final"
        
        final_results = self._save_final_results(
            final_variants, 
            output_dir, 
            title, 
            genre, 
            content_id
        )
        
        return final_results
    
    def _combine_results(
        self, 
        netflix_variants: List[Dict[str, Any]], 
        disney_results: Dict[str, Any],
        video_path: str
    ) -> List[Dict[str, Any]]:
        """Combine Netflix and Disney results, removing duplicates"""
        
        combined = []
        seen_timestamps = set()
        
        # Add Netflix results
        for variant in netflix_variants:
            timestamp = variant.get('timestamp', 0)
            if timestamp not in seen_timestamps:
                combined.append({
                    'source': 'netflix',
                    'timestamp': timestamp,
                    'scene_type': variant.get('scene_type', 'unknown'),
                    'composition': variant.get('composition', 'unknown'),
                    'people_count': variant.get('people_count', 0),
                    'score': variant.get('score', 0),
                    'description': variant.get('description', ''),
                    'metadata': {
                        'scene_type': variant.get('scene_type', 'unknown'),
                        'composition': variant.get('composition', 'unknown'),
                        'character_count': variant.get('people_count', 0),
                        'emotion': 'neutral',
                        'action_level': 0
                    }
                })
                seen_timestamps.add(timestamp)
        
        # Add Disney results
        disney_variants = disney_results.get('variants', {}).get('variants', [])
        for variant in disney_variants:
            thumb_data = variant.get('thumbnail', {})
            timestamp = thumb_data.get('timestamp', 0)
            
            # Only add if not too close to existing timestamps (within 2 seconds)
            too_close = any(abs(timestamp - seen_ts) < 2.0 for seen_ts in seen_timestamps)
            
            if not too_close:
                analysis = thumb_data.get('analysis', {})
                metadata = thumb_data.get('metadata', {})
                
                combined.append({
                    'source': 'disney',
                    'timestamp': timestamp,
                    'scene_type': analysis.get('scene_type', 'unknown'),
                    'composition': analysis.get('composition', 'unknown'),
                    'people_count': len(analysis.get('characters', [])),
                    'score': thumb_data.get('score', 0),
                    'description': f"{analysis.get('scene_type', 'unknown')} with {len(analysis.get('characters', []))} characters",
                    'metadata': metadata,
                    'frame': thumb_data.get('frame')  # Store frame if available
                })
                seen_timestamps.add(timestamp)
        
        return combined
    
    def _select_diverse_variants(
        self, 
        thumbnails: List[Dict[str, Any]], 
        num_variants: int
    ) -> List[Dict[str, Any]]:
        """Select diverse variants prioritizing different scene types"""
        
        # Categorize thumbnails
        categories = {
            'hero_closeup': [],
            'ensemble': [],
            'duo_scene': [],
            'action': [],
            'emotional': [],
            'romantic': [],
            'dramatic': [],
            'other': []
        }
        
        for thumb in thumbnails:
            scene_type = thumb.get('scene_type', '').lower()
            composition = thumb.get('composition', '').lower()
            people_count = thumb.get('people_count', 0)
            
            # Categorize based on scene type and composition
            if 'hero' in scene_type or 'closeup' in composition:
                categories['hero_closeup'].append(thumb)
            elif 'ensemble' in scene_type or people_count >= 4:
                categories['ensemble'].append(thumb)
            elif 'duo' in scene_type or people_count == 2:
                categories['duo_scene'].append(thumb)
            elif 'action' in scene_type or 'fight' in scene_type:
                categories['action'].append(thumb)
            elif 'romantic' in scene_type or 'romance' in scene_type:
                categories['romantic'].append(thumb)
            elif 'dramatic' in scene_type or 'tense' in scene_type:
                categories['dramatic'].append(thumb)
            elif 'emotional' in scene_type:
                categories['emotional'].append(thumb)
            else:
                categories['other'].append(thumb)
        
        # Select diverse variants
        selected = []
        category_order = ['hero_closeup', 'ensemble', 'action', 'duo_scene', 'romantic', 'dramatic', 'emotional', 'other']
        
        for category in category_order:
            if len(selected) >= num_variants:
                break
            
            candidates = categories[category]
            if candidates:
                # Sort by score and take the best
                candidates.sort(key=lambda x: x.get('score', 0), reverse=True)
                selected.append(candidates[0])
        
        # Fill remaining slots with highest scoring thumbnails
        remaining_needed = num_variants - len(selected)
        if remaining_needed > 0:
            remaining = [t for t in thumbnails if t not in selected]
            remaining.sort(key=lambda x: x.get('score', 0), reverse=True)
            selected.extend(remaining[:remaining_needed])
        
        return selected[:num_variants]
    
    def _save_final_results(
        self,
        variants: List[Dict[str, Any]],
        output_dir: str,
        title: str,
        genre: List[str],
        content_id: str
    ) -> Dict[str, Any]:
        """Save final hybrid results"""
        
        output_path = Path(output_dir)
        output_path.mkdir(exist_ok=True)
        
        saved_files = []
        
        for i, variant in enumerate(variants):
            timestamp = variant['timestamp']
            source = variant['source']
            scene_type = variant['scene_type']
            
            # Extract frame
            frame = variant.get('frame')
            if frame is None:
                # Need to extract frame from video
                cap = cv2.VideoCapture(variants[0].get('video_path', ''))
                if cap.isOpened():
                    frame_num = int(timestamp * cap.get(cv2.CAP_PROP_FPS))
                    cap.set(cv2.CAP_PROP_POS_FRAMES, frame_num)
                    ret, frame = cap.read()
                    cap.release()
                    if not ret:
                        continue
            
            if frame is not None:
                filename = f"hybrid_{i+1:02d}_{source}_{scene_type}_t{timestamp:.2f}.jpg"
                filepath = output_path / filename
                cv2.imwrite(str(filepath), frame)
                saved_files.append(str(filepath))
                
                print(f"   ✓ {filename}")
                print(f"      Source: {source.upper()}")
                print(f"      Scene: {scene_type}")
                print(f"      Characters: {variant.get('people_count', 0)}")
                print(f"      Score: {variant.get('score', 0):.2f}")
        
        # Save metadata
        metadata_file = output_path / "hybrid_metadata.json"
        
        hybrid_metadata = {
            "content_id": content_id,
            "title": title,
            "genre": genre,
            "timestamp": datetime.now().isoformat(),
            "system": "Hybrid Netflix + Disney+",
            "variants": [
                {
                    "id": i + 1,
                    "source": v['source'],
                    "timestamp": v['timestamp'],
                    "scene_type": v['scene_type'],
                    "composition": v['composition'],
                    "character_count": v['people_count'],
                    "score": v['score'],
                    "description": v['description']
                }
                for i, v in enumerate(variants)
            ],
            "statistics": {
                "netflix_thumbnails": len([v for v in variants if v['source'] == 'netflix']),
                "disney_thumbnails": len([v for v in variants if v['source'] == 'disney']),
                "total_variants": len(variants),
                "scene_types": list(set(v['scene_type'] for v in variants)),
                "compositions": list(set(v['composition'] for v in variants))
            }
        }
        
        with open(metadata_file, 'w') as f:
            json.dump(hybrid_metadata, f, indent=2)
        
        print(f"✓ Metadata saved: {metadata_file}")
        
        return {
            "output_dir": str(output_path),
            "thumbnails": saved_files,
            "variants": variants,
            "metadata": hybrid_metadata
        }


def main():
    parser = argparse.ArgumentParser(description="Hybrid Netflix + Disney+ Thumbnail Generation System")
    parser.add_argument("video", help="Input video file")
    parser.add_argument("--title", required=True, help="Content title")
    parser.add_argument("--genre", nargs="+", default=["action"], help="Content genres")
    parser.add_argument("--characters", nargs="+", default=[], help="Character names")
    parser.add_argument("--variants", type=int, default=20, help="Number of variants")
    parser.add_argument("--output-dir", help="Output directory")
    
    args = parser.parse_args()
    
    # Initialize hybrid system
    system = HybridThumbnailSystem()
    
    # Process content
    results = system.process_video(
        video_path=args.video,
        title=args.title,
        genre=args.genre,
        characters=args.characters,
        num_variants=args.variants,
        output_dir=args.output_dir
    )
    
    print(f"\n{'='*80}")
    print("✓ HYBRID PROCESSING COMPLETE")
    print(f"{'='*80}")
    print(f"✓ Output Location: {results['output_dir']}")
    print(f"✓ Thumbnails Generated: {len(results['thumbnails'])}")
    print(f"✓ Netflix Contributions: {results['metadata']['statistics']['netflix_thumbnails']}")
    print(f"✓ Disney+ Contributions: {results['metadata']['statistics']['disney_thumbnails']}")
    print(f"✓ System: Hybrid Netflix + Disney+ (Best of Both Worlds)")
    print("="*80)


if __name__ == '__main__':
    main()
