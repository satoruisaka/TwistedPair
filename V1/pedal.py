# pedal.py
from twistedtypes import Knobs, Mode, Tone, Signal, Prompt

def distort(signal: Signal, knobs: Knobs) -> Prompt:
    """
    Build a system + user prompt based on the signal and knob settings.
    Includes explicit temperature and metadata for provenance.
    """
    mode_instruction = MODE_INSTRUCTIONS[knobs.mode]
    tone_style = TONE_STYLES[knobs.tone]

    system_prompt = (
        "You are a distortion pedal that transforms signals using explicit rhetorical operations.\n"
        f"Operation: {knobs.mode.value}\n"
        f"Style: {knobs.tone.value}\n"
        "Guidance:\n"
        f"- {mode_instruction}\n"
        f"- {tone_style}\n"
        "- Never restate the same conclusion twice. Eliminate redundancy."
    )

    user_prompt = signal.content

    return Prompt(
        system=system_prompt,
        user=user_prompt,
        temperature=knobs.gain / 10.0,   # map gain (1–10) to temperature (0.1–1.0)
        metadata={
            "signal_id": signal.id,
            "source": signal.source,
            "captured_at": signal.captured_at,
            "tags": signal.tags,
            "mode": knobs.mode.value,
            "tone": knobs.tone.value,
            "gain": knobs.gain,
        }
    )


def gain_to_temperature(g: int) -> float:
    # Map 1..10 to 0.1..1.0 with subtle nonlinearity for mid-range nuance
    return round(0.05 + (g / 10) * 0.95, 2)

MODE_INSTRUCTIONS = {
    Mode.INVERT_ER: (
        "Flip the polarity of the signal. Negate claims, point out missing information, "
        "and provide counterarguments. Challenge assumptions directly."
    ),
    Mode.SO_WHAT_ER: (
        "Interrogate the signal by asking 'so what?'. Explore implications, consequences, "
        "and downstream effects. Focus on impact and trade-offs."
    ),
    Mode.ECHO_ER: (
        "Amplify and reverberate positives. Exaggerate opportunities, highlight strengths, "
        "and build momentum around the signal."
    ),
    Mode.WHAT_IF_ER: (
        "Hypothesize new ideas. Explore alternative scenarios, contingencies, and imaginative possibilities. "
        "Encourage speculative branching."
    ),
    Mode.CUCUMB_ER: (
        "Analyze with cool-headed academic rigor. Provide structured, balanced, and evidence-oriented commentary. "
        "Maintain logical clarity and detachment."
    ),
    Mode.ARCHIV_ER: (
        "Bring historical context and prior works into the analysis. Compare the signal to past events, "
        "literature, or inventions. Highlight parallels and lessons from history."
    ),
}

TONE_STYLES = {
    Tone.NEUTRAL: (
        "Use clear, standard English. Be concise, balanced, and accessible. "
        "Avoid jargon or excessive flourish."
    ),
    Tone.TECHNICAL: (
        "Use precise, jargon-heavy language. Adopt a scientific or engineering register. "
        "Focus on definitions, mechanisms, and structured analysis."
    ),
    Tone.PRIMAL: (
        "Use short, punchy, aggressive words. Keep sentences tight and visceral. "
        "Deliver raw impact with minimal polish."
    ),
    Tone.POETIC: (
        "Use lyrical, metaphor-rich, and mystical language. Employ rhythm, imagery, and symbolic phrasing. "
        "Convey ideas as visions or allegories."
    ),
    Tone.SATIRICAL: (
        "Use witty, ironic, and humorous language. Employ exaggeration, parody, or playful mockery. "
        "Highlight absurdities and contradictions with levity."
    ),
}

def build_prompt(signal: Signal, knobs: Knobs) -> Prompt:
    mode_instr = MODE_INSTRUCTIONS[knobs.mode]
    tone_style = TONE_STYLES[knobs.tone]
    temp = gain_to_temperature(knobs.gain)

    system = (
        "You are a distortion pedal that transforms signals using explicit rhetorical operations.\n"
        f"Operation: {knobs.mode.value}\n"
        f"Style: {knobs.tone.value}\n"
        f"Guidance:\n- {mode_instr}\n- {tone_style}\n"
        "- Never restate the same conclusion twice. Eliminate redundancy.\n"
        "- Produce 1–2 tight paragraphs or 3–5 bullet points max, whichever is sharper.\n"
        "- Keep facts grounded in the input signal unless hypothetical is requested by operation."
    )

    user = (
        f"Signal:\n{signal.content}\n\n"
        "Task:\nApply the operation and style above to this signal. "
        "If the signal is ambiguous, state the most probable interpretation, then proceed."
    )

    metadata = {
        "signal_id": signal.id,
        "source": signal.source,
        "captured_at": signal.captured_at,
        "tags": signal.tags,
        "knobs": {
            "mode": knobs.mode.value,
            "tone": knobs.tone.value,
            "gain": knobs.gain,
        },
    }

    return Prompt(system=system, user=user, temperature=temp, metadata=metadata)