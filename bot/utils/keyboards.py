"""
Inline keyboard builders for Telegram bot.
"""
from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from typing import List, Optional

from bot.config import Config


class Keyboards:
    """Factory class for creating inline keyboards."""
    
    @staticmethod
    def main_menu() -> InlineKeyboardMarkup:
        """Main menu keyboard."""
        keyboard = [
            [InlineKeyboardButton("Learn with AI Tutor", callback_data="menu_learn")],
            [InlineKeyboardButton("Take Practice Exam", callback_data="menu_exam")],
            [InlineKeyboardButton("View My Progress", callback_data="menu_progress")],
            [InlineKeyboardButton("Settings", callback_data="menu_settings")],
            [InlineKeyboardButton("Help", callback_data="menu_help")]
        ]
        return InlineKeyboardMarkup(keyboard)
    
    @staticmethod
    def learn_menu() -> InlineKeyboardMarkup:
        """Learning options menu."""
        keyboard = [
            [
                InlineKeyboardButton("Free Conversation", callback_data="learn_conversation"),
                InlineKeyboardButton("Grammar", callback_data="learn_grammar")
            ],
            [
                InlineKeyboardButton("Lesen (Reading)", callback_data="learn_lesen"),
                InlineKeyboardButton("Horen (Listening)", callback_data="learn_horen")
            ],
            [
                InlineKeyboardButton("Schreiben (Writing)", callback_data="learn_schreiben"),
                InlineKeyboardButton("Sprechen (Speaking)", callback_data="learn_sprechen")
            ],
            [InlineKeyboardButton("Vokabular (Vocabulary)", callback_data="learn_vokabular")],
            [InlineKeyboardButton("Back to Main Menu", callback_data="menu_main")]
        ]
        return InlineKeyboardMarkup(keyboard)
    
    @staticmethod
    def exam_menu() -> InlineKeyboardMarkup:
        """Exam selection menu."""
        keyboard = [
            [
                InlineKeyboardButton("Lesen Exam", callback_data="exam_lesen"),
                InlineKeyboardButton("Horen Exam", callback_data="exam_horen")
            ],
            [
                InlineKeyboardButton("Schreiben Exam", callback_data="exam_schreiben"),
                InlineKeyboardButton("Sprechen Exam", callback_data="exam_sprechen")
            ],
            [InlineKeyboardButton("Vokabular Exam", callback_data="exam_vokabular")],
            [InlineKeyboardButton("Full Mock Exam", callback_data="exam_full")],
            [InlineKeyboardButton("Back to Main Menu", callback_data="menu_main")]
        ]
        return InlineKeyboardMarkup(keyboard)
    
    @staticmethod
    def level_selection(current_level: Optional[str] = None) -> InlineKeyboardMarkup:
        """CEFR level selection keyboard."""
        keyboard = []
        for level in Config.CEFR_LEVELS:
            text = f"{level}" + (" (current)" if level == current_level else "")
            keyboard.append([InlineKeyboardButton(text, callback_data=f"level_{level}")])
        keyboard.append([InlineKeyboardButton("Cancel", callback_data="cancel")])
        return InlineKeyboardMarkup(keyboard)
    
    @staticmethod
    def language_selection(current_lang: Optional[str] = None) -> InlineKeyboardMarkup:
        """Explanation language selection."""
        lang_labels = {
            'english': 'English',
            'amharic': 'Amharic',
            'german': 'Deutsch'
        }
        keyboard = []
        for lang in Config.EXPLANATION_LANGS:
            text = lang_labels.get(lang, lang.capitalize())
            if lang == current_lang:
                text += " (current)"
            keyboard.append([InlineKeyboardButton(text, callback_data=f"lang_{lang}")])
        keyboard.append([InlineKeyboardButton("Cancel", callback_data="cancel")])
        return InlineKeyboardMarkup(keyboard)
    
    @staticmethod
    def settings_menu() -> InlineKeyboardMarkup:
        """Settings menu keyboard."""
        keyboard = [
            [InlineKeyboardButton("Change Level", callback_data="settings_level")],
            [InlineKeyboardButton("Change Language", callback_data="settings_lang")],
            [InlineKeyboardButton("View Subscription", callback_data="settings_subscription")],
            [InlineKeyboardButton("Back to Main Menu", callback_data="menu_main")]
        ]
        return InlineKeyboardMarkup(keyboard)
    
    @staticmethod
    def mcq_options(options: List[str]) -> InlineKeyboardMarkup:
        """Multiple choice question options."""
        keyboard = []
        for i, option in enumerate(options):
            letter = chr(65 + i)  # A, B, C, D
            keyboard.append([InlineKeyboardButton(
                f"{letter}) {option[:50]}...",  # Truncate long options
                callback_data=f"answer_{letter}"
            )])
        return InlineKeyboardMarkup(keyboard)
    
    @staticmethod
    def confirm_cancel() -> InlineKeyboardMarkup:
        """Confirm/Cancel buttons."""
        keyboard = [
            [
                InlineKeyboardButton("Confirm", callback_data="confirm"),
                InlineKeyboardButton("Cancel", callback_data="cancel")
            ]
        ]
        return InlineKeyboardMarkup(keyboard)
    
    @staticmethod
    def continue_exit() -> InlineKeyboardMarkup:
        """Continue or Exit buttons."""
        keyboard = [
            [
                InlineKeyboardButton("Continue", callback_data="continue"),
                InlineKeyboardButton("Exit", callback_data="exit")
            ]
        ]
        return InlineKeyboardMarkup(keyboard)
    
    @staticmethod
    def submit_cancel() -> InlineKeyboardMarkup:
        """Submit or Cancel buttons for writing tasks."""
        keyboard = [
            [
                InlineKeyboardButton("Submit", callback_data="submit"),
                InlineKeyboardButton("Cancel", callback_data="cancel")
            ]
        ]
        return InlineKeyboardMarkup(keyboard)
    
    @staticmethod
    def next_question() -> InlineKeyboardMarkup:
        """Next question button."""
        keyboard = [[InlineKeyboardButton("Next Question", callback_data="next_question")]]
        return InlineKeyboardMarkup(keyboard)
    
    @staticmethod
    def view_results() -> InlineKeyboardMarkup:
        """View results button after exam."""
        keyboard = [
            [InlineKeyboardButton("View Detailed Results", callback_data="view_results")],
            [InlineKeyboardButton("Back to Main Menu", callback_data="menu_main")]
        ]
        return InlineKeyboardMarkup(keyboard)
    
    @staticmethod
    def progress_actions() -> InlineKeyboardMarkup:
        """Progress page actions."""
        keyboard = [
            [InlineKeyboardButton("Practice Weak Areas", callback_data="practice_weak")],
            [InlineKeyboardButton("View Exam History", callback_data="view_history")],
            [InlineKeyboardButton("Back to Main Menu", callback_data="menu_main")]
        ]
        return InlineKeyboardMarkup(keyboard)
    
    @staticmethod
    def back_to_menu() -> InlineKeyboardMarkup:
        """Single back button."""
        keyboard = [[InlineKeyboardButton("Back to Main Menu", callback_data="menu_main")]]
        return InlineKeyboardMarkup(keyboard)
    
    @staticmethod
    def end_conversation() -> InlineKeyboardMarkup:
        """End conversation button for tutoring sessions."""
        keyboard = [[InlineKeyboardButton("End Conversation", callback_data="end_conversation")]]
        return InlineKeyboardMarkup(keyboard)
