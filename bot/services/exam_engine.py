"""
Exam engine service for question selection and scoring.
"""
import random
import logging
from typing import Optional, List, Dict, Any
from uuid import uuid4

from bot.services.database import db
from bot.services.ai_tutor import ai_tutor

logger = logging.getLogger(__name__)


class ExamEngine:
    """Service for exam question selection and scoring."""
    
    EXAM_TYPES = ['lesen', 'horen', 'schreiben', 'sprechen', 'vokabular']
    
    # Default question counts per exam type
    QUESTION_COUNTS = {
        'lesen': 5,
        'horen': 5,
        'schreiben': 1,
        'sprechen': 1,
        'vokabular': 10
    }
    
    async def get_exam_questions(
        self,
        level: str,
        exam_type: str,
        count: Optional[int] = None
    ) -> List[Dict[str, Any]]:
        """
        Get questions for an exam.
        Falls back to AI-generated questions if database is empty.
        """
        if count is None:
            count = self.QUESTION_COUNTS.get(exam_type, 5)
        
        # Try to get from database first
        questions = await db.get_random_exam_questions(level, exam_type, count)
        
        # If not enough questions, generate with AI
        if len(questions) < count:
            needed = count - len(questions)
            logger.info(f"Generating {needed} {exam_type} questions for {level}")
            
            for _ in range(needed):
                generated = await ai_tutor.generate_exam_question(level, exam_type)
                if generated:
                    # Format as exam question
                    questions.append({
                        'id': str(uuid4()),
                        'level': level,
                        'exam_type': exam_type,
                        'question_text': generated.get('question_text', ''),
                        'question_data': generated,
                        'correct_answer': generated.get('correct_answer', ''),
                        'difficulty': 5,
                        'generated': True  # Mark as AI-generated
                    })
        
        return questions[:count]
    
    def calculate_score(
        self,
        answers: List[Dict[str, Any]],
        exam_type: str
    ) -> Dict[str, Any]:
        """
        Calculate exam score from answers.
        
        Args:
            answers: List of answer dictionaries with question_id, user_answer, correct_answer, is_correct
            exam_type: Type of exam
        
        Returns:
            Dictionary with score, breakdown, and analysis
        """
        if not answers:
            return {
                'score': 0,
                'total_questions': 0,
                'correct_answers': 0,
                'percentage': 0,
                'passed': False,
                'weak_areas': []
            }
        
        total = len(answers)
        correct = sum(1 for a in answers if a.get('is_correct', False))
        percentage = (correct / total * 100) if total > 0 else 0
        
        # Identify weak areas from wrong answers
        weak_areas = []
        for answer in answers:
            if not answer.get('is_correct', False):
                topic = answer.get('topic', exam_type)
                if topic not in weak_areas:
                    weak_areas.append(topic)
        
        # Determine pass/fail (60% threshold)
        passed = percentage >= 60
        
        return {
            'score': round(percentage, 1),
            'total_questions': total,
            'correct_answers': correct,
            'percentage': percentage,
            'passed': passed,
            'weak_areas': weak_areas[:5]  # Top 5 weak areas
        }
    
    def calculate_weighted_score(
        self,
        section_scores: Dict[str, float]
    ) -> float:
        """
        Calculate weighted overall score for full mock exam.
        
        Weights:
        - Lesen: 25%
        - Horen: 25%
        - Schreiben: 20%
        - Sprechen: 20%
        - Vokabular: 10%
        """
        weights = {
            'lesen': 0.25,
            'horen': 0.25,
            'schreiben': 0.20,
            'sprechen': 0.20,
            'vokabular': 0.10
        }
        
        total_score = 0
        total_weight = 0
        
        for section, score in section_scores.items():
            weight = weights.get(section, 0.2)
            total_score += score * weight
            total_weight += weight
        
        if total_weight > 0:
            return round(total_score / total_weight * 100 / 100, 1)
        return 0
    
    def check_answer(
        self,
        question: Dict[str, Any],
        user_answer: str
    ) -> tuple[bool, str]:
        """
        Check if an answer is correct for objective questions.
        
        Returns:
            (is_correct, explanation)
        """
        correct_answer = question.get('correct_answer', '').strip().upper()
        user_answer_clean = user_answer.strip().upper()
        
        # Handle different answer formats
        # Accept both "A" and "A)" formats
        if user_answer_clean.endswith(')'):
            user_answer_clean = user_answer_clean[:-1]
        if correct_answer.endswith(')'):
            correct_answer = correct_answer[:-1]
        
        is_correct = user_answer_clean == correct_answer
        
        # Get explanation from question data
        question_data = question.get('question_data', {})
        explanation = question_data.get('explanation', '')
        
        if not explanation:
            if is_correct:
                explanation = "Richtig! (Correct!)"
            else:
                explanation = f"Die richtige Antwort ist {correct_answer}. (The correct answer is {correct_answer}.)"
        
        return is_correct, explanation
    
    def get_level_recommendation(
        self,
        current_level: str,
        average_score: float
    ) -> tuple[str, str]:
        """
        Recommend level change based on performance.
        
        Returns:
            (recommended_level, message)
        """
        levels = ['A1', 'A2', 'B1']
        current_idx = levels.index(current_level) if current_level in levels else 0
        
        if average_score >= 85 and current_idx < len(levels) - 1:
            new_level = levels[current_idx + 1]
            return new_level, f"Excellent! You're ready for {new_level}. Consider leveling up!"
        elif average_score < 40 and current_idx > 0:
            new_level = levels[current_idx - 1]
            return new_level, f"You might benefit from reviewing {new_level} material first."
        
        return current_level, f"Continue practicing at {current_level} level."


# Singleton instance
exam_engine = ExamEngine()
