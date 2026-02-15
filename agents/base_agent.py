import os
import json

class BaseAgent:
    def __init__(self, name, prompt_path):
        self.name = name
        self.prompt_template = self._load_prompt(prompt_path)

    def _load_prompt(self, path):
        try:
            # handle relative paths from project root
            if not os.path.exists(path):
                # try prepending project root if running from elsewhere (simplified)
                pass 
            with open(path, 'r') as f:
                return f.read()
        except FileNotFoundError:
            print(f"Warning: Prompt file not found at {path}")
            return ""

    def _call_llm(self, system_prompt, user_input):
        """
        Calls the LLM via OpenRouter API.
        """
        model = getattr(self, 'model_id', os.getenv("LLM_MODEL", "google/gemini-2.0-flash-exp:free"))
        provider = getattr(self, 'provider', os.getenv("AI_PROVIDER", "openrouter"))
        
        print(f"[{self.name}] Thinking... 🤖 (via {provider}/{model})")
        
        if provider == "simulation":
            print(f"[{self.name}] Simulation Mode Selected.")
            return None

        api_key = os.getenv("OPENROUTER_API_KEY")
        if not api_key:
            print(f"[{self.name}] No API Key found. Falling back to simulation.")
            return None

        try:
            import requests # Lazy import
            response = requests.post(
                url="https://openrouter.ai/api/v1/chat/completions",
                headers={
                    "Authorization": f"Bearer {api_key}",
                    "HTTP-Referer": "http://localhost:8000", 
                    "X-Title": "SafeCloud",
                    "Content-Type": "application/json"
                },
                json={
                    "model": model,
                    "messages": [
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": user_input}
                    ]
                },
                timeout=15 
            )
            
            if response.status_code == 200:
                return response.json()['choices'][0]['message']['content']
            else:
                print(f"[LLM Error] Status: {response.status_code}, Body: {response.text}")
                return None

        except Exception as e:
            print(f"[LLM Exception] {e}")
            return None

    def run(self, input_data):
        raise NotImplementedError("Subclasses must implement run()")
