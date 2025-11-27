# ollama_sampler.py
import requests
import json

OLLAMA_URL = "http://localhost:11434/api/generate"

AVAILABLE_LLM_MODELS = [
    "dolphin3",
    "gemma3:4b",
    "llama3.1",
    "mistral",
    "openchat",
    "phi3:14b",
    "qwen3"
]

def ollama_sampler(system: str, user: str, temperature: float, model_name: str = "llama3.1") -> str:
    """
    Sampler function for Ollama API.
    
    Args:
        system: System prompt
        user: User prompt
        temperature: Temperature (0.0-1.0)
        model_name: Ollama model name
    
    Returns:
        Generated text response
    """
    # Combine system and user prompts
    full_prompt = f"{system}\n\nUser input:\n{user}"
    
    payload = {
        "model": model_name,
        "prompt": full_prompt,
        "stream": False,
        "options": {
            "temperature": temperature
        }
    }
    
    try:
        response = requests.post(OLLAMA_URL, json=payload, timeout=120)
        response.raise_for_status()
        result = response.json()
        return result.get("response", "").strip()
    except requests.exceptions.RequestException as e:
        return f"[Error: Ollama request failed - {str(e)}]"
    except json.JSONDecodeError as e:
        return f"[Error: Invalid JSON response - {str(e)}]"
