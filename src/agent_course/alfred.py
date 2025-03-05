from smolagents import CodeAgent, DuckDuckGoSearchTool, HfApiModel, tool


# Tool to suggest a menu based on the occasion
@tool
def suggest_menu(occasion: str) -> str:
    """
    Suggests a menu based on the occasion.
    Supported occasions: casual, formal, superhero or other. Default is custom menu.

    Args:
        occasion: The type of occasion for the party.
    """
    if occasion == "casual":
        return "Pizza, snacks, and drinks."
    elif occasion == "formal":
        return "3-course dinner with wine and dessert."
    elif occasion == "superhero":
        return "Buffet with high-energy and healthy food."
    else:
        return "Custom menu for the butler."


# Alfred, the butler, preparing the menu for the party, searching for music recommendations and estimating the preparation time
agent = CodeAgent(
    tools=[suggest_menu, DuckDuckGoSearchTool()],
    model=HfApiModel(),
    additional_authorized_imports=["datetime"],
)

agent.push_to_hub("mhattingpete/AlfredAgent")

agent.run(
    """
    Alfred needs to prepare for the party. Here are the tasks:
    1. Prepare the drinks - 30 minutes
    2. Decorate the mansion - 60 minutes
    3. Decide on the menu - 5 minutes
    4. Set up the menu - 45 minutes
    5. Prepare the music and playlist - 45 minutes

    Answer the following questions:
    1. If we start right now, at what time will the party be ready?
    2. What menu should Alfred prepare for the party?
    3. What music should be played at the party?
    """
)
