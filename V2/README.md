# TwistedPair V2 - Signal Distortion with Chat Sessions

TwistedPair V2 extends the original signal distortion system with multi-turn chat capabilities, session forking, and analog knob controls.

## Features

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
   pip install fastapi uvicorn requests pyyaml
   ```

2. **Start Ollama** (must be running on localhost:11434):
   ```bash
   ollama serve
   ```

3. **Install LLM models**:
   ```bash
   ollama pull mistral
   ollama pull dolphin3
   # etc. (see config.py for full list)
   ```

4. **Start V2 server**:
   ```bash
   cd V2
   uvicorn server:app --reload
   ```

5. **Serve V2 interface** (in separate terminal):
   ```bash
   cd V2
   python -m http.server 8002
   ```

6. **Open browser**: http://localhost:8002/index.html

## Usage

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
3. Type follow-up message (press Enter to send)
4. Continue multi-turn conversation

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

**Version**: V2 Beta

**Completed**:
- ✅ Analog knob interface
- ✅ Chat sessions with forking
- ✅ V11 enhanced GAIN control

**Pending**:
- ⏳ Error handling
- ⏳ Integration tests

## License

MIT
