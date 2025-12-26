"""
Test Gemini Model Pool Configuration

This script tests the model pool fallback mechanism to ensure all models
are accessible and the fallback logic works correctly.
"""

# ruff: noqa: E402
import asyncio
from pathlib import Path
import sys

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from app.core.config import get_settings
from app.services.gemini_service import get_llm
from app.utils.logger import get_logger

logger = get_logger(__name__)

settings = get_settings()


def test_model_availability():
    """Test each model in the pool for availability"""
    logger.info("=" * 80)
    logger.info("🧪 TESTING GEMINI MODEL POOL")
    logger.info("=" * 80)

    if not settings.GOOGLE_API_KEY:
        logger.error("❌ GOOGLE_API_KEY not set in environment")
        return False

    logger.info(f"\n📋 Model Pool Configuration ({len(settings.GEMINI_MODEL_POOL)} models):")
    for i, model in enumerate(settings.GEMINI_MODEL_POOL, 1):
        logger.info(f"  {i}. {model}")

    logger.info(f"\n🎯 Primary Model: {settings.GEMINI_MODEL}")

    # Test each model
    results = {}
    test_prompt = "Say 'Hello' in one word."

    for model_name in settings.GEMINI_MODEL_POOL:
        logger.info(f"\n{'=' * 80}")
        logger.info(f"Testing Model: {model_name}")
        logger.info("-" * 80)

        try:
            # Initialize LLM with specific model
            llm = get_llm(temperature=0.1, model_name=model_name)
            logger.info("✅ Model initialized successfully")

            # Test simple invocation
            from langchain.schema import HumanMessage

            response = llm.invoke([HumanMessage(content=test_prompt)])
            logger.info(f"✅ Model responded: {response.content[:50]}...")

            results[model_name] = {
                "status": "success",
                "response": response.content,
            }

        except Exception as e:
            error_msg = str(e)
            logger.error(f"❌ Model failed: {error_msg[:100]}...")

            results[model_name] = {
                "status": "failed",
                "error": error_msg,
            }

    # Summary
    logger.info(f"\n{'=' * 80}")
    logger.info("📊 TEST RESULTS SUMMARY")
    logger.info("=" * 80)

    successful = [m for m, r in results.items() if r["status"] == "success"]
    failed = [m for m, r in results.items() if r["status"] == "failed"]

    logger.info(f"\n✅ Successful: {len(successful)}/{len(results)}")
    for model in successful:
        logger.info(f"  ✓ {model}")

    if failed:
        logger.info(f"\n❌ Failed: {len(failed)}/{len(results)}")
        for model in failed:
            error = results[model]["error"]
            logger.info(f"  ✗ {model}")
            logger.info(f"    Error: {error[:100]}...")

    # Recommendations
    logger.info(f"\n{'=' * 80}")
    logger.info("💡 RECOMMENDATIONS")
    logger.info("=" * 80)

    if len(successful) == 0:
        logger.warning("⚠️ No models working! Check your GOOGLE_API_KEY")
    elif len(successful) < len(results):
        logger.info(f"✅ Fallback working: {len(successful)} models available")
        logger.info(f"   Primary model: {settings.GEMINI_MODEL_POOL[0]}")
        if settings.GEMINI_MODEL_POOL[0] not in successful:
            logger.warning(f"⚠️ Primary model ({settings.GEMINI_MODEL_POOL[0]}) failed!")
            logger.warning(f"   Will fallback to: {successful[0]}")
    else:
        logger.info("🎉 All models working perfectly!")

    logger.info("=" * 80)

    return len(successful) > 0


async def test_streaming():
    """Test streaming with the model pool"""
    logger.info(f"\n{'=' * 80}")
    logger.info("🌊 TESTING STREAMING FUNCTIONALITY")
    logger.info("=" * 80)

    try:
        from langchain.schema import HumanMessage

        llm = get_llm(temperature=0.1)
        logger.info(f"Using model: {settings.GEMINI_MODEL_POOL[0]}")

        chunks = []
        async for chunk in llm.astream([HumanMessage(content="Count to 5")]):
            if hasattr(chunk, "content") and chunk.content:
                chunks.append(chunk.content)
                logger.info(f"Chunk: {chunk.content}")

        full_response = "".join(chunks)
        logger.info("\n✅ Streaming successful!")
        logger.info(f"   Total chunks: {len(chunks)}")
        logger.info(f"   Full response: {full_response}")

        return True

    except Exception as e:
        logger.error(f"❌ Streaming failed: {str(e)}")
        return False


def main():
    """Run all tests"""
    logger.info("🚀 Starting Gemini Model Pool Tests\n")

    # Test 1: Model availability
    availability_ok = test_model_availability()

    # Test 2: Streaming (only if at least one model works)
    if availability_ok:
        streaming_ok = asyncio.run(test_streaming())
    else:
        logger.warning("⚠️ Skipping streaming test (no models available)")
        streaming_ok = False

    # Final verdict
    logger.info(f"\n{'=' * 80}")
    logger.info("🏁 FINAL VERDICT")
    logger.info("=" * 80)

    if availability_ok and streaming_ok:
        logger.info("🎉 ALL TESTS PASSED!")
        logger.info("   Model pool is configured correctly and working.")
        return 0
    elif availability_ok:
        logger.warning("⚠️ PARTIAL SUCCESS")
        logger.warning("   Models work but streaming has issues.")
        return 1
    else:
        logger.error("❌ TESTS FAILED")
        logger.error("   Check your configuration and API key.")
        return 2


if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)
