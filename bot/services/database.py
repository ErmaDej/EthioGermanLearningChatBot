"""
Database service for Supabase operations.
Handles all CRUD operations for users, lessons, exams, progress, and conversations.
"""
from typing import Optional, List, Dict, Any
from datetime import datetime, timezone
from uuid import UUID, uuid4
import logging

from supabase import create_client, Client
from bot.config import Config

logger = logging.getLogger(__name__)


class DatabaseService:
    """Service for all Supabase database operations."""
    
    def __init__(self):
        self.client: Client = create_client(Config.SUPABASE_URL, Config.SUPABASE_KEY)
    
    # ==================== USER OPERATIONS ====================
    
    async def get_user(self, user_id: int) -> Optional[Dict[str, Any]]:
        """Get user by Telegram ID."""
        try:
            response = self.client.table('users').select('*').eq('id', user_id).execute()
            return response.data[0] if response.data else None
        except Exception as e:
            logger.error(f"Error getting user {user_id}: {e}")
            return None
    
    async def create_user(
        self,
        user_id: int,
        username: Optional[str] = None,
        first_name: Optional[str] = None,
        last_name: Optional[str] = None,
        level: str = 'A1',
        preferred_lang: str = 'english'
    ) -> Optional[Dict[str, Any]]:
        """Create a new user."""
        try:
            data = {
                'id': user_id,
                'username': username,
                'first_name': first_name,
                'last_name': last_name,
                'current_level': level,
                'preferred_lang': preferred_lang,
                'created_at': datetime.now(timezone.utc).isoformat(),
                'last_active': datetime.now(timezone.utc).isoformat()
            }
            response = self.client.table('users').insert(data).execute()
            return response.data[0] if response.data else None
        except Exception as e:
            logger.error(f"Error creating user {user_id}: {e}")
            return None
    
    async def update_user(self, user_id: int, **kwargs) -> Optional[Dict[str, Any]]:
        """Update user fields."""
        try:
            kwargs['last_active'] = datetime.now(timezone.utc).isoformat()
            response = self.client.table('users').update(kwargs).eq('id', user_id).execute()
            return response.data[0] if response.data else None
        except Exception as e:
            logger.error(f"Error updating user {user_id}: {e}")
            return None
    
    async def update_last_active(self, user_id: int) -> None:
        """Update user's last active timestamp."""
        try:
            self.client.table('users').update({
                'last_active': datetime.now(timezone.utc).isoformat()
            }).eq('id', user_id).execute()
        except Exception as e:
            logger.error(f"Error updating last_active for user {user_id}: {e}")
    
    async def check_subscription(self, user_id: int) -> tuple[bool, Optional[datetime]]:
        """
        Check if user has active subscription.
        Returns (is_active, expiry_date).
        """
        try:
            user = await self.get_user(user_id)
            if not user:
                return False, None
            
            expiry = user.get('subscription_expiry')
            if not expiry:
                return False, None
            
            # Parse the expiry date
            if isinstance(expiry, str):
                # Handle cases where the string might have 'Z' or offset
                clean_expiry = expiry.replace('Z', '+00:00')
                expiry_dt = datetime.fromisoformat(clean_expiry)
            else:
                expiry_dt = expiry
            
            # Ensure expiry_dt is timezone aware (UTC)
            if expiry_dt.tzinfo is None:
                expiry_dt = expiry_dt.replace(tzinfo=timezone.utc)
            
            is_active = expiry_dt > datetime.now(timezone.utc)
            return is_active, expiry_dt
        except Exception as e:
            logger.error(f"Error checking subscription for user {user_id}: {e}")
            return False, None
    
    # ==================== LESSON OPERATIONS ====================
    
    async def get_lessons(
        self,
        level: Optional[str] = None,
        skill: Optional[str] = None,
        limit: int = 10
    ) -> List[Dict[str, Any]]:
        """Get lessons, optionally filtered by level and skill."""
        try:
            query = self.client.table('lessons').select('*').eq('is_active', True)
            
            if level:
                query = query.eq('level', level)
            if skill:
                query = query.eq('skill', skill)
            
            response = query.limit(limit).execute()
            return response.data or []
        except Exception as e:
            logger.error(f"Error getting lessons: {e}")
            return []
    
    async def get_lesson_by_id(self, lesson_id: str) -> Optional[Dict[str, Any]]:
        """Get a specific lesson by ID."""
        try:
            response = self.client.table('lessons').select('*').eq('id', lesson_id).execute()
            return response.data[0] if response.data else None
        except Exception as e:
            logger.error(f"Error getting lesson {lesson_id}: {e}")
            return None
    
    # ==================== EXAM QUESTIONS OPERATIONS ====================
    
    async def get_exam_questions(
        self,
        level: str,
        exam_type: str,
        limit: int = 10,
        difficulty_range: Optional[tuple[int, int]] = None
    ) -> List[Dict[str, Any]]:
        """Get exam questions by level and type."""
        try:
            query = self.client.table('exam_questions').select('*')\
                .eq('level', level)\
                .eq('exam_type', exam_type)\
                .eq('is_active', True)
            
            if difficulty_range:
                query = query.gte('difficulty', difficulty_range[0])\
                            .lte('difficulty', difficulty_range[1])
            
            response = query.limit(limit).execute()
            return response.data or []
        except Exception as e:
            logger.error(f"Error getting exam questions: {e}")
            return []
    
    async def get_random_exam_questions(
        self,
        level: str,
        exam_type: str,
        count: int = 10
    ) -> List[Dict[str, Any]]:
        """Get random exam questions with difficulty distribution."""
        try:
            # Get questions from different difficulty ranges
            easy = await self.get_exam_questions(level, exam_type, limit=3, difficulty_range=(1, 3))
            medium = await self.get_exam_questions(level, exam_type, limit=5, difficulty_range=(4, 7))
            hard = await self.get_exam_questions(level, exam_type, limit=2, difficulty_range=(8, 10))
            
            # Combine and shuffle
            import random
            questions = easy[:2] + medium[:6] + hard[:2]
            random.shuffle(questions)
            
            return questions[:count]
        except Exception as e:
            logger.error(f"Error getting random exam questions: {e}")
            return []
    
    # ==================== USER PROGRESS OPERATIONS ====================
    
    async def save_progress(
        self,
        user_id: int,
        skill: str,
        activity_type: str,
        score: float,
        weak_areas: Optional[List[str]] = None
    ) -> Optional[Dict[str, Any]]:
        """Save user progress entry."""
        try:
            data = {
                'user_id': user_id,
                'skill': skill,
                'activity_type': activity_type,
                'score': score,
                'weak_areas': weak_areas or [],
                'completed_at': datetime.now(timezone.utc).isoformat()
            }
            response = self.client.table('user_progress').insert(data).execute()
            return response.data[0] if response.data else None
        except Exception as e:
            logger.error(f"Error saving progress for user {user_id}: {e}")
            return None
    
    async def get_user_progress(
        self,
        user_id: int,
        skill: Optional[str] = None,
        limit: int = 20
    ) -> List[Dict[str, Any]]:
        """Get user's progress history."""
        try:
            query = self.client.table('user_progress').select('*')\
                .eq('user_id', user_id)\
                .order('completed_at', desc=True)
            
            if skill:
                query = query.eq('skill', skill)
            
            response = query.limit(limit).execute()
            return response.data or []
        except Exception as e:
            logger.error(f"Error getting progress for user {user_id}: {e}")
            return []
    
    async def get_user_statistics(self, user_id: int) -> Dict[str, Any]:
        """Calculate user statistics from progress data."""
        try:
            progress = await self.get_user_progress(user_id, limit=100)
            
            if not progress:
                return {
                    'total_activities': 0,
                    'average_score': 0,
                    'skill_scores': {},
                    'weak_areas': [],
                    'strengths': []
                }
            
            # Calculate statistics
            skill_scores = {}
            all_weak_areas = []
            
            for entry in progress:
                skill = entry.get('skill', 'unknown')
                score = entry.get('score', 0)
                
                if skill not in skill_scores:
                    skill_scores[skill] = []
                skill_scores[skill].append(score)
                
                if entry.get('weak_areas'):
                    all_weak_areas.extend(entry['weak_areas'])
            
            # Calculate averages
            for skill in skill_scores:
                scores = skill_scores[skill]
                skill_scores[skill] = sum(scores) / len(scores) if scores else 0
            
            # Find most common weak areas
            from collections import Counter
            weak_area_counts = Counter(all_weak_areas)
            top_weak_areas = [area for area, _ in weak_area_counts.most_common(5)]
            
            # Identify strengths (skills with avg > 75%)
            strengths = [skill for skill, avg in skill_scores.items() if avg >= 75]
            
            all_scores = [e.get('score', 0) for e in progress]
            
            return {
                'total_activities': len(progress),
                'average_score': sum(all_scores) / len(all_scores) if all_scores else 0,
                'skill_scores': skill_scores,
                'weak_areas': top_weak_areas,
                'strengths': strengths
            }
        except Exception as e:
            logger.error(f"Error calculating statistics for user {user_id}: {e}")
            return {
                'total_activities': 0,
                'average_score': 0,
                'skill_scores': {},
                'weak_areas': [],
                'strengths': []
            }
    
    # ==================== CONVERSATION HISTORY OPERATIONS ====================
    
    async def save_conversation(
        self,
        user_id: int,
        session_id: str,
        role: str,
        content: str
    ) -> Optional[Dict[str, Any]]:
        """Save a conversation message."""
        try:
            data = {
                'user_id': user_id,
                'session_id': session_id,
                'role': role,
                'content': content,
                'timestamp': datetime.now(timezone.utc).isoformat()
            }
            response = self.client.table('conversation_history').insert(data).execute()
            return response.data[0] if response.data else None
        except Exception as e:
            logger.error(f"Error saving conversation for user {user_id}: {e}")
            return None
    
    async def get_conversation_history(
        self,
        user_id: int,
        session_id: Optional[str] = None,
        limit: int = 10
    ) -> List[Dict[str, Any]]:
        """Get conversation history for context."""
        try:
            query = self.client.table('conversation_history').select('*')\
                .eq('user_id', user_id)\
                .order('timestamp', desc=True)
            
            if session_id:
                query = query.eq('session_id', session_id)
            
            response = query.limit(limit).execute()
            # Reverse to get chronological order
            return list(reversed(response.data)) if response.data else []
        except Exception as e:
            logger.error(f"Error getting conversation history for user {user_id}: {e}")
            return []
    
    # ==================== EXAM ATTEMPTS OPERATIONS ====================
    
    async def create_exam_attempt(
        self,
        user_id: int,
        exam_type: str,
        level: str
    ) -> Optional[Dict[str, Any]]:
        """Create a new exam attempt."""
        try:
            data = {
                'user_id': user_id,
                'exam_type': exam_type,
                'level': level,
                'started_at': datetime.now(timezone.utc).isoformat(),
                'is_completed': False,
                'answers': []
            }
            response = self.client.table('exam_attempts').insert(data).execute()
            return response.data[0] if response.data else None
        except Exception as e:
            logger.error(f"Error creating exam attempt for user {user_id}: {e}")
            return None
    
    async def update_exam_attempt(
        self,
        attempt_id: str,
        answers: List[Dict[str, Any]],
        score: Optional[float] = None,
        is_completed: bool = False
    ) -> Optional[Dict[str, Any]]:
        """Update an exam attempt with answers and score."""
        try:
            data = {
                'answers': answers,
                'is_completed': is_completed
            }
            
            if is_completed:
                data['completed_at'] = datetime.now(timezone.utc).isoformat()
            
            if score is not None:
                data['score'] = score
            
            response = self.client.table('exam_attempts').update(data)\
                .eq('id', attempt_id).execute()
            return response.data[0] if response.data else None
        except Exception as e:
            logger.error(f"Error updating exam attempt {attempt_id}: {e}")
            return None
    
    async def get_exam_attempts(
        self,
        user_id: int,
        exam_type: Optional[str] = None,
        limit: int = 10
    ) -> List[Dict[str, Any]]:
        """Get user's exam attempts."""
        try:
            query = self.client.table('exam_attempts').select('*')\
                .eq('user_id', user_id)\
                .eq('is_completed', True)\
                .order('completed_at', desc=True)
            
            if exam_type:
                query = query.eq('exam_type', exam_type)
            
            response = query.limit(limit).execute()
            return response.data or []
        except Exception as e:
            logger.error(f"Error getting exam attempts for user {user_id}: {e}")
            return []


# Singleton instance
db = DatabaseService()
