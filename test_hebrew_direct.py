"""Direct test of Hebrew query processing"""
import requests
import json

# Test Hebrew query
hebrew_question = "כמה חברות יש במערכת?"
print(f"Testing with question: {hebrew_question}")
print(f"Question bytes: {hebrew_question.encode('utf-8')}")

# Make API request
response = requests.post(
    "http://localhost:8000/query/ask",
    json={"question": hebrew_question},
    headers={"Content-Type": "application/json; charset=utf-8"}
)

print(f"\nStatus Code: {response.status_code}")
print(f"Response: {json.dumps(response.json(), indent=2, ensure_ascii=False)}")
