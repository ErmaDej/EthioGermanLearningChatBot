"""
Progress handler.
Displays user statistics and learning progress.
"""
import logging
from telegram import Update
from telegram.ext import ContextTypes, CommandHandler, CallbackQueryHandler

from bot.services.database import db
from bot.middleware.subscription import require_subscription
from bot.utils.keyboards import Keyboards
from bot.utils.formatters import Formatters

logger = logging.getLogger(__name__)


@require_subscription
async def progress_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle /progress command - show user statistics."""
    user = update.effective_user
    
    # Get user data
    user_data = await db.get_user(user.id)
    level = user_data.get('current_level', 'A1') if user_data else 'A1'
    
    # Get statistics
    stats = await db.get_user_statistics(user.id)
    
    # Format and send
    message = Formatters.progress_summary(stats, level)
    
    await update.message.reply_text(
        message,
        parse_mode='Markdown',
        reply_markup=Keyboards.progress_actions()
    )


async def progress_callback(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle progress-related callbacks."""
    query = update.callback_query
    await query.answer()
    
    user = update.effective_user
    data = query.data
    
    if data == 'practice_weak':
        # Get weak areas and suggest practice
        stats = await db.get_user_statistics(user.id)
        weak_areas = stats.get('weak_areas', [])
        
        if weak_areas:
            message = "Your Weak Areas / Schwachstellen:\n\n"
            for i, area in enumerate(weak_areas[:5], 1):
                message += f"{i}. {area}\n"
            message += "\nStart a learning session to practice these areas!"
        else:
            message = "Great job! No significant weak areas detected.\n" \
                      "Keep practicing to maintain your skills!"
        
        await query.edit_message_text(
            message,
            reply_markup=Keyboards.learn_menu()
        )
    
    elif data == 'view_history':
        # Get exam history
        attempts = await db.get_exam_attempts(user.id, limit=10)
        
        if attempts:
            message = "*Recent Exam History*\n\n"
            for attempt in attempts[:10]:
                exam_type = attempt.get('exam_type', 'Unknown').capitalize()
                score = attempt.get('score', 0)
                date = attempt.get('completed_at', '')[:10] if attempt.get('completed_at') else 'N/A'
                
                emoji = "" if score >= 60 else ""
                message += f"{emoji} {exam_type}: {score:.0f}% ({date})\n"
        else:
            message = "No exam history yet.\n" \
                      "Take some exams to see your history here!"
        
        await query.edit_message_text(
            message,
            parse_mode='Markdown',
            reply_markup=Keyboards.progress_actions()
        )
    
    elif data == 'menu_main':
        await query.edit_message_text(
            "Main Menu / Hauptmenu",
            reply_markup=Keyboards.main_menu()
        )


# Export handlers
progress_handler = CommandHandler('progress', progress_command)
progress_callback_handler = CallbackQueryHandler(progress_callback, pattern='^(practice_weak|view_history)$')
