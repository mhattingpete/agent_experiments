import os

from dotenv import load_dotenv
from smolagents import AzureOpenAIServerModel, CodeAgent, VisitWebpageTool

from src.agent_course.tools.cargo_transfer import calculate_cargo_travel_time
from src.agent_course.tools.search import GoogleSearchTool

load_dotenv()

model = AzureOpenAIServerModel(
    model_id="gpt-4o-mini-2024-07-18",  # Or gpt-4o-2024-05-13
    azure_endpoint=os.getenv("AZURE_OPENAI_ENDPOINT"),
    api_key=os.getenv("AZURE_OPENAI_API_KEY"),
    api_version=os.getenv("OPENAI_API_VERSION"),
)

task = """Find all Batman filming locations in the world, calculate the time to transfer via cargo plane to here (we're in Gotham, 40.7128° N, 74.0060° W), and return them to me as a pandas dataframe.
Also give me some supercar factories with the same cargo plane transfer time."""

agent = CodeAgent(
    model=model,
    tools=[GoogleSearchTool("serper"), VisitWebpageTool(), calculate_cargo_travel_time],
    additional_authorized_imports=["pandas"],
    max_steps=20,
)

result = agent.run(task)

print(result)


agent.planning_interval = 4

detailed_report = agent.run(
    f"""
You're an expert analyst. You make comprehensive reports after visiting many websites.
Don't hesitate to search for many queries at once in a for loop.
For each data point that you find, visit the source url to confirm numbers.

{task}
"""
)

print(detailed_report)
