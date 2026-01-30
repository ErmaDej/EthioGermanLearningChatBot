"""
Exam handler.
Manages Goethe-style exam simulations.
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
from bot.services.exam_engine import exam_engine
from bot.services.speech import speech_service
from bot.middleware.subscription import require_subscription
from bot.utils.keyboards import Keyboards
from bot.utils.formatters import Formatters

logger = logging.getLogger(__name__)

# Conversation states
SELECTING_EXAM, ANSWERING_OBJECTIVE, WRITING_RESPONSE, SPEAKING_RESPONSE, REVIEWING_RESULTS = range(5)


async def exam_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Handle /exam command - start exam selection."""
    user = update.effective_user
    
    # Check subscription
    is_active, _ = await db.check_subscription(user.id)
    if not is_active:
        await update.message.reply_text(
            "You need an active subscription to take exams.\n"
            "Please contact @EthioGermanSchool to activate.",
            reply_markup=Keyboards.back_to_menu()
        )
        return ConversationHandler.END
    
    await update.message.reply_text(
        "Exam Center / Prufungszentrum\n\n"
        "Choose an exam type:\n"
        "Wahlen Sie eine Prufungsart:",
        reply_markup=Keyboards.exam_menu()
    )
    return SELECTING_EXAM


async def exam_selected(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Handle exam type selection."""
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
    
    # Extract exam type
    exam_type = data.replace('exam_', '')
    
    if exam_type == 'full':
        await query.edit_message_text(
            "Full Mock Exam coming soon!\n"
            "For now, please select individual exam types.",
            reply_markup=Keyboards.exam_menu()
        )
        return SELECTING_EXAM
    
    # Get user data
    user_data = await db.get_user(user.id)
    level = user_data.get('current_level', 'A1') if user_data else 'A1'
    
    # Initialize exam session
    context.user_data['exam_type'] = exam_type
    context.user_data['level'] = level
    context.user_data['answers'] = []
    context.user_data['current_question'] = 0
    
    # Get questions
    questions = await exam_engine.get_exam_questions(level, exam_type)
    
    if not questions:
        await query.edit_message_text(
            "Sorry, no questions available for this exam type.\n"
            "Please try another type or contact support.",
            reply_markup=Keyboards.exam_menu()
        )
        return SELECTING_EXAM
    
    context.user_data['questions'] = questions
    context.user_data['total_questions'] = len(questions)
    
    # Create exam attempt record
    attempt = await db.create_exam_attempt(user.id, exam_type, level)
    if attempt:
        context.user_data['attempt_id'] = attempt.get('id')
    
    # Route to appropriate handler based on exam type
    if exam_type in ['schreiben', 'sprechen']:
        return await start_subjective_exam(query, context)
    else:
        return await show_objective_question(query, context)


async def show_objective_question(query, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Display an objective (MCQ) question."""
    current = context.user_data.get('current_question', 0)
    questions = context.user_data.get('questions', [])
    total = context.user_data.get('total_questions', 0)
    
    if current >= len(questions):
        # All questions answered, show results
        return await show_exam_results(query, context)
    
    question = questions[current]
    question_data = question.get('question_data', {})
    
    # Format question text
    question_text = question.get('question_text', '')
    passage = question_data.get('passage', '')
    
    formatted = Formatters.exam_question(current + 1, total, question_text, passage)
    
    # Get options
    options = question_data.get('options', ['A', 'B', 'C', 'D'])
    
    # Store current question data for answer checking
    context.user_data['current_question_data'] = question
    
    await query.edit_message_text(
        formatted,
        parse_mode='Markdown',
        reply_markup=Keyboards.mcq_options(options)
    )
    
    return ANSWERING_OBJECTIVE


async def handle_objective_answer(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Handle answer selection for objective questions."""
    query = update.callback_query
    await query.answer()
    
    data = query.data
    
    if data == 'cancel':
        return await cancel_exam(update, context)
    
    # Extract answer
    user_answer = data.replace('answer_', '')
    
    # Get current question
    question = context.user_data.get('current_question_data', {})
    
    # Check answer
    is_correct, explanation = exam_engine.check_answer(question, user_answer)
    
    # Store answer
    answers = context.user_data.get('answers', [])
    answers.append({
        'question_id': question.get('id'),
        'user_answer': user_answer,
        'correct_answer': question.get('correct_answer', ''),
        'is_correct': is_correct,
        'topic': question.get('question_data', {}).get('topic', context.user_data.get('exam_type'))
    })
    context.user_data['answers'] = answers
    
    # Show feedback
    feedback_emoji = "" if is_correct else ""
    feedback = f"{feedback_emoji} {'Richtig!' if is_correct else 'Falsch.'}\n\n{explanation}"
    
    # Move to next question
    context.user_data['current_question'] = context.user_data.get('current_question', 0) + 1
    
    await query.edit_message_text(
        feedback,
        reply_markup=Keyboards.next_question()
    )
    
    return ANSWERING_OBJECTIVE


async def next_question(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Move to the next question."""
    query = update.callback_query
    await query.answer()
    
    current = context.user_data.get('current_question', 0)
    total = context.user_data.get('total_questions', 0)
    
    if current >= total:
        return await show_exam_results(query, context)
    
    return await show_objective_question(query, context)


async def start_subjective_exam(query, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Start a subjective (writing/speaking) exam."""
    exam_type = context.user_data.get('exam_type')
    level = context.user_data.get('level', 'A1')
    questions = context.user_data.get('questions', [])
    
    if not questions:
        await query.edit_message_text(
            "No prompts available. Please try again later.",
            reply_markup=Keyboards.exam_menu()
        )
        return SELECTING_EXAM
    
    question = questions[0]
    question_data = question.get('question_data', {})
    context.user_data['current_question_data'] = question
    
    prompt = question.get('question_text', '') or question_data.get('question_text', '')
    requirements = question_data.get('requirements', [])
    word_count = question_data.get('word_count', {'min': 50, 'max': 100})
    
    if exam_type == 'schreiben':
        message = f"""
*Writing Task / Schreibaufgabe*

*Level:* {level}

*Task:*
{prompt}

*Requirements:*
"""
        for req in requirements:
            message += f"- {req}\n"
        
        message += f"\n*Word count:* {word_count.get('min', 50)}-{word_count.get('max', 100)} words\n\n"
        message += "Type your response below. Click 'Submit' when done."
        
        context.user_data['writing_buffer'] = []
        
        await query.edit_message_text(
            message,
            parse_mode='Markdown',
            reply_markup=Keyboards.submit_cancel()
        )
        return WRITING_RESPONSE
    
    else:  # sprechen
        hints = question_data.get('hints', [])
        prep_time = question_data.get('preparation_time_sec', 30)
        
        message = f"""
*Speaking Task / Sprechaufgabe*

*Level:* {level}

*Task:*
{prompt}

*Helpful phrases:*
"""
        for hint in hints:
            message += f"- {hint}\n"
        
        if speech_service.is_available:
            message += "\n\nSend a voice message with your response."
        else:
            message += "\n\nVoice not available. Please type your spoken response."
        
        await query.edit_message_text(
            message,
            parse_mode='Markdown',
            reply_markup=Keyboards.submit_cancel()
        )
        return SPEAKING_RESPONSE


async def handle_writing_input(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Handle text input for writing exam."""
    message = update.message
    text = message.text
    
    # Add to buffer
    buffer = context.user_data.get('writing_buffer', [])
    buffer.append(text)
    context.user_data['writing_buffer'] = buffer
    
    combined = ' '.join(buffer)
    word_count = len(combined.split())
    
    await message.reply_text(
        f"Text received. Current word count: {word_count}\n\n"
        "Send more text or click Submit when done.",
        reply_markup=Keyboards.submit_cancel()
    )
    
    return WRITING_RESPONSE


async def handle_speaking_input(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Handle voice/text input for speaking exam."""
    message = update.message
    user = update.effective_user
    
    if message.voice:
        if speech_service.is_available:
            await message.reply_text("Processing your voice message...")
            
            transcribed = await speech_service.transcribe_telegram_voice(
                message.voice,
                context.bot
            )
            
            if transcribed:
                context.user_data['speaking_response'] = transcribed
                await message.reply_text(
                    f"Transcribed: \"{transcribed}\"\n\n"
                    "Click Submit to get your evaluation.",
                    reply_markup=Keyboards.submit_cancel()
                )
            else:
                await message.reply_text(
                    "Couldn't transcribe. Please try again or type your response.",
                    reply_markup=Keyboards.submit_cancel()
                )
        else:
            await message.reply_text(
                "Voice transcription not available. Please type your response.",
                reply_markup=Keyboards.submit_cancel()
            )
    else:
        context.user_data['speaking_response'] = message.text
        await message.reply_text(
            "Response received. Click Submit to get your evaluation.",
            reply_markup=Keyboards.submit_cancel()
        )
    
    return SPEAKING_RESPONSE


async def submit_subjective(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Submit subjective exam for evaluation."""
    query = update.callback_query
    await query.answer()
    
    user = update.effective_user
    exam_type = context.user_data.get('exam_type')
    level = context.user_data.get('level', 'A1')
    question = context.user_data.get('current_question_data', {})
    prompt = question.get('question_text', '') or question.get('question_data', {}).get('question_text', '')
    
    await query.edit_message_text("Evaluating your response... / Bewertung lauft...")
    
    if exam_type == 'schreiben':
        buffer = context.user_data.get('writing_buffer', [])
        user_text = ' '.join(buffer)
        
        evaluation = await ai_tutor.evaluate_writing(user_text, prompt, level)
        formatted_result = Formatters.writing_evaluation(evaluation)
    else:
        user_text = context.user_data.get('speaking_response', '')
        evaluation = await ai_tutor.evaluate_speaking(user_text, prompt, level)
        formatted_result = Formatters.speaking_evaluation(evaluation)
    
    # Save results
    score = evaluation.get('overall_score', 0)
    attempt_id = context.user_data.get('attempt_id')
    
    if attempt_id:
        await db.update_exam_attempt(
            attempt_id,
            answers=[{
                'question_id': question.get('id'),
                'user_response': user_text,
                'evaluation': evaluation
            }],
            score=score,
            is_completed=True
        )
    
    # Save progress
    await db.save_progress(
        user_id=user.id,
        skill=exam_type,
        activity_type='exam',
        score=score,
        weak_areas=evaluation.get('suggestions', [])[:3]
    )
    
    await query.edit_message_text(
        formatted_result,
        parse_mode='Markdown',
        reply_markup=Keyboards.view_results()
    )
    
    # Clear exam data
    context.user_data.clear()
    
    return ConversationHandler.END


async def show_exam_results(query, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Show final exam results for objective exams."""
    user = query.from_user
    exam_type = context.user_data.get('exam_type', 'unknown')
    answers = context.user_data.get('answers', [])
    attempt_id = context.user_data.get('attempt_id')
    
    # Calculate score
    result = exam_engine.calculate_score(answers, exam_type)
    
    # Update attempt in database
    if attempt_id:
        await db.update_exam_attempt(
            attempt_id,
            answers=answers,
            score=result['score'],
            is_completed=True
        )
    
    # Save progress
    await db.save_progress(
        user_id=user.id,
        skill=exam_type,
        activity_type='exam',
        score=result['score'],
        weak_areas=result['weak_areas']
    )
    
    # Format results
    formatted = Formatters.exam_results(
        exam_type=exam_type,
        score=result['score'],
        correct=result['correct_answers'],
        total=result['total_questions'],
        passed=result['passed'],
        weak_areas=result['weak_areas']
    )
    
    await query.edit_message_text(
        formatted,
        parse_mode='Markdown',
        reply_markup=Keyboards.view_results()
    )
    
    # Clear exam data
    context.user_data.clear()
    
    return ConversationHandler.END


async def cancel_exam(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Cancel the current exam."""
    if update.callback_query:
        query = update.callback_query
        await query.answer()
        await query.edit_message_text(
            "Exam cancelled.\nPrufung abgebrochen.",
            reply_markup=Keyboards.main_menu()
        )
    else:
        await update.message.reply_text(
            "Exam cancelled.\nPrufung abgebrochen.",
            reply_markup=Keyboards.main_menu()
        )
    
    context.user_data.clear()
    return ConversationHandler.END


# Create the conversation handler
exam_conversation_handler = ConversationHandler(
    entry_points=[
        CommandHandler('exam', exam_command),
        CallbackQueryHandler(exam_selected, pattern='^exam_')
    ],
    states={
        SELECTING_EXAM: [
            CallbackQueryHandler(exam_selected, pattern='^exam_'),
            CallbackQueryHandler(exam_selected, pattern='^menu_main$')
        ],
        ANSWERING_OBJECTIVE: [
            CallbackQueryHandler(handle_objective_answer, pattern='^answer_'),
            CallbackQueryHandler(next_question, pattern='^next_question$'),
            CallbackQueryHandler(cancel_exam, pattern='^cancel$')
        ],
        WRITING_RESPONSE: [
            MessageHandler(filters.TEXT & ~filters.COMMAND, handle_writing_input),
            CallbackQueryHandler(submit_subjective, pattern='^submit$'),
            CallbackQueryHandler(cancel_exam, pattern='^cancel$')
        ],
        SPEAKING_RESPONSE: [
            MessageHandler(filters.TEXT & ~filters.COMMAND, handle_speaking_input),
            MessageHandler(filters.VOICE, handle_speaking_input),
            CallbackQueryHandler(submit_subjective, pattern='^submit$'),
            CallbackQueryHandler(cancel_exam, pattern='^cancel$')
        ]
    },
    fallbacks=[
        CommandHandler('cancel', cancel_exam),
        CallbackQueryHandler(cancel_exam, pattern='^cancel$')
    ],
    name="exam_conversation",
    persistent=False
)
