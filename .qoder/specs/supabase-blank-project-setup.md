# EthioGerman Language School - Telegram AI Tutor Bot

## Overview
Build a Python Telegram bot for German language tutoring (A1-B1 CEFR levels) with AI-powered lessons, Goethe exam simulation, subscription management, and voice support.

## Configuration
- **Bot Token:** `8294144624:AAFnAprt-0ZOQgOvwL5neTW-PT2ow11eHdA`
- **Supabase URL:** `https://zlnoxixvxlexywyzbjqh.supabase.co`
- **Supabase Key:** `eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Inpsbm94aXh2eGxleHl3eXpianFoIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc2ODg0OTExMSwiZXhwIjoyMDg0NDI1MTExfQ.ni9Y_u64H_s33FlXYpfOyoOyPxZxTcrB4yT4dDVcQqU`
- **AI:** OpenRouter (free tier) with Mistral 7B Instruct
- **Voice:** faster-whisper for speech-to-text (Day 1 feature)

---

## Project Structure

```
FebEGLS-bot/
├── bot/
│   ├── __init__.py
│   ├── main.py                 # Entry point, bot initialization
│   ├── config.py               # Environment configuration
│   ├── handlers/
│   │   ├── __init__.py
│   │   ├── start.py            # /start, registration
│   │   ├── menu.py             # Main menu navigation
│   │   ├── learn.py            # AI tutoring sessions
│   │   ├── exam.py             # Goethe exam simulation
│   │   └── progress.py         # User statistics
│   ├── middleware/
│   │   ├── __init__.py
│   │   └── subscription.py     # Subscription validation
│   ├── services/
│   │   ├── __init__.py
│   │   ├── ai_tutor.py         # OpenRouter/Mistral integration
│   │   ├── database.py         # Supabase operations
│   │   ├── exam_engine.py      # Question selection & scoring
│   │   └── speech.py           # Voice transcription
│   └── utils/
│       ├── __init__.py
│       ├── keyboards.py        # Inline keyboard builders
│       └── formatters.py       # Message formatting
├── prompts/
│   └── tutor_system.txt        # AI system prompt
├── requirements.txt
├── .env
└── .gitignore
```

---

## Database Schema (Supabase)

### Table: `users`
| Column | Type | Description |
|--------|------|-------------|
| id | BIGINT PK | Telegram user ID |
| username | TEXT | Telegram username |
| first_name | TEXT | User's first name |
| subscription_expiry | TIMESTAMPTZ | When subscription ends (NULL = not subscribed) |
| current_level | TEXT | 'A1', 'A2', or 'B1' |
| preferred_lang | TEXT | 'amharic', 'english', 'german' |
| created_at | TIMESTAMPTZ | Registration date |
| last_active | TIMESTAMPTZ | Last interaction |

### Table: `lessons`
| Column | Type | Description |
|--------|------|-------------|
| id | UUID PK | Unique identifier |
| level | TEXT | CEFR level |
| skill | TEXT | 'lesen', 'horen', 'schreiben', 'sprechen', 'vokabular' |
| topic | TEXT | Lesson topic (e.g., 'Familie') |
| title | TEXT | Lesson title |
| content | JSONB | Structured lesson content |
| is_active | BOOLEAN | Enable/disable lesson |

### Table: `exam_questions`
| Column | Type | Description |
|--------|------|-------------|
| id | UUID PK | Unique identifier |
| level | TEXT | CEFR level |
| exam_type | TEXT | 'lesen', 'horen', 'schreiben', 'sprechen', 'vokabular' |
| question_text | TEXT | The question |
| question_data | JSONB | Options, audio_url, etc. |
| correct_answer | TEXT | For objective questions |
| rubric | JSONB | For subjective evaluation |
| difficulty | INT | 1-10 scale |

### Table: `user_progress`
| Column | Type | Description |
|--------|------|-------------|
| id | UUID PK | Unique identifier |
| user_id | BIGINT FK | References users(id) |
| skill | TEXT | Skill practiced |
| score | DECIMAL | Score achieved (0-100) |
| weak_areas | TEXT[] | Identified weaknesses |
| completed_at | TIMESTAMPTZ | When completed |

### Table: `conversation_history`
| Column | Type | Description |
|--------|------|-------------|
| id | UUID PK | Unique identifier |
| user_id | BIGINT FK | References users(id) |
| session_id | UUID | Groups conversation messages |
| role | TEXT | 'user' or 'assistant' |
| content | TEXT | Message content |
| timestamp | TIMESTAMPTZ | When sent |

### Table: `exam_attempts`
| Column | Type | Description |
|--------|------|-------------|
| id | UUID PK | Unique identifier |
| user_id | BIGINT FK | References users(id) |
| exam_type | TEXT | Type of exam |
| level | TEXT | CEFR level |
| score | DECIMAL | Final score |
| answers | JSONB | Detailed answer log |
| started_at | TIMESTAMPTZ | Start time |
| completed_at | TIMESTAMPTZ | End time |

---

## Bot Commands & Menu Flow

### Commands
- `/start` - Welcome + registration (if new user)
- `/menu` - Main menu
- `/learn` - Start AI tutoring
- `/exam` - Start exam
- `/progress` - View statistics
- `/settings` - Change level/language
- `/help` - Instructions
- `/cancel` - Exit current flow

### Main Menu (Inline Keyboard)
```
[Learn with AI Tutor]
[Take Practice Exam]
[View My Progress]
[Settings]
```

### Learn Menu
```
[Free Conversation] [Grammar Practice]
[Lesen] [Horen] [Schreiben]
[Sprechen] [Vokabular]
[Back]
```

### Exam Menu
```
[Lesen Exam] [Horen Exam]
[Schreiben Exam] [Sprechen Exam]
[Vokabular Exam]
[Full Mock Exam]
[Back]
```

---

## Core Implementation Tasks

### 1. Setup & Configuration
- Create project structure
- Setup `.env` with all credentials
- Create `config.py` to load environment variables
- Create `requirements.txt` with dependencies

### 2. Database Setup
- Create all tables in Supabase via SQL
- Implement `database.py` with CRUD operations
- Test connection and basic queries

### 3. Subscription Middleware
- Create decorator `@require_subscription`
- Check `subscription_expiry > now()` before handlers
- Show appropriate messages for expired/missing subscriptions

### 4. Bot Core
- Initialize python-telegram-bot Application
- Register all handlers
- Implement `/start` with user registration
- Build main menu navigation

### 5. AI Tutor Service
- Setup OpenRouter API client
- Create system prompt for German tutoring
- Implement conversation with context (last 10 messages)
- Handle corrections and feedback

### 6. Exam Engine
- Question selection algorithm (difficulty distribution)
- Objective exam flow (MCQ with inline buttons)
- Subjective exam flow (writing/speaking evaluation)
- Scoring and feedback generation

### 7. Voice Processing
- Integrate faster-whisper
- Transcribe voice messages for Sprechen practice
- Handle audio file downloads from Telegram

### 8. Progress Tracking
- Calculate skill-level statistics
- Identify weak areas from exam results
- Display formatted progress summary

---

## Key Files to Create

| File | Purpose |
|------|---------|
| `bot/main.py` | Entry point, initializes bot and handlers |
| `bot/config.py` | Environment variables and constants |
| `bot/services/database.py` | All Supabase operations |
| `bot/services/ai_tutor.py` | OpenRouter API integration |
| `bot/services/exam_engine.py` | Question selection and scoring |
| `bot/services/speech.py` | Voice transcription |
| `bot/middleware/subscription.py` | Subscription validation |
| `bot/handlers/start.py` | Registration and /start |
| `bot/handlers/menu.py` | Menu navigation |
| `bot/handlers/learn.py` | AI tutoring conversations |
| `bot/handlers/exam.py` | Exam flows |
| `bot/handlers/progress.py` | Statistics display |
| `bot/utils/keyboards.py` | Inline keyboard builders |
| `bot/utils/formatters.py` | Message formatting |
| `prompts/tutor_system.txt` | AI system prompt |
| `requirements.txt` | Dependencies |
| `.env` | Credentials (gitignored) |

---

## Dependencies (requirements.txt)

```
python-telegram-bot>=20.0
supabase>=2.0.0
httpx>=0.25.0
python-dotenv>=1.0.0
faster-whisper>=0.9.0
pydub>=0.25.1
```

---

## OpenRouter Setup Instructions

1. Go to https://openrouter.ai/
2. Sign up for free account
3. Navigate to "Keys" section
4. Create new API key
5. Add to `.env` as `OPENROUTER_API_KEY`
6. Use model: `mistralai/mistral-7b-instruct` (free tier)

---

## AI System Prompt (tutor_system.txt)

```
You are an expert German language tutor for EthioGerman Language School.

Student Level: {level}
Explanation Language: {preferred_lang}

Your responsibilities:
- Conduct natural German conversations appropriate for the student's level
- Correct mistakes gently with explanations
- For A1: Use simple vocabulary and basic grammar
- For A2: Introduce more complex sentences
- For B1: Use natural, fluid German

For speaking/writing corrections, always provide:
1. Brief feedback on what was wrong
2. Corrected version
3. Natural alternative (how a native would say it)

Be encouraging but accurate. Never shame the student.
Focus on practical, everyday German usage.
```

---

## Verification Steps

After implementation:

1. **Test Registration:**
   - Send `/start` to bot
   - Verify user created in Supabase with NULL subscription

2. **Test Subscription:**
   - Manually set `subscription_expiry` in Supabase to future date
   - Verify access to all features
   - Set to past date, verify access blocked

3. **Test AI Tutoring:**
   - Start conversation in German
   - Verify corrections are provided
   - Test with voice messages

4. **Test Exams:**
   - Take each exam type
   - Verify scoring works
   - Check progress recorded in `user_progress`

5. **Test Progress:**
   - View `/progress` after completing activities
   - Verify statistics are accurate

---

## Content Strategy

Since AI generates lessons dynamically:
1. AI creates lessons/questions on-demand based on level and skill
2. Store generated content in `lessons`/`exam_questions` for reuse
3. Admin can add curated content via Supabase dashboard
4. CSV import available for bulk content addition

---

## Implementation Order

1. Project setup & configuration
2. Database tables (SQL in Supabase)
3. `database.py` service
4. Basic bot with `/start` and menus
5. Subscription middleware
6. AI tutor service + `/learn` handler
7. Exam engine + `/exam` handler
8. Voice processing (faster-whisper)
9. Progress tracking + `/progress` handler
10. Testing and refinement
