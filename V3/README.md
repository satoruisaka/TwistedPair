# TwistedPair V3 - Signal Distortion with Web Search

TwistedPair V3 adds natural language web search capabilities to the V2 chat system. Simply include phrases like "check the web" in your prompts to automatically fetch and analyze real-time web content through Brave Search API or DuckDuckGo.

## Features

### V3 Web Search (NEW!)
- **Natural Language Triggers**: Use phrases like "check the web", "search online", "look up", "find on the internet"
- **Automatic Query Extraction**: Intelligently extracts the main question from your text
- **Brave Search API (Primary)**: High-quality results with free tier (2,000 queries/month)
- **DuckDuckGo Fallback**: Automatic fallback if Brave API unavailable
- **7 Search Results**: Fetches 7 sources instead of 3 for better coverage
- **Always Shows Snippets**: All 7 sources visible even if full content blocked
- **User-Agent Rotation**: 10 diverse browser agents to reduce 403 errors
- **Content Fetching**: Automatically fetches and cleans HTML from search results
- **Source Citations**: Web sources displayed as clickable links with status (fetched/snippet-only)
- **Chat Integration**: Web search works in initial queries AND follow-up conversations
- **Graceful Degradation**: Handles blocked sites by showing snippets when full content unavailable

### Core Distortion (V1 Features)
- **6 Rhetorical Modes**: INVERT_ER, SO_WHAT_ER, ECHO_ER, WHAT_IF_ER, CUCUMB_ER, ARCHIV_ER
- **5 Tone Styles**: NEUTRAL, TECHNICAL, PRIMAL, POETIC, SATIRICAL
- **Enhanced GAIN Control**: Collectively controls temperature (0.1-2.0), top-k (5-120), and top-p (0.50-0.98)
- **Analog Rotating Knobs**: Guitar pedal-style interface with 270° drag interaction
- **Ensemble Mode**: Run all 6 modes simultaneously
- **Manual Mode**: Single custom mode with selected tone/gain
- **Dynamic Loading**: Models, modes, and tones loaded from API (no hardcoded values)

### V2 Chat Features
- **Multi-turn Conversations**: Follow up on any distortion output
- **Session Persistence**: 2-hour timeout with file+memory hybrid storage
- **Session Forking**: Switch mode/tone/gain mid-conversation while preserving history
- **Ensemble Follow-up**: Pick any of 6 outputs to continue chatting
- **Chat History**: Full conversation display with role labels
- **Fork Controls**: Analog knobs for switching modes during chat

## Installation

### Prerequisites
- Python 3.10+
- Ollama with models installed (mistral, dolphin3, etc.)
- Node.js/Python HTTP server for serving static files

### Setup
1. **Install Python dependencies**:
   ```bash
   pip install fastapi uvicorn requests pyyaml ddgs beautifulsoup4 lxml
   ```

2. **Configure Brave Search API** (recommended):
   - Get free API key at: https://brave.com/search/api/ (2,000 queries/month)
   - See `BRAVE_API_SETUP.md` for detailed setup instructions
   - Set in `config.py`: `BRAVE_API_KEY = "your_key_here"`
   - Or use environment variable: `BRAVE_API_KEY`
   - System falls back to DuckDuckGo if not configured

3. **Start Ollama** (must be running on localhost:11434):
   ```bash
   ollama serve
   ```

4. **Install LLM models**:
   ```bash
   ollama pull mistral
   ollama pull dolphin3
   # etc. (see config.py for full list)
   ```

5. **Start V3 server**:
   ```bash
   cd V3
   uvicorn server:app --reload
   ```

6. **Serve V3 interface** (in separate terminal):
   ```bash
   cd V3
   python -m http.server 8003
   ```

7. **Open browser**: http://localhost:8003/index.html

## Usage

### Web Search (V3 Feature)
Simply include natural language triggers in your prompts:

**Examples:**
```
What are the latest quantum computing breakthroughs? Check the web for recent developments.
→ Searches, fetches quantum computing articles, distorts real data

Tell me about SpaceX Starship. Search online for updates.
→ Finds current news and analyzes with selected mode

How does CRISPR work? Look up recent research.
→ Fetches scientific explanations from web
```

**Trigger phrases:** "check the web", "search online", "look up", "find on the internet", "go check web"

**What happens:**
1. System detects web search intent (8 trigger patterns)
2. Extracts main question with smart query extraction (4 strategies)
3. Searches Brave API (or DuckDuckGo fallback) for 7 results
4. Fetches content from URLs with rotating user agents
5. Shows all 7 sources with snippets + full content when available
6. LLM distorts based on REAL web data (4-5 full articles typically)
7. Sources displayed as clickable links with fetch status (fetched/snippet-only)

### Initial Distortion
1. Select model from dropdown (dynamically loaded from Ollama)
2. Choose Ensemble or Manual mode
3. Rotate analog knobs:
   - **Mode** (Manual only): Select rhetorical operation
   - **Tone**: Select verbal style
   - **Gain** (1-10): Control output creativity (low=deterministic, high=creative)
4. Enter signal text
5. Click "Distort Signal"
6. View outputs with mode/tone/gain badges

### Chat Follow-Up
1. After distortion, click "Follow Up" on any output
2. Chat interface appears with conversation history
3. Type follow-up message (can include web search triggers!)
4. Web search works in chat too - ask follow-up questions with "check the web"
5. Continue multi-turn conversation with live web data

### Session Forking (Switch Mode)
1. During chat, adjust the 3 fork knobs (Mode/Tone/Gain)
2. Click "Switch Mode" button
3. System creates new session with new settings + preserved history
4. Continue conversation with new rhetorical lens

### New Query
- Click "New Query" to return to initial distortion screen

## API Endpoints

### Distortion
- `POST /distort`: Ensemble mode
- `POST /distort-manual`: Manual mode
- `GET /knobs`: Available modes/tones
- `GET /models`: Available models

### Chat
- `POST /chat/new`: Create session
- `POST /chat/followup`: Continue conversation
- `POST /chat/fork`: Switch mode mid-chat
- `GET /chat/session/{id}`: Get session
- `DELETE /chat/session/{id}`: Delete session
- `GET /health`: Health check

## Configuration

### Gain Parameters (config.py)
```python
TEMP_MIN = 0.1, TEMP_MAX = 2.0    # Temperature range
TOP_K_MIN = 5, TOP_K_MAX = 120     # Top-k range
TOP_P_MIN = 0.50, TOP_P_MAX = 0.98 # Top-p range
```

### Session Timeout (session_manager.py)
```python
SESSION_TIMEOUT = timedelta(hours=2)
```

## Development Status

**Version**: V3 Beta (Web Search Integration)

**Completed**:
- ✅ Analog knob interface with 270° rotation
- ✅ Chat sessions with forking and 2-hour persistence
- ✅ V11 enhanced GAIN control (temperature + top-k + top-p)
- ✅ Natural language web search (8 trigger patterns)
- ✅ Brave Search API integration (primary, 2K free queries/month)
- ✅ DuckDuckGo fallback (automatic, free)
- ✅ User-agent rotation (10 browsers, reduces 403 errors)
- ✅ Smart query extraction (4 extraction strategies)
- ✅ Always show snippets (7 sources visible even if blocked)
- ✅ Web source citations in UI with fetch status
- ✅ Web search in chat follow-ups

**Pending**:
- ⏳ Error handling improvements
- ⏳ Integration tests
- ⏳ FAISS local document search (V3 Phase 2)

## License

MIT
