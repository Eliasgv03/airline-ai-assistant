"""
Language Detection Service

Automatically detects user's language and provides language-specific
instructions for the LLM to ensure responses in the correct language.
"""

import logging
import re

from langdetect import LangDetectException, detect

logger = logging.getLogger(__name__)

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

# Words that distinguish Spanish from Portuguese
SPANISH_DISTINCTIVE = [
    "vuelo",
    "vuelos",
    "equipaje",
    "buscar",
    "cuánto",
    "cuándo",
    "dónde",
    "mañana",
    "avión",
]
PORTUGUESE_DISTINCTIVE = [
    "voo",
    "voos",
    "bagagem",
    "procurar",
    "quanto",
    "quando",
    "onde",
    "amanhã",
    "avião",
]

# Words that distinguish Italian from Spanish (to prevent misdetection)
ITALIAN_DISTINCTIVE = [
    "volo",
    "voli",
    "bagaglio",
    "cercare",
    "quanto",
    "quando",
    "dove",
    "domani",
    "aereo",
    "grazie",
    "prego",
    "scusa",
    "buongiorno",
    "arrivederci",
]


def detect_language(text: str, default: str = "en", session_hint: str | None = None) -> str:
    """
    Detect language of text with improved reliability for short texts.

    Uses a multi-stage approach:
    1. Keyword matching for short texts (< 15 chars)
    2. Spanish/Portuguese disambiguation
    3. langdetect for longer texts
    4. Session hint as fallback

    Args:
        text: Text to analyze
        default: Default language if detection fails
        session_hint: Previous language detected in session (helps with continuity)

    Returns:
        ISO 639-1 language code (e.g., 'en', 'es', 'hi')
    """
    if not text or not text.strip():
        logger.warning("Empty text provided for language detection")
        return session_hint or default

    text_clean = text.lower().strip()
    text_words = set(re.findall(r"\b\w+\b", text_clean))

    # Stage 1: For short texts, use keyword matching (more reliable than langdetect)
    if len(text_clean) < 15:
        for lang, keywords in LANGUAGE_KEYWORDS.items():
            if text_clean in keywords or any(kw in text_clean for kw in keywords):
                logger.info(f"🌍 Short text detected as {lang}: '{text_clean}'")
                return lang

        # If no keyword match and we have a session hint, use it
        if session_hint:
            logger.info(f"🌍 Using session hint for short text: {session_hint}")
            return session_hint

    # Stage 2: Spanish/Portuguese disambiguation
    spanish_matches = len(text_words & set(SPANISH_DISTINCTIVE))
    portuguese_matches = len(text_words & set(PORTUGUESE_DISTINCTIVE))

    if spanish_matches > portuguese_matches and spanish_matches > 0:
        logger.info(f"🌍 Spanish detected via distinctive words ({spanish_matches} matches)")
        return "es"
    elif portuguese_matches > spanish_matches and portuguese_matches > 0:
        logger.info(f"🌍 Portuguese detected via distinctive words ({portuguese_matches} matches)")
        return "pt"

    # Stage 3: Use langdetect for longer texts
    try:
        detected = str(detect(text))
        logger.info(f"🌍 langdetect result: {detected} for text: '{text[:50]}...'")

        # Post-process langdetect results
        # If langdetect says Portuguese but we have Spanish keywords, prefer Spanish
        if detected == "pt":
            spanish_keyword_count = sum(1 for kw in LANGUAGE_KEYWORDS["es"] if kw in text_clean)
            if spanish_keyword_count >= 2:
                logger.info(f"🌍 Overriding pt→es due to {spanish_keyword_count} Spanish keywords")
                return "es"

        # If langdetect says Italian but we have Spanish keywords, prefer Spanish
        # This is a common misdetection for short Spanish texts
        if detected == "it":
            spanish_keyword_count = sum(1 for kw in LANGUAGE_KEYWORDS["es"] if kw in text_clean)
            italian_keyword_count = sum(1 for kw in ITALIAN_DISTINCTIVE if kw in text_clean)
            if spanish_keyword_count > italian_keyword_count:
                logger.info(
                    f"🌍 Overriding it→es due to {spanish_keyword_count} Spanish vs {italian_keyword_count} Italian keywords"
                )
                return "es"
            # Also check if session hint is Spanish - maintain language continuity
            if session_hint == "es" and italian_keyword_count == 0:
                logger.info("🌍 Overriding it→es due to session hint (no Italian keywords found)")
                return "es"

        return detected

    except LangDetectException as e:
        logger.warning(f"⚠️ langdetect failed: {e}")
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
