"""
Quick script to verify LLM_PROVIDER configuration is being read correctly
"""

from app.core.config import get_settings

settings = get_settings()

print("=" * 80)
print("LLM CONFIGURATION CHECK")
print("=" * 80)
print(f"\nLLM_PROVIDER: {settings.LLM_PROVIDER}")
print(f"\nGemini API Key: {'✅ Set' if settings.GOOGLE_API_KEY else '❌ Not set'}")
print(f"Groq API Key: {'✅ Set' if settings.GROQ_API_KEY else '❌ Not set'}")

print(f"\nGemini Model Pool ({len(settings.GEMINI_MODEL_POOL)} models):")
for i, model in enumerate(settings.GEMINI_MODEL_POOL, 1):
    print(f"  {i}. {model}")

print(f"\nGroq Model Pool ({len(settings.GROQ_MODEL_POOL)} models):")
for i, model in enumerate(settings.GROQ_MODEL_POOL, 1):
    print(f"  {i}. {model}")

print("\n" + "=" * 80)
if settings.LLM_PROVIDER == "groq":
    if settings.GROQ_API_KEY:
        print("✅ Groq is configured and ready to use")
    else:
        print("❌ Groq selected but GROQ_API_KEY not set!")
elif settings.LLM_PROVIDER == "gemini":
    if settings.GOOGLE_API_KEY:
        print("✅ Gemini is configured and ready to use")
    else:
        print("❌ Gemini selected but GOOGLE_API_KEY not set!")
else:
    print(f"⚠️ Unknown provider: {settings.LLM_PROVIDER}")
print("=" * 80)
