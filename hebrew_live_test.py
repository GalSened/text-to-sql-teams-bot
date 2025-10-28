"""Live Hebrew testing"""
import requests
import time

print("🔴 HEBREW SUPPORT LIVE TEST")
print("=" * 70)

tests = [
    {
        "name": "Simple Hebrew COUNT",
        "question": "כמה חברות יש במערכת?",
        "expected": "pattern_matching"
    },
    {
        "name": "Complex Hebrew JOIN",
        "question": "אילו חברות יש להן הכי הרבה מסמכים?",
        "expected": "claude_cli"
    }
]

for test in tests:
    print(f"\n📝 {test['name']}")
    print(f"   Question: {test['question']}")
    print(f"   Expected method: {test['expected']}")

    start = time.time()
    try:
        response = requests.post(
            "http://localhost:8000/query/ask",
            json={"question": test['question']},
            headers={"Content-Type": "application/json; charset=utf-8"},
            timeout=60
        )
        elapsed = (time.time() - start) * 1000

        if response.status_code == 200:
            result = response.json()
            method = result.get('explanation', '')

            if test['expected'] in method:
                print(f"   ✅ PASS in {elapsed:.0f}ms")
            else:
                print(f"   ⚠️  WARN in {elapsed:.0f}ms - Got {method[:30]}")

            print(f"   SQL: {result.get('sql', '')[:80]}...")
        else:
            print(f"   ❌ FAIL: {response.status_code}")
            print(f"   Error: {response.text[:100]}")
    except Exception as e:
        print(f"   ❌ ERROR: {e}")

print("\n" + "=" * 70)
