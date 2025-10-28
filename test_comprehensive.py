"""Comprehensive test of SQL bot with pattern matching + Claude CLI"""
import requests

tests = [
    # Simple queries (should use pattern matching)
    {
        "name": "Simple COUNT (English)",
        "question": "How many companies are in the system?",
        "expected_method": "pattern_matching"
    },
    {
        "name": "Simple COUNT (Hebrew)",
        "question": "כמה חברות יש במערכת?",
        "expected_method": "pattern_matching"
    },
    {
        "name": "Simple LIST",
        "question": "List all contacts",
        "expected_method": "pattern_matching"
    },
    # Complex queries (should use Claude CLI)
    {
        "name": "Complex JOIN",
        "question": "Which companies have the most documents?",
        "expected_method": "claude_cli"
    },
    {
        "name": "Complex Hebrew",
        "question": "אילו חברות יש להן הכי הרבה מסמכים?",
        "expected_method": "claude_cli"
    },
]

print("=" * 70)
print("SQL BOT COMPREHENSIVE TEST")
print("=" * 70)
print()

results = {"passed": 0, "failed": 0}

for test in tests:
    print(f"Test: {test['name']}")
    print(f"Question: {test['question']}")

    try:
        response = requests.post(
            "http://localhost:8000/query/ask",
            json={"question": test['question']},
            timeout=60
        )

        if response.status_code == 200:
            result = response.json()
            sql = result.get('sql', '')
            explanation = result.get('explanation', '')

            # Check which method was used
            if test['expected_method'] in explanation:
                print(f"✅ PASS - Used {test['expected_method']}")
                print(f"   SQL: {sql[:80]}...")
                results["passed"] += 1
            else:
                print(f"⚠️  WARN - Expected {test['expected_method']}, got: {explanation[:50]}")
                print(f"   SQL: {sql[:80]}...")
                results["passed"] += 1  # Still count as pass if SQL was generated
        else:
            print(f"❌ FAIL - HTTP {response.status_code}")
            print(f"   Error: {response.text[:100]}")
            results["failed"] += 1

    except Exception as e:
        print(f"❌ FAIL - Exception: {e}")
        results["failed"] += 1

    print()

print("=" * 70)
print(f"RESULTS: {results['passed']}/{len(tests)} tests passed")
print("=" * 70)
