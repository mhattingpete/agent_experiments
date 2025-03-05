from pathlib import Path

from dotenv import load_dotenv
from smolagents import CodeAgent, HfApiModel

from src.agent_experiments.tracing import add_tracing

add_tracing()

# Load environment variables
load_dotenv()

MODEL = "Qwen/Qwen2.5-Coder-32B-Instruct"
# MODEL = "deepseek-ai/DeepSeek-R1-Distill-Qwen-32B"
# MODEL = "HuggingFaceTB/SmolLM2-1.7B-Instruct"

# Initialize the model
model = HfApiModel(MODEL)


# Create the agent
agent = CodeAgent(
    tools=[],
    model=model,
    max_steps=3,
    verbosity_level=2,
)

agent.prompt_templates["system_prompt"] = Path("prompt.txt").read_text()

# with open("prompt.txt", "w") as f:
#    f.write(agent.system_prompt)

# Run the agent
agent.run("")
