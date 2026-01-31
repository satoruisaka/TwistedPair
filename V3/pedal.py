# pedal.py
from twistedtypes import Knobs, Mode, Tone, Signal, Prompt
from config import (
    TEMP_MIN, TEMP_MAX, 
    TOP_K_MIN, TOP_K_MAX, 
    TOP_P_MIN, TOP_P_MAX,
    GAIN_MIN, GAIN_MAX
)

def distort(signal: Signal, knobs: Knobs) -> Prompt:
    """
    Build a system + user prompt based on the signal and knob settings.
    Includes temperature, top-k, top-p, and metadata for provenance.
    """
    mode_instruction = MODE_INSTRUCTIONS[knobs.mode]
    tone_style = TONE_STYLES[knobs.tone]
    temp = gain_to_temperature(knobs.gain)
    top_k = gain_to_top_k(knobs.gain)
    top_p = gain_to_top_p(knobs.gain)

    system_prompt = (
        "You are a distortion pedal that transforms signals using explicit rhetorical operations.\n"
        f"Operation: {knobs.mode.value}\n"
        f"Style: {knobs.tone.value}\n"
        f"Guidance:\n- {mode_instruction}\n- {tone_style}\n"
        "- Never restate the same conclusion twice. Eliminate redundancy.\n"
        "- Produce 1–2 tight paragraphs or 3–5 bullet points max, whichever is sharper.\n"
        "- Keep facts grounded in the input signal unless hypothetical is requested by operation."
    )

    user_prompt = (
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

    return Prompt(
        system=system_prompt,
        user=user_prompt,
        temperature=temp,
        top_k=top_k,
        top_p=top_p,
        metadata=metadata
    )


def gain_to_temperature(g: int) -> float:
    """Map gain to temperature using linear interpolation"""
    return round(TEMP_MIN + ((TEMP_MAX - TEMP_MIN) / (GAIN_MAX - GAIN_MIN)) * (g - GAIN_MIN), 2)


def gain_to_top_k(g: int) -> int:
    """Map gain to top-k using linear interpolation"""
    return round(TOP_K_MIN + ((TOP_K_MAX - TOP_K_MIN) / (GAIN_MAX - GAIN_MIN)) * (g - GAIN_MIN))


def gain_to_top_p(g: int) -> float:
    """Map gain to top-p using linear interpolation"""
    return round(TOP_P_MIN + ((TOP_P_MAX - TOP_P_MIN) / (GAIN_MAX - GAIN_MIN)) * (g - GAIN_MIN), 2)

MODE_INSTRUCTIONS = {
    Mode.INVERT_ER: (
        "Act like a nay-sayer. Flip the polarity. Negate user claims, point out missing information, "
        "and provide counterarguments without hedging. Challenge assumptions directly and state objections plainly."
    ),
    Mode.SO_WHAT_ER: (
        "Ask 'so what?'. Interrogate the signal. Explore implications, consequences, "
        "and downstream effects. Focus on impact and trade-offs. Don't just describe—provoke and probe."
    ),
    Mode.ECHO_ER: (
        "Act like an amplifier with reverb. Exaggerate, highlight strengths, "
        "and build momentum around the signal. Be boldly enthusiastic. Dismiss doubts."
    ),
    Mode.WHAT_IF_ER: (
        "Ask 'what if?'. Hypothesize new ideas. Explore alternative scenarios, contingencies, and imaginative possibilities. "
        "Encourage speculative branching. Venture beyond obvious alternatives."
    ),
    Mode.CUCUMB_ER: (
        "Act like a cucumber. Stay cool, detached, logical, and analytical. Provide structured, balanced, and evidence-oriented commentary. "
        "Avoid emotional language or exaggeration."),
    Mode.ARCHIV_ER: (
        "Act like a librarian. Bring historical context and prior works into the analysis. Compare the signal to past events, "
        "literature, or inventions. Highlight parallels and lessons from history. Cite specific events, figures, or works by name."
    ),
}

TONE_STYLES = {
    Tone.NEUTRAL: (
        "Use clear, standard English. Be concise, balanced, and accessible. "
        "Avoid jargon or excessive flourish."
    ),
    Tone.TECHNICAL: (
        "Use precise, jargon-heavy language. Adopt a scientific or engineering register. "
        "Focus on definitions, mechanisms, and structured analysis. Avoid layman explanations."
    ),
    Tone.PRIMAL: (
        "Use short, punchy, aggressive words. Keep sentences tight and visceral. "
        "Deliver raw impact with minimal polish. No complete sentences if fragments work."
    ),
    Tone.POETIC: (
        "Use lyrical, metaphor-rich, and mystical language. Employ rhythm, imagery, and symbolic phrasing. "
        "Convey ideas as visions or allegories."
    ),
    Tone.SATIRICAL: (
        "Use witty, ironic, and humorous language. Employ exaggeration, parody, or playful mockery. "
        "Highlight absurdities and contradictions with levity. Think late-night monologue or The Onion."
    ),
}