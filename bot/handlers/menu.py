"""
Menu navigation handler.
Handles main menu and navigation between different sections.
"""
import logging
from telegram import Update
from telegram.ext import ContextTypes, CommandHandler, CallbackQueryHandler

from bot.services.database import db
from bot.middleware.subscription import require_subscription, require_subscription_callback
from bot.utils.keyboards import Keyboards
from bot.utils.formatters import Formatters

logger = logging.getLogger(__name__)


@require_subscription
async def menu_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle /menu command - show main menu."""
    await update.message.reply_text(
        "Main Menu / Hauptmenu\n\n"
        "What would you like to do?",
        reply_markup=Keyboards.main_menu()
    )


async def menu_callback(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle menu navigation callbacks."""
    query = update.callback_query
    await query.answer()
    
    user = update.effective_user
    data = query.data
    
    # Handle registration callbacks first (no subscription needed)
    if data.startswith('level_') and context.user_data.get('registering'):
        from bot.handlers.start import registration_level_callback
        await registration_level_callback(update, context)
        return
    
    if data.startswith('lang_') and context.user_data.get('registering'):
        from bot.handlers.start import registration_lang_callback
        await registration_lang_callback(update, context)
        return
    
    # For other callbacks, check subscription
    if not data.startswith('menu_') or data == 'menu_help':
        # menu_help doesn't require subscription
        pass
    else:
        # Check subscription for menu navigation
        is_active, _ = await db.check_subscription(user.id)
        if not is_active and data not in ['menu_main', 'menu_help', 'cancel']:
            await query.answer(
                "Subscription required. Contact @EthioGermanSchool",
                show_alert=True
            )
            return
    
    # Handle different menu options
    if data == 'menu_main':
        await query.edit_message_text(
            "Main Menu / Hauptmenu\n\n"
            "What would you like to do?",
            reply_markup=Keyboards.main_menu()
        )
    
    elif data == 'menu_learn':
        await query.edit_message_text(
            "Learning Center / Lernzentrum\n\n"
            "Choose what you'd like to practice:",
            reply_markup=Keyboards.learn_menu()
        )
    
    elif data == 'menu_exam':
        await query.edit_message_text(
            "Exam Center / Prufungszentrum\n\n"
            "Choose an exam type:\n"
            "Wahlen Sie eine Prufungsart:",
            reply_markup=Keyboards.exam_menu()
        )
    
    elif data == 'menu_progress':
        # Get user stats
        user_data = await db.get_user(user.id)
        stats = await db.get_user_statistics(user.id)
        level = user_data.get('current_level', 'A1') if user_data else 'A1'
        
        await query.edit_message_text(
            Formatters.progress_summary(stats, level),
            parse_mode='Markdown',
            reply_markup=Keyboards.progress_actions()
        )
    
    elif data == 'menu_settings':
        await query.edit_message_text(
            "Settings / Einstellungen\n\n"
            "What would you like to change?",
            reply_markup=Keyboards.settings_menu()
        )
    
    elif data == 'menu_help':
        await query.edit_message_text(
            Formatters.help_message(),
            parse_mode='Markdown',
            reply_markup=Keyboards.back_to_menu()
        )
    
    elif data == 'cancel':
        context.user_data.clear()
        await query.edit_message_text(
            "Operation cancelled.\n"
            "Vorgang abgebrochen.",
            reply_markup=Keyboards.main_menu()
        )


async def settings_callback(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle settings-related callbacks."""
    query = update.callback_query
    await query.answer()
    
    user = update.effective_user
    data = query.data
    
    if data == 'settings_level':
        user_data = await db.get_user(user.id)
        current_level = user_data.get('current_level', 'A1') if user_data else 'A1'
        
        context.user_data['changing_level'] = True
        await query.edit_message_text(
            f"Current level: {current_level}\n\n"
            "Select your new level:",
            reply_markup=Keyboards.level_selection(current_level)
        )
    
    elif data == 'settings_lang':
        user_data = await db.get_user(user.id)
        current_lang = user_data.get('preferred_lang', 'english') if user_data else 'english'
        
        context.user_data['changing_lang'] = True
        await query.edit_message_text(
            f"Current language: {current_lang.capitalize()}\n\n"
            "Select your preferred explanation language:",
            reply_markup=Keyboards.language_selection(current_lang)
        )
    
    elif data == 'settings_subscription':
        is_active, expiry_date = await db.check_subscription(user.id)
        
        await query.edit_message_text(
            Formatters.subscription_info(expiry_date, is_active),
            parse_mode='Markdown',
            reply_markup=Keyboards.back_to_menu()
        )
    
    elif data.startswith('level_') and context.user_data.get('changing_level'):
        level = data.replace('level_', '')
        await db.update_user(user.id, current_level=level)
        context.user_data['changing_level'] = False
        
        await query.edit_message_text(
            f"Level updated to {level}!\n"
            f"Stufe aktualisiert auf {level}!",
            reply_markup=Keyboards.settings_menu()
        )
    
    elif data.startswith('lang_') and context.user_data.get('changing_lang'):
        lang = data.replace('lang_', '')
        await db.update_user(user.id, preferred_lang=lang)
        context.user_data['changing_lang'] = False
        
        await query.edit_message_text(
            f"Language updated to {lang.capitalize()}!\n"
            "Sprache aktualisiert!",
            reply_markup=Keyboards.settings_menu()
        )


# Export handlers
menu_handler = CommandHandler('menu', menu_command)
menu_callback_handler = CallbackQueryHandler(menu_callback, pattern='^(menu_|cancel)')
settings_callback_handler = CallbackQueryHandler(settings_callback, pattern='^(settings_|level_|lang_)')
