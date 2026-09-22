import requests

OLLAMA_URL = "http://localhost:11434/api/generate"

payload = {
    "model": "qwen2.5:1.5b",
    "prompt": "What is an AI agent? Explain in one sentence.",
    "stream": False
}

response = requests.post(
    OLLAMA_URL,
    json=payload,
    timeout=120
)

response.raise_for_status()

data = response.json()

print("Model:", payload["model"])
print("Response:", data["response"])