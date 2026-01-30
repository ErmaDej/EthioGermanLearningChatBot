# Getting Started

<cite>
**Referenced Files in This Document**
- [requirements.txt](file://requirements.txt)
- [setup_database.py](file://setup_database.py)
- [database_setup.sql](file://database_setup.sql)
- [bot/config.py](file://bot/config.py)
- [bot/main.py](file://bot/main.py)
- [bot/services/database.py](file://bot/services/database.py)
- [bot/services/speech.py](file://bot/services/speech.py)
- [bot/handlers/start.py](file://bot/handlers/start.py)
- [bot/utils/formatters.py](file://bot/utils/formatters.py)
</cite>

## Table of Contents
1. [Introduction](#introduction)
2. [Prerequisites](#prerequisites)
3. [Installation](#installation)
4. [Environment Setup](#environment-setup)
5. [Database Initialization](#database-initialization)
6. [First Run](#first-run)
7. [Verification](#verification)
8. [Initial Testing](#initial-testing)
9. [Troubleshooting](#troubleshooting)
10. [Docker Setup](#docker-setup)
11. [Local Development](#local-development)

## Introduction
FebEGLS-bot is a Telegram AI tutor bot designed for German language learning. It provides interactive lessons, exam preparation, progress tracking, and speech practice capabilities powered by AI technologies and Supabase database infrastructure.

## Prerequisites

### Python Environment
- **Python 3.8 or higher** required for optimal compatibility
- Ensure your system meets the minimum Python version requirement before proceeding

### Required Dependencies
The bot requires several key dependencies for full functionality:
- python-telegram-bot >= 20.0 (Telegram bot framework)
- supabase >= 2.0.0 (Supabase database client)
- httpx >= 0.25.0 (HTTP client for API requests)
- python-dotenv >= 1.0.0 (Environment variable management)
- faster-whisper >= 0.9.0 (Voice transcription)
- pydub >= 0.25.1 (Audio processing)

**Section sources**
- [requirements.txt](file://requirements.txt#L1-L7)

## Installation

### Step 1: Clone or Download the Repository
Clone the repository to your local machine using Git or download the source code as a zip file.

### Step 2: Create Virtual Environment
```bash
python -m venv venv
```

### Step 3: Activate Virtual Environment
- **Windows:** `venv\Scripts\activate`
- **Linux/Mac:** `source venv/bin/activate`

### Step 4: Install Dependencies
```bash
pip install -r requirements.txt
```

**Section sources**
- [requirements.txt](file://requirements.txt#L1-L7)

## Environment Setup

### Create .env Configuration File
Create a `.env` file in the project root directory with the following required environment variables:

#### Required Variables
- `TELEGRAM_BOT_TOKEN`: Your Telegram bot token from @BotFather
- `OPENROUTER_API_KEY`: API key for OpenRouter AI services
- `SUPABASE_URL`: Your Supabase project URL
- `SUPABASE_KEY`: Your Supabase project API key

#### Optional Variables
- `VOICE_API_KEY`: Voice API key for speech services (optional)

### Environment Variable Reference
| Variable | Purpose | Required | Example |
|----------|---------|----------|---------|
| TELEGRAM_BOT_TOKEN | Telegram bot authentication | Yes | `123456789:AABBCCDDEEFFGGHHIIJJKKLLMMNNOOPPQQ` |
| OPENROUTER_API_KEY | AI service authentication | Yes | `sk-or-v1-xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx` |
| SUPABASE_URL | Database endpoint URL | Yes | `https://xxxxxxxx.supabase.co` |
| SUPABASE_KEY | Database API key | Yes | `eyJhbGciOiJIUzI1NiIs...` |
| VOICE_API_KEY | Speech service key | No | `your-voice-api-key` |

**Section sources**
- [bot/config.py](file://bot/config.py#L13-L23)

## Database Initialization

### Method 1: Using setup_database.py Script
The recommended approach uses the automated setup script:

1. **Run the database setup script:**
   ```bash
   python setup_database.py
   ```

2. **Follow the on-screen instructions:**
   - The script will display the SQL commands to execute
   - Copy the SQL from the console output
   - Navigate to your Supabase dashboard
   - Go to SQL Editor and paste the SQL
   - Execute the SQL to create all required tables

3. **Verify database setup:**
   - The script will attempt to connect to verify table existence
   - Look for success/failure messages in the console output

### Method 2: Manual SQL Execution
Alternatively, you can manually execute the SQL from the `database_setup.sql` file:

1. **Open Supabase Dashboard**
2. **Navigate to SQL Editor**
3. **Copy and paste the SQL from `database_setup.sql`**
4. **Execute the SQL commands**

### Database Schema Overview
The setup creates the following tables:
- **users**: User profiles and subscription management
- **lessons**: German language lessons by skill and level
- **exam_questions**: Question bank for Goethe exam preparation
- **user_progress**: Learning progress tracking
- **conversation_history**: AI conversation context storage
- **exam_attempts**: Exam attempt records

**Section sources**
- [setup_database.py](file://setup_database.py#L15-L99)
- [database_setup.sql](file://database_setup.sql#L1-L84)

## First Run

### Starting the Bot
1. **Ensure all environment variables are configured**
2. **Verify database tables exist in Supabase**
3. **Run the main bot application:**
   ```bash
   python bot/main.py
   ```

### Expected Startup Output
When the bot starts successfully, you should see:
- Configuration validation passing
- Database connection establishment
- Bot polling initialization
- Ready-to-use status in console logs

### Initial User Registration Flow
Upon first interaction, users will experience:
1. Welcome message with level selection
2. Preferred language choice
3. Profile creation in database
4. Subscription status check

**Section sources**
- [bot/main.py](file://bot/main.py#L60-L89)
- [bot/handlers/start.py](file://bot/handlers/start.py#L16-L74)

## Verification

### Configuration Validation
The bot performs automatic validation of required environment variables:

1. **Check configuration loading:**
   ```python
   # This validates all required variables automatically
   Config.validate()
   ```

2. **Expected validation results:**
   - All required variables present: Configuration OK
   - Missing variables: ValueError with specific missing items

### Database Connectivity Test
1. **Test database connection:**
   ```python
   # The DatabaseService constructor tests Supabase connectivity
   db = DatabaseService()
   ```

2. **Expected outcomes:**
   - Successful connection: Database ready
   - Connection failure: Error logs with connection details

### Telegram Bot Test
1. **Send test commands:**
   - `/start` - Should initiate registration flow
   - `/help` - Should display help information
   - `/menu` - Should show main menu

**Section sources**
- [bot/config.py](file://bot/config.py#L40-L56)
- [bot/services/database.py](file://bot/services/database.py#L19-L21)

## Initial Testing

### Basic Functionality Tests
Perform these tests to ensure proper setup:

#### Test 1: Bot Commands
1. **Command Availability:**
   - `/start` - Registration/welcome flow
   - `/help` - Help information
   - `/menu` - Main navigation
   - `/learn` - Learning interface
   - `/exam` - Exam interface
   - `/progress` - Progress tracking
   - `/settings` - Settings management
   - `/cancel` - Operation cancellation

#### Test 2: Database Operations
1. **User Registration:**
   - Complete registration process
   - Verify user creation in database
   - Check subscription status handling

2. **Progress Tracking:**
   - Complete sample activities
   - Verify progress records
   - Check statistics calculation

#### Test 3: AI Integration
1. **Conversation Testing:**
   - Send sample messages
   - Verify AI responses
   - Check conversation context

#### Test 4: Speech Services (Optional)
1. **Voice Message Testing:**
   - Send voice messages
   - Verify transcription (if available)
   - Check fallback to text input

**Section sources**
- [bot/utils/formatters.py](file://bot/utils/formatters.py#L24-L56)
- [bot/handlers/start.py](file://bot/handlers/start.py#L144-L150)

## Troubleshooting

### Common Setup Issues

#### Issue 1: Missing Environment Variables
**Symptoms:**
- Configuration validation errors
- Bot fails to start
- ValueError about missing configuration

**Solution:**
1. Verify `.env` file exists in project root
2. Check all required variables are present
3. Restart the bot after corrections

#### Issue 2: Database Connection Failures
**Symptoms:**
- Database connection errors
- Supabase API errors
- Empty query results

**Solutions:**
1. **Verify Supabase credentials:**
   - Check SUPABASE_URL format
   - Verify SUPABASE_KEY validity
   - Confirm project accessibility

2. **Database setup verification:**
   - Ensure all tables were created
   - Check SQL execution in Supabase dashboard
   - Verify table permissions

#### Issue 3: Telegram Bot Token Issues
**Symptoms:**
- Telegram API errors
- Bot not responding to commands
- Authentication failures

**Solutions:**
1. **Verify token validity:**
   - Check token format from @BotFather
   - Ensure token hasn't expired
   - Verify bot is active

2. **Network connectivity:**
   - Check firewall settings
   - Verify outbound connections
   - Test proxy configurations if needed

#### Issue 4: Speech Service Unavailable
**Symptoms:**
- Voice transcription disabled warnings
- Speech functionality not working
- Faster-whisper import errors

**Solutions:**
1. **Install speech dependencies:**
   ```bash
   pip install faster-whisper pydub
   ```

2. **System requirements:**
   - Ensure sufficient disk space for model downloads
   - Check Python version compatibility
   - Verify CPU/GPU support if using CUDA

#### Issue 5: Permission Denied Errors
**Symptoms:**
- Database permission errors
- File system access issues
- Network connectivity problems

**Solutions:**
1. **Database permissions:**
   - Check Supabase row-level security policies
   - Verify API key permissions
   - Confirm table access rights

2. **File system permissions:**
   - Check temporary directory access
   - Verify write permissions for logs

### Error Logging and Debugging
The bot includes comprehensive logging:

1. **Console logging:**
   - Informational messages during startup
   - Error details for troubleshooting
   - Debug information for development

2. **File logging:**
   - Log file creation (`bot.log`)
   - Persistent error tracking
   - Historical debugging information

**Section sources**
- [bot/main.py](file://bot/main.py#L28-L42)
- [bot/services/speech.py](file://bot/services/speech.py#L13-L18)

## Docker Setup

### Docker Configuration
While the project doesn't include a Dockerfile, you can containerize the bot using the following approach:

#### Dockerfile Template
```dockerfile
FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

ENV PYTHONPATH=/app

CMD ["python", "bot/main.py"]
```

#### Docker Compose Template
```yaml
version: '3.8'
services:
  telegram-bot:
    build: .
    env_file:
      - .env
    volumes:
      - ./logs:/app/logs
    restart: unless-stopped
```

#### Build and Run Commands
```bash
# Build the image
docker build -t febegls-bot .

# Run the container
docker run -d \
  --name febegls-bot \
  --env-file .env \
  --restart unless-stopped \
  febegls-bot
```

### Docker Environment Variables
When using Docker, ensure all environment variables are properly configured in your Docker environment or docker-compose file.

## Local Development

### Development Environment Setup
1. **Fork and clone the repository**
2. **Create development branch:**
   ```bash
   git checkout -b develop
   ```

3. **Install development dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

4. **Configure development .env file:**
   - Use test Telegram bot token
   - Set up development database
   - Configure debug logging

### Development Workflow
1. **Code modifications:**
   - Follow existing code patterns
   - Maintain backward compatibility
   - Add appropriate logging

2. **Testing:**
   - Test locally before commits
   - Verify database operations
   - Check error handling

3. **Documentation:**
   - Update README with changes
   - Document new features
   - Update API documentation

### Hot Reload Development
For rapid development cycles, consider using:
```bash
# Install watch mode tool
pip install watchdog

# Monitor file changes and restart on modifications
```

### Debug Mode Configuration
Enable debug logging for development:
```python
# In your .env file
LOG_LEVEL=DEBUG
```

**Section sources**
- [bot/main.py](file://bot/main.py#L28-L42)