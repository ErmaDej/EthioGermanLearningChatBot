# Exam Simulation Mechanics

<cite>
**Referenced Files in This Document**
- [bot/handlers/exam.py](file://bot/handlers/exam.py)
- [bot/services/exam_engine.py](file://bot/services/exam_engine.py)
- [bot/services/database.py](file://bot/services/database.py)
- [bot/services/ai_tutor.py](file://bot/services/ai_tutor.py)
- [bot/services/speech.py](file://bot/services/speech.py)
- [bot/utils/keyboards.py](file://bot/utils/keyboards.py)
- [bot/utils/formatters.py](file://bot/utils/formatters.py)
- [bot/middleware/subscription.py](file://bot/middleware/subscription.py)
- [bot/main.py](file://bot/main.py)
- [bot/config.py](file://bot/config.py)
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
This document explains the exam simulation mechanics implemented in the EthioGerman Language School Telegram bot. It covers the conversation flow architecture, state management across five distinct states, the exam selection process, user data persistence via context.user_data, the ConversationHandler implementation, routing logic between objective and subjective exam types, exam attempt creation and tracking, and integration with the exam_engine for question retrieval. It also documents user interaction patterns, error handling scenarios, exam cancellation workflows, progress tracking, and session cleanup procedures.

## Project Structure
The exam simulation spans several modules:
- Handlers orchestrate user interactions and manage conversation states
- Services encapsulate business logic for database operations, AI evaluation, speech processing, and exam question generation/scoring
- Utilities provide consistent UI and messaging formatting
- Middleware enforces subscription-based access control
- Configuration centralizes environment variables and constants

```mermaid
graph TB
subgraph "Handlers"
HExam["bot/handlers/exam.py"]
end
subgraph "Services"
SDB["bot/services/database.py"]
SEng["bot/services/exam_engine.py"]
SAI["bot/services/ai_tutor.py"]
SSpeech["bot/services/speech.py"]
end
subgraph "Utilities"
UKey["bot/utils/keyboards.py"]
UFmt["bot/utils/formatters.py"]
end
subgraph "Middleware"
MSub["bot/middleware/subscription.py"]
end
subgraph "Core"
Main["bot/main.py"]
Cfg["bot/config.py"]
end
DBSchema["database_setup.sql"]
Main --> HExam
HExam --> SDB
HExam --> SEng
HExam --> SAI
HExam --> SSpeech
HExam --> UKey
HExam --> UFmt
HExam --> MSub
SEng --> SDB
SEng --> SAI
SDB --> DBSchema
```

**Diagram sources**
- [bot/handlers/exam.py](file://bot/handlers/exam.py#L1-L523)
- [bot/services/database.py](file://bot/services/database.py#L1-L416)
- [bot/services/exam_engine.py](file://bot/services/exam_engine.py#L1-L211)
- [bot/services/ai_tutor.py](file://bot/services/ai_tutor.py#L1-L451)
- [bot/services/speech.py](file://bot/services/speech.py#L1-L140)
- [bot/utils/keyboards.py](file://bot/utils/keyboards.py#L1-L183)
- [bot/utils/formatters.py](file://bot/utils/formatters.py#L1-L300)
- [bot/middleware/subscription.py](file://bot/middleware/subscription.py#L1-L156)
- [bot/main.py](file://bot/main.py#L1-L93)
- [bot/config.py](file://bot/config.py#L1-L60)
- [database_setup.sql](file://database_setup.sql#L1-L84)

**Section sources**
- [bot/handlers/exam.py](file://bot/handlers/exam.py#L1-L523)
- [bot/main.py](file://bot/main.py#L1-L93)

## Core Components
- ConversationHandler manages five states: SELECTING_EXAM, ANSWERING_OBJECTIVE, WRITING_RESPONSE, SPEAKING_RESPONSE, REVIEWING_RESULTS
- Exam selection routes to either objective (MCQ) or subjective (writing/speaking) flows
- User data persistence via context.user_data stores exam metadata, current question index, answers, and attempt identifiers
- Database integration tracks user progress, exam attempts, and question sourcing
- AI-driven evaluation for writing and speaking tasks
- Speech transcription for voice-based speaking tasks

**Section sources**
- [bot/handlers/exam.py](file://bot/handlers/exam.py#L27-L523)
- [bot/services/database.py](file://bot/services/database.py#L342-L412)
- [bot/services/ai_tutor.py](file://bot/services/ai_tutor.py#L154-L325)
- [bot/services/speech.py](file://bot/services/speech.py#L83-L129)

## Architecture Overview
The exam flow begins with the /exam command or exam menu selection. The handler validates subscription, initializes user data, retrieves questions from the exam engine (with AI fallback), creates an exam attempt, and routes to the appropriate state machine branch. Objective exams iterate through MCQ questions, while subjective exams collect text or voice responses and evaluate them via AI.

```mermaid
sequenceDiagram
participant User as "User"
participant Bot as "Telegram Bot"
participant Handler as "Exam Handler"
participant Engine as "Exam Engine"
participant DB as "Database Service"
participant AI as "AI Tutor"
participant Speech as "Speech Service"
User->>Bot : "/exam" or "Take Practice Exam"
Bot->>Handler : exam_command()
Handler->>DB : check_subscription(user_id)
DB-->>Handler : (active?, expiry)
alt inactive/expired
Handler-->>User : "Subscription required"
Handler-->>Bot : ConversationHandler.END
else active
Handler-->>User : "Exam menu"
Handler-->>Bot : SELECTING_EXAM
end
User->>Bot : Select exam type
Bot->>Handler : exam_selected()
Handler->>DB : get_user(user_id)
DB-->>Handler : user_data
Handler->>Engine : get_exam_questions(level, exam_type)
Engine->>DB : get_random_exam_questions(level, exam_type, count)
DB-->>Engine : questions
Engine-->>Handler : questions
Handler->>DB : create_exam_attempt(user_id, exam_type, level)
DB-->>Handler : attempt_id
alt objective exam
Handler-->>Bot : show_objective_question()
loop MCQ iteration
User->>Bot : Answer option
Bot->>Handler : handle_objective_answer()
Handler->>Engine : check_answer(question, user_answer)
Engine-->>Handler : (is_correct, explanation)
Handler-->>User : Feedback + Next
end
Handler-->>Bot : show_exam_results()
Handler->>DB : update_exam_attempt(attempt_id, answers, score, is_completed=True)
Handler->>DB : save_progress(user_id, skill, activity_type, score, weak_areas)
Handler-->>Bot : ConversationHandler.END
else subjective exam
Handler-->>Bot : start_subjective_exam()
alt writing
User->>Bot : Text input (multiple messages)
Bot->>Handler : handle_writing_input()
Handler-->>User : Word count feedback
User->>Bot : Submit
Bot->>Handler : submit_subjective()
Handler->>AI : evaluate_writing(text, prompt, level)
AI-->>Handler : evaluation
else speaking
User->>Bot : Voice or Text input
Bot->>Handler : handle_speaking_input()
alt voice available
Handler->>Speech : transcribe_telegram_voice(voice, bot)
Speech-->>Handler : transcribed_text
else voice unavailable
Handler-->>User : "Type your response"
end
User->>Bot : Submit
Bot->>Handler : submit_subjective()
Handler->>AI : evaluate_speaking(transcribed_text, prompt, level)
AI-->>Handler : evaluation
end
Handler->>DB : update_exam_attempt(attempt_id, [{question_id, user_response, evaluation}], score, is_completed=True)
Handler->>DB : save_progress(user_id, skill, activity_type, score, suggestions[ : 3])
Handler-->>Bot : ConversationHandler.END
end
```

**Diagram sources**
- [bot/handlers/exam.py](file://bot/handlers/exam.py#L31-L523)
- [bot/services/exam_engine.py](file://bot/services/exam_engine.py#L29-L183)
- [bot/services/database.py](file://bot/services/database.py#L342-L412)
- [bot/services/ai_tutor.py](file://bot/services/ai_tutor.py#L154-L325)
- [bot/services/speech.py](file://bot/services/speech.py#L83-L129)

## Detailed Component Analysis

### ConversationHandler and States
The ConversationHandler coordinates the entire exam flow with five states:
- SELECTING_EXAM: Initial state for choosing exam type
- ANSWERING_OBJECTIVE: MCQ question display and answer handling
- WRITING_RESPONSE: Collecting written responses for writing tasks
- SPEAKING_RESPONSE: Collecting voice or typed responses for speaking tasks
- REVIEWING_RESULTS: Final score display and cleanup

Routing logic:
- Objective exams route to show_objective_question() and handle_objective_answer()
- Subjective exams route to start_subjective_exam(), then to either handle_writing_input() or handle_speaking_input(), followed by submit_subjective()

```mermaid
stateDiagram-v2
[*] --> SELECTING_EXAM
SELECTING_EXAM --> ANSWERING_OBJECTIVE : "Objective exam"
SELECTING_EXAM --> WRITING_RESPONSE : "Writing exam"
SELECTING_EXAM --> SPEAKING_RESPONSE : "Speaking exam"
ANSWERING_OBJECTIVE --> ANSWERING_OBJECTIVE : "Next question"
ANSWERING_OBJECTIVE --> REVIEWING_RESULTS : "All questions answered"
WRITING_RESPONSE --> WRITING_RESPONSE : "Add text"
WRITING_RESPONSE --> REVIEWING_RESULTS : "Submit"
SPEAKING_RESPONSE --> SPEAKING_RESPONSE : "Voice/Text input"
SPEAKING_RESPONSE --> REVIEWING_RESULTS : "Submit"
REVIEWING_RESULTS --> [*]
```

**Diagram sources**
- [bot/handlers/exam.py](file://bot/handlers/exam.py#L27-L523)

**Section sources**
- [bot/handlers/exam.py](file://bot/handlers/exam.py#L488-L523)

### Exam Selection and Routing Logic
- Subscription check occurs at the start of exam_command() and during exam_selected()
- Exam type extraction transforms callback data (e.g., "exam_lesen") into internal identifiers
- Routing branches:
  - Objective: lesen, horen, vokabular → ANSWERING_OBJECTIVE
  - Subjective: schreiben, sprechen → WRITING_RESPONSE/SPEAKING_RESPONSE
- Full mock exam is reserved for future implementation

**Section sources**
- [bot/handlers/exam.py](file://bot/handlers/exam.py#L31-L123)
- [bot/utils/keyboards.py](file://bot/utils/keyboards.py#L47-L62)

### Objective Exam Flow
- Question retrieval: exam_engine.get_exam_questions() pulls from database with AI fallback
- Question display: show_objective_question() formats text and passage, presents options
- Answer handling: handle_objective_answer() checks correctness, persists answer, advances to next question
- Results calculation: show_exam_results() computes score, updates attempt, saves progress, clears context

```mermaid
flowchart TD
Start(["Start Objective Exam"]) --> Init["Initialize user_data<br/>- exam_type, level<br/>- answers=[], current_question=0<br/>- questions, total_questions"]
Init --> Attempt["Create exam attempt<br/>store attempt_id"]
Attempt --> Loop{"More questions?"}
Loop --> |Yes| Display["Format question + options"]
Display --> Answer["Receive answer"]
Answer --> Check["Check answer via exam_engine"]
Check --> Store["Store answer in context.user_data.answers"]
Store --> Feedback["Show correctness + explanation"]
Feedback --> Next["Advance current_question"]
Next --> Loop
Loop --> |No| Results["Calculate score<br/>Update attempt + progress<br/>Clear context.user_data"]
Results --> End(["End"])
```

**Diagram sources**
- [bot/handlers/exam.py](file://bot/handlers/exam.py#L94-L123)
- [bot/handlers/exam.py](file://bot/handlers/exam.py#L125-L216)
- [bot/handlers/exam.py](file://bot/handlers/exam.py#L419-L467)
- [bot/services/exam_engine.py](file://bot/services/exam_engine.py#L29-L114)

**Section sources**
- [bot/handlers/exam.py](file://bot/handlers/exam.py#L125-L216)
- [bot/services/exam_engine.py](file://bot/services/exam_engine.py#L29-L114)

### Subjective Exam Flow (Writing and Speaking)
- Writing:
  - start_subjective_exam() prepares prompt, requirements, word count
  - handle_writing_input() accumulates text into a buffer and reports word count
  - submit_subjective() evaluates via AI tutor, updates attempt and progress, clears context
- Speaking:
  - start_subjective_exam() prepares prompt, hints, preparation time
  - handle_speaking_input() accepts voice or text; voice path uses speech_service.transcribe_telegram_voice()
  - submit_subjective() evaluates via AI tutor, updates attempt and progress, clears context

```mermaid
sequenceDiagram
participant User as "User"
participant Handler as "Exam Handler"
participant Speech as "Speech Service"
participant AI as "AI Tutor"
participant DB as "Database Service"
User->>Handler : Select writing/speaking
Handler->>Handler : start_subjective_exam()
alt writing
loop until submit
User->>Handler : send text
Handler->>Handler : handle_writing_input()
Handler-->>User : word count feedback
end
else speaking
loop until submit
User->>Handler : send voice or text
alt voice available
Handler->>Speech : transcribe_telegram_voice()
Speech-->>Handler : transcribed_text
else voice unavailable
Handler-->>User : "Type your response"
end
Handler->>Handler : handle_speaking_input()
end
end
Handler->>AI : evaluate_writing()/evaluate_speaking()
AI-->>Handler : evaluation
Handler->>DB : update_exam_attempt()
Handler->>DB : save_progress()
Handler-->>User : formatted results
Handler->>Handler : context.user_data.clear()
```

**Diagram sources**
- [bot/handlers/exam.py](file://bot/handlers/exam.py#L218-L417)
- [bot/services/speech.py](file://bot/services/speech.py#L83-L129)
- [bot/services/ai_tutor.py](file://bot/services/ai_tutor.py#L154-L325)
- [bot/services/database.py](file://bot/services/database.py#L364-L412)

**Section sources**
- [bot/handlers/exam.py](file://bot/handlers/exam.py#L218-L417)
- [bot/services/speech.py](file://bot/services/speech.py#L83-L129)
- [bot/services/ai_tutor.py](file://bot/services/ai_tutor.py#L154-L325)

### User Data Persistence and Session Management
- context.user_data keys used:
  - exam_type, level, answers, current_question, questions, total_questions, current_question_data
  - attempt_id for database linkage
  - writing_buffer for multi-message writing tasks
  - speaking_response for evaluated responses
- Session cleanup:
  - context.user_data.clear() executed upon completion or cancellation
  - ConversationHandler.END terminates the handler

**Section sources**
- [bot/handlers/exam.py](file://bot/handlers/exam.py#L94-L117)
- [bot/handlers/exam.py](file://bot/handlers/exam.py#L300-L303)
- [bot/handlers/exam.py](file://bot/handlers/exam.py#L414-L416)
- [bot/handlers/exam.py](file://bot/handlers/exam.py#L484-L485)

### Exam Attempt Creation and Tracking
- create_exam_attempt() initializes an attempt with user_id, exam_type, level, timestamps, and empty answers
- update_exam_attempt() appends answers, optional score, marks completion, and sets completion timestamp
- get_exam_attempts() retrieves completed attempts for reporting/history

**Section sources**
- [bot/services/database.py](file://bot/services/database.py#L342-L412)

### Integration with Exam Engine
- get_exam_questions():
  - Prefers database-backed questions via get_random_exam_questions()
  - Falls back to AI-generated questions when insufficient database content exists
  - Returns questions up to configured counts per exam type
- check_answer():
  - Normalizes answer formats (accepts "A" or "A)")
  - Provides localized explanations
- calculate_score():
  - Computes percentage, pass/fail threshold (60%), and identifies weak areas
- calculate_weighted_score():
  - Supports full mock exam weighting across skill categories

**Section sources**
- [bot/services/exam_engine.py](file://bot/services/exam_engine.py#L29-L183)

### AI Tutor Integration
- evaluate_writing():
  - Evaluates grammar, vocabulary, task completion, coherence
  - Returns structured feedback, mistakes, strengths, suggestions, corrected text
- evaluate_speaking():
  - Evaluates grammar, vocabulary, task completion, fluency
  - Returns pronunciation tips, strengths, suggestions
- generate_exam_question():
  - Produces JSON-formatted questions for different exam types and levels

**Section sources**
- [bot/services/ai_tutor.py](file://bot/services/ai_tutor.py#L154-L325)
- [bot/services/ai_tutor.py](file://bot/services/ai_tutor.py#L327-L424)

### Speech Service Integration
- transcribe_telegram_voice():
  - Downloads voice file, transcribes to German text using faster-whisper
  - Gracefully handles unavailability by falling back to text input
- Status reporting:
  - speech_service.is_available controls UI messaging

**Section sources**
- [bot/services/speech.py](file://bot/services/speech.py#L83-L129)

### Subscription Middleware
- require_subscription():
  - Decorator enforcing subscription for handlers
  - Stores subscription warnings in context.user_data for downstream use
- require_subscription_callback():
  - Decorator variant for callback handlers
- check_subscription():
  - Returns active/expired/no-subscription states with expiry dates

**Section sources**
- [bot/middleware/subscription.py](file://bot/middleware/subscription.py#L47-L137)

### Database Schema and Indexes
- Users, Lessons, Exam Questions, User Progress, Conversation History, Exam Attempts
- Indexes optimize lookups by level/type, user_id, timestamps

**Section sources**
- [database_setup.sql](file://database_setup.sql#L4-L84)

## Dependency Analysis
The exam system exhibits layered dependencies:
- Handlers depend on Services (database, exam_engine, ai_tutor, speech), Utilities (keyboards, formatters), and Middleware (subscription)
- Services depend on Configuration and external APIs (Supabase, OpenRouter)
- Database schema underpins all persistence operations

```mermaid
graph LR
H["Exam Handler"] --> DB["Database Service"]
H --> ENG["Exam Engine"]
H --> AI["AI Tutor"]
H --> SP["Speech Service"]
H --> K["Keyboards"]
H --> F["Formatters"]
H --> SUB["Subscription Middleware"]
ENG --> DB
ENG --> AI
DB --> CFG["Config"]
AI --> CFG
```

**Diagram sources**
- [bot/handlers/exam.py](file://bot/handlers/exam.py#L17-L23)
- [bot/services/exam_engine.py](file://bot/services/exam_engine.py#L9-L10)
- [bot/services/ai_tutor.py](file://bot/services/ai_tutor.py#L11)
- [bot/services/database.py](file://bot/services/database.py#L10-L11)
- [bot/config.py](file://bot/config.py#L1-L60)

**Section sources**
- [bot/handlers/exam.py](file://bot/handlers/exam.py#L17-L23)
- [bot/services/exam_engine.py](file://bot/services/exam_engine.py#L9-L10)
- [bot/services/ai_tutor.py](file://bot/services/ai_tutor.py#L11)
- [bot/services/database.py](file://bot/services/database.py#L10-L11)
- [bot/config.py](file://bot/config.py#L1-L60)

## Performance Considerations
- Question sourcing:
  - Database queries are limited by count and difficulty distribution to balance load
  - AI fallback ensures availability but adds latency; consider caching frequently used question templates
- Speech transcription:
  - faster-whisper requires CPU/GPU resources; availability impacts UX
  - Consider pre-downloading model or providing fallback text input
- AI evaluations:
  - OpenRouter requests have timeouts; implement retry logic and graceful degradation
- Database operations:
  - Indexes on user_id, level/type, and timestamps improve query performance
  - Batch updates for exam attempts reduce round-trips

## Troubleshooting Guide
Common issues and resolutions:
- Subscription required:
  - Handlers check subscription early; ensure users receive clear messages and menu navigation
- No questions available:
  - When database lacks sufficient questions, AI generation is attempted; if still empty, guide users to try another exam type
- Voice transcription failures:
  - If speech_service.is_available is False, inform users to type their response
- API errors:
  - AI tutor returns default evaluations on JSON parse or HTTP errors; log and notify users to retry
- Session cleanup:
  - Always clear context.user_data on completion or cancellation to prevent stale state

**Section sources**
- [bot/handlers/exam.py](file://bot/handlers/exam.py#L35-L43)
- [bot/handlers/exam.py](file://bot/handlers/exam.py#L102-L108)
- [bot/services/speech.py](file://bot/services/speech.py#L18-L18)
- [bot/services/ai_tutor.py](file://bot/services/ai_tutor.py#L232-L237)
- [bot/handlers/exam.py](file://bot/handlers/exam.py#L414-L416)
- [bot/handlers/exam.py](file://bot/handlers/exam.py#L470-L485)

## Conclusion
The exam simulation integrates a robust conversation flow with clear state management, subscription enforcement, and seamless AI-driven evaluation. Objective and subjective exams share a unified routing mechanism while leveraging specialized services for question sourcing, evaluation, and speech processing. User data persistence via context.user_data ensures continuity across steps, and database-backed attempt tracking enables progress analytics. The architecture balances reliability with extensibility, supporting future enhancements such as full mock exam weighting and expanded exam types.