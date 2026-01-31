# ollama_sampler.py
# Sampler function for Ollama API

import requests
import json
from config import OLLAMA_URL, DEFAULT_MODEL, NUM_CTX

def ollama_sampler(system: str, user: str, temperature: float, top_k: int = 40, top_p: float = 0.9, model_name: str = DEFAULT_MODEL) -> str:
    """
    Sampler function for Ollama API.
    
    Args:
        system: System prompt
        user: User prompt
        temperature: Temperature (0.1-2.0)
        top_k: Top-k sampling parameter (5-120)
        top_p: Top-p (nucleus) sampling parameter (0.5-0.98)
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
            "temperature": temperature,
            "num_ctx": NUM_CTX,
            "top_k": int(top_k),
            "top_p": float(top_p)
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
