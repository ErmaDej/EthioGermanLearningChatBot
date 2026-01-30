-- EthioGerman Language School - Database Setup
-- Run this SQL in Supabase SQL Editor

-- Users table
CREATE TABLE IF NOT EXISTS users (
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

-- Lessons table
CREATE TABLE IF NOT EXISTS lessons (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    level TEXT NOT NULL,
    skill TEXT NOT NULL,
    topic TEXT,
    title TEXT NOT NULL,
    content JSONB,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Exam questions table
CREATE TABLE IF NOT EXISTS exam_questions (
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

-- User progress table
CREATE TABLE IF NOT EXISTS user_progress (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id BIGINT REFERENCES users(id) ON DELETE CASCADE,
    skill TEXT NOT NULL,
    activity_type TEXT,
    score DECIMAL(5,2),
    weak_areas TEXT[],
    completed_at TIMESTAMPTZ DEFAULT NOW()
);

-- Conversation history table
CREATE TABLE IF NOT EXISTS conversation_history (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id BIGINT REFERENCES users(id) ON DELETE CASCADE,
    session_id UUID,
    role TEXT NOT NULL,
    content TEXT NOT NULL,
    timestamp TIMESTAMPTZ DEFAULT NOW()
);

-- Exam attempts table
CREATE TABLE IF NOT EXISTS exam_attempts (
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

-- Create indexes for performance
CREATE INDEX IF NOT EXISTS idx_users_subscription ON users(subscription_expiry);
CREATE INDEX IF NOT EXISTS idx_lessons_level_skill ON lessons(level, skill);
CREATE INDEX IF NOT EXISTS idx_exam_questions_level_type ON exam_questions(level, exam_type);
CREATE INDEX IF NOT EXISTS idx_user_progress_user ON user_progress(user_id);
CREATE INDEX IF NOT EXISTS idx_conversation_history_user ON conversation_history(user_id, session_id);
CREATE INDEX IF NOT EXISTS idx_exam_attempts_user ON exam_attempts(user_id);
