# ensemble.py
from datetime import datetime, timezone
from typing import List
from twistedtypes import Signal, Knobs, AgentOutput, Prompt
from pedal import distort

def run_ensemble(agent, signal: Signal, knob_sets: List[Knobs]) -> List[AgentOutput]:
    """
    Run the ensemble: distort the same signal with multiple knob settings.
    """
    outputs = []
    for knobs in knob_sets:
        prompt: Prompt = distort(signal, knobs)
        response = agent.sampler(prompt.system, prompt.user, temperature=prompt.temperature)

        outputs.append(
            AgentOutput(
                agent_id=agent.agent_id,
                knobs=knobs,
                response=response,
                signal_id=signal.id,
                reasoning_style=f"{knobs.mode.value}/{knobs.tone.value}",
                model_info={"model_name": agent.model_name},
                # created_at=datetime.utcnow().isoformat(),
                created_at=datetime.now(timezone.utc).isoformat(),
                provenance=prompt.metadata
            )
        )
    return outputs

def braid(outputs: List[AgentOutput]) -> str:
    lines = []
    for o in outputs:
        label = f"{o.agent_id}:{o.knobs.mode.value}/{o.knobs.tone.value}/g{o.knobs.gain}"
        lines.append(f"- [{label}] {o.response.strip()}")
    return "\n".join(lines)


