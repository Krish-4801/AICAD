import requests

url = "https://api.minimax.io/v1/chat/completions"

headers = {
    "Authorization": "Bearer sk-api-AmeIU0m7ALxt4dY_jwO0KzsrjvyznXKBwCy5s0Gqf-3QzuxwIeIwHKIGxg0P5NqZf0feymfXiJmes5Q6BQ5ea7_-StWorcrq0KnCi5mEXRZyCJwNz7AXq0A",
    "Content-Type": "application/json"
}

payload = {
    "model": "MiniMax-M2.5",
    "messages": [{"role": "user", "content": "hello"}]
}

r = requests.post(url, headers=headers, json=payload, timeout=30)

print(r.status_code)
print(r.text)