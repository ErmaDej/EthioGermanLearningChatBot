"""
Speech processing service using faster-whisper for voice transcription.
"""
import os
import logging
import tempfile
from typing import Optional
from pathlib import Path

logger = logging.getLogger(__name__)

# Try to import faster-whisper
WHISPER_AVAILABLE = False
try:
    from faster_whisper import WhisperModel
    WHISPER_AVAILABLE = True
except ImportError:
    logger.warning("faster-whisper not available. Voice transcription will be disabled.")


class SpeechService:
    """Service for speech-to-text transcription."""
    
    def __init__(self):
        self.model = None
        self.model_size = "base"  # Options: tiny, base, small, medium, large
        
        if WHISPER_AVAILABLE:
            try:
                # Use CPU for compatibility, can change to "cuda" for GPU
                self.model = WhisperModel(
                    self.model_size,
                    device="cpu",
                    compute_type="int8"
                )
                logger.info(f"Whisper model '{self.model_size}' loaded successfully")
            except Exception as e:
                logger.error(f"Failed to load Whisper model: {e}")
    
    @property
    def is_available(self) -> bool:
        """Check if speech transcription is available."""
        return self.model is not None
    
    async def transcribe_audio(
        self,
        audio_path: str,
        language: str = "de"
    ) -> Optional[str]:
        """
        Transcribe audio file to text.
        
        Args:
            audio_path: Path to audio file (OGG, WAV, MP3)
            language: Language code (de for German)
        
        Returns:
            Transcribed text or None if failed
        """
        if not self.is_available:
            logger.warning("Whisper model not available for transcription")
            return None
        
        try:
            # Transcribe with German language hint
            segments, info = self.model.transcribe(
                audio_path,
                language=language,
                beam_size=5,
                vad_filter=True  # Filter out non-speech
            )
            
            # Combine all segments
            transcription = " ".join(segment.text for segment in segments)
            
            logger.info(f"Transcribed audio: {transcription[:100]}...")
            return transcription.strip()
        
        except Exception as e:
            logger.error(f"Error transcribing audio: {e}")
            return None
    
    async def transcribe_telegram_voice(
        self,
        voice_file,
        bot
    ) -> Optional[str]:
        """
        Transcribe a Telegram voice message.
        
        Args:
            voice_file: Telegram Voice or Audio object
            bot: Telegram Bot instance for downloading
        
        Returns:
            Transcribed text or None
        """
        if not self.is_available:
            return None
        
        temp_path = None
        try:
            # Download voice file
            file = await bot.get_file(voice_file.file_id)
            
            # Create temp file for the audio
            with tempfile.NamedTemporaryFile(suffix='.ogg', delete=False) as temp:
                temp_path = temp.name
            
            # Download to temp file
            await file.download_to_drive(temp_path)
            
            # Transcribe
            transcription = await self.transcribe_audio(temp_path)
            
            return transcription
        
        except Exception as e:
            logger.error(f"Error processing Telegram voice: {e}")
            return None
        
        finally:
            # Cleanup temp file
            if temp_path and os.path.exists(temp_path):
                try:
                    os.remove(temp_path)
                except:
                    pass
    
    def get_status_message(self) -> str:
        """Get status message about speech service availability."""
        if self.is_available:
            return "Voice messages are supported. Send a voice message to practice speaking!"
        else:
            return "Voice transcription is currently unavailable. Please type your responses."


# Singleton instance
speech_service = SpeechService()
