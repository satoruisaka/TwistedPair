# pipeline.py
import uuid
from twistedtypes import Signal, Knobs, Mode, Tone
from agent import Agent
from ensemble import run_ensemble, braid
from utils import to_serializable

import os, json
from index_generator import generate_index

import json, os
from dataclasses import asdict
from index_generator import generate_index

def write_index_incremental(new_run: dict, out_dir: str = "./runs"):
    os.makedirs(out_dir, exist_ok=True)
    archive_path = os.path.join(out_dir, "runs.json")

    # Load existing archive
    if os.path.exists(archive_path):
        with open(archive_path, "r", encoding="utf-8") as f:
            runs = json.load(f)
    else:
        runs = []

    # Append new run (convert dataclasses to dicts)
    runs.append(to_serializable(new_run))

    # Save archive
    with open(archive_path, "w", encoding="utf-8") as f:
        json.dump(runs, f, indent=2)

    # Regenerate index.html
    html = generate_index(runs)
    with open(os.path.join(out_dir, "index.html"), "w", encoding="utf-8") as f:
        f.write(html)


        
def write_index(runs: list[dict], out_dir: str = "./runs"):
    """
    Write an index.html file summarizing all runs.
    """
    os.makedirs(out_dir, exist_ok=True)
    html = generate_index(runs)
    with open(os.path.join(out_dir, "index.html"), "w", encoding="utf-8") as f:
        f.write(html)

def normalize_capture(raw: dict) -> Signal:
    return Signal(
        id=str(uuid.uuid4()),
        content=raw["text"],
        source=raw.get("source", "screenpipe://unknown"),
        captured_at=raw["captured_at"],
        tags=raw.get("tags", []),
        metadata={k: v for k, v in raw.items() if k not in ("text", "captured_at", "tags")},
    )

# pipeline.py
def default_knob_sets() -> list[Knobs]:
    return [
        Knobs(Mode.INVERT_ER, Tone.SATIRICAL, 4),
        Knobs(Mode.SO_WHAT_ER, Tone.NEUTRAL, 3),
        Knobs(Mode.ECHO_ER, Tone.POETIC, 5),
        Knobs(Mode.WHAT_IF_ER, Tone.PRIMAL, 6),
        Knobs(Mode.CUCUMB_ER, Tone.TECHNICAL, 2),
        Knobs(Mode.ARCHIV_ER, Tone.TECHNICAL, 3),
    ]

def process_signal(agent: Agent, signal: Signal, ensemble: bool = True) -> dict:
    if ensemble:
        outputs = run_ensemble(agent, signal, default_knob_sets())
        summary = braid(outputs)
        return {"signal": signal, "outputs": outputs, "summary": summary}
    else:
        # single default pedal
        knobs = Knobs(Mode.SO_WHAT_ER, Tone.NEUTRAL, 3)
        out = agent.run(signal, knobs)
        return {"signal": signal, "outputs": [out], "summary": out.response}