# server.py - V2 with Chat Session Support
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from datetime import datetime, timezone
from typing import Optional
import uuid

# Import V2 local modules
from pipeline_v2 import process_signal, normalize_capture, default_knob_sets
from agent import Agent
from ollama_sampler import ollama_sampler
from config import DEFAULT_MODEL, AVAILABLE_LLM_MODELS
from twistedtypes import Signal, Knobs, Mode, Tone
from ensemble import run_ensemble

# Import V2 chat modules
from session_manager import get_session_store, ChatSession
from chat_context import build_chat_prompt, format_history_for_display


app = FastAPI()

# Enable CORS for local development
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Create agent dynamically based on model
def get_agent(model_name: str = DEFAULT_MODEL):
    return Agent(
        agent_id="twistedpair-web",
        model_name=model_name,
        sampler=lambda system, user, temperature, top_k, top_p: ollama_sampler(system, user, temperature, top_k, top_p, model_name)
    )

class Capture(BaseModel):
    text: str
    source: str
    captured_at: str
    tags: list[str] = []
    tone: str = None
    gain: int = None
    model: str = None

class ManualDistort(BaseModel):
    text: str
    mode: str
    tone: str
    gain: int
    model: str = None

class ChatFollowUpRequest(BaseModel):
    session_id: str
    message: str

class ChatNewRequest(BaseModel):
    mode: str
    tone: str
    gain: int
    model: str = None
    initial_message: Optional[str] = None
    parent_signal_id: Optional[str] = None

class ChatForkRequest(BaseModel):
    session_id: str
    mode: str
    tone: str
    gain: int


@app.get("/knobs")
def get_knobs():
    """Return available mode, tone options for UI dropdowns"""
    return {
        "modes": [m.value for m in Mode],
        "tones": [t.value for t in Tone]
    }

@app.get("/models")
def get_models():
    """Return available LLM models"""
    return {
        "models": AVAILABLE_LLM_MODELS,
        "default": DEFAULT_MODEL
    }

@app.post("/distort")
def distort(capture: Capture):
    """Ensemble mode - runs all 6 modes with user-selected tone/gain"""
    agent = get_agent(capture.model or DEFAULT_MODEL)
    signal = normalize_capture(capture.dict())
    
    # If tone/gain provided, create custom ensemble with those settings
    if capture.tone and capture.gain:
        tone = Tone(capture.tone)
        gain = capture.gain
        custom_knobs = [Knobs(mode, tone, gain) for mode in Mode]
        # Use custom knobs directly - don't call process_signal first
        outputs = run_ensemble(agent, signal, custom_knobs)
        result = {"signal": signal, "outputs": outputs, "summary": ""}
    else:
        # Use default ensemble
        result = process_signal(agent, signal, ensemble=True)
    
    return {
        "signal_id": signal.id,
        "summary": result.get("summary", ""),
        "outputs": [
            {
                "agent_id": o.agent_id,
                "mode": o.knobs.mode.value,
                "tone": o.knobs.tone.value,
                "gain": o.knobs.gain,
                "response": o.response,
            } for o in result["outputs"]
        ],
        "provenance": {"source": signal.source, "captured_at": signal.captured_at},
    }

@app.post("/distort-manual")
def distort_manual(req: ManualDistort):
    """Manual mode - single distortion with custom mode/tone/gain"""
    agent = get_agent(req.model or DEFAULT_MODEL)
    signal = Signal(
        id=str(uuid.uuid4()),
        content=req.text,
        source="web-ui-manual",
        captured_at=datetime.now(timezone.utc).isoformat(),
        tags=[],
        metadata={}
    )
    
    knobs = Knobs(
        mode=Mode(req.mode),
        tone=Tone(req.tone),
        gain=req.gain
    )
    
    output = agent.run(signal, knobs)
    
    return {
        "signal_id": signal.id,
        "output": {
            "agent_id": output.agent_id,
            "mode": output.knobs.mode.value,
            "tone": output.knobs.tone.value,
            "gain": output.knobs.gain,
            "response": output.response,
        }
    }


# ============= V2 Chat Session Endpoints =============

@app.post("/chat/new")
def chat_new(req: ChatNewRequest):
    """
    Create a new chat session with specified knobs.
    Optionally include an initial message and parent signal ID.
    """
    store = get_session_store()
    
    knobs = Knobs(
        mode=Mode(req.mode),
        tone=Tone(req.tone),
        gain=req.gain
    )
    
    session = store.create_session(
        knobs=knobs,
        model_name=req.model or DEFAULT_MODEL,
        parent_signal_id=req.parent_signal_id
    )
    
    # If initial message provided, process it immediately
    response_text = None
    if req.initial_message:
        agent = get_agent(session.model_name)
        
        # For initial message, use standard distort (no history yet)
        signal = Signal(
            id=str(uuid.uuid4()),
            content=req.initial_message,
            source="chat-session",
            captured_at=datetime.now(timezone.utc).isoformat(),
            tags=[],
            metadata={"session_id": session.session_id}
        )
        
        output = agent.run(signal, knobs)
        response_text = output.response
        
        # Add to session history
        session.add_message("user", req.initial_message)
        session.add_message("assistant", response_text)
        store.update_session(session)
    
    return {
        "session_id": session.session_id,
        "knobs": {
            "mode": session.knobs.mode.value,
            "tone": session.knobs.tone.value,
            "gain": session.knobs.gain
        },
        "model": session.model_name,
        "history": format_history_for_display(session),
        "response": response_text
    }


@app.post("/chat/followup")
def chat_followup(req: ChatFollowUpRequest):
    """
    Continue an existing chat session with a follow-up message.
    Uses conversation history to build context for LLM.
    """
    store = get_session_store()
    session = store.get_session(req.session_id)
    
    if not session:
        raise HTTPException(status_code=404, detail="Session not found or expired")
    
    # Build prompt with conversation history
    prompt = build_chat_prompt(session, req.message)
    
    # Get LLM response
    agent = get_agent(session.model_name)
    response = agent.sampler(prompt.system, prompt.user, prompt.temperature, prompt.top_k, prompt.top_p)
    
    # Update session history
    session.add_message("user", req.message)
    session.add_message("assistant", response)
    store.update_session(session)
    
    return {
        "session_id": session.session_id,
        "response": response,
        "history": format_history_for_display(session),
        "knobs": {
            "mode": session.knobs.mode.value,
            "tone": session.knobs.tone.value,
            "gain": session.knobs.gain
        }
    }


@app.get("/chat/session/{session_id}")
def get_session(session_id: str):
    """Retrieve session details and conversation history."""
    store = get_session_store()
    session = store.get_session(session_id)
    
    if not session:
        raise HTTPException(status_code=404, detail="Session not found or expired")
    
    return {
        "session_id": session.session_id,
        "knobs": {
            "mode": session.knobs.mode.value,
            "tone": session.knobs.tone.value,
            "gain": session.knobs.gain
        },
        "model": session.model_name,
        "history": format_history_for_display(session),
        "created_at": session.created_at,
        "last_active": session.last_active,
        "parent_signal_id": session.parent_signal_id
    }


@app.delete("/chat/session/{session_id}")
def delete_session(session_id: str):
    """Delete a chat session (for 'New Query' functionality)."""
    store = get_session_store()
    store.delete_session(session_id)
    return {"status": "deleted", "session_id": session_id}


@app.post("/chat/fork")
def chat_fork(req: ChatForkRequest):
    """
    Fork a chat session with new mode/tone/gain settings.
    Copies conversation history to new session with different knobs.
    """
    store = get_session_store()
    old_session = store.get_session(req.session_id)
    
    if not old_session:
        raise HTTPException(status_code=404, detail="Original session not found or expired")
    
    # Create new knobs
    new_knobs = Knobs(
        mode=Mode(req.mode),
        tone=Tone(req.tone),
        gain=req.gain
    )
    
    # Create new session with same model
    new_session = store.create_session(
        knobs=new_knobs,
        model_name=old_session.model_name,
        parent_signal_id=old_session.parent_signal_id
    )
    
    # Copy conversation history
    for msg in old_session.messages:
        new_session.messages.append(msg)
    
    # Update timestamp
    new_session.last_active = datetime.now(timezone.utc).isoformat()
    store.update_session(new_session)
    
    return {
        "session_id": new_session.session_id,
        "old_session_id": req.session_id,
        "knobs": {
            "mode": new_session.knobs.mode.value,
            "tone": new_session.knobs.tone.value,
            "gain": new_session.knobs.gain
        },
        "model": new_session.model_name,
        "history": format_history_for_display(new_session),
        "message": f"Session forked from {old_session.knobs.mode.value} to {new_knobs.mode.value}"
    }


@app.get("/health")
def health_check():
    """Health check endpoint for monitoring."""
    store = get_session_store()
    return {
        "status": "healthy",
        "active_sessions": len(store.sessions),
        "timestamp": datetime.now(timezone.utc).isoformat()
    }
