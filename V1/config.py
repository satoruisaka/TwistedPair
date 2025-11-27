# config.py
# TwistedPair configuration

# Ollama settings
OLLAMA_URL = "http://localhost:11434/api/generate"

# Available LLM models (make sure these are installed in Ollama)
AVAILABLE_LLM_MODELS = [
    "dolphin3",
    "gemma3:4b",
    "llama3.1",
    "mistral",
    "openchat",
    "phi3:14b",
    "qwen3"
]

# Default model for TwistedPair
DEFAULT_MODEL = "mistral"

# Output settings
OUTPUT_DIR = "./runs"
