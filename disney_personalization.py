"""
Disney+ Personalization and A/B Testing System
Complete mirror of Disney's personalization algorithms
"""

import json
from typing import List, Dict, Any, Optional
from dataclasses import dataclass, field
from datetime import datetime
import random

from disney_metadata_spec import ContentMetadata, Character, Scene


@dataclass
class UserProfile:
    """Disney user profile for personalization"""
    user_id: str
    age_group: str  # child, teen, young_adult, adult, senior
    gender: Optional[str] = None
    location: Optional[str] = None
    
    # Content preferences
    preferred_genres: List[str] = field(default_factory=list)
    favorite_characters: List[str] = field(default_factory=list)
    preferred_scene_types: List[str] = field(default_factory=list)
    
    # Behavior
    viewing_history: List[str] = field(default_factory=list)
    search_queries: List[str] = field(default_factory=list)
    click_through_rates: Dict[str, float] = field(default_factory=dict)
    watch_times: Dict[str, float] = field(default_factory=dict)
    
    # Thumbnail preferences
    thumbnail_types_clicked: List[str] = field(default_factory=list)
    composition_preferences: List[str] = field(default_factory=list)
    emotion_preferences: List[str] = field(default_factory=list)
    
    # A/B test assignments
    test_group: Optional[str] = None
    active_experiments: List[str] = field(default_factory=list)


@dataclass
class ABTest:
    """Disney A/B test configuration"""
    test_id: str
    test_name: str
    description: str
    
    # Test configuration
    variants: List[Dict[str, Any]]  # Different thumbnail strategies
    traffic_split: Dict[str, float]  # Percentage per variant
    
    # Metrics to track
    success_metrics: List[str] = field(default_factory=lambda: [
        'click_through_rate', 'watch_time', 'completion_rate', 'engagement_score'
    ])
    
    # Experiment dates
    start_date: str = ""
    end_date: str = ""
    status: str = "active"  # active, paused, completed
    
    # Results
    results: Dict[str, Dict[str, float]] = field(default_factory=dict)


class DisneyPersonalizationEngine:
    """Disney's personalization engine for thumbnails"""
    
    def __init__(self):
        self.active_tests: List[ABTest] = []
    
    def personalize_thumbnails(
        self, 
        thumbnails: List[Dict[str, Any]], 
        user_profile: UserProfile,
        metadata: ContentMetadata
    ) -> List[Dict[str, Any]]:
        """Personalize thumbnails based on user profile"""
        
        # Score each thumbnail for this user
        personalized_scores = []
        for thumb in thumbnails:
            score = self._calculate_personalization_score(thumb, user_profile, metadata)
            personalized_scores.append((thumb, score))
        
        # Sort by personalized score
        personalized_scores.sort(key=lambda x: x[1], reverse=True)
        
        # Apply A/B testing if active
        if user_profile.test_group:
            personalized_scores = self._apply_ab_testing(personalized_scores, user_profile)
        
        # Select top thumbnails
        selected = [thumb for thumb, score in personalized_scores[:10]]
        
        return selected
    
    def _calculate_personalization_score(
        self, 
        thumbnail: Dict[str, Any], 
        user_profile: UserProfile,
        metadata: ContentMetadata
    ) -> float:
        """Disney's personalization scoring algorithm"""
        base_score = thumbnail.get('score', 0.0)
        personalization_boost = 0.0
        
        analysis = thumbnail.get('analysis', {})
        scene_type = analysis.get('scene_type', '')
        emotion = analysis.get('emotion', '')
        composition = analysis.get('composition', '')
        
        # Genre preference (30% weight)
        if metadata.genre and user_profile.preferred_genres:
            matching_genres = len(set(metadata.genre) & set(user_profile.preferred_genres))
            personalization_boost += (matching_genres / len(metadata.genre)) * 2.0 * 0.3
        
        # Scene type preference (25% weight)
        if scene_type in user_profile.preferred_scene_types:
            personalization_boost += 1.5 * 0.25
        
        # Composition preference (20% weight)
        if composition in user_profile.composition_preferences:
            personalization_boost += 1.0 * 0.2
        
        # Emotion preference (15% weight)
        if emotion in user_profile.emotion_preferences:
            personalization_boost += 1.0 * 0.15
        
        # Historical performance (10% weight)
        thumb_type = f"{scene_type}_{composition}"
        if thumb_type in user_profile.thumbnail_types_clicked:
            click_rate = user_profile.click_through_rates.get(thumb_type, 0.0)
            personalization_boost += click_rate * 2.0 * 0.1
        
        return base_score + personalization_boost
    
    def _apply_ab_testing(
        self, 
        thumbnails: List[tuple], 
        user_profile: UserProfile
    ) -> List[tuple]:
        """Apply A/B testing modifications"""
        # Find active test for this user
        for test in self.active_tests:
            if test.test_id in user_profile.active_experiments:
                # Apply test variant logic
                variant = user_profile.test_group
                
                if variant == 'character_focus':
                    # Boost character-focused thumbnails
                    thumbnails = [(thumb, score * 1.2 if 'character' in str(thumb.get('analysis', {})) else score) 
                                for thumb, score in thumbnails]
                
                elif variant == 'action_boost':
                    # Boost action scenes
                    thumbnails = [(thumb, score * 1.3 if thumb.get('analysis', {}).get('action_level', 0) > 5 else score) 
                                for thumb, score in thumbnails]
                
                elif variant == 'ensemble_preference':
                    # Boost ensemble scenes
                    thumbnails = [(thumb, score * 1.15 if thumb.get('analysis', {}).get('scene_type') == 'ensemble' else score) 
                                for thumb, score in thumbnails]
                
                break
        
        # Resort after modifications
        thumbnails.sort(key=lambda x: x[1], reverse=True)
        
        return thumbnails
    
    def track_thumbnail_performance(
        self,
        thumbnail_id: str,
        user_profile: UserProfile,
        action: str,  # click, view, complete
        metadata: Dict[str, Any]
    ):
        """Track thumbnail performance Disney-style"""
        
        # Update click-through rates
        scene_type = metadata.get('scene_type', 'unknown')
        composition = metadata.get('composition', 'unknown')
        thumb_type = f"{scene_type}_{composition}"
        
        if action == 'click':
            user_profile.thumbnail_types_clicked.append(thumb_type)
            current_clicks = user_profile.click_through_rates.get(thumb_type, 0.0)
            user_profile.click_through_rates[thumb_type] = current_clicks + 1.0
        
        elif action == 'view':
            watch_time = metadata.get('watch_time', 0.0)
            current_watch = user_profile.watch_times.get(thumb_type, 0.0)
            user_profile.watch_times[thumb_type] = current_watch + watch_time
        
        elif action == 'complete':
            # Mark as high-quality thumbnail
            if thumb_type not in user_profile.preferred_scene_types:
                user_profile.preferred_scene_types.append(thumb_type)


class DisneyABTestingFramework:
    """Disney's A/B testing framework"""
    
    def __init__(self):
        self.active_tests: List[ABTest] = []
    
    def create_test(self, config: Dict[str, Any]) -> ABTest:
        """Create new A/B test"""
        test = ABTest(
            test_id=config.get('test_id', f"test_{datetime.now().isoformat()}"),
            test_name=config.get('test_name'),
            description=config.get('description'),
            variants=config.get('variants', []),
            traffic_split=config.get('traffic_split', {'control': 0.5, 'variant_a': 0.5}),
            start_date=datetime.now().isoformat(),
            status='active'
        )
        
        self.active_tests.append(test)
        return test
    
    def get_user_variant(self, user_profile: UserProfile) -> str:
        """Assign user to test variant"""
        if not self.active_tests:
            return 'control'
        
        # Find most relevant test
        active_test = self.active_tests[0] if self.active_tests else None
        
        if not active_test:
            return 'control'
        
        # Assign based on traffic split
        rand = random.random()
        cumulative = 0.0
        
        for variant, percentage in active_test.traffic_split.items():
            cumulative += percentage
            if rand <= cumulative:
                user_profile.test_group = variant
                user_profile.active_experiments = [active_test.test_id]
                return variant
        
        return 'control'
    
    def record_result(
        self, 
        test_id: str, 
        variant: str, 
        metric: str, 
        value: float
    ):
        """Record A/B test result"""
        for test in self.active_tests:
            if test.test_id == test_id:
                if variant not in test.results:
                    test.results[variant] = {}
                
                if metric not in test.results[variant]:
                    test.results[variant][metric] = []
                
                test.results[variant][metric].append(value)
                break
    
    def analyze_results(self, test_id: str) -> Dict[str, Any]:
        """Analyze A/B test results"""
        for test in self.active_tests:
            if test.test_id == test_id:
                analysis = {
                    'test_id': test_id,
                    'test_name': test.test_name,
                    'variants': {}
                }
                
                for variant, metrics in test.results.items():
                    variant_analysis = {}
                    for metric, values in metrics.items():
                        if values:
                            variant_analysis[metric] = {
                                'mean': sum(values) / len(values),
                                'count': len(values),
                                'std': self._calculate_std(values)
                            }
                    
                    analysis['variants'][variant] = variant_analysis
                
                # Determine winner
                if 'control' in analysis['variants'] and len(analysis['variants']) > 1:
                    control_click_rate = analysis['variants']['control'].get('click_through_rate', {}).get('mean', 0)
                    
                    for variant, data in analysis['variants'].items():
                        if variant != 'control':
                            variant_click_rate = data.get('click_through_rate', {}).get('mean', 0)
                            improvement = ((variant_click_rate - control_click_rate) / control_click_rate * 100) if control_click_rate > 0 else 0
                            variant_analysis = analysis['variants'][variant]
                            variant_analysis['improvement'] = f"{improvement:.2f}%"
                
                return analysis
        
        return {}
    
    def _calculate_std(self, values: List[float]) -> float:
        """Calculate standard deviation"""
        if not values:
            return 0.0
        mean = sum(values) / len(values)
        variance = sum((x - mean) ** 2 for x in values) / len(values)
        return variance ** 0.5


class DisneyContentAnalyzer:
    """Disney's complete content analysis system"""
    
    def __init__(self):
        self.personalization_engine = DisneyPersonalizationEngine()
        self.ab_framework = DisneyABTestingFramework()
    
    def generate_thumbnail_variants(
        self,
        thumbnails: List[Dict[str, Any]],
        metadata: ContentMetadata,
        num_variants: int = 15
    ) -> Dict[str, Any]:
        """Generate Disney-style thumbnail variants with maximum diversity"""
        
        variants = {
            'metadata': {
                'content_id': metadata.content_id,
                'title': metadata.title,
                'genre': metadata.genre,
                'generated_at': datetime.now().isoformat()
            },
            'variants': []
        }
        
        # Enhanced categorization for maximum diversity
        hero_shots = []
        heroine_shots = []
        ensemble_shots = []
        duo_shots = []
        trio_shots = []
        action_shots = []
        fight_scenes = []
        emotional_shots = []
        closeup_shots = []
        wide_shots = []
        dramatic_shots = []
        comedic_shots = []
        romantic_shots = []
        establishing_shots = []
        
        for thumb in thumbnails:
            analysis = thumb.get('analysis', {})
            scene_type = analysis.get('scene_type', '')
            composition = analysis.get('composition', '')
            emotion = analysis.get('emotion', '')
            action_level = analysis.get('action_level', 0)
            intensity = analysis.get('intensity', 0)
            
            # Hero/Heroine shots
            if 'hero_closeup' in scene_type or 'character_focus' in scene_type:
                if composition == 'closeup':
                    closeup_shots.append(thumb)
                hero_shots.append(thumb)
            
            # Ensemble shots
            if scene_type == 'ensemble':
                ensemble_shots.append(thumb)
            
            # Duo/Trio shots
            if scene_type == 'duo_scene':
                duo_shots.append(thumb)
            elif scene_type == 'trio_scene':
                trio_shots.append(thumb)
            
            # Action and fight scenes
            if action_level > 6:
                action_shots.append(thumb)
            if action_level > 7:
                fight_scenes.append(thumb)
            
            # Emotional content
            if intensity > 0.7:
                emotional_shots.append(thumb)
            
            # Composition-based
            if composition == 'closeup':
                closeup_shots.append(thumb)
            elif composition == 'wide':
                wide_shots.append(thumb)
            
            # Emotion-based
            if emotion in ['tense', 'dramatic']:
                dramatic_shots.append(thumb)
            elif emotion in ['uplifting', 'happy']:
                comedic_shots.append(thumb)
            elif emotion in ['romantic']:
                romantic_shots.append(thumb)
            
            # Establishing shots
            if scene_type == 'establishing':
                establishing_shots.append(thumb)
        
        # Create diverse variants with priority order
        selected = []
        variant_types = {
            'hero_closeup': closeup_shots,
            'heroine_closeup': heroine_shots,
            'ensemble_shot': ensemble_shots,
            'action_sequence': action_shots,
            'fight_scene': fight_scenes,
            'duo_interaction': duo_shots,
            'trio_scene': trio_shots,
            'emotional_moment': emotional_shots,
            'dramatic_scene': dramatic_shots,
            'comedic_moment': comedic_shots,
            'romantic_scene': romantic_shots,
            'wide_establishing': wide_shots,
            'establishing_shot': establishing_shots,
            'hero_shot': hero_shots
        }
        
        # Select diverse variants
        for variant_type, candidate_list in variant_types.items():
            if candidate_list and len(selected) < num_variants:
                # Select best from this category
                candidate_list.sort(key=lambda x: x.get('score', 0), reverse=True)
                selected.append({
                    'variant_type': variant_type,
                    'thumbnail': candidate_list[0]
                })
        
        # If we still need more variants, add from remaining thumbnails
        remaining_needed = num_variants - len(selected)
        if remaining_needed > 0:
            remaining_thumbnails = [t for t in thumbnails if t not in [s['thumbnail'] for s in selected]]
            remaining_thumbnails.sort(key=lambda x: x.get('score', 0), reverse=True)
            
            for i, thumb in enumerate(remaining_thumbnails[:remaining_needed]):
                selected.append({
                    'variant_type': f'diverse_shot_{i+1}',
                    'thumbnail': thumb
                })
        
        variants['variants'] = selected[:num_variants]
        
        return variants
    
    def apply_disney_filters(
        self,
        thumbnails: List[Dict[str, Any]],
        metadata: ContentMetadata
    ) -> List[Dict[str, Any]]:
        """Apply Disney's content filters - more permissive for diversity"""
        
        filtered = []
        
        for thumb in thumbnails:
            analysis = thumb.get('analysis', {})
            
            # Family-friendly filter (always pass for Disney)
            if not analysis.get('family_friendly', True):
                continue
            
            # Much lower quality threshold for diversity
            if thumb.get('score', 0) < 0.5:  # Very low threshold
                continue
            
            # Always pass genre alignment for diversity
            # if not thumb.get('genre_alignment', True):
            #     continue
            
            filtered.append(thumb)
        
        return filtered
