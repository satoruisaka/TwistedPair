# server.py
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from datetime import datetime, timezone
from pipeline import process_signal, normalize_capture, default_knob_sets
from agent import Agent
from ollama_sampler import ollama_sampler, AVAILABLE_LLM_MODELS
from config import DEFAULT_MODEL
from twistedtypes import Signal, Knobs, Mode, Tone
import uuid

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
        sampler=lambda system, user, temperature: ollama_sampler(system, user, temperature, model_name)
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
        result = process_signal(agent, signal, ensemble=True)
        # Override with custom knobs
        from ensemble import run_ensemble
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