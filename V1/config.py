# config.py
# TwistedPair configuration
# top-k and top-p sampling are not used currently. Only temperature is applied.
# to control randomness and creativity of outputs.

# Ollama settings
OLLAMA_URL = "http://localhost:11434/api/generate"

# Available LLM models (make sure these are installed in Ollama)
AVAILABLE_LLM_MODELS = [
    "deepseek-r1:8b",
    "dolphin3:latest",
    "gemma3:4b",
    "gpt-oss:20b",
    "llama3.1:8b",
    "mistral:latest",
    "openchat:latest",
    "phi3:14b",
    "qwen3:latest"
]

# Default model for TwistedPair
DEFAULT_MODEL = "mistral:latest"

# Context window size (tokens) - most open-weight models support 20k+
NUM_CTX = 32768

# Output settings
OUTPUT_DIR = "./runs"
