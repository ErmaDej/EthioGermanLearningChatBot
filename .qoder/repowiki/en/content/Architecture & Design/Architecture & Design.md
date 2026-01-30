# Architecture & Design

<cite>
**Referenced Files in This Document**
- [bot/main.py](file://bot/main.py)
- [bot/config.py](file://bot/config.py)
- [bot/handlers/__init__.py](file://bot/handlers/__init__.py)
- [bot/handlers/start.py](file://bot/handlers/start.py)
- [bot/handlers/menu.py](file://bot/handlers/menu.py)
- [bot/handlers/learn.py](file://bot/handlers/learn.py)
- [bot/handlers/exam.py](file://bot/handlers/exam.py)
- [bot/handlers/progress.py](file://bot/handlers/progress.py)
- [bot/middleware/__init__.py](file://bot/middleware/__init__.py)
- [bot/middleware/subscription.py](file://bot/middleware/subscription.py)
- [bot/services/__init__.py](file://bot/services/__init__.py)
- [bot/services/database.py](file://bot/services/database.py)
- [bot/services/ai_tutor.py](file://bot/services/ai_tutor.py)
- [bot/services/exam_engine.py](file://bot/services/exam_engine.py)
- [bot/services/speech.py](file://bot/services/speech.py)
- [bot/utils/formatters.py](file://bot/utils/formatters.py)
- [bot/utils/keyboards.py](file://bot/utils/keyboards.py)
- [prompts/tutor_system.txt](file://prompts/tutor_system.txt)
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
10. [Appendices](#appendices)

## Introduction
This document describes the system architecture of the FebEGLS-bot, an event-driven Telegram bot implementing a Handler pattern for command processing, a Service layer for external integrations, and a Middleware pattern for access control. The bot integrates with the Telegram Bot API, OpenRouter, Supabase, and faster-whisper. It emphasizes modularity, separation of concerns, and clear component boundaries to enable scalability, maintainability, and robust error handling.

## Project Structure
The project is organized into distinct layers:
- Entry point initializes the Telegram Application, registers handlers, and sets up logging.
- Handlers encapsulate Telegram command and callback logic, delegating business logic to Services and Utilities.
- Middleware enforces cross-cutting access control policies.
- Services abstract external integrations (database, AI, speech, exam generation).
- Utilities provide shared formatting and keyboard builders.
- Configuration centralizes environment variables and constants.

```mermaid
graph TB
subgraph "Entry Point"
M["bot/main.py"]
end
subgraph "Handlers"
HS["handlers/start.py"]
HM["handlers/menu.py"]
HL["handlers/learn.py"]
HE["handlers/exam.py"]
HP["handlers/progress.py"]
end
subgraph "Middleware"
MS["middleware/subscription.py"]
end
subgraph "Services"
SD["services/database.py"]
SA["services/ai_tutor.py"]
SE["services/exam_engine.py"]
SS["services/speech.py"]
end
subgraph "Utilities"
UF["utils/formatters.py"]
UK["utils/keyboards.py"]
end
CFG["bot/config.py"]
M --> HS
M --> HM
M --> HL
M --> HE
M --> HP
HS --> SD
HM --> SD
HM --> MS
HL --> SD
HL --> SA
HL --> SS
HE --> SD
HE --> SA
HE --> SE
HE --> SS
HP --> SD
HP --> MS
HS --> UF
HM --> UF
HL --> UF
HE --> UF
HP --> UF
HS --> UK
HM --> UK
HL --> UK
HE --> UK
HP --> UK
CFG --> SD
CFG --> SA
CFG --> SE
CFG --> SS
```

**Diagram sources**
- [bot/main.py](file://bot/main.py#L60-L88)
- [bot/handlers/start.py](file://bot/handlers/start.py#L16-L168)
- [bot/handlers/menu.py](file://bot/handlers/menu.py#L17-L183)
- [bot/handlers/learn.py](file://bot/handlers/learn.py#L30-L314)
- [bot/handlers/exam.py](file://bot/handlers/exam.py#L31-L522)
- [bot/handlers/progress.py](file://bot/handlers/progress.py#L17-L98)
- [bot/middleware/subscription.py](file://bot/middleware/subscription.py#L47-L137)
- [bot/services/database.py](file://bot/services/database.py#L16-L415)
- [bot/services/ai_tutor.py](file://bot/services/ai_tutor.py#L19-L450)
- [bot/services/exam_engine.py](file://bot/services/exam_engine.py#L15-L210)
- [bot/services/speech.py](file://bot/services/speech.py#L21-L139)
- [bot/utils/formatters.py](file://bot/utils/formatters.py)
- [bot/utils/keyboards.py](file://bot/utils/keyboards.py)
- [bot/config.py](file://bot/config.py#L10-L59)

**Section sources**
- [bot/main.py](file://bot/main.py#L60-L88)
- [bot/config.py](file://bot/config.py#L10-L59)
- [bot/handlers/__init__.py](file://bot/handlers/__init__.py#L1-L19)
- [bot/middleware/__init__.py](file://bot/middleware/__init__.py#L1-L4)
- [bot/services/__init__.py](file://bot/services/__init__.py#L1-L7)

## Core Components
- Handler pattern: Telegram commands and callbacks are implemented as discrete handlers that orchestrate user sessions and delegate to Services and Utilities.
- Service layer: Encapsulates external integrations behind typed services with clear responsibilities:
  - DatabaseService: Supabase operations for users, lessons, progress, conversations, and exam attempts.
  - AITutorService: OpenRouter integration for tutoring, evaluations, and dynamic question generation.
  - ExamEngine: Question selection, scoring, and level recommendations.
  - SpeechService: faster-whisper integration for voice transcription.
- Middleware pattern: Access control enforced centrally via decorators that validate subscriptions and inject warnings into user contexts.
- Utilities: Shared formatting and keyboard builders used across handlers.

**Section sources**
- [bot/handlers/start.py](file://bot/handlers/start.py#L16-L168)
- [bot/handlers/menu.py](file://bot/handlers/menu.py#L17-L183)
- [bot/handlers/learn.py](file://bot/handlers/learn.py#L30-L314)
- [bot/handlers/exam.py](file://bot/handlers/exam.py#L31-L522)
- [bot/handlers/progress.py](file://bot/handlers/progress.py#L17-L98)
- [bot/middleware/subscription.py](file://bot/middleware/subscription.py#L47-L156)
- [bot/services/database.py](file://bot/services/database.py#L16-L415)
- [bot/services/ai_tutor.py](file://bot/services/ai_tutor.py#L19-L450)
- [bot/services/exam_engine.py](file://bot/services/exam_engine.py#L15-L210)
- [bot/services/speech.py](file://bot/services/speech.py#L21-L139)
- [bot/utils/formatters.py](file://bot/utils/formatters.py)
- [bot/utils/keyboards.py](file://bot/utils/keyboards.py)

## Architecture Overview
The system follows an event-driven architecture powered by python-telegram-bot. The Application polls for updates and routes them to registered handlers. Handlers coordinate user sessions, maintain conversational state in user_data, and delegate to Services for external operations. Middleware intercepts requests to enforce access control. Logging is configured globally, and configuration is centralized.

```mermaid
sequenceDiagram
participant TGB as "Telegram Bot API"
participant APP as "Application (bot/main.py)"
participant HD as "Handler (e.g., handlers/learn.py)"
participant MW as "Middleware (middleware/subscription.py)"
participant SVC as "Service (e.g., services/ai_tutor.py)"
participant DB as "Supabase (services/database.py)"
participant OR as "OpenRouter API"
participant WH as "faster-whisper (services/speech.py)"
TGB->>APP : "Update (Command/Callback/Message)"
APP->>HD : "Dispatch to matching handler"
HD->>MW : "Apply access control (if decorated)"
MW-->>HD : "Allow or block"
alt "Needs AI"
HD->>SVC : "Call AI service"
SVC->>OR : "POST /chat/completions"
OR-->>SVC : "Response"
SVC-->>HD : "AI response"
else "Needs DB"
HD->>DB : "Read/Write operations"
DB-->>HD : "Data"
else "Voice processing"
HD->>WH : "Transcribe voice"
WH-->>HD : "Text"
end
HD-->>TGB : "Reply/Inline Keyboard"
```

**Diagram sources**
- [bot/main.py](file://bot/main.py#L60-L88)
- [bot/handlers/learn.py](file://bot/handlers/learn.py#L159-L232)
- [bot/middleware/subscription.py](file://bot/middleware/subscription.py#L47-L101)
- [bot/services/ai_tutor.py](file://bot/services/ai_tutor.py#L82-L153)
- [bot/services/database.py](file://bot/services/database.py#L24-L103)
- [bot/services/speech.py](file://bot/services/speech.py#L83-L129)

## Detailed Component Analysis

### Handler Pattern: Telegram Command Processing
Handlers register Telegram CommandHandler and CallbackQueryHandler entries and manage conversational flows. They:
- Validate user state and subscription status.
- Interact with Services for data and AI operations.
- Use Utilities for consistent formatting and keyboard layouts.
- Manage session state in user_data for multi-step flows.

```mermaid
classDiagram
class LearnHandler {
+learn_command(update, context)
+skill_selected(update, context)
+handle_message(update, context)
+end_conversation(update, context)
+cancel_conversation(update, context)
}
class ExamHandler {
+exam_command(update, context)
+exam_selected(update, context)
+show_objective_question(query, context)
+handle_objective_answer(update, context)
+next_question(update, context)
+start_subjective_exam(query, context)
+handle_writing_input(update, context)
+handle_speaking_input(update, context)
+submit_subjective(update, context)
+show_exam_results(query, context)
+cancel_exam(update, context)
}
class StartHandler {
+_start_command(update, context)
+registration_level_callback(update, context)
+registration_lang_callback(update, context)
+_help_command(update, context)
+_cancel_command(update, context)
}
class MenuHandler {
+menu_command(update, context)
+menu_callback(update, context)
+settings_callback(update, context)
}
class ProgressHandler {
+progress_command(update, context)
+progress_callback(update, context)
}
LearnHandler --> DatabaseService : "reads/writes"
LearnHandler --> AITutorService : "chat"
LearnHandler --> SpeechService : "transcribe"
ExamHandler --> DatabaseService : "attempts/results"
ExamHandler --> AITutorService : "evaluations"
ExamHandler --> ExamEngine : "questions"
ExamHandler --> SpeechService : "transcribe"
StartHandler --> DatabaseService : "user CRUD"
MenuHandler --> DatabaseService : "stats/subscriptions"
ProgressHandler --> DatabaseService : "stats/history"
```

**Diagram sources**
- [bot/handlers/learn.py](file://bot/handlers/learn.py#L30-L314)
- [bot/handlers/exam.py](file://bot/handlers/exam.py#L31-L522)
- [bot/handlers/start.py](file://bot/handlers/start.py#L16-L168)
- [bot/handlers/menu.py](file://bot/handlers/menu.py#L17-L183)
- [bot/handlers/progress.py](file://bot/handlers/progress.py#L17-L98)
- [bot/services/database.py](file://bot/services/database.py#L16-L415)
- [bot/services/ai_tutor.py](file://bot/services/ai_tutor.py#L19-L450)
- [bot/services/exam_engine.py](file://bot/services/exam_engine.py#L15-L210)
- [bot/services/speech.py](file://bot/services/speech.py#L21-L139)

**Section sources**
- [bot/handlers/learn.py](file://bot/handlers/learn.py#L26-L314)
- [bot/handlers/exam.py](file://bot/handlers/exam.py#L28-L522)
- [bot/handlers/start.py](file://bot/handlers/start.py#L16-L168)
- [bot/handlers/menu.py](file://bot/handlers/menu.py#L17-L183)
- [bot/handlers/progress.py](file://bot/handlers/progress.py#L17-L98)

### Service Layer: External Integrations
Services encapsulate external dependencies and provide a stable interface for Handlers.

- DatabaseService (Supabase):
  - User lifecycle, subscriptions, lessons, progress, conversations, and exam attempts.
  - Centralized error logging and safe defaults.
- AITutorService (OpenRouter):
  - Chat tutoring with configurable system prompts and conversation history.
  - Writing and speaking evaluations returning structured JSON.
  - Dynamic question generation for exams.
- ExamEngine:
  - Question retrieval with fallback to AI generation.
  - Scoring and weak-area analysis.
- SpeechService (faster-whisper):
  - Voice transcription with graceful degradation when unavailable.

```mermaid
classDiagram
class DatabaseService {
+get_user(user_id)
+create_user(...)
+update_user(...)
+check_subscription(user_id)
+get_lessons(level, skill, limit)
+get_exam_questions(level, exam_type, limit)
+save_progress(...)
+get_user_progress(user_id, skill, limit)
+get_user_statistics(user_id)
+save_conversation(user_id, session_id, role, content)
+create_exam_attempt(user_id, exam_type, level)
+update_exam_attempt(attempt_id, answers, score, is_completed)
+get_exam_attempts(user_id, exam_type, limit)
}
class AITutorService {
+chat(user_message, conversation_history, level, preferred_lang, skill_focus, weak_areas)
+evaluate_writing(user_text, prompt, level)
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
DatabaseService <.. LearnHandler : "used by"
DatabaseService <.. ExamHandler : "used by"
DatabaseService <.. MenuHandler : "used by"
DatabaseService <.. ProgressHandler : "used by"
AITutorService <.. LearnHandler : "used by"
AITutorService <.. ExamHandler : "used by"
AITutorService <.. ExamEngine : "fallback questions"
ExamEngine <.. ExamHandler : "used by"
SpeechService <.. LearnHandler : "used by"
SpeechService <.. ExamHandler : "used by"
```

**Diagram sources**
- [bot/services/database.py](file://bot/services/database.py#L16-L415)
- [bot/services/ai_tutor.py](file://bot/services/ai_tutor.py#L19-L450)
- [bot/services/exam_engine.py](file://bot/services/exam_engine.py#L15-L210)
- [bot/services/speech.py](file://bot/services/speech.py#L21-L139)
- [bot/handlers/learn.py](file://bot/handlers/learn.py#L159-L232)
- [bot/handlers/exam.py](file://bot/handlers/exam.py#L358-L416)

**Section sources**
- [bot/services/database.py](file://bot/services/database.py#L16-L415)
- [bot/services/ai_tutor.py](file://bot/services/ai_tutor.py#L19-L450)
- [bot/services/exam_engine.py](file://bot/services/exam_engine.py#L15-L210)
- [bot/services/speech.py](file://bot/services/speech.py#L21-L139)

### Middleware Pattern: Access Control
The subscription middleware enforces access control for paid features:
- Decorators wrap handlers to check subscription status before execution.
- Subscription status and expiry are injected into user_data for downstream use.
- Special exemptions apply to specific commands.

```mermaid
flowchart TD
Start(["Handler Entry"]) --> CheckUser["Check effective_user"]
CheckUser --> GetUser["Check subscription status"]
GetUser --> Status{"Status"}
Status --> |No subscription| Block1["Reply no-subscription message<br/>Return"]
Status --> |Expired| Block2["Reply expired message<br/>Return"]
Status --> |Active| Allow["Store status in user_data<br/>Update last_active"]
Allow --> Next["Call original handler"]
Block1 --> End(["Exit"])
Block2 --> End
Next --> End
```

**Diagram sources**
- [bot/middleware/subscription.py](file://bot/middleware/subscription.py#L47-L101)

**Section sources**
- [bot/middleware/subscription.py](file://bot/middleware/subscription.py#L17-L156)
- [bot/handlers/menu.py](file://bot/handlers/menu.py#L17-L183)
- [bot/handlers/progress.py](file://bot/handlers/progress.py#L17-L98)
- [bot/handlers/learn.py](file://bot/handlers/learn.py#L30-L50)

### Event-Driven Data Flow
The bot’s runtime is driven by Telegram updates. Handlers receive updates, manage state, and call Services. Responses are sent back to users with inline keyboards and formatted text.

```mermaid
sequenceDiagram
participant U as "User"
participant T as "Telegram Bot API"
participant A as "Application"
participant H as "Handler"
participant S as "Service"
participant X as "External API"
U->>T : "Send message/command"
T->>A : "Deliver Update"
A->>H : "Route to handler"
H->>S : "Invoke service method"
S->>X : "HTTP request"
X-->>S : "Response"
S-->>H : "Processed data"
H-->>T : "Edit/Reply message"
T-->>U : "Rendered response"
```

**Diagram sources**
- [bot/main.py](file://bot/main.py#L60-L88)
- [bot/handlers/learn.py](file://bot/handlers/learn.py#L205-L232)
- [bot/services/ai_tutor.py](file://bot/services/ai_tutor.py#L127-L145)

## Dependency Analysis
- Handlers depend on Services and Utilities; Services depend on configuration and external APIs.
- Middleware depends on Services for subscription checks.
- Configuration is consumed by Services and Handlers to configure clients and constants.
- There is no circular dependency among modules; dependencies are unidirectional from Handlers → Services → External APIs.

```mermaid
graph LR
HStart["handlers/start.py"] --> DB["services/database.py"]
HMenu["handlers/menu.py"] --> DB
HMenu --> MW["middleware/subscription.py"]
HLearn["handlers/learn.py"] --> DB
HLearn --> AIT["services/ai_tutor.py"]
HLearn --> SP["services/speech.py"]
HExam["handlers/exam.py"] --> DB
HExam --> AIT
HExam --> EE["services/exam_engine.py"]
HExam --> SP
HProg["handlers/progress.py"] --> DB
HProg --> MW
CFG["bot/config.py"] --> DB
CFG --> AIT
CFG --> EE
CFG --> SP
AIT --> PROM["prompts/tutor_system.txt"]
```

**Diagram sources**
- [bot/handlers/start.py](file://bot/handlers/start.py#L9-L11)
- [bot/handlers/menu.py](file://bot/handlers/menu.py#L9-L12)
- [bot/handlers/learn.py](file://bot/handlers/learn.py#L17-L22)
- [bot/handlers/exam.py](file://bot/handlers/exam.py#L17-L23)
- [bot/handlers/progress.py](file://bot/handlers/progress.py#L9-L12)
- [bot/middleware/subscription.py](file://bot/middleware/subscription.py#L13)
- [bot/services/database.py](file://bot/services/database.py#L10-L11)
- [bot/services/ai_tutor.py](file://bot/services/ai_tutor.py#L11)
- [bot/services/exam_engine.py](file://bot/services/exam_engine.py#L9-L10)
- [bot/services/speech.py](file://bot/services/speech.py#L14-L18)
- [bot/config.py](file://bot/config.py#L17-L23)
- [prompts/tutor_system.txt](file://prompts/tutor_system.txt)

**Section sources**
- [bot/handlers/__init__.py](file://bot/handlers/__init__.py#L1-L19)
- [bot/middleware/__init__.py](file://bot/middleware/__init__.py#L1-L4)
- [bot/services/__init__.py](file://bot/services/__init__.py#L1-L7)

## Performance Considerations
- Asynchronous design: Handlers and Services use async/await to minimize blocking and improve concurrency under Telegram’s polling model.
- External API timeouts: AI and database operations specify timeouts to prevent stalls; failures are handled gracefully with user-friendly messages.
- Conversation history limits: AI requests truncate conversation history to reduce latency and cost.
- Speech transcription availability: Graceful degradation when faster-whisper is unavailable; handlers adapt messaging accordingly.
- Logging: Global logging reduces overhead and improves observability; noisy third-party loggers are suppressed.

[No sources needed since this section provides general guidance]

## Troubleshooting Guide
- Error handling:
  - Global error handler logs exceptions and attempts to notify users.
  - Service methods catch and log exceptions, returning safe default responses.
- Subscription issues:
  - Middleware blocks unauthorized access and informs users; handlers also check subscription before proceeding.
- Database connectivity:
  - Service methods return None or empty lists on failure; Handlers fall back to safe states.
- AI API failures:
  - Service methods return pre-defined fallback messages and log errors.
- Speech transcription:
  - Service logs warnings when unavailable; Handlers provide alternative input methods.

**Section sources**
- [bot/main.py](file://bot/main.py#L45-L58)
- [bot/services/database.py](file://bot/services/database.py#L29-L31)
- [bot/services/ai_tutor.py](file://bot/services/ai_tutor.py#L147-L152)
- [bot/middleware/subscription.py](file://bot/middleware/subscription.py#L68-L98)
- [bot/services/speech.py](file://bot/services/speech.py#L17-L18)

## Conclusion
FebEGLS-bot employs a clean, modular architecture leveraging the Handler, Service, and Middleware patterns. The event-driven design, centralized configuration, and robust error handling enable scalable development and reliable operation across Telegram, OpenRouter, Supabase, and speech processing integrations. The separation of concerns ensures maintainability and facilitates future enhancements.

## Appendices
- Configuration keys and defaults are validated at import time and consumed by Services and Handlers.
- Utilities provide reusable UI components and formatting helpers to keep Handlers concise and consistent.

**Section sources**
- [bot/config.py](file://bot/config.py#L40-L59)
- [bot/utils/formatters.py](file://bot/utils/formatters.py)
- [bot/utils/keyboards.py](file://bot/utils/keyboards.py)