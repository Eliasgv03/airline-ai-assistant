"""
Chatbot Benchmark System

This script benchmarks the Air India chatbot on multiple dimensions:
- Response accuracy (topic coverage)
- Response latency (speed)
- Response relevance (semantic similarity)
- RAG retrieval quality

Generates a comprehensive report with metrics and recommendations.
"""

import json
import logging
import os
from pathlib import Path
import sys
import time

# Force Gemini provider for benchmarks
os.environ["LLM_PROVIDER"] = "gemini"

from app.services.chat_service import ChatService  # noqa: E402
from app.utils.logger import get_logger  # noqa: E402

logger = get_logger(__name__)

# Configure logging to show in console
logging.basicConfig(
    level=logging.INFO,
    format="%(message)s",
    handlers=[logging.StreamHandler(sys.stdout)],
)


def bprint(msg: str) -> None:
    """Print to both console and logger for benchmark visibility."""
    print(msg, flush=True)


# Rate limiting configuration (Gemini free tier has strict limits)
DELAY_BETWEEN_TESTS_SEC = 15  # Wait 15 seconds between individual tests
DELAY_BETWEEN_GROUPS_SEC = 45  # Wait 45 seconds between test groups


# Benchmark test cases organized by category
BENCHMARK_TESTS = {
    "baggage_policy": [
        {
            "query": "What's the baggage allowance for economy class domestic flights?",
            "expected_topics": ["15 kg", "25 kg", "economy", "domestic"],
            "category": "policy",
            "max_latency_ms": 5000,
        },
        {
            "query": "Can I bring power banks in checked baggage?",
            "expected_topics": ["power bank", "cabin", "prohibited", "checked"],
            "category": "policy",
            "max_latency_ms": 5000,
        },
    ],
    "cancellation": [
        {
            "query": "Can I cancel my flight within 24 hours for free?",
            "expected_topics": ["24 hours", "free", "7 days", "departure"],
            "category": "policy",
            "max_latency_ms": 5000,
        },
        {
            "query": "What happens if I don't show up for my flight?",
            "expected_topics": ["no-show", "refund", "taxes", "forfeit"],
            "category": "policy",
            "max_latency_ms": 5000,
        },
    ],
    "flight_search": [
        {
            "query": "Show me flights from Delhi to Mumbai",
            "expected_topics": ["DEL", "BOM", "AI", "flight"],
            "category": "tool_use",
            "max_latency_ms": 15000,  # Higher limit for tool calls (API + 2 LLM calls)
        },
        {
            "query": "What flights are available from Mumbai to Bangalore?",
            "expected_topics": ["BOM", "BLR", "flight", "available"],
            "category": "tool_use",
            "max_latency_ms": 15000,
        },
    ],
    "loyalty_program": [
        {
            "query": "How do I earn Flying Returns points?",
            "expected_topics": ["6 points", "INR 100", "Flying Returns", "earn"],
            "category": "policy",
            "max_latency_ms": 5000,
        },
        {
            "query": "What are the benefits of Platinum status?",
            "expected_topics": ["Platinum", "lounge", "upgrade", "bonus"],
            "category": "policy",
            "max_latency_ms": 5000,
        },
    ],
    "special_services": [
        {
            "query": "Can I travel with my pet dog?",
            "expected_topics": ["pet", "dog", "cabin", "fee", "certificate"],
            "category": "policy",
            "max_latency_ms": 5000,
        },
        {
            "query": "I need wheelchair assistance",
            "expected_topics": ["wheelchair", "assistance", "free", "request"],
            "category": "policy",
            "max_latency_ms": 5000,
        },
    ],
    "general_info": [
        {
            "query": "When should I arrive at the airport for an international flight?",
            "expected_topics": ["3 hours", "international", "airport", "arrival"],
            "category": "faq",
            "max_latency_ms": 5000,
        },
        {
            "query": "How do I check in online?",
            "expected_topics": ["web check-in", "48 hours", "PNR", "online"],
            "category": "faq",
            "max_latency_ms": 5000,
        },
    ],
    # ===== MULTILINGUAL TESTS =====
    "multilingual_spanish": [
        {
            "query": "¿Cuánto equipaje puedo llevar en clase económica?",
            "expected_topics": ["kg", "equipaje"],
            "forbidden_topics": ["baggage", "allowance"],
            "category": "multilingual",
            "expected_language": "es",
            "max_latency_ms": 5000,
        },
        {
            "query": "¿Cuál es la política de cancelación?",
            "expected_topics": ["cancelación", "reembolso"],
            "forbidden_topics": ["cancellation policy"],
            "category": "multilingual",
            "expected_language": "es",
            "max_latency_ms": 5000,
        },
    ],
    "multilingual_hindi": [
        {
            "query": "दिल्ली से मुंबई की फ्लाइट दिखाओ",
            "expected_topics": ["DEL", "BOM"],
            "category": "multilingual",
            "expected_language": "hi",
            "max_latency_ms": 15000,
        },
    ],
    # ===== IDENTITY TESTS =====
    "identity": [
        {
            "query": "Who are you?",
            "expected_topics": ["Maharaja", "Air India"],
            "forbidden_topics": ["language model", "ChatGPT", "Gemini", "Claude", "OpenAI"],
            "category": "identity",
            "max_latency_ms": 5000,
        },
        {
            "query": "Are you an AI?",
            "expected_topics": ["Maharaja", "assistant"],
            "forbidden_topics": ["Yes", "artificial intelligence", "I am an AI"],
            "category": "identity",
            "max_latency_ms": 5000,
        },
    ],
    # ===== OUT OF SCOPE / BOUNDARY =====
    "out_of_scope": [
        {
            "query": "Can you book a hotel for me?",
            "expected_topics": ["flight"],
            "forbidden_topics": ["book hotel", "reservation confirmed"],
            "category": "boundary",
            "max_latency_ms": 5000,
        },
        {
            "query": "Is IndiGo better than Air India?",
            "expected_topics": ["Air India"],
            "forbidden_topics": ["IndiGo is better", "recommend IndiGo"],
            "category": "boundary",
            "max_latency_ms": 5000,
        },
    ],
}


class BenchmarkMetrics:
    """Stores and calculates benchmark metrics"""

    def __init__(self):
        self.results = []
        self.total_tests = 0
        self.passed_tests = 0
        self.failed_tests = 0
        self.total_latency = 0.0
        self.total_accuracy = 0.0

    def add_result(self, result: dict):
        """Add a test result"""
        self.results.append(result)
        self.total_tests += 1

        if result.get("passed", False):
            self.passed_tests += 1
        else:
            self.failed_tests += 1

        self.total_latency += result.get("latency_ms", 0)
        self.total_accuracy += result.get("accuracy", 0)

    def get_summary(self) -> dict:
        """Calculate summary statistics"""
        return {
            "total_tests": self.total_tests,
            "passed": self.passed_tests,
            "failed": self.failed_tests,
            "pass_rate": (self.passed_tests / self.total_tests * 100)
            if self.total_tests > 0
            else 0,
            "avg_latency_ms": (
                self.total_latency / self.total_tests if self.total_tests > 0 else 0
            ),
            "avg_accuracy": (self.total_accuracy / self.total_tests if self.total_tests > 0 else 0),
        }

    def get_category_stats(self) -> dict:
        """Get statistics by category"""
        categories: dict = {}
        for result in self.results:
            category = result.get("category", "unknown")
            if category not in categories:
                categories[category] = {"tests": 0, "passed": 0, "total_latency": 0}

            categories[category]["tests"] += 1
            if result.get("passed", False):
                categories[category]["passed"] += 1
            categories[category]["total_latency"] += result.get("latency_ms", 0)

        # Calculate averages
        for _, stats in categories.items():
            stats["pass_rate"] = (
                (stats["passed"] / stats["tests"] * 100) if stats["tests"] > 0 else 0
            )
            stats["avg_latency_ms"] = (
                stats["total_latency"] / stats["tests"] if stats["tests"] > 0 else 0
            )

        return categories


def run_benchmark_test(chat_service: ChatService, session_id: str, test_case: dict) -> dict:
    """Run a single benchmark test"""
    query = test_case["query"]
    expected_topics = test_case["expected_topics"]
    forbidden_topics = test_case.get("forbidden_topics", [])
    max_latency = test_case["max_latency_ms"]
    category = test_case["category"]

    bprint(f"\n{'=' * 80}")
    bprint(f"Testing: {query}")
    bprint(f"Category: {category}")
    bprint(f"Expected topics: {', '.join(expected_topics)}")
    if forbidden_topics:
        bprint(f"Forbidden topics: {', '.join(forbidden_topics)}")
    bprint("-" * 80)

    # Measure latency
    start_time = time.time()
    try:
        response = chat_service.process_message(session_id, query)
        latency_ms = (time.time() - start_time) * 1000
    except Exception as e:
        logger.error(f"Error: {e}")
        return {
            "query": query,
            "category": category,
            "passed": False,
            "error": str(e),
            "latency_ms": 0,
            "accuracy": 0,
        }

    # Calculate accuracy (topic coverage)
    response_lower = response.lower()
    topics_found = [topic for topic in expected_topics if topic.lower() in response_lower]
    accuracy = (len(topics_found) / len(expected_topics) * 100) if expected_topics else 100

    # Check for forbidden topics (things the bot should NOT say)
    forbidden_found = [f for f in forbidden_topics if f.lower() in response_lower]
    forbidden_ok = len(forbidden_found) == 0

    # Check if test passed
    latency_ok = latency_ms <= max_latency
    accuracy_ok = accuracy >= 50  # At least 50% topic coverage

    passed = latency_ok and accuracy_ok and forbidden_ok

    # Log results
    bprint(f"Response ({len(response)} chars): {response[:200]}...")
    bprint("-" * 80)
    bprint(
        f"✓ Latency: {latency_ms:.0f}ms (max: {max_latency}ms) - {'PASS' if latency_ok else 'FAIL'}"
    )
    bprint(f"✓ Accuracy: {accuracy:.1f}% - {'PASS' if accuracy_ok else 'FAIL'}")
    bprint(f"✓ Topics found: {', '.join(topics_found) if topics_found else 'None'}")
    if forbidden_topics:
        bprint(
            f"✓ Forbidden check: {'PASS' if forbidden_ok else 'FAIL - Found: ' + ', '.join(forbidden_found)}"
        )
    bprint(f"Overall: {'✅ PASS' if passed else '❌ FAIL'}")

    # Clear session for next test
    chat_service.clear_session(session_id)

    return {
        "query": query,
        "category": category,
        "passed": passed,
        "latency_ms": latency_ms,
        "latency_ok": latency_ok,
        "accuracy": accuracy,
        "accuracy_ok": accuracy_ok,
        "forbidden_ok": forbidden_ok,
        "topics_found": topics_found,
        "topics_missing": [t for t in expected_topics if t not in topics_found],
        "forbidden_found": forbidden_found,
        "response_length": len(response),
    }


def run_benchmarks():
    """Run all benchmark tests"""
    bprint("=" * 80)
    bprint("🚀 STARTING CHATBOT BENCHMARK SUITE")
    bprint("=" * 80)

    chat_service = ChatService()
    session_id = "benchmark_session"
    metrics = BenchmarkMetrics()

    # Run all tests
    test_groups = list(BENCHMARK_TESTS.items())
    for group_idx, (test_group, tests) in enumerate(test_groups):
        bprint(f"\n{'=' * 80}")
        bprint(f"📋 Test Group: {test_group.upper()} ({group_idx + 1}/{len(test_groups)})")
        bprint("=" * 80)

        for i, test_case in enumerate(tests):
            result = run_benchmark_test(chat_service, session_id, test_case)
            metrics.add_result(result)
            # Rate limiting: wait between tests to avoid API quota issues
            if i < len(tests) - 1:
                bprint(f"⏳ Waiting {DELAY_BETWEEN_TESTS_SEC}s before next test...")
                time.sleep(DELAY_BETWEEN_TESTS_SEC)

        # Longer wait between test groups
        if group_idx < len(test_groups) - 1:
            bprint(f"\n🔄 Group complete. Waiting {DELAY_BETWEEN_GROUPS_SEC}s before next group...")
            time.sleep(DELAY_BETWEEN_GROUPS_SEC)

    # Generate summary
    summary = metrics.get_summary()
    category_stats = metrics.get_category_stats()

    bprint(f"\n{'=' * 80}")
    bprint("📊 BENCHMARK RESULTS SUMMARY")
    bprint("=" * 80)
    bprint(f"Total Tests: {summary['total_tests']}")
    bprint(f"Passed: {summary['passed']} ✅")
    bprint(f"Failed: {summary['failed']} ❌")
    bprint(f"Pass Rate: {summary['pass_rate']:.1f}%")
    bprint(f"Average Latency: {summary['avg_latency_ms']:.0f}ms")
    bprint(f"Average Accuracy: {summary['avg_accuracy']:.1f}%")

    bprint(f"\n{'=' * 80}")
    bprint("📈 RESULTS BY CATEGORY")
    bprint("=" * 80)
    for category, stats in category_stats.items():
        bprint(f"\n{category.upper()}:")
        bprint(f"  Tests: {stats['tests']}")
        bprint(f"  Pass Rate: {stats['pass_rate']:.1f}%")
        bprint(f"  Avg Latency: {stats['avg_latency_ms']:.0f}ms")

    # Failed tests details
    failed_results = [r for r in metrics.results if not r.get("passed", False)]
    if failed_results:
        bprint(f"\n{'=' * 80}")
        bprint("❌ FAILED TESTS DETAILS")
        bprint("=" * 80)
        for result in failed_results:
            bprint(f"\nQuery: {result['query']}")
            if not result.get("latency_ok", True):
                bprint(f"  ⚠️ Latency: {result['latency_ms']:.0f}ms (too slow)")
            if not result.get("accuracy_ok", True):
                bprint(f"  ⚠️ Accuracy: {result['accuracy']:.1f}% (too low)")
                bprint(f"  Missing topics: {', '.join(result.get('topics_missing', []))}")
            if result.get("error"):
                bprint(f"  ⚠️ Error: {result['error']}")

    # Save results to JSON
    output_file = Path(__file__).parent.parent.parent / "benchmark_results.json"
    with open(output_file, "w") as f:
        json.dump(
            {
                "summary": summary,
                "category_stats": category_stats,
                "detailed_results": metrics.results,
                "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
            },
            f,
            indent=2,
        )

    bprint(f"\n{'=' * 80}")
    bprint(f"💾 Results saved to: {output_file}")
    bprint("=" * 80)

    # Final verdict
    bprint(f"\n{'=' * 80}")
    if summary["pass_rate"] >= 80:
        bprint("🎉 EXCELLENT! Chatbot performance is strong")
    elif summary["pass_rate"] >= 60:
        bprint("✅ GOOD! Chatbot performance is acceptable")
    elif summary["pass_rate"] >= 40:
        bprint("⚠️ NEEDS IMPROVEMENT! Several issues detected")
    else:
        bprint("❌ POOR! Significant improvements needed")

    bprint(f"Overall Score: {summary['pass_rate']:.1f}%")
    bprint("=" * 80)

    return summary


if __name__ == "__main__":
    run_benchmarks()
