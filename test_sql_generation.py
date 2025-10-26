#!/usr/bin/env python3
"""
Test SQL Generation (without executing queries)
Tests the intelligent SQL generator with sample questions
"""
from app.services.sql_generator import intelligent_sql_generator


def test_question(question: str, language: str = 'en'):
    """Test SQL generation for a question."""
    print(f"\n{'=' * 70}")
    print(f"Question ({language}): {question}")
    print(f"{'=' * 70}")

    result = intelligent_sql_generator.generate_sql(
        question=question,
        language=language
    )

    if result['success']:
        print(f"✅ Success")
        print(f"   Pattern: {result.get('pattern_type', 'N/A')}")
        print(f"   Confidence: {result.get('confidence', 0):.2f}")
        print(f"   SQL: {result['sql']}")
    else:
        print(f"❌ Failed: {result.get('error', 'Unknown error')}")


def main():
    """Run all tests."""
    print("\n" + "=" * 70)
    print("🧪 Testing Intelligent SQL Generator")
    print("=" * 70)

    # Test English questions
    test_question("How many customers joined last month?", "en")
    test_question("Show me the top 10 customers by revenue", "en")
    test_question("List all active customers", "en")
    test_question("What is the total sales last week?", "en")
    test_question("Average order value today", "en")

    # Test Hebrew questions
    test_question("כמה לקוחות הצטרפו בחודש שעבר?", "he")
    test_question("הצג את 10 הלקוחות המובילים", "he")

    # Test edge cases
    test_question("This is not a valid question", "en")
    test_question("Random words without meaning", "en")

    print("\n" + "=" * 70)
    print("✅ All tests completed!")
    print("=" * 70 + "\n")


if __name__ == "__main__":
    main()
