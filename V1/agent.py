# agent.py
from datetime import datetime, timezone
from twistedtypes import Prompt, Knobs, Signal, AgentOutput
from pedal import distort

class Agent:
    def __init__(self, agent_id: str, model_name: str, sampler):
        self.agent_id = agent_id
        self.model_name = model_name
        self.sampler = sampler  # callable(system, user, temperature) -> str

    def run(self, signal: Signal, knobs: Knobs) -> AgentOutput:
        prompt = distort(signal, knobs)
        response = self.sampler(
            system=prompt.system,
            user=prompt.user,
            temperature=prompt.temperature,
        )
        return AgentOutput(
            agent_id=self.agent_id,
            knobs=knobs,
            signal_id=signal.id,
            response=response,
            reasoning_style=knobs.mode.value,
            model_info={"model_name": self.model_name, "temperature": prompt.temperature},
            created_at=datetime.now(timezone.utc).isoformat(),
            provenance={
                "prompt_metadata": prompt.metadata,
            },
        )

# ensemble.py
from typing import Iterable, List

def run_ensemble(agent: Agent, signal: Signal, knob_sets: Iterable[Knobs]) -> List[AgentOutput]:
    return [agent.run(signal, k) for k in knob_sets]

def braid(outputs: List[AgentOutput]) -> str:
    # Create a compact, non-redundant “twisted pair” summary
    lines = []
    for o in outputs:
        label = f"{o.agent_id}:{o.knobs.mode.value}/{o.knobs.tone.value}/g{o.knobs.gain}"
        lines.append(f"- [{label}] {o.response.strip()}")
    return "\n".join(lines)