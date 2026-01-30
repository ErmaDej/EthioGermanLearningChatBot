# EthioGerman Language School - Telegram AI Tutor Bot Implementation Plan

## Model Change
**Updated:** Using `meta-llama/llama-3.3-70b-instruct:free` instead of Mistral 7B for better performance.

## Credentials
- **Bot Token:** `8294144624:AAFnAprt-0ZOQgOvwL5neTW-PT2ow11eHdA`
- **Supabase URL:** `https://zlnoxixvxlexywyzbjqh.supabase.co`
- **Supabase Key:** `eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...` (service role)
- **AI Model:** `meta-llama/llama-3.3-70b-instruct:free` via OpenRouter

---

## Project Structure

```
FebEGLS-bot/
├── bot/
│   ├── __init__.py
│   ├── main.py                 # Entry point
│   ├── config.py               # Environment config
│   ├── handlers/
│   │   ├── __init__.py
│   │   ├── start.py            # Registration, /start
│   │   ├── menu.py             # Navigation
│   │   ├── learn.py            # AI tutoring
│   │   ├── exam.py             # Goethe exams
│   │   └── progress.py         # Statistics
│   ├── middleware/
│   │   ├── __init__.py
│   │   └── subscription.py     # Access control
│   ├── services/
│   │   ├── __init__.py
│   │   ├── ai_tutor.py         # OpenRouter + Llama 3.3
│   │   ├── database.py         # Supabase client
│   │   ├── exam_engine.py      # Question logic
│   │   └── speech.py           # Voice transcription
│   └── utils/
│       ├── __init__.py
│       ├── keyboards.py        # Inline keyboards
│       └── formatters.py       # Message formatting
├── prompts/
│   └── tutor_system.txt        # AI system prompt
├── requirements.txt
├── .env
└── .gitignore
```

---

## Implementation Steps

### Step 1: Project Setup
Create folder structure, `.env`, `config.py`, `requirements.txt`

**Files:**
- `d:/Extras/EthioGerman-Project-SnD-Ermax7/FebEGLS-bot/.env`
- `d:/Extras/EthioGerman-Project-SnD-Ermax7/FebEGLS-bot/.gitignore`
- `d:/Extras/EthioGerman-Project-SnD-Ermax7/FebEGLS-bot/requirements.txt`
- `d:/Extras/EthioGerman-Project-SnD-Ermax7/FebEGLS-bot/bot/config.py`

### Step 2: Database Schema (Supabase SQL)
Create tables: `users`, `lessons`, `exam_questions`, `user_progress`, `conversation_history`, `exam_attempts`

### Step 3: Database Service
Implement `bot/services/database.py` with CRUD operations

### Step 4: AI Tutor Service
Implement `bot/services/ai_tutor.py` with OpenRouter API using **Llama 3.3 70B**

### Step 5: Subscription Middleware
Implement `bot/middleware/subscription.py` decorator

### Step 6: Utility Functions
Create `keyboards.py` and `formatters.py`

### Step 7: Bot Handlers
Implement handlers: start, menu, learn, exam, progress

### Step 8: Speech Processing
Implement `bot/services/speech.py` with faster-whisper

### Step 9: Main Entry Point
Create `bot/main.py` to initialize and run bot

### Step 10: System Prompt
Create `prompts/tutor_system.txt`

---

## Database Tables (SQL)

```sql
-- users table
CREATE TABLE users (
    id BIGINT PRIMARY KEY,
    username TEXT,
    first_name TEXT,
    last_name TEXT,
    subscription_expiry TIMESTAMPTZ,
    current_level TEXT DEFAULT 'A1',
    preferred_lang TEXT DEFAULT 'english',
    created_at TIMESTAMPTZ DEFAULT NOW(),
    last_active TIMESTAMPTZ
);

-- lessons table
CREATE TABLE lessons (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    level TEXT NOT NULL,
    skill TEXT NOT NULL,
    topic TEXT,
    title TEXT NOT NULL,
    content JSONB,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- exam_questions table
CREATE TABLE exam_questions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    level TEXT NOT NULL,
    exam_type TEXT NOT NULL,
    question_text TEXT NOT NULL,
    question_data JSONB,
    correct_answer TEXT,
    rubric JSONB,
    difficulty INT DEFAULT 5,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- user_progress table
CREATE TABLE user_progress (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id BIGINT REFERENCES users(id) ON DELETE CASCADE,
    skill TEXT NOT NULL,
    activity_type TEXT,
    score DECIMAL(5,2),
    weak_areas TEXT[],
    completed_at TIMESTAMPTZ DEFAULT NOW()
);

-- conversation_history table
CREATE TABLE conversation_history (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id BIGINT REFERENCES users(id) ON DELETE CASCADE,
    session_id UUID,
    role TEXT NOT NULL,
    content TEXT NOT NULL,
    timestamp TIMESTAMPTZ DEFAULT NOW()
);

-- exam_attempts table
CREATE TABLE exam_attempts (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id BIGINT REFERENCES users(id) ON DELETE CASCADE,
    exam_type TEXT NOT NULL,
    level TEXT NOT NULL,
    score DECIMAL(5,2),
    answers JSONB,
    started_at TIMESTAMPTZ DEFAULT NOW(),
    completed_at TIMESTAMPTZ,
    is_completed BOOLEAN DEFAULT FALSE
);
```

---

## Key Configuration

### .env
```
TELEGRAM_BOT_TOKEN=8294144624:AAFnAprt-0ZOQgOvwL5neTW-PT2ow11eHdA
SUPABASE_URL=https://zlnoxixvxlexywyzbjqh.supabase.co
SUPABASE_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Inpsbm94aXh2eGxleHl3eXpianFoIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc2ODg0OTExMSwiZXhwIjoyMDg0NDI1MTExfQ.ni9Y_u64H_s33FlXYpfOyoOyPxZxTcrB4yT4dDVcQqU
OPENROUTER_API_KEY=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
```

### OpenRouter API (ai_tutor.py)
```python
MODEL = "meta-llama/llama-3.3-70b-instruct:free"
API_URL = "https://openrouter.ai/api/v1/chat/completions"
```

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

## Verification Plan

1. **Run bot:** `python -m bot.main`
2. **Test /start:** Send to bot, verify user created in Supabase
3. **Test subscription:** Set expiry date in Supabase, verify access control
4. **Test AI chat:** Start German conversation, verify Llama 3.3 responses
5. **Test voice:** Send voice message, verify transcription
6. **Test exam:** Take a vocab quiz, verify scoring
7. **Test progress:** View /progress, verify statistics display


