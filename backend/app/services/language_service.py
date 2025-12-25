"""
Language Detection Service

Automatically detects user's language and provides language-specific
instructions for the LLM to ensure responses in the correct language.
"""

import logging

from langdetect import LangDetectException, detect

logger = logging.getLogger(__name__)

# Mapeo de códigos ISO 639-1 a nombres completos
LANGUAGE_NAMES = {
    "en": "English",
    "es": "Spanish",
    "hi": "Hindi",
    "fr": "French",
    "de": "German",
    "pt": "Portuguese",
    "it": "Italian",
    "ja": "Japanese",
    "ko": "Korean",
    "zh-cn": "Chinese",
    "ar": "Arabic",
    "ru": "Russian",
    "nl": "Dutch",
    "sv": "Swedish",
    "pl": "Polish",
    "tr": "Turkish",
}


def detect_language(text: str, default: str = "en") -> str:
    """
    Detect language of text using langdetect.

    Args:
        text: Text to analyze
        default: Default language if detection fails (default: 'en')

    Returns:
        ISO 639-1 language code (e.g., 'en', 'es', 'hi')

    """
    if not text or not text.strip():
        logger.warning("Empty text provided for language detection")
        return default

    try:
        # Detectar idioma
        lang_code = detect(text)
        logger.info(f"🌍 Detected language: {lang_code} for text: '{text[:50]}...'")
        return lang_code
    except LangDetectException as e:
        logger.warning(f"⚠️ Language detection failed: {e}. Using default: {default}")
        return default


def get_language_name(lang_code: str) -> str:
    """
    Get full language name from ISO 639-1 code.

    Args:
        lang_code: ISO 639-1 language code

    Returns:
        Full language name (defaults to 'English' if unknown)

    """
    return LANGUAGE_NAMES.get(lang_code, "English")


def get_language_instruction(lang_code: str) -> str:
    """
    Generate instruction for LLM to respond in specific language.

    This instruction is injected into the system prompt to ensure
    the LLM responds in the user's detected language.

    Args:
        lang_code: ISO 639-1 language code

    Returns:
        Instruction string for system prompt

    """
    lang_name = get_language_name(lang_code)

    return f"""
**DETECTED USER LANGUAGE: {lang_name.upper()} ({lang_code})**

**CRITICAL INSTRUCTION:**
- The user is communicating in **{lang_name}**.
- You MUST respond ENTIRELY in **{lang_name}**.
- Do NOT use English unless the user explicitly switches to English.
- Maintain natural, professional {lang_name} throughout your response.
- Use appropriate greetings and cultural context for {lang_name} speakers.
"""
