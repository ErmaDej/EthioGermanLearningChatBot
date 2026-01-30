"""
Database setup script for EthioGerman Language School Telegram Bot.
Run this script once to create all required tables in Supabase.
"""
import httpx
import os
from dotenv import load_dotenv

load_dotenv()

SUPABASE_URL = os.getenv('SUPABASE_URL')
SUPABASE_KEY = os.getenv('SUPABASE_KEY')

# SQL to create all tables
SETUP_SQL = """
-- Enable UUID extension
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

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
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
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
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
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
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id BIGINT REFERENCES users(id) ON DELETE CASCADE,
    skill TEXT NOT NULL,
    activity_type TEXT,
    score DECIMAL(5,2),
    weak_areas TEXT[],
    completed_at TIMESTAMPTZ DEFAULT NOW()
);

-- Conversation history table
CREATE TABLE IF NOT EXISTS conversation_history (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id BIGINT REFERENCES users(id) ON DELETE CASCADE,
    session_id UUID,
    role TEXT NOT NULL,
    content TEXT NOT NULL,
    timestamp TIMESTAMPTZ DEFAULT NOW()
);

-- Exam attempts table
CREATE TABLE IF NOT EXISTS exam_attempts (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
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
"""


def setup_database():
    """Execute SQL to set up database tables."""
    
    # Use Supabase's REST API with raw SQL via RPC
    # First, let's try using the SQL editor endpoint
    headers = {
        'apikey': SUPABASE_KEY,
        'Authorization': f'Bearer {SUPABASE_KEY}',
        'Content-Type': 'application/json',
        'Prefer': 'return=minimal'
    }
    
    # Split into individual statements and execute via postgrest
    # Actually, we need to use the SQL endpoint or create tables via REST
    # Let's provide the SQL for manual execution in Supabase dashboard
    
    print("=" * 60)
    print("DATABASE SETUP SQL")
    print("=" * 60)
    print("\nPlease run the following SQL in your Supabase SQL Editor:")
    print("(Dashboard -> SQL Editor -> New Query)")
    print("\n" + "=" * 60)
    print(SETUP_SQL)
    print("=" * 60)
    
    # Alternative: Try to create tables via REST API
    print("\n\nAttempting to create tables via API...")
    
    # Create users table by inserting and deleting a test record
    # This won't work for table creation, but we can verify connection
    
    try:
        response = httpx.get(
            f"{SUPABASE_URL}/rest/v1/users",
            headers=headers,
            params={'select': 'id', 'limit': '1'}
        )
        
        if response.status_code == 200:
            print("✓ Connection successful! Tables may already exist.")
            print("  If you see errors later, please run the SQL above in Supabase dashboard.")
        elif response.status_code == 404:
            print("✗ Tables do not exist yet.")
            print("  Please run the SQL above in your Supabase SQL Editor.")
        else:
            print(f"Response: {response.status_code}")
            print(f"Please run the SQL above in your Supabase SQL Editor.")
            
    except Exception as e:
        print(f"Error connecting to Supabase: {e}")
        print("Please run the SQL above in your Supabase SQL Editor.")


if __name__ == '__main__':
    setup_database()
