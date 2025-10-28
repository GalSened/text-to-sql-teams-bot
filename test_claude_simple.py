"""Simple test of complex query"""
import requests

response = requests.post(
    "http://localhost:8000/query/ask",
    json={"question": "Which companies have the most documents?"}
)

print(f"Status: {response.status_code}")
if response.status_code == 200:
    result = response.json()
    print(f"SQL: {result.get('sql', 'N/A')}")
    print(f"Explanation: {result.get('explanation', 'N/A')}")
else:
    print(f"Error: {response.text}")
