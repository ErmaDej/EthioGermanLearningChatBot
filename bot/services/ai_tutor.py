"""
AI Tutor service using OpenRouter API with Llama 3.3 70B model.
Handles German language tutoring, evaluation, and feedback.
"""
import httpx
import json
import logging
from typing import Optional, List, Dict, Any
from pathlib import Path

from bot.config import Config

logger = logging.getLogger(__name__)

# Load system prompt
PROMPTS_DIR = Path(__file__).parent.parent.parent / 'prompts'


class AITutorService:
    """AI-powered German language tutoring service."""
    
    def __init__(self):
        self.api_url = Config.OPENROUTER_API_URL
        self.api_key = Config.OPENROUTER_API_KEY
        self.model = Config.AI_MODEL
        self.headers = {
            'Authorization': f'Bearer {self.api_key}',
            'Content-Type': 'application/json',
            'HTTP-Referer': 'https://ethiogerman-school.com',
            'X-Title': 'EthioGerman Language School Bot'
        }
    
    def _get_system_prompt(
        self,
        level: str = 'A1',
        preferred_lang: str = 'english',
        skill_focus: Optional[str] = None,
        weak_areas: Optional[List[str]] = None
    ) -> str:
        """Generate system prompt for the AI tutor."""
        
        # Base system prompt
        prompt = f"""You are an expert German language tutor for EthioGerman Language School.

STUDENT PROFILE:
- Current CEFR Level: {level}
- Preferred explanation language: {preferred_lang.capitalize()}
- {"Skill focus: " + skill_focus.capitalize() if skill_focus else "General practice"}
{"- Known weak areas: " + ", ".join(weak_areas) if weak_areas else ""}

YOUR TEACHING STYLE:
- Adapt complexity strictly to the student's {level} level
- For A1: Use basic vocabulary, simple present tense, short sentences
- For A2: Introduce past tense, modal verbs, compound sentences
- For B1: Use complex grammar, subjunctive, varied vocabulary
- Correct mistakes gently with clear explanations
- Provide translations in {preferred_lang.capitalize()} when the student struggles
- Ask follow-up questions to encourage practice
- Be encouraging and patient - never shame the student

RESPONSE FORMAT FOR CORRECTIONS:
When correcting mistakes, always provide:
1. Brief feedback (what was wrong)
2. Corrected sentence in German
3. Natural alternative (how a native speaker would say it)

LANGUAGE RULES:
- Primary teaching language: German
- Explanation language: {preferred_lang.capitalize()} (use when student needs clarification)
- For Amharic explanations, use simple transliteration if needed

CONVERSATION STYLE:
- Keep responses concise but helpful
- Use appropriate emojis sparingly for engagement
- End with a question or prompt to continue practice
- Celebrate small wins to encourage the student

You are a PAID German tutor AI - maintain professional quality in all responses."""

        return prompt
    
    async def chat(
        self,
        user_message: str,
        conversation_history: List[Dict[str, str]],
        level: str = 'A1',
        preferred_lang: str = 'english',
        skill_focus: Optional[str] = None,
        weak_areas: Optional[List[str]] = None
    ) -> str:
        """
        Send a message to the AI tutor and get a response.
        
        Args:
            user_message: The user's message
            conversation_history: Previous messages for context
            level: User's CEFR level
            preferred_lang: User's preferred explanation language
            skill_focus: Current skill being practiced
            weak_areas: User's known weak areas
        
        Returns:
            AI tutor's response
        """
        try:
            system_prompt = self._get_system_prompt(
                level=level,
                preferred_lang=preferred_lang,
                skill_focus=skill_focus,
                weak_areas=weak_areas
            )
            
            # Build messages array
            messages = [{'role': 'system', 'content': system_prompt}]
            
            # Add conversation history (last N messages)
            for msg in conversation_history[-Config.MAX_CONVERSATION_HISTORY:]:
                messages.append({
                    'role': msg.get('role', 'user'),
                    'content': msg.get('content', '')
                })
            
            # Add current user message
            messages.append({'role': 'user', 'content': user_message})
            
            # Make API request
            async with httpx.AsyncClient(timeout=60.0) as client:
                response = await client.post(
                    self.api_url,
                    headers=self.headers,
                    json={
                        'model': self.model,
                        'messages': messages,
                        'temperature': 0.7,
                        'max_tokens': 800,
                        'top_p': 0.9
                    }
                )
                
                if response.status_code != 200:
                    logger.error(f"OpenRouter API error: {response.status_code} - {response.text}")
                    return "Entschuldigung, es gab einen technischen Fehler. Bitte versuchen Sie es erneut. (Sorry, there was a technical error. Please try again.)"
                
                data = response.json()
                return data['choices'][0]['message']['content']
        
        except httpx.TimeoutException:
            logger.error("OpenRouter API timeout")
            return "Die Anfrage hat zu lange gedauert. Bitte versuchen Sie es erneut. (The request took too long. Please try again.)"
        except Exception as e:
            logger.error(f"Error in AI chat: {e}")
            return "Ein Fehler ist aufgetreten. Bitte versuchen Sie es erneut. (An error occurred. Please try again.)"
    
    async def evaluate_writing(
        self,
        user_text: str,
        prompt: str,
        level: str,
        rubric: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Evaluate a writing (Schreiben) submission.
        
        Returns:
            Dictionary with scores, feedback, and corrections
        """
        try:
            evaluation_prompt = f"""You are evaluating a German writing submission for a {level} level student.

ORIGINAL TASK:
{prompt}

STUDENT'S RESPONSE:
{user_text}

EVALUATION CRITERIA:
1. Grammar (30%): Correct use of grammar appropriate for {level} level
2. Vocabulary (30%): Range and appropriateness of vocabulary
3. Task Completion (20%): How well the response addresses the prompt
4. Coherence (20%): Logical flow and organization

Please provide your evaluation in the following JSON format:
{{
    "scores": {{
        "grammar": <0-100>,
        "vocabulary": <0-100>,
        "task_completion": <0-100>,
        "coherence": <0-100>
    }},
    "overall_score": <0-100>,
    "mistakes": [
        {{"original": "...", "correction": "...", "explanation": "..."}}
    ],
    "strengths": ["..."],
    "suggestions": ["..."],
    "corrected_text": "Full corrected version of the text"
}}

Be constructive and encouraging while being accurate. Provide explanations suitable for a {level} learner."""

            async with httpx.AsyncClient(timeout=90.0) as client:
                response = await client.post(
                    self.api_url,
                    headers=self.headers,
                    json={
                        'model': self.model,
                        'messages': [
                            {'role': 'system', 'content': 'You are a German language examiner. Respond only with valid JSON.'},
                            {'role': 'user', 'content': evaluation_prompt}
                        ],
                        'temperature': 0.3,
                        'max_tokens': 1500
                    }
                )
                
                if response.status_code != 200:
                    logger.error(f"OpenRouter API error: {response.status_code}")
                    return self._default_evaluation()
                
                data = response.json()
                content = data['choices'][0]['message']['content']
                
                # Parse JSON from response
                # Try to extract JSON if wrapped in markdown
                if '```json' in content:
                    content = content.split('```json')[1].split('```')[0]
                elif '```' in content:
                    content = content.split('```')[1].split('```')[0]
                
                return json.loads(content.strip())
        
        except json.JSONDecodeError as e:
            logger.error(f"JSON parsing error in evaluation: {e}")
            return self._default_evaluation()
        except Exception as e:
            logger.error(f"Error in writing evaluation: {e}")
            return self._default_evaluation()
    
    async def evaluate_speaking(
        self,
        transcribed_text: str,
        prompt: str,
        level: str
    ) -> Dict[str, Any]:
        """
        Evaluate a speaking (Sprechen) submission.
        Includes analysis of accent, sentiment, and emotional tone.
        
        Args:
            transcribed_text: Text transcribed from voice message
            prompt: The speaking task prompt
            level: User's CEFR level
        
        Returns:
            Dictionary with scores, feedback, and corrections
        """
        try:
            evaluation_prompt = f"""You are evaluating a German speaking submission (transcribed from audio) for a {level} level student.
            
SPECIAL FOCUS: 
Analyze the student's "Accent Sentimental Understanding" - this includes evaluating the emotional tone, sentiment, and perceived confidence in the spoken German (as far as can be determined from the transcribed text and its structure).

SPEAKING TASK:
{prompt}

TRANSCRIBED RESPONSE:
{transcribed_text}

EVALUATION CRITERIA:
1. Grammar (20%): Correct use of grammar appropriate for {level} level
2. Vocabulary (20%): Range and appropriateness of vocabulary
3. Task Completion (20%): How well the response addresses the prompt
4. Fluency & Sentiment (20%): Natural flow, perceived confidence, and appropriate emotional tone
5. Accent & Pronunciation (20%): Based on the transcription patterns, identify potential pronunciation or accent-related issues (e.g., common phonetic misspellings in transcription).

Please provide your evaluation in the following JSON format:
{{
    "scores": {{
        "grammar": <0-100>,
        "vocabulary": <0-100>,
        "task_completion": <0-100>,
        "fluency_sentiment": <0-100>,
        "accent_pronunciation": <0-100>
    }},
    "overall_score": <0-100>,
    "sentiment_analysis": "Brief analysis of the student's emotional tone and confidence",
    "accent_feedback": "Specific feedback on potential accent/pronunciation issues",
    "mistakes": [
        {{"original": "...", "correction": "...", "explanation": "..."}}
    ],
    "pronunciation_tips": ["..."],
    "strengths": ["..."],
    "suggestions": ["..."]
}}

Be constructive and encouraging. Consider that this is transcribed speech, so some errors might be transcription artifacts. Focus on helping the student sound more natural and confident."""

            async with httpx.AsyncClient(timeout=90.0) as client:
                response = await client.post(
                    self.api_url,
                    headers=self.headers,
                    json={
                        'model': self.model,
                        'messages': [
                            {'role': 'system', 'content': 'You are a German language examiner. Respond only with valid JSON.'},
                            {'role': 'user', 'content': evaluation_prompt}
                        ],
                        'temperature': 0.3,
                        'max_tokens': 1500
                    }
                )
                
                if response.status_code != 200:
                    logger.error(f"OpenRouter API error: {response.status_code}")
                    return self._default_evaluation(speaking=True)
                
                data = response.json()
                content = data['choices'][0]['message']['content']
                
                # Parse JSON from response
                if '```json' in content:
                    content = content.split('```json')[1].split('```')[0]
                elif '```' in content:
                    content = content.split('```')[1].split('```')[0]
                
                return json.loads(content.strip())
        
        except json.JSONDecodeError as e:
            logger.error(f"JSON parsing error in speaking evaluation: {e}")
            return self._default_evaluation(speaking=True)
        except Exception as e:
            logger.error(f"Error in speaking evaluation: {e}")
            return self._default_evaluation(speaking=True)
    
    async def generate_exam_question(
        self,
        level: str,
        exam_type: str,
        topic: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Generate a new exam question dynamically.
        
        Args:
            level: CEFR level (A1, A2, B1)
            exam_type: Type of exam (lesen, horen, schreiben, sprechen, vokabular)
            topic: Optional topic focus
        
        Returns:
            Dictionary with question data
        """
        try:
            type_prompts = {
                'vokabular': f"""Generate a German vocabulary multiple-choice question for {level} level.
{f"Topic: {topic}" if topic else "Any common topic suitable for this level."}

Return JSON:
{{
    "question_text": "What does 'German word' mean?",
    "options": ["A) option1", "B) option2", "C) option3", "D) option4"],
    "correct_answer": "A",
    "explanation": "Brief explanation"
}}""",
                'lesen': f"""Generate a German reading comprehension question for {level} level.
{f"Topic: {topic}" if topic else "Any suitable topic."}

Return JSON:
{{
    "passage": "A short German text (3-5 sentences for A1, 5-8 for A2, 8-12 for B1)",
    "question_text": "Question about the passage",
    "options": ["A) option1", "B) option2", "C) option3", "D) option4"],
    "correct_answer": "B",
    "explanation": "Why this answer is correct"
}}""",
                'schreiben': f"""Generate a German writing prompt for {level} level.
{f"Topic: {topic}" if topic else "Any suitable topic."}

Return JSON:
{{
    "question_text": "Writing task description",
    "requirements": ["requirement 1", "requirement 2"],
    "word_count": {{"min": 30, "max": 50}} for A1, {{"min": 50, "max": 80}} for A2, {{"min": 80, "max": 120}} for B1,
    "example_points": ["Point to cover 1", "Point to cover 2"]
}}""",
                'sprechen': f"""Generate a German speaking prompt for {level} level.
{f"Topic: {topic}" if topic else "Any suitable topic."}

Return JSON:
{{
    "question_text": "Speaking task description",
    "preparation_time_sec": 30,
    "response_time_sec": 60,
    "hints": ["Useful phrase 1", "Useful phrase 2"]
}}"""
            }
            
            prompt = type_prompts.get(exam_type, type_prompts['vokabular'])
            
            async with httpx.AsyncClient(timeout=60.0) as client:
                response = await client.post(
                    self.api_url,
                    headers=self.headers,
                    json={
                        'model': self.model,
                        'messages': [
                            {'role': 'system', 'content': 'You are a German exam question generator. Respond only with valid JSON.'},
                            {'role': 'user', 'content': prompt}
                        ],
                        'temperature': 0.8,
                        'max_tokens': 800
                    }
                )
                
                if response.status_code != 200:
                    logger.error(f"OpenRouter API error: {response.status_code}")
                    return {}
                
                data = response.json()
                content = data['choices'][0]['message']['content']
                
                # Parse JSON from response
                if '```json' in content:
                    content = content.split('```json')[1].split('```')[0]
                elif '```' in content:
                    content = content.split('```')[1].split('```')[0]
                
                return json.loads(content.strip())
        
        except Exception as e:
            logger.error(f"Error generating exam question: {e}")
            return {}
    
    def _default_evaluation(self, speaking: bool = False) -> Dict[str, Any]:
        """Return default evaluation when API fails."""
        result = {
            'scores': {
                'grammar': 0,
                'vocabulary': 0,
                'task_completion': 0,
            },
            'overall_score': 0,
            'mistakes': [],
            'strengths': ['Unable to evaluate at this time'],
            'suggestions': ['Please try again later']
        }
        
        if speaking:
            result['scores']['fluency'] = 0
            result['pronunciation_tips'] = []
        else:
            result['scores']['coherence'] = 0
            result['corrected_text'] = ''
        
        return result


# Singleton instance
ai_tutor = AITutorService()
