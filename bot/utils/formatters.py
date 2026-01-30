"""
Message formatting utilities for consistent bot responses.
"""
from datetime import datetime
from typing import Dict, Any, List, Optional


class Formatters:
    """Utility class for formatting bot messages."""
    
    @staticmethod
    def welcome_message(user_name: str, level: str) -> str:
        """Format welcome message for new/returning users."""
        return f"""
Willkommen bei EthioGerman Language School!
Welcome, {user_name}!

Your current level: {level}

What would you like to do today?
Was mochten Sie heute tun?
"""
    
    @staticmethod
    def help_message() -> str:
        """Format help/instructions message."""
        return """
*EthioGerman Language School - Help*

*Commands:*
/start - Start the bot / Main menu
/menu - Open main menu
/learn - Start learning session
/exam - Take a practice exam
/progress - View your progress
/settings - Change settings
/help - Show this help
/cancel - Cancel current action

*Features:*
- AI-powered German tutoring
- Goethe exam simulation
- Voice message practice
- Progress tracking

*Levels:* A1, A2, B1 (CEFR)

*Skills:*
- Lesen (Reading)
- Horen (Listening)
- Schreiben (Writing)
- Sprechen (Speaking)
- Vokabular (Vocabulary)

*Support:* Contact @EthioGermanSchool
"""
    
    @staticmethod
    def subscription_info(expiry_date: Optional[datetime], is_active: bool) -> str:
        """Format subscription information."""
        if not expiry_date:
            return """
*Subscription Status:* Not Active

You don't have an active subscription.
Please contact @EthioGermanSchool to activate.
"""
        
        expiry_str = expiry_date.strftime('%d %B %Y')
        status = "Active" if is_active else "Expired"
        
        return f"""
*Subscription Status:* {status}
*Expires:* {expiry_str}

{"Your subscription is active. Enjoy learning!" if is_active else "Please renew your subscription to continue."}
Contact: @EthioGermanSchool
"""
    
    @staticmethod
    def progress_summary(stats: Dict[str, Any], level: str) -> str:
        """Format progress summary."""
        skill_scores = stats.get('skill_scores', {})
        weak_areas = stats.get('weak_areas', [])
        strengths = stats.get('strengths', [])
        avg_score = stats.get('average_score', 0)
        total = stats.get('total_activities', 0)
        
        # Create progress bar
        filled = int(avg_score / 10)
        progress_bar = '|' + '' * filled + '' * (10 - filled) + '|'
        
        # Format skill scores
        skill_text = ""
        skill_icons = {
            'lesen': '',
            'horen': '',
            'schreiben': '',
            'sprechen': '',
            'vokabular': ''
        }
        
        for skill, score in skill_scores.items():
            icon = skill_icons.get(skill, '')
            stars = '' * int(score / 25) + '' * (4 - int(score / 25))
            skill_text += f"{icon} {skill.capitalize()}: {score:.0f}% {stars}\n"
        
        # Format weak areas
        weak_text = ""
        if weak_areas:
            weak_text = "\n*Areas to Improve:*\n"
            for area in weak_areas[:3]:
                weak_text += f"- {area}\n"
        
        return f"""
*Your Progress Summary*

*Level:* {level}
*Overall Score:* {avg_score:.0f}%
{progress_bar}

*Skills:*
{skill_text if skill_text else "No data yet. Start practicing!"}

*Total Activities:* {total}
{weak_text}
*Tip:* Practice your weak areas to improve faster!
"""
    
    @staticmethod
    def exam_question(
        question_num: int,
        total: int,
        question_text: str,
        passage: Optional[str] = None
    ) -> str:
        """Format exam question display."""
        header = f"*Question {question_num}/{total}*\n\n"
        
        if passage:
            return f"{header}*Text:*\n_{passage}_\n\n*Question:*\n{question_text}"
        
        return f"{header}{question_text}"
    
    @staticmethod
    def exam_results(
        exam_type: str,
        score: float,
        correct: int,
        total: int,
        passed: bool,
        weak_areas: List[str]
    ) -> str:
        """Format exam results."""
        status = "PASSED" if passed else "NEEDS IMPROVEMENT"
        emoji = "" if passed else ""
        
        # Create score visualization
        filled = int(score / 10)
        score_bar = '' * filled + '' * (10 - filled)
        
        result = f"""
*{exam_type.upper()} Exam Results* {emoji}

*Score:* {score:.1f}%
[{score_bar}]

*Correct Answers:* {correct}/{total}
*Status:* {status}

"""
        
        if weak_areas:
            result += "*Areas to Review:*\n"
            for area in weak_areas[:3]:
                result += f"- {area}\n"
        
        if passed:
            result += "\nGreat job! Keep up the good work!"
        else:
            result += "\nDon't worry! Practice makes perfect. Try again!"
        
        return result
    
    @staticmethod
    def writing_evaluation(evaluation: Dict[str, Any]) -> str:
        """Format writing evaluation feedback."""
        scores = evaluation.get('scores', {})
        overall = evaluation.get('overall_score', 0)
        mistakes = evaluation.get('mistakes', [])
        strengths = evaluation.get('strengths', [])
        suggestions = evaluation.get('suggestions', [])
        corrected = evaluation.get('corrected_text', '')
        
        result = f"""
*Writing Evaluation*

*Overall Score:* {overall:.0f}%

*Breakdown:*
- Grammar: {scores.get('grammar', 0)}%
- Vocabulary: {scores.get('vocabulary', 0)}%
- Task Completion: {scores.get('task_completion', 0)}%
- Coherence: {scores.get('coherence', 0)}%

"""
        
        if strengths:
            result += "*Strengths:*\n"
            for s in strengths[:3]:
                result += f"- {s}\n"
            result += "\n"
        
        if mistakes:
            result += "*Corrections:*\n"
            for m in mistakes[:3]:
                result += f'- "{m.get("original", "")}" "{m.get("correction", "")}"\n'
                if m.get('explanation'):
                    result += f'  _{m["explanation"]}_\n'
            result += "\n"
        
        if suggestions:
            result += "*Suggestions:*\n"
            for s in suggestions[:2]:
                result += f"- {s}\n"
        
        return result
    
    @staticmethod
    def speaking_evaluation(evaluation: Dict[str, Any]) -> str:
        """Format speaking evaluation feedback."""
        scores = evaluation.get('scores', {})
        overall = evaluation.get('overall_score', 0)
        mistakes = evaluation.get('mistakes', [])
        tips = evaluation.get('pronunciation_tips', [])
        strengths = evaluation.get('strengths', [])
        
        result = f"""
*Speaking Evaluation*

*Overall Score:* {overall:.0f}%

*Breakdown:*
- Grammar: {scores.get('grammar', 0)}%
- Vocabulary: {scores.get('vocabulary', 0)}%
- Task Completion: {scores.get('task_completion', 0)}%
- Fluency: {scores.get('fluency', 0)}%

"""
        
        if strengths:
            result += "*Strengths:*\n"
            for s in strengths[:3]:
                result += f"- {s}\n"
            result += "\n"
        
        if tips:
            result += "*Pronunciation Tips:*\n"
            for t in tips[:3]:
                result += f"- {t}\n"
            result += "\n"
        
        if mistakes:
            result += "*Corrections:*\n"
            for m in mistakes[:3]:
                result += f'- "{m.get("original", "")}" "{m.get("correction", "")}"\n'
        
        return result
    
    @staticmethod
    def lesson_intro(title: str, level: str, skill: str, topic: str) -> str:
        """Format lesson introduction."""
        skill_icons = {
            'lesen': '',
            'horen': '',
            'schreiben': '',
            'sprechen': '',
            'vokabular': '',
            'grammar': ''
        }
        icon = skill_icons.get(skill, '')
        
        return f"""
{icon} *{title}*

*Level:* {level}
*Skill:* {skill.capitalize()}
*Topic:* {topic}

Let's begin! Los geht's!
"""
    
    @staticmethod
    def escape_markdown(text: str) -> str:
        """Escape special characters for Telegram MarkdownV2."""
        special_chars = ['_', '*', '[', ']', '(', ')', '~', '`', '>', '#', '+', '-', '=', '|', '{', '}', '.', '!']
        for char in special_chars:
            text = text.replace(char, f'\\{char}')
        return text
