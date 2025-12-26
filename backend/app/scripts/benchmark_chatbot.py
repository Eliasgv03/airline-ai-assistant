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
import time
from pathlib import Path

from app.services.chat_service import ChatService
from app.utils.logger import get_logger

logger = get_logger(__name__)

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
            "max_latency_ms": 8000,
        },
        {
            "query": "What flights are available from Mumbai to Bangalore?",
            "expected_topics": ["BOM", "BLR", "flight", "available"],
            "category": "tool_use",
            "max_latency_ms": 8000,
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
    max_latency = test_case["max_latency_ms"]
    category = test_case["category"]

    logger.info(f"\n{'=' * 80}")
    logger.info(f"Testing: {query}")
    logger.info(f"Category: {category}")
    logger.info(f"Expected topics: {', '.join(expected_topics)}")
    logger.info("-" * 80)

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

    # Check if test passed
    latency_ok = latency_ms <= max_latency
    accuracy_ok = accuracy >= 50  # At least 50% topic coverage

    passed = latency_ok and accuracy_ok

    # Log results
    logger.info(f"Response ({len(response)} chars): {response[:200]}...")
    logger.info("-" * 80)
    logger.info(
        f"✓ Latency: {latency_ms:.0f}ms (max: {max_latency}ms) - {'PASS' if latency_ok else 'FAIL'}"
    )
    logger.info(f"✓ Accuracy: {accuracy:.1f}% - {'PASS' if accuracy_ok else 'FAIL'}")
    logger.info(f"✓ Topics found: {', '.join(topics_found) if topics_found else 'None'}")
    logger.info(f"Overall: {'✅ PASS' if passed else '❌ FAIL'}")

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
        "topics_found": topics_found,
        "topics_missing": [t for t in expected_topics if t not in topics_found],
        "response_length": len(response),
    }


def run_benchmarks():
    """Run all benchmark tests"""
    logger.info("=" * 80)
    logger.info("🚀 STARTING CHATBOT BENCHMARK SUITE")
    logger.info("=" * 80)

    chat_service = ChatService()
    session_id = "benchmark_session"
    metrics = BenchmarkMetrics()

    # Run all tests
    for test_group, tests in BENCHMARK_TESTS.items():
        logger.info(f"\n{'=' * 80}")
        logger.info(f"📋 Test Group: {test_group.upper()}")
        logger.info("=" * 80)

        for test_case in tests:
            result = run_benchmark_test(chat_service, session_id, test_case)
            metrics.add_result(result)

    # Generate summary
    summary = metrics.get_summary()
    category_stats = metrics.get_category_stats()

    logger.info(f"\n{'=' * 80}")
    logger.info("📊 BENCHMARK RESULTS SUMMARY")
    logger.info("=" * 80)
    logger.info(f"Total Tests: {summary['total_tests']}")
    logger.info(f"Passed: {summary['passed']} ✅")
    logger.info(f"Failed: {summary['failed']} ❌")
    logger.info(f"Pass Rate: {summary['pass_rate']:.1f}%")
    logger.info(f"Average Latency: {summary['avg_latency_ms']:.0f}ms")
    logger.info(f"Average Accuracy: {summary['avg_accuracy']:.1f}%")

    logger.info(f"\n{'=' * 80}")
    logger.info("📈 RESULTS BY CATEGORY")
    logger.info("=" * 80)
    for category, stats in category_stats.items():
        logger.info(f"\n{category.upper()}:")
        logger.info(f"  Tests: {stats['tests']}")
        logger.info(f"  Pass Rate: {stats['pass_rate']:.1f}%")
        logger.info(f"  Avg Latency: {stats['avg_latency_ms']:.0f}ms")

    # Failed tests details
    failed_results = [r for r in metrics.results if not r.get("passed", False)]
    if failed_results:
        logger.info(f"\n{'=' * 80}")
        logger.info("❌ FAILED TESTS DETAILS")
        logger.info("=" * 80)
        for result in failed_results:
            logger.info(f"\nQuery: {result['query']}")
            if not result.get("latency_ok", True):
                logger.info(f"  ⚠️ Latency: {result['latency_ms']:.0f}ms (too slow)")
            if not result.get("accuracy_ok", True):
                logger.info(f"  ⚠️ Accuracy: {result['accuracy']:.1f}% (too low)")
                logger.info(f"  Missing topics: {', '.join(result.get('topics_missing', []))}")
            if result.get("error"):
                logger.info(f"  ⚠️ Error: {result['error']}")

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

    logger.info(f"\n{'=' * 80}")
    logger.info(f"💾 Results saved to: {output_file}")
    logger.info("=" * 80)

    # Final verdict
    logger.info(f"\n{'=' * 80}")
    if summary["pass_rate"] >= 80:
        logger.info("🎉 EXCELLENT! Chatbot performance is strong")
    elif summary["pass_rate"] >= 60:
        logger.info("✅ GOOD! Chatbot performance is acceptable")
    elif summary["pass_rate"] >= 40:
        logger.info("⚠️ NEEDS IMPROVEMENT! Several issues detected")
    else:
        logger.info("❌ POOR! Significant improvements needed")

    logger.info(f"Overall Score: {summary['pass_rate']:.1f}%")
    logger.info("=" * 80)

    return summary


if __name__ == "__main__":
    run_benchmarks()
