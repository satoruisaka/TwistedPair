# config.py
# TwistedPair configuration

# Ollama settings
OLLAMA_URL = "http://localhost:11434/api/generate"

# Gain-to-parameter mapping ranges
# Temperature: controls probability distribution sharpness
TEMP_MIN = 0.1
TEMP_MAX = 2.0

# Top-k: restricts sampling to top k tokens
TOP_K_MIN = 5
TOP_K_MAX = 120

# Top-p: dynamically selects tokens by cumulative probability
TOP_P_MIN = 0.50
TOP_P_MAX = 0.98

# Gain range (knob values)
GAIN_MIN = 1
GAIN_MAX = 10

# Available LLM models (make sure these are installed in Ollama)
AVAILABLE_LLM_MODELS = [
    "deepseek-r1:latest",
    "gemma3:27b",
    "gpt-oss:20b",
    "ministral-3:latest",
    "ministral-3:14b",
    "qwen3:latest"
]

# Default model for TwistedPair
DEFAULT_MODEL = "ministral-3:14b"

# Context window size (tokens) - most open-weight models support 20k+
NUM_CTX = 32768

# Output settings
OUTPUT_DIR = "./runs"
