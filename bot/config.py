import os
from dotenv import load_dotenv
from pathlib import Path

# Load environment variables
env_path = Path(__file__).parent.parent / '.env'
load_dotenv(env_path)


class Config:
    """Application configuration loaded from environment variables."""
    
    # Telegram
    TELEGRAM_BOT_TOKEN: str = os.getenv('TELEGRAM_BOT_TOKEN', '')
    
    # Supabase
    SUPABASE_URL: str = os.getenv('SUPABASE_URL', '')
    SUPABASE_KEY: str = os.getenv('SUPABASE_KEY', '')
    
    # OpenRouter
    OPENROUTER_API_KEY: str = os.getenv('OPENROUTER_API_KEY', '')
    OPENROUTER_API_URL: str = 'https://openrouter.ai/api/v1/chat/completions'
    AI_MODEL: str = 'google/gemini-2.0-flash-exp:free'
    
    # CEFR Levels
    CEFR_LEVELS: list = ['A1', 'A2', 'B1']
    
    # Skills
    SKILLS: list = ['lesen', 'horen', 'schreiben', 'sprechen', 'vokabular']
    
    # Explanation Languages
    EXPLANATION_LANGS: list = ['english', 'amharic', 'german']
    
    # Session timeout (minutes)
    SESSION_TIMEOUT: int = 30
    
    # Max conversation history for AI context
    MAX_CONVERSATION_HISTORY: int = 10
    
    @classmethod
    def validate(cls) -> bool:
        """Validate that all required configuration is present."""
        required = [
            ('TELEGRAM_BOT_TOKEN', cls.TELEGRAM_BOT_TOKEN),
            ('SUPABASE_URL', cls.SUPABASE_URL),
            ('SUPABASE_KEY', cls.SUPABASE_KEY),
            ('OPENROUTER_API_KEY', cls.OPENROUTER_API_KEY),
        ]
        
        missing = [name for name, value in required if not value]
        
        if missing:
            raise ValueError(f"Missing required configuration: {', '.join(missing)}")
        
        return True


# Validate on import
Config.validate()
