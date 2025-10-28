"""Test complex queries that need Claude CLI fallback"""
import requests
import json

# Test 1: Simple query (should use pattern matching)
print("=" * 60)
print("TEST 1: Simple COUNT query (pattern matching)")
print("=" * 60)
simple_query = "How many companies are in the system?"
response = requests.post(
    "http://localhost:8000/query/ask",
    json={"question": simple_query},
    headers={"Content-Type": "application/json; charset=utf-8"}
)
print(f"Question: {simple_query}")
print(f"Status: {response.status_code}")
result = response.json()
print(f"SQL: {result.get('sql', 'N/A')}")
print(f"Method: {result.get('explanation', 'N/A')}")
print()

# Test 2: Complex query with JOIN (should try Claude CLI)
print("=" * 60)
print("TEST 2: Complex query requiring JOIN (Claude CLI fallback)")
print("=" * 60)
complex_query = "Which companies have the most documents?"
response2 = requests.post(
    "http://localhost:8000/query/ask",
    json={"question": complex_query},
    headers={"Content-Type": "application/json; charset=utf-8"}
)
print(f"Question: {complex_query}")
print(f"Status: {response2.status_code}")
if response2.status_code == 200:
    result2 = response2.json()
    print(f"SQL: {result2.get('sql', 'N/A')}")
    print(f"Method: {result2.get('explanation', 'N/A')}")
else:
    print(f"Error: {response2.text}")
print()

# Test 3: Hebrew complex query
print("=" * 60)
print("TEST 3: Hebrew complex query")
print("=" * 60)
hebrew_complex = "אילו חברות יש להן הכי הרבה מסמכים?"
response3 = requests.post(
    "http://localhost:8000/query/ask",
    json={"question": hebrew_complex},
    headers={"Content-Type": "application/json; charset=utf-8"}
)
print(f"Question: {hebrew_complex}")
print(f"Status: {response3.status_code}")
if response3.status_code == 200:
    result3 = response3.json()
    print(f"SQL: {result3.get('sql', 'N/A')}")
    print(f"Method: {result3.get('explanation', 'N/A')}")
else:
    print(f"Error: {response3.text}")
