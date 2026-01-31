# pipeline_v2.py - Minimal V2 version without index_generator dependency
import uuid
from twistedtypes import Signal, Knobs, Mode, Tone
from agent import Agent
from ensemble import run_ensemble, braid


def normalize_capture(raw: dict) -> Signal:
    """Convert raw capture dict to Signal object."""
    return Signal(
        id=str(uuid.uuid4()),
        content=raw["text"],
        source=raw.get("source", "manual://input"),
        captured_at=raw["captured_at"],
        tags=raw.get("tags", []),
        metadata={k: v for k, v in raw.items() if k not in ("text", "captured_at", "tags")},
    )


def default_knob_sets() -> list[Knobs]:
    """Return default ensemble knob configurations."""
    return [
        Knobs(Mode.INVERT_ER, Tone.SATIRICAL, 4),
        Knobs(Mode.SO_WHAT_ER, Tone.NEUTRAL, 3),
        Knobs(Mode.ECHO_ER, Tone.POETIC, 5),
        Knobs(Mode.WHAT_IF_ER, Tone.PRIMAL, 6),
        Knobs(Mode.CUCUMB_ER, Tone.TECHNICAL, 2),
        Knobs(Mode.ARCHIV_ER, Tone.TECHNICAL, 3),
    ]


def process_signal(agent: Agent, signal: Signal, ensemble: bool = True) -> dict:
    """Process a signal through ensemble or single mode."""
    if ensemble:
        outputs = run_ensemble(agent, signal, default_knob_sets())
        summary = braid(outputs)
        return {"signal": signal, "outputs": outputs, "summary": summary}
    else:
        # Single default pedal
        knobs = Knobs(Mode.SO_WHAT_ER, Tone.NEUTRAL, 3)
        out = agent.run(signal, knobs)
        return {"signal": signal, "outputs": [out], "summary": out.response}
