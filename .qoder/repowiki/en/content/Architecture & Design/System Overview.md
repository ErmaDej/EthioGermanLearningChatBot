# System Overview

<cite>
**Referenced Files in This Document**
- [bot/main.py](file://bot/main.py)
- [bot/config.py](file://bot/config.py)
- [bot/handlers/start.py](file://bot/handlers/start.py)
- [bot/handlers/menu.py](file://bot/handlers/menu.py)
- [bot/handlers/learn.py](file://bot/handlers/learn.py)
- [bot/handlers/exam.py](file://bot/handlers/exam.py)
- [bot/handlers/progress.py](file://bot/handlers/progress.py)
- [bot/middleware/subscription.py](file://bot/middleware/subscription.py)
- [bot/services/database.py](file://bot/services/database.py)
- [bot/services/ai_tutor.py](file://bot/services/ai_tutor.py)
- [bot/services/exam_engine.py](file://bot/services/exam_engine.py)
- [bot/services/speech.py](file://bot/services/speech.py)
- [requirements.txt](file://requirements.txt)
- [database_setup.sql](file://database_setup.sql)
</cite>

## Table of Contents
1. [Introduction](#introduction)
2. [Project Structure](#project-structure)
3. [Core Components](#core-components)
4. [Architecture Overview](#architecture-overview)
5. [Detailed Component Analysis](#detailed-component-analysis)
6. [Dependency Analysis](#dependency-analysis)
7. [Performance Considerations](#performance-considerations)
8. [Troubleshooting Guide](#troubleshooting-guide)
9. [Conclusion](#conclusion)

## Introduction
This document presents a comprehensive system overview of the FebEGLS-bot, an event-driven Telegram bot implementing a modular architecture for German language education. The system integrates Telegram’s Bot API, an AI tutoring service, a speech transcription engine, and a Supabase-backed persistence layer. It follows clear separation of concerns:
- Event-driven updates flow from Telegram through handlers to services.
- Handlers implement the Handler pattern for command and callback processing.
- Services encapsulate external integrations (AI, database, speech).
- Middleware enforces access control for paid features.
- Configuration centralizes environment-specific settings.

## Project Structure
The project is organized by functional layers:
- bot/: Core application code
  - handlers/: Command and callback handlers implementing the Handler pattern
  - middleware/: Access control middleware
  - services/: External integrations and domain services
  - utils/: Shared UI helpers and formatters
  - config.py: Centralized configuration and validation
  - main.py: Application bootstrap and update routing
- prompts/: System prompts for the AI tutor
- database_setup.sql: Supabase schema and indexes
- requirements.txt: External dependencies

```mermaid
graph TB
subgraph "Telegram Bot"
TGBot["Telegram Bot API"]
end
subgraph "App Layer"
Main["bot/main.py"]
Handlers["bot/handlers/*"]
Middleware["bot/middleware/*"]
Utils["bot/utils/*"]
end
subgraph "Services"
DB["bot/services/database.py"]
AITutor["bot/services/ai_tutor.py"]
ExamEngine["bot/services/exam_engine.py"]
Speech["bot/services/speech.py"]
end
subgraph "External Systems"
Supabase["Supabase (PostgreSQL)"]
OpenRouter["OpenRouter API"]
Whisper["faster-whisper"]
end
TGBot --> Main
Main --> Handlers
Handlers --> Middleware
Handlers --> DB
Handlers --> AITutor
Handlers --> Speech
Handlers --> ExamEngine
DB --> Supabase
AITutor --> OpenRouter
Speech --> Whisper
```

**Diagram sources**
- [bot/main.py](file://bot/main.py#L60-L101)
- [bot/handlers/start.py](file://bot/handlers/start.py#L177-L181)
- [bot/handlers/menu.py](file://bot/handlers/menu.py#L180-L183)
- [bot/handlers/learn.py](file://bot/handlers/learn.py#L291-L314)
- [bot/handlers/exam.py](file://bot/handlers/exam.py#L488-L522)
- [bot/services/database.py](file://bot/services/database.py#L16-L21)
- [bot/services/ai_tutor.py](file://bot/services/ai_tutor.py#L19-L32)
- [bot/services/speech.py](file://bot/services/speech.py#L21-L44)

**Section sources**
- [bot/main.py](file://bot/main.py#L1-L106)
- [bot/config.py](file://bot/config.py#L10-L60)

## Core Components
- Configuration and Environment
  - Centralized via Config class with validation and environment loading.
  - Defines Telegram token, Supabase credentials, OpenRouter API endpoint and model, CEFR levels, skills, languages, timeouts, and conversation history limits.
- Event Pipeline
  - Application builder constructs the bot, registers handlers, error handler, and logging.
  - Updates are routed to handlers based on filter patterns and conversation states.
- Handler Pattern
  - CommandHandler and CallbackQueryHandler instances export handler objects.
  - ConversationHandler manages multi-step flows for learning and exams.
- Service Layer
  - DatabaseService: Supabase client wrapper for CRUD operations.
  - AITutorService: OpenRouter API integration for tutoring, evaluation, and dynamic question generation.
  - ExamEngine: Question selection, scoring, and level recommendation.
  - SpeechService: faster-whisper integration for voice transcription.
- Middleware
  - require_subscription and require_subscription_callback enforce subscription checks and provide warnings.
- Utilities
  - Keyboards and Formatters provide consistent UI and messaging.

**Section sources**
- [bot/config.py](file://bot/config.py#L10-L60)
- [bot/main.py](file://bot/main.py#L60-L101)
- [bot/handlers/start.py](file://bot/handlers/start.py#L177-L181)
- [bot/handlers/learn.py](file://bot/handlers/learn.py#L291-L314)
- [bot/handlers/exam.py](file://bot/handlers/exam.py#L488-L522)
- [bot/services/database.py](file://bot/services/database.py#L16-L21)
- [bot/services/ai_tutor.py](file://bot/services/ai_tutor.py#L19-L32)
- [bot/services/exam_engine.py](file://bot/services/exam_engine.py#L15-L27)
- [bot/services/speech.py](file://bot/services/speech.py#L21-L44)
- [bot/middleware/subscription.py](file://bot/middleware/subscription.py#L47-L101)

## Architecture Overview
The system follows an event-driven architecture:
- Telegram sends Update events (commands, messages, callbacks).
- The Application routes updates to registered handlers.
- Handlers delegate to services for external integrations and persistence.
- Middleware validates access before invoking handlers.
- Responses are sent back to Telegram via the bot API.

```mermaid
sequenceDiagram
participant TG as "Telegram"
participant APP as "Application (bot/main.py)"
participant HAND as "Handlers (bot/handlers/*)"
participant MW as "Middleware (bot/middleware/subscription.py)"
participant SVC_DB as "DatabaseService (bot/services/database.py)"
participant SVC_AI as "AITutorService (bot/services/ai_tutor.py)"
participant SVC_SP as "SpeechService (bot/services/speech.py)"
TG->>APP : "Update (Command/Callback/Message)"
APP->>HAND : "Route to matching handler"
HAND->>MW : "Access control check (@require_subscription)"
alt "Subscription OK"
MW-->>HAND : "Proceed"
HAND->>SVC_DB : "Read/Write (users, lessons, progress, attempts)"
HAND->>SVC_AI : "Chat/Evaluate/Generate (OpenRouter)"
HAND->>SVC_SP : "Transcribe voice (optional)"
HAND-->>TG : "Reply/Inline Keyboard"
else "Subscription required"
MW-->>TG : "Alert/Error message"
end
```

**Diagram sources**
- [bot/main.py](file://bot/main.py#L60-L101)
- [bot/handlers/learn.py](file://bot/handlers/learn.py#L159-L232)
- [bot/handlers/exam.py](file://bot/handlers/exam.py#L317-L355)
- [bot/middleware/subscription.py](file://bot/middleware/subscription.py#L47-L101)
- [bot/services/database.py](file://bot/services/database.py#L16-L21)
- [bot/services/ai_tutor.py](file://bot/services/ai_tutor.py#L82-L153)
- [bot/services/speech.py](file://bot/services/speech.py#L83-L129)

## Detailed Component Analysis

### Event Pipeline and Handler Pattern
- Registration
  - Conversation handlers are registered first, followed by command and callback handlers.
  - Error handler logs exceptions and attempts to notify users.
  - A debug MessageHandler logs all incoming updates.
- Handler Types
  - Command handlers for /start, /help, /cancel, /menu, /progress.
  - Callback handlers for menu navigation, settings, and progress actions.
  - Conversation handlers for /learn and /exam manage multi-step flows with states and fallbacks.

```mermaid
flowchart TD
Start(["Update Received"]) --> CheckConv{"Is Conversation Update?"}
CheckConv --> |Yes| Conv["Dispatch to ConversationHandler"]
CheckConv --> |No| CheckCmd{"Is Command?"}
CheckCmd --> |Yes| Cmd["Dispatch to CommandHandler"]
CheckCmd --> |No| CheckCB{"Is Callback?"}
CheckCB --> |Yes| CB["Dispatch to CallbackQueryHandler"]
CheckCB --> |No| Log["Log/Ignore"]
Conv --> End(["Handled"])
Cmd --> End
CB --> End
Log --> End
```

**Diagram sources**
- [bot/main.py](file://bot/main.py#L60-L101)
- [bot/handlers/learn.py](file://bot/handlers/learn.py#L291-L314)
- [bot/handlers/exam.py](file://bot/handlers/exam.py#L488-L522)

**Section sources**
- [bot/main.py](file://bot/main.py#L60-L101)
- [bot/handlers/start.py](file://bot/handlers/start.py#L177-L181)
- [bot/handlers/menu.py](file://bot/handlers/menu.py#L180-L183)
- [bot/handlers/progress.py](file://bot/handlers/progress.py#L96-L99)

### Learning/Tutoring Flow (ConversationHandler)
- Entry points: /learn command and skill selection callbacks.
- States:
  - SELECTING_SKILL: choose a skill (conversation, grammar, lesen, horen, schreiben, sprechen, vokabular).
  - IN_CONVERSATION: exchange messages with optional voice transcription.
- Behavior:
  - Validates subscription before proceeding.
  - Builds conversation context and forwards to AI tutor.
  - Saves conversation history and progress.
  - Ends session and persists results.

```mermaid
sequenceDiagram
participant U as "User"
participant H as "learn.py"
participant M as "require_subscription"
participant D as "DatabaseService"
participant A as "AITutorService"
participant S as "SpeechService"
U->>H : "/learn"
H->>M : "Check subscription"
alt "Active"
M-->>H : "OK"
H->>D : "Load user data, weak areas"
H->>U : "Skill selection"
U->>H : "Skill selected"
H->>U : "Welcome + instructions"
loop "Conversation Loop"
U->>H : "Text or Voice"
alt "Voice"
H->>S : "Transcribe"
S-->>H : "Text"
end
H->>A : "Chat with context"
A-->>H : "Response"
H->>D : "Save conversation"
H-->>U : "Response + warning"
end
H->>D : "Save progress"
H-->>U : "Session ended"
else "Not Active"
M-->>U : "Error message"
end
```

**Diagram sources**
- [bot/handlers/learn.py](file://bot/handlers/learn.py#L30-L156)
- [bot/handlers/learn.py](file://bot/handlers/learn.py#L159-L232)
- [bot/middleware/subscription.py](file://bot/middleware/subscription.py#L47-L101)
- [bot/services/database.py](file://bot/services/database.py#L300-L344)
- [bot/services/ai_tutor.py](file://bot/services/ai_tutor.py#L82-L153)
- [bot/services/speech.py](file://bot/services/speech.py#L83-L129)

**Section sources**
- [bot/handlers/learn.py](file://bot/handlers/learn.py#L291-L314)

### Exam Flow (ConversationHandler)
- Entry points: /exam command and exam type selection.
- States:
  - SELECTING_EXAM: choose exam type (lesen, horen, schreiben, sprechen, vokabular).
  - ANSWERING_OBJECTIVE: MCQ flow with next/submit.
  - WRITING_RESPONSE: collect writing input until submit.
  - SPEAKING_RESPONSE: collect voice or text input until submit.
- Behavior:
  - Validates subscription.
  - Loads questions from DB or generates via AI.
  - Evaluates writing/speaking submissions with AI.
  - Persists exam attempts and progress.

```mermaid
sequenceDiagram
participant U as "User"
participant H as "exam.py"
participant M as "require_subscription"
participant D as "DatabaseService"
participant E as "ExamEngine"
participant A as "AITutorService"
U->>H : "/exam"
H->>M : "Check subscription"
alt "Active"
M-->>H : "OK"
H->>D : "Create exam attempt"
H->>E : "Get questions (DB or AI)"
alt "Objective"
H->>U : "Show question"
U->>H : "Answer"
H->>E : "Check answer"
H-->>U : "Feedback"
else "Writing/Speaking"
H->>U : "Prompt + instructions"
U->>H : "Text/Voice"
H->>A : "Evaluate"
A-->>H : "Evaluation"
H->>D : "Update attempt + progress"
H-->>U : "Results"
end
else "Not Active"
M-->>U : "Error message"
end
```

**Diagram sources**
- [bot/handlers/exam.py](file://bot/handlers/exam.py#L31-L123)
- [bot/handlers/exam.py](file://bot/handlers/exam.py#L125-L215)
- [bot/handlers/exam.py](file://bot/handlers/exam.py#L218-L292)
- [bot/handlers/exam.py](file://bot/handlers/exam.py#L358-L416)
- [bot/middleware/subscription.py](file://bot/middleware/subscription.py#L47-L101)
- [bot/services/database.py](file://bot/services/database.py#L348-L417)
- [bot/services/exam_engine.py](file://bot/services/exam_engine.py#L29-L65)
- [bot/services/ai_tutor.py](file://bot/services/ai_tutor.py#L154-L325)

**Section sources**
- [bot/handlers/exam.py](file://bot/handlers/exam.py#L488-L522)

### Middleware Pattern: Access Control
- Decorators:
  - require_subscription: Enforces subscription for commands and messages.
  - require_subscription_callback: Enforces subscription for inline keyboard actions.
- Subscription Checks:
  - Validates presence, expiration, and near-expiration status.
  - Stores status in user_data for downstream handlers.
  - Provides warning messages for expiring subscriptions.

```mermaid
flowchart TD
A["Incoming Update"] --> B["Extract user_id"]
B --> C{"Status?"}
C --> |No subscription| D["Reply: no subscription"]
C --> |Expired| E["Reply: expired"]
C --> |Active| F["Store status in context.user_data"]
F --> G["Call original handler"]
D --> H(["Exit"])
E --> H
G --> H
```

**Diagram sources**
- [bot/middleware/subscription.py](file://bot/middleware/subscription.py#L21-L44)
- [bot/middleware/subscription.py](file://bot/middleware/subscription.py#L47-L101)
- [bot/middleware/subscription.py](file://bot/middleware/subscription.py#L104-L137)

**Section sources**
- [bot/middleware/subscription.py](file://bot/middleware/subscription.py#L47-L101)

### Service Layer Patterns
- DatabaseService
  - Encapsulates Supabase client initialization and operations.
  - Provides user, lesson, exam question, progress, conversation history, and exam attempt management.
- AITutorService
  - Integrates OpenRouter API for tutoring, evaluations, and dynamic question generation.
  - Manages system prompts and message history limits.
- ExamEngine
  - Orchestrates question retrieval (DB or AI-generated) and scoring logic.
  - Computes weighted scores and level recommendations.
- SpeechService
  - Optional voice transcription using faster-whisper with Telegram voice files.

```mermaid
classDiagram
class DatabaseService {
+get_user(user_id)
+create_user(...)
+update_user(...)
+check_subscription(user_id)
+get_lessons(level, skill, limit)
+get_exam_questions(level, exam_type, limit, diffRange)
+save_progress(user_id, skill, activity, score, weak_areas)
+save_conversation(user_id, session_id, role, content)
+create_exam_attempt(user_id, exam_type, level)
+update_exam_attempt(attempt_id, answers, score, is_completed)
+get_user_progress(user_id, skill, limit)
+get_user_statistics(user_id)
}
class AITutorService {
+chat(user_message, conversation_history, level, preferred_lang, skill_focus, weak_areas)
+evaluate_writing(user_text, prompt, level, rubric)
+evaluate_speaking(transcribed_text, prompt, level)
+generate_exam_question(level, exam_type, topic)
}
class ExamEngine {
+get_exam_questions(level, exam_type, count)
+calculate_score(answers, exam_type)
+calculate_weighted_score(section_scores)
+check_answer(question, user_answer)
+get_level_recommendation(current_level, average_score)
}
class SpeechService {
+is_available bool
+transcribe_audio(audio_path, language)
+transcribe_telegram_voice(voice_file, bot)
+get_status_message()
}
DatabaseService <.. AITutorService : "used by"
DatabaseService <.. ExamEngine : "used by"
DatabaseService <.. SpeechService : "not used"
```

**Diagram sources**
- [bot/services/database.py](file://bot/services/database.py#L16-L422)
- [bot/services/ai_tutor.py](file://bot/services/ai_tutor.py#L19-L451)
- [bot/services/exam_engine.py](file://bot/services/exam_engine.py#L15-L211)
- [bot/services/speech.py](file://bot/services/speech.py#L21-L140)

**Section sources**
- [bot/services/database.py](file://bot/services/database.py#L16-L422)
- [bot/services/ai_tutor.py](file://bot/services/ai_tutor.py#L19-L451)
- [bot/services/exam_engine.py](file://bot/services/exam_engine.py#L15-L211)
- [bot/services/speech.py](file://bot/services/speech.py#L21-L140)

## Dependency Analysis
- Internal Dependencies
  - Handlers depend on DatabaseService, AITutorService, SpeechService, and middleware.
  - Learn and exam handlers depend on ExamEngine for question management.
- External Dependencies
  - python-telegram-bot: Event pipeline and update handling.
  - supabase: PostgreSQL persistence.
  - httpx: Async HTTP client for OpenRouter API.
  - python-dotenv: Environment variable loading.
  - faster-whisper/pydub: Optional voice transcription.

```mermaid
graph LR
Main["bot/main.py"] --> Handlers["bot/handlers/*"]
Handlers --> DB["bot/services/database.py"]
Handlers --> AITutor["bot/services/ai_tutor.py"]
Handlers --> Speech["bot/services/speech.py"]
Handlers --> ExamEngine["bot/services/exam_engine.py"]
DB --> Supabase["Supabase"]
AITutor --> OpenRouter["OpenRouter API"]
Speech --> Whisper["faster-whisper"]
Main --> TGBot["python-telegram-bot"]
DB --> Supabase
AITutor --> httpx["httpx"]
Main --> dotenv["python-dotenv"]
```

**Diagram sources**
- [bot/main.py](file://bot/main.py#L12-L19)
- [requirements.txt](file://requirements.txt#L1-L7)
- [bot/services/database.py](file://bot/services/database.py#L10-L21)
- [bot/services/ai_tutor.py](file://bot/services/ai_tutor.py#L5-L31)
- [bot/services/speech.py](file://bot/services/speech.py#L12-L44)

**Section sources**
- [requirements.txt](file://requirements.txt#L1-L7)
- [bot/main.py](file://bot/main.py#L12-L19)

## Performance Considerations
- Asynchronous Operations
  - All external calls use async HTTP clients and database operations to avoid blocking the event loop.
- Conversation Context Limits
  - AI chat uses a capped conversation history to control token usage and latency.
- Speech Transcription
  - Optional and offloaded to CPU; gracefully degrades when unavailable.
- Database Indexes
  - Schema includes indexes on frequently queried columns to optimize reads.

[No sources needed since this section provides general guidance]

## Troubleshooting Guide
- Configuration Validation
  - Missing environment variables cause immediate startup failure with a descriptive error.
- Error Handler
  - Logs exceptions and attempts to notify users on message updates.
- Subscription Issues
  - Handlers decorated with require_subscription reply with actionable messages for missing/expired subscriptions.
- Logging
  - Debug handler logs update IDs and message/callback payloads for diagnostics.

**Section sources**
- [bot/config.py](file://bot/config.py#L40-L56)
- [bot/main.py](file://bot/main.py#L45-L58)
- [bot/main.py](file://bot/main.py#L86-L94)
- [bot/middleware/subscription.py](file://bot/middleware/subscription.py#L68-L89)

## Conclusion
FebEGLS-bot demonstrates a clean, modular, and extensible architecture:
- Event-driven updates are routed through clearly defined handlers.
- The service layer isolates external dependencies behind cohesive interfaces.
- Middleware ensures access control without cluttering handler logic.
- The system is designed for maintainability, testability, and scalability, with explicit boundaries between Telegram, handlers, services, and external systems.