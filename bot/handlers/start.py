"""
Start and help command handlers.
Handles user registration and initial interactions.
"""
import logging
from telegram import Update
from telegram.ext import ContextTypes, CommandHandler

from bot.services.database import db
from bot.utils.keyboards import Keyboards
from bot.utils.formatters import Formatters

logger = logging.getLogger(__name__)


async def _start_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """
    Handle /start command.
    Register new users or show welcome message to existing users.
    """
    user = update.effective_user
    if not user:
        logger.warning("Start command received but no effective user found.")
        return
    
    user_id = user.id
    logger.info(f"Start command from user {user_id} ({user.username})")
    
    try:
        # Check if user exists
        existing_user = await db.get_user(user_id)
        logger.info(f"User exists check for {user_id}: {bool(existing_user)}")
        
        if existing_user:
            # Existing user - show welcome back message
            level = existing_user.get('current_level', 'A1')
            name = existing_user.get('first_name') or user.first_name or 'Student'
            
            # Check subscription
            is_active, expiry_date = await db.check_subscription(user_id)
            logger.info(f"Subscription check for {user_id}: active={is_active}")
            
            if is_active:
                await update.message.reply_text(
                    f"Willkommen zuruck, {name}!\n"
                    f"Welcome back!\n\n"
                    f"Your level: {level}\n\n"
                    "What would you like to do today?",
                    reply_markup=Keyboards.main_menu()
                )
            else:
                expiry_str = expiry_date.strftime('%d %B %Y') if expiry_date else 'Not activated'
                await update.message.reply_text(
                    f"Welcome back, {name}!\n\n"
                    f"Your subscription status: {'Expired on ' + expiry_str if expiry_date else 'Not activated'}\n\n"
                    "Please contact @EthioGermanSchool to activate or renew your subscription.\n\n"
                    "Bitte kontaktieren Sie uns um Ihr Abonnement zu aktivieren.",
                    reply_markup=Keyboards.back_to_menu()
                )
            
            # Update last active
            await db.update_last_active(user_id)
        
        else:
            # New user - start registration
            logger.info(f"Starting registration flow for {user_id}")
            await update.message.reply_text(
                f"Willkommen bei EthioGerman Language School!\n"
                f"Welcome, {user.first_name or 'Student'}!\n\n"
                "Let's set up your profile.\n"
                "Please select your German level:",
                reply_markup=Keyboards.level_selection()
            )
            
            # Store registration state
            context.user_data['registering'] = True
            context.user_data['reg_username'] = user.username
            context.user_data['reg_first_name'] = user.first_name
            context.user_data['reg_last_name'] = user.last_name
            
    except Exception as e:
        logger.error(f"Error in _start_command for user {user_id}: {e}", exc_info=True)
        await update.message.reply_text(
            "An error occurred while starting the bot. Please try again later."
        )


async def registration_level_callback(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle level selection during registration."""
    query = update.callback_query
    await query.answer()
    
    if not context.user_data.get('registering'):
        return
    
    data = query.data
    if data.startswith('level_'):
        level = data.replace('level_', '')
        context.user_data['reg_level'] = level
        
        # Ask for preferred language
        await query.edit_message_text(
            f"Selected level: {level}\n\n"
            "Now, choose your preferred language for explanations:",
            reply_markup=Keyboards.language_selection()
        )


async def registration_lang_callback(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle language selection during registration."""
    query = update.callback_query
    await query.answer()
    
    if not context.user_data.get('registering'):
        return
    
    user = update.effective_user
    data = query.data
    
    if data.startswith('lang_'):
        lang = data.replace('lang_', '')
        level = context.user_data.get('reg_level', 'A1')
        
        # Create user in database
        new_user = await db.create_user(
            user_id=user.id,
            username=context.user_data.get('reg_username'),
            first_name=context.user_data.get('reg_first_name'),
            last_name=context.user_data.get('reg_last_name'),
            level=level,
            preferred_lang=lang
        )
        
        # Clear registration state
        context.user_data['registering'] = False
        
        if new_user:
            await query.edit_message_text(
                f"Registration complete!\n"
                f"Registrierung abgeschlossen!\n\n"
                f"Level: {level}\n"
                f"Language: {lang.capitalize()}\n\n"
                "Note: Your subscription is not yet active.\n"
                "Please contact @EthioGermanSchool to activate your account.\n\n"
                "Once activated, you can start learning German!\n"
                "Sobald aktiviert, konnen Sie Deutsch lernen!",
                reply_markup=Keyboards.back_to_menu()
            )
        else:
            await query.edit_message_text(
                "There was an error during registration. Please try /start again.",
                reply_markup=Keyboards.back_to_menu()
            )


async def _help_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle /help command."""
    await update.message.reply_text(
        Formatters.help_message(),
        parse_mode='Markdown',
        reply_markup=Keyboards.back_to_menu()
    )


async def _cancel_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle /cancel command - exit current operation."""
    # Clear any ongoing states
    context.user_data.clear()
    
    await update.message.reply_text(
        "Operation cancelled. Returning to main menu.\n"
        "Vorgang abgebrochen.",
        reply_markup=Keyboards.main_menu()
    )


# Export handlers
start_handler = CommandHandler('start', _start_command)
help_handler = CommandHandler('help', _help_command)
cancel_handler = CommandHandler('cancel', _cancel_command)

