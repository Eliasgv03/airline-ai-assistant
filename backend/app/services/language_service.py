"""
Language Detection Service

Automatically detects user's language and provides language-specific
instructions for the LLM to ensure responses in the correct language.

Using Lingua for high-accuracy language detection (95%+ accuracy).
"""

import logging

from lingua import Language, LanguageDetectorBuilder

logger = logging.getLogger(__name__)

# Build Lingua detector with supported languages
# Using a focused set for performance (loads only needed language models)
LINGUA_DETECTOR = (
    LanguageDetectorBuilder.from_languages(
        Language.ENGLISH,
        Language.SPANISH,
        Language.PORTUGUESE,
        Language.FRENCH,
        Language.GERMAN,
        Language.ITALIAN,
        Language.HINDI,
        Language.JAPANESE,
        Language.KOREAN,
        Language.CHINESE,
        Language.ARABIC,
        Language.RUSSIAN,
    )
    .with_preloaded_language_models()
    .build()
)

# Map Lingua Language enum to ISO 639-1 codes
LINGUA_TO_ISO = {
    Language.ENGLISH: "en",
    Language.SPANISH: "es",
    Language.PORTUGUESE: "pt",
    Language.FRENCH: "fr",
    Language.GERMAN: "de",
    Language.ITALIAN: "it",
    Language.HINDI: "hi",
    Language.JAPANESE: "ja",
    Language.KOREAN: "ko",
    Language.CHINESE: "zh-cn",
    Language.ARABIC: "ar",
    Language.RUSSIAN: "ru",
}

# ISO 639-1 language code to full name mapping
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

# Keyword patterns for short text detection (avoids langdetect unreliability)
# These are common words/phrases that clearly indicate a language
LANGUAGE_KEYWORDS = {
    "es": [
        "hola",
        "gracias",
        "buenos días",
        "buenas tardes",
        "buenas noches",
        "ayuda",
        "vuelos",
        "equipaje",
        "buscar",
        "cuánto",
        "cuándo",
        "dónde",
        "quiero",
        "necesito",
        "puedo",
        "tengo",
        "cómo",
        "qué",
        "por favor",
        "aeropuerto",
        "avión",
        "pasaje",
        "reserva",
        "cancelar",
        "maleta",
        "dame",
        "dime",
        "mañana",
        "hoy",
        "ayer",
        "vuelo",
        "viajar",
    ],
    "en": [
        "hello",
        "hi",
        "hey",
        "thanks",
        "thank you",
        "help",
        "please",
        "flights",
        "baggage",
        "luggage",
        "book",
        "cancel",
        "airport",
        "how",
        "what",
        "where",
        "when",
        "can",
        "want",
        "need",
        "find",
        "tomorrow",
        "today",
        "search",
        "show",
        "get",
    ],
    "hi": [
        "नमस्ते",
        "धन्यवाद",
        "मदद",
        "कृपया",
        "उड़ान",
        "सामान",
        "हवाई",
        "कब",
        "कहाँ",
        "कैसे",
        "क्या",
        "चाहिए",
        "बुक",
        "रद्द",
    ],
    "pt": [
        "olá",
        "obrigado",
        "obrigada",
        "ajuda",
        "voos",
        "bagagem",
        "aeroporto",
        "quando",
        "onde",
        "como",
        "quero",
        "preciso",
        "amanhã",
        "hoje",
        "procurar",
        "reservar",
        "cancelar",
    ],
    "fr": [
        "bonjour",
        "merci",
        "aide",
        "vols",
        "bagages",
        "aéroport",
        "quand",
        "où",
        "comment",
        "voulez",
        "besoin",
        "chercher",
    ],
}


def detect_language(text: str, default: str = "en", session_hint: str | None = None) -> str:
    """
    Detect language of text using keywords + Lingua.

    Strategy:
    1. Keywords for short texts (< 15 chars) - instant and reliable
    2. Lingua for longer texts - 95%+ accuracy
    3. Session hint as fallback

    Args:
        text: Text to analyze
        default: Default language if detection fails
        session_hint: Previous language detected in session

    Returns:
        ISO 639-1 language code (e.g., 'en', 'es', 'hi')
    """
    if not text or not text.strip():
        logger.warning("Empty text provided for language detection")
        return session_hint or default

    text_clean = text.lower().strip()

    # Stage 1: For short texts, use keyword matching (faster and reliable)
    if len(text_clean) < 15:
        for lang, keywords in LANGUAGE_KEYWORDS.items():
            if text_clean in keywords or any(kw in text_clean for kw in keywords):
                logger.info(f"🌍 Short text detected as {lang}: '{text_clean}'")
                return lang

        # If no keyword match and we have a session hint, use it
        if session_hint:
            logger.info(f"🌍 Using session hint for short text: {session_hint}")
            return session_hint

    # Stage 2: Use Lingua (95%+ accuracy)
    lingua_result = LINGUA_DETECTOR.detect_language_of(text)
    if lingua_result:
        detected = LINGUA_TO_ISO.get(lingua_result, default)
        logger.info(f"🌍 Lingua: {lingua_result.name} ({detected}) for: '{text[:40]}...'")
        return detected

    # Fallback
    logger.warning("⚠️ Lingua could not detect language")
    return session_hint or default


def get_language_name(lang_code: str) -> str:
    """Get full language name from ISO 639-1 code."""
    return LANGUAGE_NAMES.get(lang_code, "English")


def get_language_instruction(lang_code: str) -> str:
    """
    Generate instruction for LLM to respond in specific language.

    This instruction is injected into the system prompt to ensure
    the LLM responds in the user's detected language.
    """
    lang_name = get_language_name(lang_code)

    # Special handling for Spanish/Portuguese confusion
    disambiguation = ""
    if lang_code == "es":
        disambiguation = (
            "\n- **IMPORTANT**: User is speaking SPANISH (not Portuguese). Use Spanish vocabulary."
        )
    elif lang_code == "pt":
        disambiguation = "\n- **IMPORTANT**: User is speaking PORTUGUESE (not Spanish). Use Portuguese vocabulary."

    return f"""
**DETECTED USER LANGUAGE: {lang_name.upper()} ({lang_code})**

**CRITICAL LANGUAGE INSTRUCTION:**
- The user is communicating in **{lang_name}**.
- You MUST respond ENTIRELY in **{lang_name}**.
- Do NOT switch to English unless the user explicitly asks.
- Maintain natural, professional {lang_name} throughout your entire response.{disambiguation}
"""
