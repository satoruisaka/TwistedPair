# TwistedPair API User Guide

**Version**: V2/V3  
**Last Updated**: December 3, 2025  
**Base URL**: `http://localhost:8000` (default)

**Caution**: *This repo is not actively maintained. Use at your own risk.*

---

## Table of Contents
1. [Introduction](#introduction)
2. [Getting Started](#getting-started)
3. [Core Concepts](#core-concepts)
4. [API Endpoints](#api-endpoints)
   - [Utility Endpoints](#utility-endpoints)
   - [Distortion Endpoints](#distortion-endpoints)
   - [Chat Session Endpoints](#chat-session-endpoints)
5. [Request/Response Schemas](#requestresponse-schemas)
6. [Code Examples](#code-examples)
7. [Error Handling](#error-handling)
8. [Performance Tips](#performance-tips)

---

## Introduction

TwistedPair is a signal distortion system that transforms text through LLM-based "distortion pedals" with three control knobs:
- **Mode**: Rhetorical operation (6 types)
- **Tone**: Verbal style (5 types)
- **Gain**: Sampling control (1-10, affects temperature/top-k/top-p)

The API provides both **single-shot distortion** (stateless) and **chat sessions** (stateful multi-turn conversations).

---

## Getting Started

### Prerequisites
- TwistedPair server running (V2 or V3)
- Ollama running at `localhost:11434`
- Python 3.8+ with `requests` library (for Python examples)

### Start Server
```bash
# V2 (recommended for API-only usage, no web search)
cd V2
uvicorn server:app --host 0.0.0.0 --port 8000

# V3 (includes automatic web search on "check web" triggers)
cd V3
uvicorn server:app --host 0.0.0.0 --port 8000
```

### Test Connection
```bash
curl http://localhost:8000/knobs
```

---

## Core Concepts

### Modes (Rhetorical Operations)
| Mode | Value | Description |
|------|-------|-------------|
| INVERT_ER | `invert_er` | Challenge assumptions, expose contradictions |
| SO_WHAT_ER | `so_what_er` | Ask "why does this matter?" for deeper implications |
| ECHO_ER | `echo_er` | Amplify core message, reinforce key insights |
| WHAT_IF_ER | `what_if_er` | Explore hypotheticals and alternative scenarios |
| CUCUMB_ER | `cucumb_er` | Ground with evidence, cite examples/references |
| ARCHIV_ER | `archiv_er` | Historical context, precedents, evolution |

### Tones (Verbal Styles)
| Tone | Value | Description |
|------|-------|-------------|
| NEUTRAL | `neutral` | Balanced, factual, measured |
| TECHNICAL | `technical` | Precise terminology, structured analysis |
| PRIMAL | `primal` | Visceral, direct, stripped-down |
| POETIC | `poetic` | Metaphorical, evocative, lyrical |
| SATIRICAL | `satirical` | Ironic, critical, subversive |

### Gain (Sampling Control)
- **Range**: 1-10
- **Low (1-3)**: Deterministic, factual, conservative (temp: 0.1-0.7, top-k: 5-40, top-p: 0.50-0.65)
- **Mid (4-6)**: Balanced creativity and coherence (temp: 0.8-1.3, top-k: 45-80, top-p: 0.66-0.81)
- **High (7-10)**: Creative, exploratory, chaotic (temp: 1.4-2.0, top-k: 85-120, top-p: 0.82-0.98)

### Available Models
See `/models` endpoint for current list. Common models:
- `qwen3:latest` - Strong reasoning, 128K context
- `deepseek-r1:8b` - Good reasoning, 64K context
- `mistral:latest` - Fast inference, 128K context
- `llama3.1:8b` - Reliable, 128K context

---

## API Endpoints

### Utility Endpoints

#### `GET /knobs`
Returns available modes and tones for UI dropdowns.

**curl Example:**
```bash
curl http://localhost:8000/knobs
```

**Python Example:**
```python
import requests
response = requests.get("http://localhost:8000/knobs")
data = response.json()
print(f"Modes: {data['modes']}")
print(f"Tones: {data['tones']}")
```

**Response:**
```json
{
  "modes": ["invert_er", "so_what_er", "echo_er", "what_if_er", "cucumb_er", "archiv_er"],
  "tones": ["neutral", "technical", "primal", "poetic", "satirical"]
}
```

---

#### `GET /models`
Returns available Ollama models and default model.

**curl Example:**
```bash
curl http://localhost:8000/models
```

**Python Example:**
```python
import requests
response = requests.get("http://localhost:8000/models")
data = response.json()
print(f"Available: {data['models']}")
print(f"Default: {data['default']}")
```

**Response:**
```json
{
  "models": ["deepseek-r1:8b", "qwen3:latest", "mistral:latest", ...],
  "default": "mistral:latest"
}
```

---

#### `GET /health` (V2/V3 Chat Endpoints Only)
Health check with active session count.

**curl Example:**
```bash
curl http://localhost:8000/health
```

**Response:**
```json
{
  "status": "healthy",
  "active_sessions": 3
}
```

---

### Distortion Endpoints

#### `POST /distort` (Ensemble Mode)
Run all 6 modes simultaneously with shared tone/gain.

**Request Body:**
```json
{
  "text": "Your content here",
  "source": "api-client",
  "captured_at": "2025-12-03T00:00:00Z",
  "tags": [],
  "tone": "technical",
  "gain": 5,
  "model": "qwen3:latest"
}
```

**curl Example:**
```bash
curl -X POST http://localhost:8000/distort \
  -H "Content-Type: application/json" \
  -d '{
    "text": "AI systems struggle with long-context understanding.",
    "source": "api-client",
    "captured_at": "2025-12-03T10:00:00Z",
    "tags": [],
    "tone": "technical",
    "gain": 5,
    "model": "qwen3:latest"
  }'
```

**Python Example:**
```python
import requests
from datetime import datetime, timezone

response = requests.post(
    "http://localhost:8000/distort",
    json={
        "text": "AI systems struggle with long-context understanding.",
        "source": "api-client",
        "captured_at": datetime.now(timezone.utc).isoformat(),
        "tags": [],
        "tone": "technical",
        "gain": 5,
        "model": "qwen3:latest"
    },
    timeout=300
)

data = response.json()
print(f"Signal ID: {data['signal_id']}")
for output in data['outputs']:
    print(f"\n{output['mode'].upper()}:")
    print(output['response'])
```

**Response:**
```json
{
  "signal_id": "uuid-string",
  "summary": "",
  "outputs": [
    {
      "agent_id": "agent-id",
      "mode": "invert_er",
      "tone": "technical",
      "gain": 5,
      "response": "Full text response from INVERT_ER mode..."
    },
    {
      "agent_id": "agent-id",
      "mode": "so_what_er",
      "tone": "technical",
      "gain": 5,
      "response": "Full text response from SO_WHAT_ER mode..."
    }
    // ... 4 more outputs (echo_er, what_if_er, cucumb_er, archiv_er)
  ],
  "provenance": {
    "source": "api-client",
    "captured_at": "2025-12-03T10:00:00Z",
    "metadata": {}
  }
}
```

---

#### `POST /distort-manual` (Manual Mode)
Single distortion with custom mode/tone/gain.

**Request Body:**
```json
{
  "text": "Your content here",
  "mode": "cucumb_er",
  "tone": "technical",
  "gain": 5,
  "model": "qwen3:latest"
}
```

**curl Example:**
```bash
curl -X POST http://localhost:8000/distort-manual \
  -H "Content-Type: application/json" \
  -d '{
    "text": "AI systems struggle with long-context understanding.",
    "mode": "cucumb_er",
    "tone": "technical",
    "gain": 5,
    "model": "qwen3:latest"
  }'
```

**Python Example:**
```python
import requests

response = requests.post(
    "http://localhost:8000/distort-manual",
    json={
        "text": "AI systems struggle with long-context understanding.",
        "mode": "cucumb_er",
        "tone": "technical",
        "gain": 5,
        "model": "qwen3:latest"
    },
    timeout=300
)

data = response.json()
output = data['output']
print(f"Mode: {output['mode'].upper()}")
print(f"Response: {output['response']}")
```

**Response:**
```json
{
  "signal_id": "uuid-string",
  "output": {
    "agent_id": "agent-id",
    "mode": "cucumb_er",
    "tone": "technical",
    "gain": 5,
    "response": "Full text response with evidence and examples...",
    "provenance": {
      "source": "web-ui-manual",
      "captured_at": "2025-12-03T10:00:00Z",
      "metadata": {}
    }
  }
}
```

---

### Chat Session Endpoints

#### `POST /chat/new`
Create new chat session with optional initial message.

**Request Body:**
```json
{
  "mode": "cucumb_er",
  "tone": "technical",
  "gain": 5,
  "model": "qwen3:latest",
  "initial_message": "Optional first message",
  "parent_signal_id": null
}
```

**curl Example:**
```bash
curl -X POST http://localhost:8000/chat/new \
  -H "Content-Type: application/json" \
  -d '{
    "mode": "cucumb_er",
    "tone": "technical",
    "gain": 5,
    "model": "qwen3:latest",
    "initial_message": "Explain transformer architecture"
  }'
```

**Python Example:**
```python
import requests

response = requests.post(
    "http://localhost:8000/chat/new",
    json={
        "mode": "cucumb_er",
        "tone": "technical",
        "gain": 5,
        "model": "qwen3:latest",
        "initial_message": "Explain transformer architecture"
    },
    timeout=300
)

data = response.json()
session_id = data['session_id']
print(f"Session ID: {session_id}")
print(f"Response: {data['response']}")
```

**Response:**
```json
{
  "session_id": "uuid-string",
  "mode": "cucumb_er",
  "tone": "technical",
  "gain": 5,
  "message_count": 1,
  "response": "Transformers are neural network architectures...",
  "created_at": "2025-12-03T10:00:00Z"
}
```

---

#### `POST /chat/followup`
Continue conversation in existing session.

**Request Body:**
```json
{
  "session_id": "uuid-string",
  "message": "Your follow-up question"
}
```

**curl Example:**
```bash
curl -X POST http://localhost:8000/chat/followup \
  -H "Content-Type: application/json" \
  -d '{
    "session_id": "your-session-id-here",
    "message": "What are the key limitations?"
  }'
```

**Python Example:**
```python
import requests

response = requests.post(
    "http://localhost:8000/chat/followup",
    json={
        "session_id": session_id,  # From /chat/new
        "message": "What are the key limitations?"
    },
    timeout=300
)

data = response.json()
print(f"Response: {data['response']}")
print(f"Message count: {data['message_count']}")
```

**Response:**
```json
{
  "session_id": "uuid-string",
  "mode": "cucumb_er",
  "tone": "technical",
  "gain": 5,
  "message_count": 3,
  "response": "Key limitations include...",
  "updated_at": "2025-12-03T10:05:00Z"
}
```

---

#### `POST /chat/fork`
Switch mode/tone/gain mid-conversation while preserving history.

**Request Body:**
```json
{
  "session_id": "uuid-string",
  "mode": "what_if_er",
  "tone": "technical",
  "gain": 7
}
```

**curl Example:**
```bash
curl -X POST http://localhost:8000/chat/fork \
  -H "Content-Type: application/json" \
  -d '{
    "session_id": "your-session-id-here",
    "mode": "what_if_er",
    "tone": "technical",
    "gain": 7
  }'
```

**Python Example:**
```python
import requests

response = requests.post(
    "http://localhost:8000/chat/fork",
    json={
        "session_id": session_id,
        "mode": "what_if_er",
        "tone": "technical",
        "gain": 7
    }
)

data = response.json()
new_session_id = data['session_id']
print(f"New session ID: {new_session_id}")
print(f"Forked from: {data['parent_session_id']}")
```

**Response:**
```json
{
  "session_id": "new-uuid-string",
  "parent_session_id": "original-uuid-string",
  "mode": "what_if_er",
  "tone": "technical",
  "gain": 7,
  "message_count": 3,
  "created_at": "2025-12-03T10:10:00Z"
}
```

---

#### `GET /chat/session/{session_id}`
Retrieve full session details and history.

**curl Example:**
```bash
curl http://localhost:8000/chat/session/your-session-id-here
```

**Python Example:**
```python
import requests

response = requests.get(f"http://localhost:8000/chat/session/{session_id}")
data = response.json()

print(f"Session: {data['session_id']}")
print(f"Mode: {data['mode']}, Tone: {data['tone']}, Gain: {data['gain']}")
print(f"\nHistory ({len(data['history'])} exchanges):")
for exchange in data['history']:
    print(f"\nUser: {exchange['user']}")
    print(f"Assistant: {exchange['assistant'][:200]}...")
```

**Response:**
```json
{
  "session_id": "uuid-string",
  "mode": "cucumb_er",
  "tone": "technical",
  "gain": 5,
  "model_name": "qwen3:latest",
  "created_at": "2025-12-03T10:00:00Z",
  "updated_at": "2025-12-03T10:05:00Z",
  "message_count": 3,
  "history": [
    {
      "user": "Explain transformer architecture",
      "assistant": "Transformers are neural network architectures...",
      "timestamp": "2025-12-03T10:00:00Z"
    },
    {
      "user": "What are the key limitations?",
      "assistant": "Key limitations include...",
      "timestamp": "2025-12-03T10:05:00Z"
    }
  ]
}
```

---

#### `DELETE /chat/session/{session_id}`
Delete session and cleanup files.

**curl Example:**
```bash
curl -X DELETE http://localhost:8000/chat/session/your-session-id-here
```

**Python Example:**
```python
import requests

response = requests.delete(f"http://localhost:8000/chat/session/{session_id}")
data = response.json()
print(f"Status: {data['status']}")
```

**Response:**
```json
{
  "status": "deleted",
  "session_id": "uuid-string"
}
```

---

## Request/Response Schemas

### Common Parameters

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `text` | string | Yes | - | Content to distort |
| `mode` | string | Conditional | - | Required for manual/chat modes |
| `tone` | string | Yes | `neutral` | Verbal style |
| `gain` | integer | Yes | `5` | Sampling control (1-10) |
| `model` | string | No | `mistral:latest` | Ollama model name |
| `source` | string | Ensemble only | - | Provenance identifier |
| `captured_at` | string | Ensemble only | - | ISO-8601 timestamp |
| `tags` | array | No | `[]` | Metadata tags |

### Response Fields

| Field | Type | Description |
|-------|------|-------------|
| `signal_id` | string | Unique identifier for input |
| `session_id` | string | Chat session identifier |
| `response` | string | Generated text output |
| `mode` | string | Mode used for generation |
| `tone` | string | Tone used for generation |
| `gain` | integer | Gain used for generation |
| `agent_id` | string | Agent identifier |
| `provenance` | object | Input metadata |
| `created_at` | string | ISO-8601 creation timestamp |
| `updated_at` | string | ISO-8601 last update timestamp |
| `message_count` | integer | Number of exchanges in session |

---

## Code Examples

### Complete Python Client

```python
import requests
from datetime import datetime, timezone

class TwistedPairClient:
    def __init__(self, base_url="http://localhost:8000"):
        self.base_url = base_url
    
    def distort_ensemble(self, text, tone="technical", gain=5, model="qwen3:latest"):
        """Get all 6 mode perspectives"""
        response = requests.post(
            f"{self.base_url}/distort",
            json={
                "text": text,
                "source": "python-client",
                "captured_at": datetime.now(timezone.utc).isoformat(),
                "tags": [],
                "tone": tone,
                "gain": gain,
                "model": model
            },
            timeout=300
        )
        response.raise_for_status()
        return response.json()['outputs']
    
    def distort_manual(self, text, mode, tone="technical", gain=5, model="qwen3:latest"):
        """Get single mode perspective"""
        response = requests.post(
            f"{self.base_url}/distort-manual",
            json={
                "text": text,
                "mode": mode,
                "tone": tone,
                "gain": gain,
                "model": model
            },
            timeout=300
        )
        response.raise_for_status()
        return response.json()['output']
    
    def chat_new(self, mode, tone, gain, model="qwen3:latest", initial_message=None):
        """Start new chat session"""
        response = requests.post(
            f"{self.base_url}/chat/new",
            json={
                "mode": mode,
                "tone": tone,
                "gain": gain,
                "model": model,
                "initial_message": initial_message
            },
            timeout=300
        )
        response.raise_for_status()
        return response.json()
    
    def chat_followup(self, session_id, message):
        """Continue chat session"""
        response = requests.post(
            f"{self.base_url}/chat/followup",
            json={
                "session_id": session_id,
                "message": message
            },
            timeout=300
        )
        response.raise_for_status()
        return response.json()
    
    def chat_fork(self, session_id, mode, tone, gain):
        """Fork session with new settings"""
        response = requests.post(
            f"{self.base_url}/chat/fork",
            json={
                "session_id": session_id,
                "mode": mode,
                "tone": tone,
                "gain": gain
            }
        )
        response.raise_for_status()
        return response.json()

# Usage example
client = TwistedPairClient()

# Ensemble mode
outputs = client.distort_ensemble(
    "AI systems struggle with long-context understanding.",
    tone="technical",
    gain=5
)
for output in outputs:
    print(f"{output['mode'].upper()}: {output['response'][:200]}...")

# Chat session
session = client.chat_new(
    mode="cucumb_er",
    tone="technical",
    gain=5,
    initial_message="Explain transformers"
)
session_id = session['session_id']

# Follow-up
followup = client.chat_followup(session_id, "What are the limitations?")
print(followup['response'])
```

### Batch Processing Example

```python
import os
from twistedpair_client import TwistedPairClient

client = TwistedPairClient()

# Process all markdown files in directory
papers_dir = "pdfs_md/"
for filename in os.listdir(papers_dir):
    if filename.endswith(".md"):
        filepath = os.path.join(papers_dir, filename)
        
        # Read content
        with open(filepath, "r", encoding="utf-8") as f:
            content = f.read()
        
        # Get ensemble perspectives
        print(f"Processing {filename}...")
        outputs = client.distort_ensemble(content, tone="technical", gain=5)
        
        # Save summaries
        summary_file = f"summaries/{filename}"
        with open(summary_file, "w", encoding="utf-8") as f:
            for output in outputs:
                f.write(f"## {output['mode'].upper()}\n\n")
                f.write(f"{output['response']}\n\n")
                f.write("-" * 80 + "\n\n")
        
        print(f"✓ Saved to {summary_file}")
```

### Long Document Chunking Strategy

```python
import tiktoken
from twistedpair_client import TwistedPairClient

def chunk_and_summarize(long_doc, chunk_size=15000):
    """Handle 60K+ token documents"""
    client = TwistedPairClient()
    enc = tiktoken.get_encoding("cl100k_base")
    tokens = enc.encode(long_doc)
    
    # Split into chunks
    chunks = [tokens[i:i+chunk_size] for i in range(0, len(tokens), chunk_size)]
    chunk_texts = [enc.decode(chunk) for chunk in chunks]
    
    # Summarize each chunk
    summaries = []
    for i, chunk in enumerate(chunk_texts):
        print(f"Processing chunk {i+1}/{len(chunk_texts)}...")
        output = client.distort_manual(chunk, mode="cucumb_er", tone="technical", gain=5)
        summaries.append(output['response'])
    
    # Synthesize final summary
    combined = "\n\n".join(summaries)
    final = client.distort_manual(
        f"Synthesize these section summaries:\n\n{combined}",
        mode="cucumb_er",
        tone="technical",
        gain=5
    )
    return final['response']

# Usage
with open("long_paper.md", "r") as f:
    content = f.read()

summary = chunk_and_summarize(content)
print(summary)
```

---

## Error Handling

### Common HTTP Status Codes

| Code | Meaning | Solution |
|------|---------|----------|
| 200 | Success | - |
| 422 | Unprocessable Entity | Check request body matches schema |
| 404 | Not Found | Session ID doesn't exist or expired |
| 500 | Internal Server Error | Check server logs, Ollama connection |
| 502 | Bad Gateway | Ollama not running or unreachable |
| 504 | Gateway Timeout | Document too long (>60K tokens), use chunking |

### Python Error Handling Example

```python
import requests
from requests.exceptions import Timeout, ConnectionError

def robust_distort(client, text, mode, tone, gain, max_retries=3):
    """Retry on timeout/connection errors"""
    for attempt in range(max_retries):
        try:
            result = client.distort_manual(text, mode, tone, gain)
            return result['response']
        except Timeout:
            print(f"Timeout on attempt {attempt+1}, retrying...")
            if attempt == max_retries - 1:
                raise
        except ConnectionError:
            print(f"Connection error on attempt {attempt+1}, retrying...")
            if attempt == max_retries - 1:
                raise
        except requests.HTTPError as e:
            if e.response.status_code == 422:
                print(f"Invalid request: {e.response.json()}")
                raise
            elif e.response.status_code == 504:
                print("Document too long, use chunking strategy")
                raise
            else:
                print(f"HTTP error: {e}")
                raise
```

### Session Timeout Handling

```python
def safe_chat_followup(client, session_id, message):
    """Handle expired sessions gracefully"""
    try:
        return client.chat_followup(session_id, message)
    except requests.HTTPError as e:
        if e.response.status_code == 404:
            print("Session expired or not found")
            # Create new session
            session = client.chat_new(
                mode="cucumb_er",
                tone="technical",
                gain=5,
                initial_message=message
            )
            return session
        else:
            raise
```

---

## Performance Tips

### Token Limits by Model

| Model | Max Context | Effective Quality Limit | Notes |
|-------|-------------|-------------------------|-------|
| qwen3:latest | 128K | ~60K | Strong reasoning, degrades >60K |
| deepseek-r1:8b | 64K | ~60K | Good reasoning, timeouts >60K |
| mistral:latest | 128K | ~60K | Fast inference |
| llama3.1:8b | 128K | ~60K | Reliable, extended context |

### Optimization Strategies

1. **Document Length**:
   - <30K tokens: Use directly with any model
   - 30-60K tokens: Use qwen3/deepseek-r1 with caution
   - >60K tokens: Apply chunking strategy (15K chunks)

2. **Batch Processing**:
   - Process serially to avoid Ollama overload
   - Use `timeout=600` for long documents
   - Monitor memory usage with large batches

3. **Model Selection**:
   - Quick summaries: `mistral:latest` (fast)
   - Detailed analysis: `qwen3:latest` (reasoning)
   - Balanced: `llama3.1:8b` (reliable)

4. **Session Management**:
   - Sessions expire after 2 hours of inactivity (V2 default)
   - Store session IDs for later reference
   - Delete old sessions to free disk space

5. **Timeout Adjustment**:
   ```python
   # Increase timeout for long documents
   response = requests.post(url, json=payload, timeout=600)  # 10 minutes
   ```

---

## Deployment Notes

### Production Configuration

```bash
# Run server on all interfaces
uvicorn server:app --host 0.0.0.0 --port 8000

# Use Gunicorn for production (ASGI server)
pip install gunicorn uvicorn[standard]
gunicorn server:app -k uvicorn.workers.UvicornWorker --bind 0.0.0.0:8000 --workers 4
```

### Nginx Reverse Proxy

```nginx
server {
    listen 80;
    server_name twistedpair.example.com;

    location / {
        proxy_pass http://localhost:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_read_timeout 600s;  # Long timeout for LLM generation
    }
}
```

### Docker Deployment

```bash
# Build and run (see docker_distortion_service.dockerfile)
docker build -f docker_distortion_service.dockerfile -t twistedpair .
docker run -p 8000:8000 twistedpair
```

---

## Documentation and Contributing

- **GitHub**: [TwistedPair Repository](https://github.com/satoruisaka/TwistedPair)
- **Issues**: You may report bugs via GitHub Issues but be aware that this repo is **not actively maintained**.

---

**Last Updated**: December 3, 2025  
**API Version**: V2/V3  
**License**: MIT
