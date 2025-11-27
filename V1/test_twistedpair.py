# test_twistedpair.py
import uuid
from twistedtypes import Signal
from agent import Agent
from pipeline import process_signal, write_index_incremental
from ollama_sampler import ollama_sampler
from config import DEFAULT_MODEL

def main():
    # Create a test agent with real Ollama sampler
    agent = Agent(
        agent_id="twistedpair-1", 
        model_name=DEFAULT_MODEL, 
        sampler=lambda system, user, temperature: ollama_sampler(system, user, temperature, DEFAULT_MODEL)
    )

    # Simulate a captured signal
    signal = Signal(
        id=str(uuid.uuid4()),
        content="AI systems will replace many jobs.",
        source="screenpipe://window/Chrome",
        captured_at="2025-11-26T08:45:00Z",
        tags=["workforce", "AI"],
        metadata={}
    )

    # Run through the ensemble
    result = process_signal(agent, signal, ensemble=True)

    # Write to archive + index
    write_index_incremental(result, out_dir="./runs")

    # Print summary to console
    print("Braided summary:\n")
    print(result["summary"])
    print("\nRun written to ./runs/index.html")

if __name__ == "__main__":
    main()