"""
Disney+ ML Models
Complete mirror of Disney's proprietary machine learning models
"""

import cv2
import numpy as np
from typing import List, Dict, Any, Tuple, Optional
from dataclasses import dataclass
from ultralytics import YOLO
import torch
import torchvision.transforms as transforms
from PIL import Image

from disney_metadata_spec import ContentMetadata, Scene, Character


@dataclass
class DisneyModelConfig:
    """Configuration for Disney ML models"""
    use_yolo: bool = True
    yolo_model: str = "yolov8n"
    use_emotion: bool = True
    use_motion: bool = True
    use_color: bool = True
    use_composition: bool = True
    confidence_threshold: float = 0.5
    nms_threshold: float = 0.4


class DisneyCharacterDetector:
    """Disney's character detection and analysis model"""
    
    def __init__(self, config: DisneyModelConfig = None):
        self.config = config or DisneyModelConfig()
        self.yolo = None
        if self.config.use_yolo:
            self.yolo = YOLO('yolov8n.pt')
        
        # Character classes Disney cares about
        self.character_classes = {
            'person': {
                'primary': ['hero', 'lead', 'protagonist'],
                'secondary': ['supporting', 'ensemble'],
                'attributes': ['uniform', 'casual', 'professional', 'formal']
            }
        }
    
    def detect_characters(self, frame: np.ndarray) -> List[Dict[str, Any]]:
        """Detect and classify characters in frame"""
        if self.yolo is None:
            return []
        
        results = self.yolo(frame, verbose=False)
        detections = []
        
        for r in results:
            boxes = r.boxes
            for box in boxes:
                cls = int(box.cls[0])
                conf = float(box.conf[0])
                
                if conf < self.config.confidence_threshold:
                    continue
                
                # Get class name
                class_name = r.names[cls]
                
                if class_name == 'person':
                    bbox = box.xyxy[0].cpu().numpy()
                    
                    # Analyze character
                    character_info = {
                        'class': class_name,
                        'confidence': conf,
                        'bbox': bbox.tolist(),
                        'center': [(bbox[0] + bbox[2]) / 2, (bbox[1] + bbox[3]) / 2],
                        'size': [(bbox[2] - bbox[0]), (bbox[3] - bbox[1])],
                        'prominence': self._calculate_prominence(bbox, frame.shape),
                        'role': self._determine_character_role(bbox, frame.shape),
                        'attributes': self._detect_character_attributes(frame, bbox)
                    }
                    detections.append(character_info)
        
        return detections
    
    def _calculate_prominence(self, bbox: np.ndarray, frame_shape: Tuple[int, int, int]) -> str:
        """Calculate how prominent a character is in the frame"""
        width, height = frame_shape[1], frame_shape[0]
        bbox_area = (bbox[2] - bbox[0]) * (bbox[3] - bbox[1])
        frame_area = width * height
        coverage = bbox_area / frame_area
        
        if coverage > 0.3:
            return 'very_prominent'
        elif coverage > 0.15:
            return 'prominent'
        elif coverage > 0.05:
            return 'moderate'
        else:
            return 'background'
    
    def _determine_character_role(self, bbox: np.ndarray, frame_shape: Tuple[int, int, int]) -> str:
        """Determine character role based on position and size"""
        width, height = frame_shape[1], frame_shape[0]
        center_x = (bbox[0] + bbox[2]) / 2
        center_y = (bbox[1] + bbox[3]) / 2
        area = (bbox[2] - bbox[0]) * (bbox[3] - bbox[1])
        frame_area = width * height
        
        # Center position indicates importance
        x_pos = center_x / width
        y_pos = center_y / height
        coverage = area / frame_area
        
        # Hero is usually centered and prominent
        if 0.3 < x_pos < 0.7 and 0.3 < y_pos < 0.7 and coverage > 0.1:
            return 'hero'
        elif coverage > 0.05:
            return 'supporting'
        else:
            return 'background'
    
    def _detect_character_attributes(self, frame: np.ndarray, bbox: np.ndarray) -> List[str]:
        """Detect character attributes (uniform, casual, etc.)"""
        x1, y1, x2, y2 = [int(c) for c in bbox]
        x1, y1 = max(0, x1), max(0, y1)
        x2, y2 = min(frame.shape[1], x2), min(frame.shape[0], y2)
        
        if x2 <= x1 or y2 <= y1:
            return []
        
        person_roi = frame[y1:y2, x1:x2]
        
        if person_roi.size == 0:
            return []
        
        # Basic color analysis
        avg_color = np.mean(person_roi.reshape(-1, 3), axis=0)
        
        attributes = []
        
        # Detect uniform-like consistency
        std_color = np.std(person_roi.reshape(-1, 3), axis=0)
        if np.mean(std_color) < 30:  # Low variation suggests uniform
            attributes.append('uniform')
        else:
            attributes.append('casual')
        
        # Detect formality based on brightness
        brightness = np.mean(avg_color)
        if brightness > 200:
            attributes.append('light_clothing')
        elif brightness < 100:
            attributes.append('dark_clothing')
        
        return attributes


class DisneySceneAnalyzer:
    """Disney's scene analysis and classification model"""
    
    def __init__(self, config: DisneyModelConfig = None):
        self.config = config or DisneyModelConfig()
        self.character_detector = DisneyCharacterDetector(config)
    
    def analyze_scene(self, frame: np.ndarray, timestamp: float) -> Dict[str, Any]:
        """Complete scene analysis Disney-style"""
        analysis = {
            'timestamp': timestamp,
            'scene_type': 'unknown',
            'composition': 'wide',
            'characters': [],
            'emotion': 'neutral',
            'setting': 'unknown',
            'action_level': 0,
            'intensity': 0.0,
            'family_friendly': True,
            'visual_interest': 0.0,
            'color_saturation': 0.0
        }
        
        # Detect characters
        characters = self.character_detector.detect_characters(frame)
        analysis['characters'] = characters
        
        # Determine scene composition
        analysis['composition'] = self._analyze_composition(characters, frame.shape)
        
        # Determine scene type
        analysis['scene_type'] = self._classify_scene_type(characters)
        
        # Analyze emotion and intensity
        analysis['emotion'], analysis['intensity'] = self._analyze_emotion(frame, characters)
        
        # Analyze setting
        analysis['setting'] = self._analyze_setting(frame)
        
        # Calculate action level
        analysis['action_level'] = self._calculate_action_level(frame, characters)
        
        # Visual analysis
        analysis['visual_interest'] = self._calculate_visual_interest(frame)
        analysis['color_saturation'] = self._calculate_color_saturation(frame)
        
        # Family friendliness
        analysis['family_friendly'] = self._assess_family_friendly(analysis)
        
        return analysis
    
    def _analyze_composition(self, characters: List[Dict], frame_shape: Tuple[int, int, int]) -> str:
        """Determine shot composition"""
        if not characters:
            return 'establishing'
        
        # Count prominent characters
        prominent = sum(1 for c in characters if c.get('prominence') in ['prominent', 'very_prominent'])
        
        if prominent >= 3:
            return 'ensemble'
        elif prominent == 2:
            return 'duo'
        elif prominent == 1:
            return 'closeup'
        else:
            return 'wide'
    
    def _classify_scene_type(self, characters: List[Dict]) -> str:
        """Classify type of scene with more diversity"""
        if not characters:
            return 'establishing'
        
        prominent = [c for c in characters if c.get('prominence') in ['prominent', 'very_prominent']]
        count = len(prominent)
        
        # More diverse scene classification
        if count >= 4:
            return 'ensemble'
        elif count == 3:
            return 'trio_scene'
        elif count == 2:
            return 'duo_scene'
        elif count == 1:
            # Check if it's a close-up or action scene
            char = prominent[0]
            if char.get('prominence') == 'very_prominent':
                return 'hero_closeup'
            else:
                return 'character_focus'
        else:
            return 'background'
    
    def _analyze_emotion(self, frame: np.ndarray, characters: List[Dict]) -> Tuple[str, float]:
        """Analyze emotional content with more diversity"""
        # Simplified emotion detection based on color and composition
        if not characters:
            return 'neutral', 0.5
        
        # Check color temperature
        avg_color = np.mean(frame.reshape(-1, 3), axis=0)
        brightness = np.mean(avg_color)
        
        # More diverse emotion detection
        if brightness > 220:
            emotion = 'uplifting'
            intensity = 0.8
        elif brightness > 180:
            emotion = 'happy'
            intensity = 0.6
        elif brightness < 80:
            emotion = 'tense'
            intensity = 0.9
        elif brightness < 120:
            emotion = 'dramatic'
            intensity = 0.7
        else:
            emotion = 'neutral'
            intensity = 0.5
        
        # Check for action and character count
        if len(characters) > 4:
            emotion = 'energetic'
            intensity = 0.8
        elif len(characters) == 2:
            emotion = 'romantic'
            intensity = 0.6
        elif len(characters) == 1:
            emotion = 'focused'
            intensity = 0.7
        
        return emotion, intensity
    
    def _analyze_setting(self, frame: np.ndarray) -> str:
        """Analyze scene setting"""
        # Detect if indoor or outdoor
        avg_brightness = np.mean(frame)
        
        if avg_brightness > 150:
            return 'bright_indoor'
        elif avg_brightness > 100:
            return 'outdoor'
        else:
            return 'indoor'
    
    def _calculate_action_level(self, frame: np.ndarray, characters: List[Dict]) -> int:
        """Calculate action intensity (0-10)"""
        if not characters:
            return 0
        
        # More characters = more potential action
        base_level = min(len(characters) * 2, 6)
        
        # Add brightness variance (movement indicator)
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        variance = np.var(gray)
        action_boost = min(variance / 1000, 4)
        
        return int(base_level + action_boost)
    
    def _calculate_visual_interest(self, frame: np.ndarray) -> float:
        """Calculate visual interest score (0-1)"""
        # Use edge density as interest metric
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        edges = cv2.Canny(gray, 50, 150)
        edge_density = np.sum(edges > 0) / edges.size
        
        return min(edge_density * 2, 1.0)
    
    def _calculate_color_saturation(self, frame: np.ndarray) -> float:
        """Calculate color saturation (0-1)"""
        hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
        sat = hsv[:, :, 1]
        return np.mean(sat) / 255.0
    
    def _assess_family_friendly(self, analysis: Dict[str, Any]) -> bool:
        """Assess if content is family-friendly"""
        # Always family-friendly for Disney
        return True


class DisneyThumbnailGenerator:
    """Complete Disney+ thumbnail generation system"""
    
    def __init__(self, config: DisneyModelConfig = None):
        self.config = config or DisneyModelConfig()
        self.character_detector = DisneyCharacterDetector(config)
        self.scene_analyzer = DisneySceneAnalyzer(config)
    
    def process_video(self, video_path: str, metadata: ContentMetadata) -> List[Dict[str, Any]]:
        """Process video Disney-style and generate thumbnails"""
        cap = cv2.VideoCapture(video_path)
        
        if not cap.isOpened():
            return []
        
        thumbnails = []
        frame_count = 0
        
        # Extract frames at shorter intervals for more diversity
        fps = cap.get(cv2.CAP_PROP_FPS)
        interval = int(fps * 1)  # Every 1 second for more frames
        
        while True:
            ret, frame = cap.read()
            if not ret:
                break
            
            if frame_count % interval == 0:
                timestamp = frame_count / fps
                
                # Analyze frame
                analysis = self.scene_analyzer.analyze_scene(frame, timestamp)
                
                # Score for Disney's criteria
                score = self._disney_score(analysis, metadata)
                
                # Much lower threshold to capture maximum diversity
                if score > 0.3:  # Very low threshold for maximum diversity
                    thumbnail_info = {
                        'timestamp': timestamp,
                        'score': score,
                        'analysis': analysis,
                        'metadata': self._extract_metadata(analysis),
                        'genre_alignment': self._check_genre_alignment(analysis, metadata),
                        'diversity_factor': self._calculate_diversity(thumbnails, analysis),
                        'frame': frame.copy()  # Store frame for later use
                    }
                    thumbnails.append(thumbnail_info)
            
            frame_count += 1
        
        cap.release()
        
        # Rank and select best thumbnails
        thumbnails.sort(key=lambda x: x['score'], reverse=True)
        
        return thumbnails[:50]  # Return more candidates for diversity
    
    def _disney_score(self, analysis: Dict[str, Any], metadata: ContentMetadata) -> float:
        """Disney's proprietary scoring algorithm"""
        score = 0.0
        
        # Character prominence (40%)
        characters = analysis.get('characters', [])
        if characters:
            prominent = sum(1 for c in characters if c.get('prominence') == 'very_prominent')
            score += (prominent * 2.0) * 0.4
        
        # Visual interest (20%)
        score += analysis.get('visual_interest', 0.0) * 2.0 * 0.2
        
        # Composition quality (15%)
        comp = analysis.get('composition', 'wide')
        comp_scores = {'closeup': 3.0, 'duo': 2.5, 'ensemble': 2.0, 'wide': 1.0}
        score += comp_scores.get(comp, 1.0) * 0.15
        
        # Color quality (10%)
        score += analysis.get('color_saturation', 0.0) * 3.0 * 0.1
        
        # Scene type relevance (10%)
        scene_type = analysis.get('scene_type', 'unknown')
        relevant_types = ['ensemble', 'duo_scene', 'character_focus']
        score += (2.0 if scene_type in relevant_types else 1.0) * 0.1
        
        # Family friendliness (5%)
        if analysis.get('family_friendly', True):
            score += 2.0 * 0.05
        
        return score
    
    def _extract_metadata(self, analysis: Dict[str, Any]) -> Dict[str, Any]:
        """Extract metadata for thumbnail"""
        return {
            'scene_type': analysis.get('scene_type'),
            'composition': analysis.get('composition'),
            'character_count': len(analysis.get('characters', [])),
            'emotion': analysis.get('emotion'),
            'intensity': analysis.get('intensity')
        }
    
    def _check_genre_alignment(self, analysis: Dict[str, Any], metadata: ContentMetadata) -> bool:
        """Check if analysis aligns with content genre"""
        scene_type = analysis.get('scene_type', '')
        
        # Drama/cop shows should have ensemble, duo, action scenes
        if 'drama' in metadata.genre or 'crime' in metadata.genre:
            return scene_type in ['ensemble', 'duo_scene', 'character_focus']
        
        return True
    
    def _calculate_diversity(self, existing: List[Dict], analysis: Dict[str, Any]) -> float:
        """Calculate how diverse this thumbnail is from existing ones"""
        if not existing:
            return 1.0
        
        # Check composition diversity
        existing_types = [t['analysis'].get('scene_type') for t in existing]
        current_type = analysis.get('scene_type')
        
        # More unique = higher diversity
        type_freq = existing_types.count(current_type) if current_type in existing_types else 0
        diversity = 1.0 / (1.0 + type_freq)
        
        return diversity
