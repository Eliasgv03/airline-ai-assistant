"""
Test RAG Quality with New Policy Documents

This script tests the RAG system with queries related to the newly added policies.
"""

import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

# ruff: noqa: E402
from app.services.chat_service import ChatService
from app.utils.logger import get_logger

logger = get_logger(__name__)

# Test queries covering new policy documents
TEST_QUERIES = [
    # Cancellation policy
    {
        "query": "Can I cancel my flight for free?",
        "expected_topics": ["24 hours", "free cancellation", "7 days"],
        "document": "cancellation.md",
    },
    {
        "query": "What's the cancellation fee for domestic flights?",
        "expected_topics": ["INR", "2500", "3500", "Classic", "Value"],
        "document": "cancellation.md",
    },
    {
        "query": "How long does a refund take?",
        "expected_topics": ["7-10", "business days", "payment method"],
        "document": "cancellation.md",
    },
    # Flight changes
    {
        "query": "How much does it cost to change my flight?",
        "expected_topics": ["change fee", "INR", "fare difference"],
        "document": "flight_changes.md",
    },
    {
        "query": "Can I change my flight date?",
        "expected_topics": ["Manage Booking", "change", "fee"],
        "document": "flight_changes.md",
    },
    # Flying Returns
    {
        "query": "How do I join the Flying Returns program?",
        "expected_topics": ["flyingreturns", "free", "enrollment"],
        "document": "flying_returns.md",
    },
    {
        "query": "What are the benefits of Gold status?",
        "expected_topics": ["lounge", "bonus", "baggage", "Star Alliance"],
        "document": "flying_returns.md",
    },
    {
        "query": "How do I earn Flying Returns points?",
        "expected_topics": ["6 points", "INR 100", "bonus"],
        "document": "flying_returns.md",
    },
    # Special services
    {
        "query": "Can I travel with my dog?",
        "expected_topics": ["pet", "cabin", "cargo", "fee", "certificate"],
        "document": "special_services.md",
    },
    {
        "query": "I need wheelchair assistance at the airport",
        "expected_topics": ["wheelchair", "WCHR", "WCHS", "WCHC", "free"],
        "document": "special_services.md",
    },
    {
        "query": "Can pregnant women fly on Air India?",
        "expected_topics": ["pregnant", "32 weeks", "36 weeks", "certificate"],
        "document": "special_services.md",
    },
    # FAQ
    {
        "query": "When should I arrive at the airport?",
        "expected_topics": ["2 hours", "3 hours", "domestic", "international"],
        "document": "faq.md",
    },
    {
        "query": "How do I check in online?",
        "expected_topics": ["Web Check-In", "48 hours", "PNR", "boarding pass"],
        "document": "faq.md",
    },
]


def test_rag_quality():
    """Test RAG system with new policy queries"""
    logger.info("=" * 80)
    logger.info("Testing RAG Quality with New Policy Documents")
    logger.info("=" * 80)

    chat_service = ChatService()
    session_id = "test_rag_quality_session"

    results = []

    for i, test_case in enumerate(TEST_QUERIES, 1):
        query = test_case["query"]
        expected_topics = test_case["expected_topics"]
        document = test_case["document"]

        logger.info(f"\n{'=' * 80}")
        logger.info(f"Test {i}/{len(TEST_QUERIES)}")
        logger.info(f"Document: {document}")
        logger.info(f"Query: {query}")
        logger.info(f"Expected topics: {', '.join(expected_topics)}")
        logger.info("-" * 80)

        try:
            # Get response from chat service
            response = chat_service.process_message(session_id, query)

            # Check if expected topics are in response
            response_lower = response.lower()
            topics_found = [topic for topic in expected_topics if topic.lower() in response_lower]
            topics_missing = [
                topic for topic in expected_topics if topic.lower() not in response_lower
            ]

            coverage = len(topics_found) / len(expected_topics) * 100

            result = {
                "query": query,
                "document": document,
                "coverage": coverage,
                "topics_found": topics_found,
                "topics_missing": topics_missing,
                "response_length": len(response),
            }
            results.append(result)

            logger.info(f"Response ({len(response)} chars):")
            logger.info(response[:500] + ("..." if len(response) > 500 else ""))
            logger.info("-" * 80)
            logger.info(f"Coverage: {coverage:.1f}%")
            logger.info(f"Topics found: {', '.join(topics_found) if topics_found else 'None'}")
            logger.info(
                f"Topics missing: {', '.join(topics_missing) if topics_missing else 'None'}"
            )

            # Clear session for next query
            chat_service.clear_session(session_id)

        except Exception as e:
            logger.error(f"Error processing query: {e}")
            results.append(
                {
                    "query": query,
                    "document": document,
                    "coverage": 0,
                    "error": str(e),
                }
            )

    # Summary
    logger.info(f"\n{'=' * 80}")
    logger.info("SUMMARY")
    logger.info("=" * 80)

    successful_tests = [r for r in results if "error" not in r]
    avg_coverage = (
        sum(r["coverage"] for r in successful_tests) / len(successful_tests)
        if successful_tests
        else 0
    )

    logger.info(f"Total tests: {len(TEST_QUERIES)}")
    logger.info(f"Successful: {len(successful_tests)}")
    logger.info(f"Failed: {len(results) - len(successful_tests)}")
    logger.info(f"Average coverage: {avg_coverage:.1f}%")

    # Coverage by document
    logger.info("\nCoverage by Document:")
    for doc in {r["document"] for r in results}:
        doc_results = [r for r in successful_tests if r["document"] == doc]
        if doc_results:
            doc_coverage = sum(r["coverage"] for r in doc_results) / len(doc_results)
            logger.info(f"  {doc}: {doc_coverage:.1f}%")

    # Tests with low coverage
    low_coverage = [r for r in successful_tests if r["coverage"] < 50]
    if low_coverage:
        logger.info("\nTests with Low Coverage (<50%):")
        for r in low_coverage:
            logger.info(f"  - {r['query']} ({r['coverage']:.1f}%)")
            logger.info(f"    Missing: {', '.join(r['topics_missing'])}")

    logger.info("=" * 80)
    logger.info(f"✅ RAG Quality Test Complete - Average Coverage: {avg_coverage:.1f}%")
    logger.info("=" * 80)


if __name__ == "__main__":
    test_rag_quality()
