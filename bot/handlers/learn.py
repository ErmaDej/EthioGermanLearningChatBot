"""
Learning/tutoring conversation handler.
Manages AI-powered German tutoring sessions.
"""
import logging
from uuid import uuid4
from telegram import Update
from telegram.ext import (
    ContextTypes,
    ConversationHandler,
    CommandHandler,
    MessageHandler,
    CallbackQueryHandler,
    filters
)

from bot.services.database import db
from bot.services.ai_tutor import ai_tutor
from bot.services.speech import speech_service
from bot.middleware.subscription import require_subscription, get_subscription_warning
from bot.utils.keyboards import Keyboards
from bot.utils.formatters import Formatters

logger = logging.getLogger(__name__)

# Conversation states
SELECTING_SKILL, IN_CONVERSATION = range(2)


async def learn_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Handle /learn command - start learning session."""
    user = update.effective_user
    
    # Check subscription
    is_active, _ = await db.check_subscription(user.id)
    if not is_active:
        await update.message.reply_text(
            "You need an active subscription to use the learning features.\n"
            "Please contact @EthioGermanSchool to activate.",
            reply_markup=Keyboards.back_to_menu()
        )
        return ConversationHandler.END
    
    await update.message.reply_text(
        "Learning Center / Lernzentrum\n\n"
        "Choose what you'd like to practice:\n"
        "Wahlen Sie was Sie uben mochten:",
        reply_markup=Keyboards.learn_menu()
    )
    return SELECTING_SKILL


async def skill_selected(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Handle skill selection from learn menu."""
    query = update.callback_query
    await query.answer()
    
    user = update.effective_user
    data = query.data
    
    # Check subscription
    is_active, _ = await db.check_subscription(user.id)
    if not is_active:
        await query.edit_message_text(
            "Subscription required. Contact @EthioGermanSchool",
            reply_markup=Keyboards.back_to_menu()
        )
        return ConversationHandler.END
    
    if data == 'menu_main':
        await query.edit_message_text(
            "Main Menu / Hauptmenu",
            reply_markup=Keyboards.main_menu()
        )
        return ConversationHandler.END
    
    # Extract skill from callback data
    skill = data.replace('learn_', '')
    
    # Get user data
    user_data = await db.get_user(user.id)
    level = user_data.get('current_level', 'A1') if user_data else 'A1'
    preferred_lang = user_data.get('preferred_lang', 'english') if user_data else 'english'
    
    # Store session data
    context.user_data['session_id'] = str(uuid4())
    context.user_data['skill'] = skill
    context.user_data['level'] = level
    context.user_data['preferred_lang'] = preferred_lang
    context.user_data['conversation_history'] = []
    
    # Get user's weak areas for context
    stats = await db.get_user_statistics(user.id)
    context.user_data['weak_areas'] = stats.get('weak_areas', [])
    
    # Prepare welcome message based on skill
    skill_intros = {
        'conversation': (
            "Free Conversation Mode\n\n"
            f"Level: {level}\n\n"
            "Let's chat in German! I'll help you practice.\n"
            "Start by saying something in German, or ask me a question.\n\n"
            "Lass uns auf Deutsch sprechen!"
        ),
        'grammar': (
            "Grammar Practice Mode\n\n"
            f"Level: {level}\n\n"
            "I'll help you practice German grammar.\n"
            "Ask me about any grammar topic or let's practice together!\n\n"
            "Frag mich etwas uber deutsche Grammatik!"
        ),
        'lesen': (
            "Reading Practice Mode\n\n"
            f"Level: {level}\n\n"
            "I'll provide texts for you to read and discuss.\n"
            "Type 'ready' to get a reading passage.\n\n"
            "Ich gebe dir Texte zum Lesen."
        ),
        'horen': (
            "Listening Practice Mode\n\n"
            f"Level: {level}\n\n"
            "Note: Audio features depend on your device.\n"
            "I'll describe scenarios and we'll practice listening comprehension.\n\n"
            "Wir uben das Horverstehen."
        ),
        'schreiben': (
            "Writing Practice Mode\n\n"
            f"Level: {level}\n\n"
            "I'll give you writing prompts and provide feedback.\n"
            "Type 'prompt' to get a writing task.\n\n"
            "Ich gebe dir Schreibaufgaben."
        ),
        'sprechen': (
            "Speaking Practice Mode\n\n"
            f"Level: {level}\n\n"
            "Send voice messages to practice speaking!\n"
            f"{'Voice transcription is available.' if speech_service.is_available else 'Note: Type your responses for now.'}\n\n"
            "Schick mir Sprachnachrichten!"
        ),
        'vokabular': (
            "Vocabulary Practice Mode\n\n"
            f"Level: {level}\n\n"
            "Let's expand your German vocabulary!\n"
            "Ask about words, or say 'quiz' for a vocabulary quiz.\n\n"
            "Lass uns deinen Wortschatz erweitern!"
        )
    }
    
    intro = skill_intros.get(skill, skill_intros['conversation'])
    
    await query.edit_message_text(
        intro + "\n\nType /cancel to exit.",
        reply_markup=Keyboards.end_conversation()
    )
    
    return IN_CONVERSATION


async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Handle user messages during tutoring session."""
    user = update.effective_user
    message = update.message
    
    # Check if it's a text or voice message
    if message.voice:
        # Handle voice message
        if speech_service.is_available:
            await message.reply_text("Processing your voice message... / Verarbeite Sprachnachricht...")
            
            transcribed = await speech_service.transcribe_telegram_voice(
                message.voice,
                context.bot
            )
            
            if transcribed:
                user_text = transcribed
                await message.reply_text(f"I heard: \"{transcribed}\"")
            else:
                await message.reply_text(
                    "Sorry, I couldn't transcribe your voice message. Please try again or type your message."
                )
                return IN_CONVERSATION
        else:
            await message.reply_text(
                "Voice transcription is not available. Please type your message."
            )
            return IN_CONVERSATION
    else:
        user_text = message.text
    
    # Get session data
    session_id = context.user_data.get('session_id', str(uuid4()))
    skill = context.user_data.get('skill', 'conversation')
    level = context.user_data.get('level', 'A1')
    preferred_lang = context.user_data.get('preferred_lang', 'english')
    weak_areas = context.user_data.get('weak_areas', [])
    history = context.user_data.get('conversation_history', [])
    
    # Save user message to history
    history.append({'role': 'user', 'content': user_text})
    
    # Send typing indicator
    await context.bot.send_chat_action(chat_id=message.chat_id, action='typing')
    
    # Get AI response
    response = await ai_tutor.chat(
        user_message=user_text,
        conversation_history=history,
        level=level,
        preferred_lang=preferred_lang,
        skill_focus=skill if skill != 'conversation' else None,
        weak_areas=weak_areas
    )
    
    # Save AI response to history
    history.append({'role': 'assistant', 'content': response})
    context.user_data['conversation_history'] = history
    
    # Save to database for long-term memory
    await db.save_conversation(user.id, session_id, 'user', user_text)
    await db.save_conversation(user.id, session_id, 'assistant', response)
    
    # Add subscription warning if needed
    warning = get_subscription_warning(context)
    
    # Send response
    await message.reply_text(
        response + warning,
        reply_markup=Keyboards.end_conversation()
    )
    
    return IN_CONVERSATION


async def end_conversation(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """End the tutoring conversation."""
    query = update.callback_query
    await query.answer()
    
    user = update.effective_user
    
    # Calculate session stats
    history = context.user_data.get('conversation_history', [])
    messages_count = len(history)
    
    # Save progress if meaningful conversation
    if messages_count >= 4:
        skill = context.user_data.get('skill', 'conversation')
        # Basic score based on conversation length (can be improved)
        score = min(100, 50 + messages_count * 5)
        
        await db.save_progress(
            user_id=user.id,
            skill=skill,
            activity_type='tutoring',
            score=score
        )
    
    # Clear session data
    session_data = {
        'session_id': context.user_data.get('session_id'),
        'skill': context.user_data.get('skill'),
        'messages': messages_count
    }
    context.user_data.clear()
    
    await query.edit_message_text(
        f"Tutoring session ended.\n"
        f"Sitzung beendet.\n\n"
        f"Messages exchanged: {messages_count}\n"
        f"Keep practicing! Weiter uben!",
        reply_markup=Keyboards.main_menu()
    )
    
    return ConversationHandler.END


async def cancel_conversation(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Cancel the tutoring conversation via /cancel command."""
    context.user_data.clear()
    
    await update.message.reply_text(
        "Session cancelled. Returning to menu.\n"
        "Sitzung abgebrochen.",
        reply_markup=Keyboards.main_menu()
    )
    
    return ConversationHandler.END


# Create the conversation handler
learn_conversation_handler = ConversationHandler(
    entry_points=[
        CommandHandler('learn', learn_command),
        CallbackQueryHandler(skill_selected, pattern='^learn_')
    ],
    states={
        SELECTING_SKILL: [
            CallbackQueryHandler(skill_selected, pattern='^learn_'),
            CallbackQueryHandler(skill_selected, pattern='^menu_main$')
        ],
        IN_CONVERSATION: [
            MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message),
            MessageHandler(filters.VOICE, handle_message),
            CallbackQueryHandler(end_conversation, pattern='^end_conversation$')
        ]
    },
    fallbacks=[
        CommandHandler('cancel', cancel_conversation),
        CallbackQueryHandler(end_conversation, pattern='^end_conversation$')
    ],
    name="learn_conversation",
    persistent=False
)
