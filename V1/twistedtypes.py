# types.py
from dataclasses import dataclass
from enum import Enum
from typing import List, Dict, Any, Optional

class Mode(Enum):
    INVERT_ER = "invert_er"     # Negates signals, flips polarity, points out missing info
    SO_WHAT_ER = "so_what_er"   # Questions signals, explores implications and consequences
    ECHO_ER = "echo_er"         # Amplifies positives, reverberates opportunities
    WHAT_IF_ER = "what_if_er"   # Hypothesizes new ideas, explores alternative scenarios
    CUCUMB_ER = "cucumb_er"     # Cool-headed academic analysis
    ARCHIV_ER = "archiv_er"     # Brings historical context, prior works, literature parallels

class Tone(Enum):
    NEUTRAL = "neutral"     # Clear, standard English
    TECHNICAL = "technical" # Precise, jargon-heavy, scientific/engineering register
    PRIMAL = "primal"       # Short, punchy, aggressive
    POETIC = "poetic"       # Lyrical, metaphor-rich, mystical
    SATIRICAL = "satirical" # Witty, ironic, humorous

@dataclass(frozen=True)
class Knobs:
    mode: Mode
    tone: Tone
    gain: int  # 1..10

@dataclass(frozen=True)
class Signal:
    id: str
    content: str
    source: str           # e.g., "screenpipe://window/Chrome"
    captured_at: str      # ISO-8601 UTC
    tags: List[str]
    metadata: Dict[str, Any]  # e.g., window title, app, URL, frame coords

@dataclass(frozen=True)
class Prompt:
    system: str
    user: str
    temperature: float
    metadata: Dict[str, Any]

@dataclass
class AgentOutput:
    agent_id: str
    knobs: Knobs
    signal_id: str
    response: str
    reasoning_style: str   # not chain-of-thought; just label e.g., "counterargument/extrapolation"
    model_info: Dict[str, Any]
    created_at: str
    provenance: Dict[str, Any]