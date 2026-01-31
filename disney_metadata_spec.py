"""
Disney+ Metadata Specification System
Complete mirror of Disney's metadata standards
"""

from dataclasses import dataclass, field
from typing import List, Dict, Optional, Any
from datetime import datetime
import json

@dataclass
class Character:
    """Disney character metadata specification"""
    name: str
    character_type: str  # hero, heroine, villain, supporting, ensemble
    importance: str  # primary, secondary, background
    age_range: Optional[str] = None  # child, teen, young_adult, adult, elderly
    gender: Optional[str] = None  # male, female, non_binary
    role: Optional[str] = None  # protagaonist, antagonist, deuteragonist, tritagonist
    traits: List[str] = field(default_factory=list)  # brave, kind, funny, etc.
    appearance_tags: List[str] = field(default_factory=list)  # superhero, princess, etc.
    
@dataclass
class Scene:
    """Disney scene metadata specification"""
    timestamp: str  # HH:MM:SS or seconds
    scene_type: str  # action, romance, ensemble, dramatic, comedic, fantasy, realistic
    characters_present: List[str]
    emotion: str  # happy, sad, excited, tense, romantic, adventurous
    setting: str  # indoor, outdoor, fantasy, realistic, space, underwater
    composition: str  # closeup, mid, wide, extreme_wide, aerial
    action_level: int = 0  # 0-10 scale
    intensity: float = 0.0  # 0.0-1.0
    family_friendly: bool = True
    visual_interest: float = 0.0  # 0.0-1.0
    color_saturation: float = 0.0  # 0.0-1.0
    
@dataclass
class ContentMetadata:
    """Complete Disney content metadata specification"""
    content_id: str
    title: str
    content_type: str  # movie, tv_show, series, short, documentary
    genre: List[str]
    subgenre: List[str] = field(default_factory=list)
    year: Optional[int] = None
    rating: str = "PG"  # G, PG, PG-13, R
    duration_minutes: Optional[int] = None
    studio: str = "Disney"
    
    # Character information
    characters: List[Character] = field(default_factory=list)
    
    # Scene information
    scenes: List[Scene] = field(default_factory=list)
    
    # Target audience
    target_audience: Dict[str, Any] = field(default_factory=dict)
    age_rating_recommendation: str = "all_ages"
    demographic_tags: List[str] = field(default_factory=list)
    
    # Content themes
    themes: List[str] = field(default_factory=list)  # friendship, courage, family, etc.
    tone: str = "uplifting"  # uplifting, dramatic, comedic, intense, heartwarming
    
    # Visual characteristics
    animation_style: Optional[str] = None  # 2d, 3d, stop_motion, live_action
    color_palette: Dict[str, float] = field(default_factory=dict)
    visual_complexity: str = "moderate"  # simple, moderate, complex, hyper_complex
    
    # Disney-specific
    franchise: Optional[str] = None  # Marvel, Star Wars, Pixar, Disney Classic
    era: Optional[str] = None  # classic, renaissance, modern, contemporary
    awards: List[str] = field(default_factory=list)
    
    # Thumbnail metadata
    thumbnail_candidates: List[Dict[str, Any]] = field(default_factory=list)
    selected_thumbnails: List[Dict[str, Any]] = field(default_factory=list)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to Disney metadata dictionary"""
        return {
            "content_id": self.content_id,
            "title": self.title,
            "content_type": self.content_type,
            "genre": self.genre,
            "characters": [
                {
                    "name": c.name,
                    "type": c.character_type,
                    "importance": c.importance,
                    "demographics": {
                        "age_range": c.age_range,
                        "gender": c.gender
                    },
                    "role": c.role,
                    "traits": c.traits,
                    "appearance_tags": c.appearance_tags
                }
                for c in self.characters
            ],
            "scenes": [
                {
                    "timestamp": s.timestamp,
                    "type": s.scene_type,
                    "characters_present": s.characters_present,
                    "emotion": s.emotion,
                    "setting": s.setting,
                    "composition": s.composition,
                    "action_level": s.action_level,
                    "intensity": s.intensity,
                    "family_friendly": s.family_friendly,
                    "visual_interest": s.visual_interest,
                    "color_saturation": s.color_saturation
                }
                for s in self.scenes
            ],
            "target_audience": self.target_audience,
            "themes": self.themes,
            "tone": self.tone,
            "thumbnail_candidates": self.thumbnail_candidates
        }
    
    def to_json(self) -> str:
        """Convert to JSON string"""
        return json.dumps(self.to_dict(), indent=2, default=str)


class DisneyMetadataBuilder:
    """Builder for Disney metadata specification"""
    
    @staticmethod
    def create_for_cop_show(title: str, content_id: str, characters: List[str]) -> ContentMetadata:
        """Create metadata for cop/police procedural shows"""
        metadata = ContentMetadata(
            content_id=content_id,
            title=title,
            content_type="tv_show",
            genre=["drama", "crime", "procedural"],
            subgenre=["police_procedural", "detective"],
            rating="TV-14",
            studio="ABC Studios",
            tone="dramatic",
            themes=["justice", "duty", "camaraderie", "professionalism"],
            demographic_tags=["adults", "young_adults", "crime_fans"]
        )
        
        # Add characters
        hero_roles = ["lead_detective", "rookie_officer", "veteran_officer", "captain", "forensic_specialist"]
        metadata.characters = [
            Character(
                name=name,
                character_type="hero" if "lead" in name.lower() or "captain" in name.lower() else "supporting",
                importance="primary" if i < 3 else "secondary",
                age_range="adult",
                gender=None,
                traits=["dedicated", "skilled", "professional"],
                appearance_tags=["officer", "detective", "police"]
            )
            for i, name in enumerate(characters[:10])
        ]
        
        return metadata
    
    @staticmethod
    def enhance_with_analysis(metadata: ContentMetadata, analysis_results: Dict[str, Any]):
        """Enhance metadata with AI analysis results"""
        # Add scene information from analysis
        if "scenes" in analysis_results:
            metadata.scenes = [
                Scene(
                    timestamp=str(ts),
                    scene_type=scene.get("type", "unknown"),
                    characters_present=scene.get("characters", []),
                    emotion=scene.get("emotion", "neutral"),
                    setting=scene.get("setting", "unknown"),
                    composition=scene.get("composition", "wide"),
                    action_level=scene.get("action_level", 0),
                    intensity=scene.get("intensity", 0.0),
                    family_friendly=scene.get("family_friendly", True),
                    visual_interest=scene.get("visual_interest", 0.0),
                    color_saturation=scene.get("color_saturation", 0.0)
                )
                for ts, scene in analysis_results["scenes"].items()
            ]
        
        # Add thumbnail candidates
        if "thumbnails" in analysis_results:
            metadata.thumbnail_candidates = analysis_results["thumbnails"]









