import httpx, os

REST_API_URL = os.getenv("LLM_API_URL")
REST_API_KEY = os.getenv("LLM_API_KEY")
OLLAMA_URL = "http://localhost:11434/api/chat"

class LLMRouter:
    def __init__(self, backend: str = "rest"):
        self.backend = backend

    def chat(self, messages):
        if self.backend == "rest":
            headers = {"Authorization": f"Bearer {REST_API_KEY}"} if REST_API_KEY else {}
            with httpx.Client(timeout=120.0) as client:
                r = client.post(REST_API_URL, headers=headers, json={"messages": messages})
                r.raise_for_status()
                return r.json()["choices"][0]["message"]["content"]
        elif self.backend == "ollama":
            with httpx.Client(timeout=120.0) as client:
                r = client.post(OLLAMA_URL, json={"model": "codellama", "messages": messages})
                r.raise_for_status()
                return r.json()["message"]["content"]
        else:
            raise ValueError("Unknown backend")
