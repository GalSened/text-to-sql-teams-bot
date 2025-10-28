"""Live debugging session"""
import requests
import time

print("=" * 70)
print("🔴 LIVE SQL BOT DEBUGGING SESSION")
print("=" * 70)
print()

# Test 1: Simple pattern query
print("📝 TEST 1: Simple pattern-based query (should be fast)")
print("Question: How many companies are in the system?")
print("Expected: Pattern matching < 100ms")
print()

start = time.time()
try:
    response = requests.post(
        "http://localhost:8000/query/ask",
        json={"question": "How many companies are in the system?"},
        timeout=10
    )
    elapsed = (time.time() - start) * 1000

    if response.status_code == 200:
        result = response.json()
        print(f"✅ SUCCESS in {elapsed:.0f}ms")
        print(f"   SQL: {result.get('sql', '')}")
        print(f"   Method: {result.get('explanation', '')}")
    else:
        print(f"❌ FAILED: HTTP {response.status_code}")
        print(f"   Error: {response.text}")
except Exception as e:
    print(f"❌ EXCEPTION: {e}")

print()
print("-" * 70)
print()

# Test 2: Complex Claude CLI query
print("📝 TEST 2: Complex query (Claude CLI - should take ~10s)")
print("Question: Which companies have the most documents?")
print("Expected: Claude CLI with JOIN")
print()

start = time.time()
try:
    response = requests.post(
        "http://localhost:8000/query/ask",
        json={"question": "Which companies have the most documents?"},
        timeout=60
    )
    elapsed = (time.time() - start) * 1000

    if response.status_code == 200:
        result = response.json()
        print(f"✅ SUCCESS in {elapsed:.0f}ms ({elapsed/1000:.1f}s)")
        print(f"   SQL: {result.get('sql', '')[:100]}...")
        print(f"   Method: {result.get('explanation', '')}")
    else:
        print(f"❌ FAILED: HTTP {response.status_code}")
        print(f"   Error: {response.text}")
except Exception as e:
    print(f"❌ EXCEPTION: {e}")

print()
print("=" * 70)
print("🔴 LIVE DEBUGGING COMPLETE")
print("=" * 70)
