from smolagents import CodeAgent, HfApiModel

agent = CodeAgent(
    tools=[], model=HfApiModel(), additional_authorized_imports=["datetime"]
)

agent.run(
    """
    Alfred needs to prepare for the party. Here are the tasks:
    1. Prepare the drinks - 30 minutes
    2. Decorate the mansion - 60 minutes
    3. Set up the menu - 45 minutes
    3. Prepare the music and playlist - 45 minutes

    If we start right now, at what time will the party be ready?
    """
)
