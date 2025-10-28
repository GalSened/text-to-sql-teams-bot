"""Interactive debugging session with detailed output"""
import requests
import time
import json

def test_query(question, description):
    """Test a single query with detailed output"""
    print(f"\n{'='*70}")
    print(f"🔍 {description}")
    print(f"{'='*70}")
    print(f"Question: {question}")
    print(f"Timestamp: {time.strftime('%H:%M:%S')}")
    print()

    start = time.time()
    try:
        print("⏳ Sending request...")
        response = requests.post(
            "http://localhost:8000/query/ask",
            json={"question": question},
            headers={"Content-Type": "application/json; charset=utf-8"},
            timeout=60
        )
        elapsed = (time.time() - start) * 1000

        print(f"✓ Response received in {elapsed:.0f}ms")
        print()

        if response.status_code == 200:
            result = response.json()

            print("📊 RESULT BREAKDOWN:")
            print(f"   Status: ✅ SUCCESS")
            print(f"   Query ID: {result.get('query_id', 'N/A')}")
            print(f"   Method: {result.get('explanation', 'N/A')}")
            print(f"   Query Type: {result.get('query_type', 'N/A')}")
            print(f"   Risk Level: {result.get('risk_level', 'N/A')}")
            print(f"   Requires Confirmation: {result.get('requires_confirmation', 'N/A')}")
            print()

            print("📝 GENERATED SQL:")
            sql = result.get('sql', '')
            # Pretty print SQL
            for line in sql.split('FROM'):
                if 'FROM' in sql and line == sql.split('FROM')[0]:
                    print(f"   {line.strip()}")
                    print(f"   FROM", end='')
                else:
                    print(f" {line.strip()}")

            print()

            # Estimate if pattern or AI
            if "pattern_matching" in result.get('explanation', ''):
                print("⚡ Method: PATTERN MATCHING (Fast, Free)")
                print(f"   Time: {elapsed:.0f}ms")
                print("   Cost: $0.00")
            elif "claude_cli" in result.get('explanation', ''):
                print("🧠 Method: CLAUDE CLI (AI-Powered)")
                print(f"   Time: {elapsed/1000:.1f}s")
                print("   Cost: $0.00 (local)")

            return True

        else:
            print(f"❌ FAILED: HTTP {response.status_code}")
            print(f"Error: {response.text}")
            return False

    except Exception as e:
        print(f"❌ EXCEPTION: {e}")
        import traceback
        traceback.print_exc()
        return False

# Run interactive tests
print("\n" + "="*70)
print("🔴 INTERACTIVE SQL BOT DEBUG SESSION")
print("="*70)

tests = [
    ("How many companies are in the system?", "Test 1: Simple English COUNT"),
    ("כמה חברות יש במערכת?", "Test 2: Simple Hebrew COUNT"),
    ("List all contacts", "Test 3: Pattern-based LIST"),
    ("Which companies have the most documents?", "Test 4: Complex JOIN (English)"),
    ("אילו חברות יש להן הכי הרבה מסמכים?", "Test 5: Complex JOIN (Hebrew)"),
]

results = []
for question, description in tests:
    success = test_query(question, description)
    results.append(success)
    time.sleep(1)  # Brief pause between tests

# Summary
print(f"\n{'='*70}")
print("📊 FINAL SUMMARY")
print(f"{'='*70}")
print(f"Total Tests: {len(results)}")
print(f"Passed: {sum(results)}")
print(f"Failed: {len(results) - sum(results)}")
print(f"Success Rate: {(sum(results)/len(results)*100):.0f}%")

if all(results):
    print("\n✅ ALL TESTS PASSED! System is working perfectly!")
else:
    print(f"\n⚠️ Some tests failed. Check logs for details.")

print("="*70)
