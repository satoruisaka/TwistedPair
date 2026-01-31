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

# Web Search Settings
# Brave Search API (primary)
# Get your API key at: https://brave.com/search/api/
# See BRAVE_API_SETUP.md for configuration instructions
BRAVE_API_KEY = None  # Set your API key here or via environment variable
BRAVE_API_URL = "https://api.search.brave.com/res/v1/web/search"

# User-Agent rotation to avoid bot detection
USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:122.0) Gecko/20100101 Firefox/122.0",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.2 Safari/605.1.15",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:122.0) Gecko/20100101 Firefox/122.0",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36 Edg/121.0.0.0",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36 OPR/106.0.0.0",
    "Mozilla/5.0 (X11; Linux x86_64; rv:122.0) Gecko/20100101 Firefox/122.0"
]
