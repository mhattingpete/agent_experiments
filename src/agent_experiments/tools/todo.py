import subprocess

from smolagents import tool


@tool
def add_todo_item(content: str) -> str:
    """Add a todo item.

    Args:
        content (str): The content of the todo item.

    Raises:
        ValueError: If the content is not a string.

    Returns:
        str: A message indicating the success of the operation.
    """
    try:
        subprocess.run(
            f'shortcuts run "Add reminder" -i="{content}"',
            shell=True,
            text=True,
            check=True,
        )
    except Exception as e:
        raise ValueError(
            "Creating a todo item failed. Make sure the content is a string and try again. Full trace:"
            + str(e)
        ) from e
    return f"Item added successfully! With content: {content}"
