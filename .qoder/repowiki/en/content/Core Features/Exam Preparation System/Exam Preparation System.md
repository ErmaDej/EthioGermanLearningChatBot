# Exam Preparation System

<cite>
**Referenced Files in This Document**
- [main.py](file://bot/main.py)
- [config.py](file://bot/config.py)
- [database_setup.sql](file://database_setup.sql)
- [setup_database.py](file://setup_database.py)
- [subscription.py](file://bot/middleware/subscription.py)
- [formatters.py](file://bot/utils/formatters.py)
- [keyboards.py](file://bot/utils/keyboards.py)
- [speech.py](file://bot/services/speech.py)
- [database.py](file://bot/services/database.py)
- [ai_tutor.py](file://bot/services/ai_tutor.py)
- [exam_engine.py](file://bot/services/exam_engine.py)
- [exam.py](file://bot/handlers/exam.py)
- [progress.py](file://bot/handlers/progress.py)
- [tutor_system.txt](file://prompts/tutor_system.txt)
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
This document describes the Goethe exam preparation system built as a Telegram bot. It focuses on the exam simulation functionality, including question generation, answer evaluation, automated scoring, and reporting. It also covers the exam engine architecture, skill-based categorization (reading, writing, listening, speaking, vocabulary), difficulty adaptation, exam attempt tracking, performance analytics, weak area identification, and integration with AI-driven templates and rubrics. Certification preparation workflows and subscription gating are addressed.

## Project Structure
The system is organized around a Telegram bot entry point, handler modules for commands and conversations, service modules for AI, database, speech, and exam logic, and utility modules for formatting and keyboard layouts. Configuration and database schema are provided separately.

```mermaid
graph TB
subgraph "Entry Point"
M["bot/main.py"]
end
subgraph "Handlers"
EH["bot/handlers/exam.py"]
PH["bot/handlers/progress.py"]
end
subgraph "Services"
DB["bot/services/database.py"]
ET["bot/services/exam_engine.py"]
AI["bot/services/ai_tutor.py"]
SP["bot/services/speech.py"]
end
subgraph "Utilities"
FM["bot/utils/formatters.py"]
KB["bot/utils/keyboards.py"]
end
subgraph "Middleware"
SUB["bot/middleware/subscription.py"]
end
subgraph "Config"
CFG["bot/config.py"]
end
subgraph "Schema"
DS["database_setup.sql"]
end
M --> EH
M --> PH
EH --> DB
EH --> ET
EH --> AI
EH --> SP
PH --> DB
DB --> CFG
ET --> CFG
AI --> CFG
EH --> FM
EH --> KB
PH --> FM
PH --> KB
EH --> SUB
PH --> SUB
DS --> DB
```

**Diagram sources**
- [main.py](file://bot/main.py#L60-L93)
- [exam.py](file://bot/handlers/exam.py#L488-L523)
- [progress.py](file://bot/handlers/progress.py#L17-L99)
- [database.py](file://bot/services/database.py#L16-L416)
- [exam_engine.py](file://bot/services/exam_engine.py#L15-L211)
- [ai_tutor.py](file://bot/services/ai_tutor.py#L19-L451)
- [speech.py](file://bot/services/speech.py#L21-L140)
- [formatters.py](file://bot/utils/formatters.py#L8-L300)
- [keyboards.py](file://bot/utils/keyboards.py#L10-L183)
- [subscription.py](file://bot/middleware/subscription.py#L21-L156)
- [config.py](file://bot/config.py#L10-L60)
- [database_setup.sql](file://database_setup.sql#L1-L84)

**Section sources**
- [main.py](file://bot/main.py#L60-L93)
- [config.py](file://bot/config.py#L10-L60)
- [database_setup.sql](file://database_setup.sql#L1-L84)

## Core Components
- Exam Engine: Selects questions, generates AI-backed questions when needed, evaluates answers, calculates scores, and provides level recommendations.
- Exam Handlers: Manage the Telegram conversation flow for exam selection, objective and subjective (writing/speaking) tasks, and result presentation.
- Database Service: Provides CRUD operations for users, lessons, exam questions, progress, conversation history, and exam attempts.
- AI Tutor Service: Generates exam questions and evaluates writing/speaking submissions using a large language model.
- Speech Service: Provides optional voice transcription for speaking tasks.
- Utilities: Formatting and keyboard builders for consistent UI and navigation.
- Middleware: Subscription checks for access control.
- Configuration: Centralized settings for Telegram, Supabase, OpenRouter, CEFR levels, and skills.

**Section sources**
- [exam_engine.py](file://bot/services/exam_engine.py#L15-L211)
- [exam.py](file://bot/handlers/exam.py#L31-L523)
- [database.py](file://bot/services/database.py#L16-L416)
- [ai_tutor.py](file://bot/services/ai_tutor.py#L19-L451)
- [speech.py](file://bot/services/speech.py#L21-L140)
- [formatters.py](file://bot/utils/formatters.py#L8-L300)
- [keyboards.py](file://bot/utils/keyboards.py#L10-L183)
- [subscription.py](file://bot/middleware/subscription.py#L21-L156)
- [config.py](file://bot/config.py#L10-L60)

## Architecture Overview
The exam preparation system follows a layered architecture:
- Presentation Layer: Telegram handlers orchestrate user interactions and conversation states.
- Business Logic Layer: Exam engine encapsulates scoring, weighting, and recommendation logic.
- AI Integration Layer: AI tutor service generates questions and evaluates subjective tasks.
- Data Access Layer: Database service abstracts Supabase operations.
- Infrastructure Layer: Configuration, utilities, and middleware.

```mermaid
graph TB
U["User"]
TG["Telegram Bot"]
EH["Exam Handler<br/>(bot/handlers/exam.py)"]
EE["Exam Engine<br/>(bot/services/exam_engine.py)"]
DB["Database Service<br/>(bot/services/database.py)"]
AI["AI Tutor Service<br/>(bot/services/ai_tutor.py)"]
SP["Speech Service<br/>(bot/services/speech.py)"]
FM["Formatters<br/>(bot/utils/formatters.py)"]
KB["Keyboards<br/>(bot/utils/keyboards.py)"]
SUB["Subscription Middleware<br/>(bot/middleware/subscription.py)"]
U --> TG
TG --> EH
EH --> SUB
EH --> EE
EH --> DB
EH --> AI
EH --> SP
EH --> FM
EH --> KB
EE --> DB
EE --> AI
DB --> |Supabase| DB
AI --> |OpenRouter API| AI
SP --> |faster-whisper| SP
```

**Diagram sources**
- [exam.py](file://bot/handlers/exam.py#L31-L523)
- [exam_engine.py](file://bot/services/exam_engine.py#L15-L211)
- [database.py](file://bot/services/database.py#L16-L416)
- [ai_tutor.py](file://bot/services/ai_tutor.py#L19-L451)
- [speech.py](file://bot/services/speech.py#L21-L140)
- [formatters.py](file://bot/utils/formatters.py#L8-L300)
- [keyboards.py](file://bot/utils/keyboards.py#L10-L183)
- [subscription.py](file://bot/middleware/subscription.py#L21-L156)

## Detailed Component Analysis

### Exam Engine
Responsibilities:
- Question selection by level and type with difficulty distribution.
- Fallback to AI-generated questions when the database lacks sufficient items.
- Answer evaluation for objective questions and explanation generation.
- Automated scoring with pass/fail thresholds and weak area identification.
- Weighted scoring across exam sections for full mock exams.
- Level recommendation based on performance trends.

Key behaviors:
- Objective answer checking supports flexible answer formats and provides explanations.
- Scoring aggregates correctness and topic metadata to surface weak areas.
- Weighted calculation applies Goethe-aligned weights to each skill.

```mermaid
classDiagram
class ExamEngine {
+EXAM_TYPES
+QUESTION_COUNTS
+get_exam_questions(level, exam_type, count) Dict[]
+calculate_score(answers, exam_type) Dict
+calculate_weighted_score(section_scores) float
+check_answer(question, user_answer) tuple~bool,str~
+get_level_recommendation(current_level, average_score) tuple~str,str~
}
class DatabaseService {
+get_random_exam_questions(level, exam_type, count) Dict[]
+create_exam_attempt(user_id, exam_type, level) Dict
+update_exam_attempt(attempt_id, answers, score, is_completed) Dict
+save_progress(user_id, skill, activity_type, score, weak_areas) Dict
+get_user_statistics(user_id) Dict
}
class AITutorService {
+generate_exam_question(level, exam_type, topic) Dict
+evaluate_writing(user_text, prompt, level) Dict
+evaluate_speaking(transcribed_text, prompt, level) Dict
}
ExamEngine --> DatabaseService : "uses"
ExamEngine --> AITutorService : "fallback generation"
```

**Diagram sources**
- [exam_engine.py](file://bot/services/exam_engine.py#L15-L211)
- [database.py](file://bot/services/database.py#L16-L416)
- [ai_tutor.py](file://bot/services/ai_tutor.py#L19-L451)

**Section sources**
- [exam_engine.py](file://bot/services/exam_engine.py#L15-L211)

### Exam Handler (Conversation Flow)
Responsibilities:
- Enforce subscription gating for exam access.
- Initialize exam sessions, persist attempt records, and route to appropriate handlers.
- Present objective questions with MCQ options and provide immediate feedback.
- Manage writing and speaking tasks with optional voice transcription.
- Aggregate answers, calculate scores, and present results with weak area insights.
- Persist progress and weak areas for analytics.

```mermaid
sequenceDiagram
participant U as "User"
participant TG as "Telegram Bot"
participant EH as "Exam Handler"
participant EE as "Exam Engine"
participant DB as "Database Service"
participant AI as "AI Tutor Service"
participant SP as "Speech Service"
U->>TG : "/exam"
TG->>EH : exam_command()
EH->>DB : check_subscription()
alt subscription invalid
EH-->>U : "Access denied"
else subscription valid
EH-->>U : "Exam menu"
U->>TG : Select exam type
TG->>EH : exam_selected()
EH->>DB : get_user()
EH->>EE : get_exam_questions(level, exam_type)
alt questions available
EH->>DB : create_exam_attempt(user_id, exam_type, level)
alt objective exam
loop until all questions
EH-->>U : "Question + options"
U->>TG : Select answer
TG->>EH : handle_objective_answer()
EH->>EE : check_answer(question, user_answer)
EH->>DB : update_exam_attempt(append answer)
end
EH->>EE : calculate_score(answers, exam_type)
EH->>DB : update_exam_attempt(score, is_completed=true)
EH->>DB : save_progress(skill, activity_type='exam', score, weak_areas)
EH-->>U : "Results + weak areas"
else subjective exam (writing/speaking)
EH-->>U : "Prompt + requirements"
U->>TG : Send text or voice
TG->>EH : handle_speaking_input()/handle_writing_input()
EH->>SP : transcribe_voice() (optional)
EH->>AI : evaluate_writing()/evaluate_speaking()
EH->>DB : update_exam_attempt(evaluation, score, is_completed=true)
EH->>DB : save_progress(skill, activity_type='exam', score, suggestions)
EH-->>U : "Evaluation feedback"
end
else no questions
EH-->>U : "Try another type"
end
end
```

**Diagram sources**
- [exam.py](file://bot/handlers/exam.py#L31-L523)
- [exam_engine.py](file://bot/services/exam_engine.py#L15-L211)
- [database.py](file://bot/services/database.py#L16-L416)
- [ai_tutor.py](file://bot/services/ai_tutor.py#L19-L451)
- [speech.py](file://bot/services/speech.py#L21-L140)

**Section sources**
- [exam.py](file://bot/handlers/exam.py#L31-L523)

### Question Generation and Difficulty Adaptation
- Database-backed selection with difficulty distribution across easy, medium, and hard bands.
- AI fallback generation for vocabulary, reading, writing, and speaking tasks with structured JSON outputs.
- Question templates embed CEFR-aligned complexity and task-specific requirements.

```mermaid
flowchart TD
Start(["Start get_exam_questions"]) --> Count["Resolve count from defaults or input"]
Count --> FetchDB["Fetch random questions by difficulty bands"]
FetchDB --> Enough{"Enough questions?"}
Enough --> |Yes| ReturnDB["Return subset"]
Enough --> |No| Need["Compute needed count"]
Need --> Loop["Loop needed times"]
Loop --> Gen["AI generate question (type, level, topic)"]
Gen --> Append["Append to results"]
Append --> Loop
ReturnDB --> End(["End"])
Append --> Enough
```

**Diagram sources**
- [exam_engine.py](file://bot/services/exam_engine.py#L29-L65)
- [database.py](file://bot/services/database.py#L163-L184)
- [ai_tutor.py](file://bot/services/ai_tutor.py#L327-L424)

**Section sources**
- [database.py](file://bot/services/database.py#L163-L184)
- [ai_tutor.py](file://bot/services/ai_tutor.py#L327-L424)
- [exam_engine.py](file://bot/services/exam_engine.py#L29-L65)

### Answer Evaluation and Automated Scoring
- Objective scoring compares normalized user answers to correct answers and annotates explanations.
- Subjective scoring leverages AI rubrics to produce structured evaluations with scores, strengths, suggestions, and corrections.
- Weak areas are derived from incorrect answers and evaluation suggestions.

```mermaid
flowchart TD
AStart(["Start calculate_score"]) --> Empty{"Any answers?"}
Empty --> |No| ReturnEmpty["Return zeros and no weak areas"]
Empty --> |Yes| Compute["Count total and correct answers"]
Compute --> Percent["Compute percentage"]
Percent --> Weak["Collect weak areas from wrong answers"]
Weak --> PassFail["Pass if >= 60%"]
PassFail --> AEnd(["End"])
ReturnEmpty --> AEnd
```

**Diagram sources**
- [exam_engine.py](file://bot/services/exam_engine.py#L67-L114)

**Section sources**
- [exam_engine.py](file://bot/services/exam_engine.py#L67-L114)
- [ai_tutor.py](file://bot/services/ai_tutor.py#L154-L326)

### Performance Analytics and Weak Area Identification
- Progress entries capture skill, activity type, score, and weak areas.
- Statistics aggregation computes averages per skill, identifies top weak areas, and highlights strengths.
- Progress handler surfaces summaries and recent exam history.

```mermaid
sequenceDiagram
participant U as "User"
participant PH as "Progress Handler"
participant DB as "Database Service"
U->>PH : "/progress"
PH->>DB : get_user_statistics(user_id)
DB-->>PH : {total_activities, average_score, skill_scores, weak_areas, strengths}
PH-->>U : "Progress summary + actions"
U->>PH : "Practice weak areas / View history"
PH->>DB : get_exam_attempts(user_id, limit=10)
DB-->>PH : Recent attempts
PH-->>U : "Weak areas list or history"
```

**Diagram sources**
- [progress.py](file://bot/handlers/progress.py#L17-L99)
- [database.py](file://bot/services/database.py#L233-L292)

**Section sources**
- [progress.py](file://bot/handlers/progress.py#L17-L99)
- [database.py](file://bot/services/database.py#L233-L292)

### Integration with Templates and Rubrics
- AI tutor generates structured question JSON aligned with CEFR levels and exam types.
- Writing and speaking evaluations adhere to rubrics with weighted criteria and detailed feedback.
- System prompt defines teaching style and correction format for consistency.

**Section sources**
- [ai_tutor.py](file://bot/services/ai_tutor.py#L327-L424)
- [ai_tutor.py](file://bot/services/ai_tutor.py#L154-L326)
- [tutor_system.txt](file://prompts/tutor_system.txt#L1-L74)

### Subscription Gating and Access Control
- Middleware validates subscription status and provides contextual warnings for expiring subscriptions.
- Handlers enforce subscription checks before allowing exam access.

**Section sources**
- [subscription.py](file://bot/middleware/subscription.py#L21-L156)
- [exam.py](file://bot/handlers/exam.py#L31-L523)

## Dependency Analysis
The system exhibits clear separation of concerns:
- Handlers depend on services for data and AI operations.
- Services depend on configuration and external APIs.
- Utilities support consistent UI and messaging.
- Middleware enforces policy at the handler boundary.

```mermaid
graph LR
EH["handlers/exam.py"] --> EE["services/exam_engine.py"]
EH --> DB["services/database.py"]
EH --> AI["services/ai_tutor.py"]
EH --> SP["services/speech.py"]
EH --> FM["utils/formatters.py"]
EH --> KB["utils/keyboards.py"]
EH --> SUB["middleware/subscription.py"]
EE --> DB
EE --> AI
DB --> CFG["config.py"]
AI --> CFG
SP --> CFG
```

**Diagram sources**
- [exam.py](file://bot/handlers/exam.py#L17-L24)
- [exam_engine.py](file://bot/services/exam_engine.py#L9-L11)
- [database.py](file://bot/services/database.py#L10-L11)
- [ai_tutor.py](file://bot/services/ai_tutor.py#L11-L12)
- [speech.py](file://bot/services/speech.py#L12-L13)
- [formatters.py](file://bot/utils/formatters.py#L1-L10)
- [keyboards.py](file://bot/utils/keyboards.py#L1-L10)
- [subscription.py](file://bot/middleware/subscription.py#L13-L13)
- [config.py](file://bot/config.py#L10-L60)

**Section sources**
- [exam.py](file://bot/handlers/exam.py#L17-L24)
- [exam_engine.py](file://bot/services/exam_engine.py#L9-L11)
- [database.py](file://bot/services/database.py#L10-L11)
- [ai_tutor.py](file://bot/services/ai_tutor.py#L11-L12)
- [speech.py](file://bot/services/speech.py#L12-L13)
- [formatters.py](file://bot/utils/formatters.py#L1-L10)
- [keyboards.py](file://bot/utils/keyboards.py#L1-L10)
- [subscription.py](file://bot/middleware/subscription.py#L13-L13)
- [config.py](file://bot/config.py#L10-L60)

## Performance Considerations
- Asynchronous operations: AI requests and database calls are awaited to prevent blocking.
- Efficient question retrieval: Difficulty-based sampling reduces bias and improves coverage.
- Streaming voice transcription: Optional whisper model with CPU-friendly compute type.
- Logging: Structured logs minimize overhead and aid debugging.
- Recommendations: Weighted scoring and level recommendations reduce churn by aligning expectations.

[No sources needed since this section provides general guidance]

## Troubleshooting Guide
Common issues and resolutions:
- Subscription errors: Verify subscription status and renewal reminders; ensure middleware is applied to handlers.
- Missing questions: Confirm database tables and indexes exist; fallback to AI generation if database is empty.
- AI evaluation failures: Inspect API keys and timeouts; default evaluation ensures graceful degradation.
- Voice transcription unavailable: Install faster-whisper; fall back to typed responses.
- Database connectivity: Validate Supabase URL and keys; check network and firewall settings.

**Section sources**
- [subscription.py](file://bot/middleware/subscription.py#L21-L156)
- [database.py](file://bot/services/database.py#L16-L416)
- [ai_tutor.py](file://bot/services/ai_tutor.py#L147-L153)
- [speech.py](file://bot/services/speech.py#L12-L18)
- [config.py](file://bot/config.py#L40-L60)

## Conclusion
The exam preparation system integrates Telegram UX, AI-driven question generation and evaluation, and robust analytics to simulate Goethe-style assessments. It supports skill-based categorization, adaptive difficulty, and personalized weak area identification, enabling effective certification preparation workflows.

[No sources needed since this section summarizes without analyzing specific files]

## Appendices

### Data Model Overview
The database schema supports users, lessons, exam questions, progress tracking, conversation history, and exam attempts with appropriate indexing.

```mermaid
erDiagram
USERS {
bigint id PK
text username
text first_name
text last_name
timestamptz subscription_expiry
text current_level
text preferred_lang
timestamptz created_at
timestamptz last_active
}
LESSONS {
uuid id PK
text level
text skill
text topic
text title
jsonb content
boolean is_active
timestamptz created_at
}
EXAM_QUESTIONS {
uuid id PK
text level
text exam_type
text question_text
jsonb question_data
text correct_answer
jsonb rubric
int difficulty
boolean is_active
timestamptz created_at
}
USER_PROGRESS {
uuid id PK
bigint user_id FK
text skill
text activity_type
decimal score
text[] weak_areas
timestamptz completed_at
}
CONVERSATION_HISTORY {
uuid id PK
bigint user_id FK
uuid session_id
text role
text content
timestamptz timestamp
}
EXAM_ATTEMPTS {
uuid id PK
bigint user_id FK
text exam_type
text level
decimal score
jsonb answers
timestamptz started_at
timestamptz completed_at
boolean is_completed
}
USERS ||--o{ USER_PROGRESS : "has"
USERS ||--o{ CONVERSATION_HISTORY : "has"
USERS ||--o{ EXAM_ATTEMPTS : "has"
```

**Diagram sources**
- [database_setup.sql](file://database_setup.sql#L4-L84)

**Section sources**
- [database_setup.sql](file://database_setup.sql#L1-L84)

### Configuration Reference
- Telegram Bot Token: Required for bot operation.
- Supabase URL and Key: Required for database operations.
- OpenRouter API Key and URL: Required for AI evaluation and question generation.
- CEFR Levels and Skills: Define supported exam types and levels.
- Session Timeout and Conversation History Limits: Control memory and responsiveness.

**Section sources**
- [config.py](file://bot/config.py#L10-L60)