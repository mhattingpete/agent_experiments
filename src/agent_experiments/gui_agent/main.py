import re
from io import BytesIO
from pathlib import Path
from time import sleep

import helium
import requests
from dotenv import load_dotenv
from markdownify import markdownify
from PIL import Image
from requests.exceptions import RequestException
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from smolagents import CodeAgent, HfApiModel, tool
from smolagents.agents import ActionStep

from src.agent_experiments.tracing import add_tracing

add_tracing()

# Load environment variables
load_dotenv()

MODEL = "Qwen/Qwen2.5-Coder-32B-Instruct"
# MODEL = "deepseek-ai/DeepSeek-R1-Distill-Qwen-32B"
# MODEL = "HuggingFaceTB/SmolLM2-1.7B-Instruct"

# Initialize the model
model = HfApiModel(MODEL)


def _extract_github_issue_content(
    repo_owner: str, repo_name: str, issue_number: int
) -> str:
    """Extracts the content of a GitHub issue and converts it to Markdown.

    Args:
        repo_owner: The owner of the GitHub repository.
        repo_name: The name of the GitHub repository.
        issue_number: The number of the GitHub issue.

    Returns:
        str: The content of the GitHub issue in Markdown format.
    """
    try:
        # Construct the URL for the GitHub API
        url = f"https://api.github.com/repos/{repo_owner}/{repo_name}/issues/{issue_number}"

        # Make the GET request
        response = requests.get(url)
        response.raise_for_status()  # Raise an exception for bad status codes

        # Check if the request was successful
        issue_data = response.json()

        # Extract key details from the issue data
        title = issue_data.get("title")
        body = issue_data.get("body")

        # Convert the HTML content to Markdown
        markdown_content = markdownify(body).strip()

        markdown_content = f"## {title}\n\n{markdown_content}"

        # Remove multiple line breaks
        markdown_content = re.sub(r"\n{3,}", "\n\n", markdown_content)

        return markdown_content

    except RequestException as e:
        return f"Error fetching the webpage: {str(e)}"
    except Exception as e:
        return f"An unexpected error occurred: {str(e)}"


def _score_issues(issues: list[str]) -> list[int]:
    """Scores a list of GitHub issues based on the ease of implementation.

    Args:
        issues: A list of GitHub issues in Markdown format.

    Returns:
        list[int]: A list of scores for each issue, where higher scores indicate easier implementation.
    """
    scores = []
    for issue in issues:
        # Score the issue based on the number of code blocks
        messages = [
            {
                "role": "system",
                "content": """Please score the ease of implementation of this issue. Higher scores indicate easier implementation. 
                Use the following scale: 1 (difficult) to 5 (easy). Respond with a single number.""",
            },
            {"role": "user", "content": issue},
        ]
        score = int(model(messages, stop_sequences=["END"]).content)
        scores.append(score)
    return scores


@tool
def score_issues(
    repo_owner: str, repo_name: str, issue_numbers: list[int]
) -> list[int]:
    """Scores a list of GitHub issues based on the ease of implementation.

    Args:
        repo_owner: The owner of the GitHub repository.
        repo_name: The name of the GitHub repository.
        issue_numbers: The numbers of the GitHub issues.

    Returns:
        list[int]: A list of scores for each issue, where higher scores indicate easier implementation.
    """
    if not repo_owner or not repo_name:
        raise ValueError("Please provide the repository owner and name.")
    if not issue_numbers:
        raise ValueError("Please provide at least one issue number.")
    issues = [
        _extract_github_issue_content(repo_owner, repo_name, issue_number)
        for issue_number in issue_numbers
    ]
    scores = _score_issues(issues)
    return scores


@tool
def get_github_issue_numbers(repo_owner: str, repo_name: str) -> list[int]:
    """Extracts the issue number of a GitHub issue.

    Args:
        repo_owner: The owner of the GitHub repository.
        repo_name: The name of the GitHub repository.

    Returns:
        list[int]: A list of issue numbers.
    """
    try:
        # Construct the URL for the GitHub API
        url = f"https://api.github.com/repos/{repo_owner}/{repo_name}/issues"

        # Make the GET request
        response = requests.get(url)
        response.raise_for_status()  # Raise an exception for bad status codes

        # Check if the request was successful
        issue_data = response.json()

        return [int(issue.get("number")) for issue in issue_data]

    except RequestException as e:
        return f"Error fetching the webpage: {str(e)}"
    except Exception as e:
        return f"An unexpected error occurred: {str(e)}"


@tool
def search_item_ctrl_f(text: str, nth_result: int = 1) -> str:
    """Searches for text on the current page via Ctrl + F and jumps to the nth occurrence.

    Args:
        text: The text to search for
        nth_result: Which occurrence to jump to. Defaults to 1.

    Raises:
        Exception: If the nth occurrence is not found

    Returns:
        str: A message indicating the number of matches and the focused element
    """
    elements = driver.find_elements(By.XPATH, f"//*[contains(text(), '{text}')]")
    if nth_result > len(elements):
        raise Exception(
            f"Match n°{nth_result} not found (only {len(elements)} matches found)"
        )
    result = f"Found {len(elements)} matches for '{text}'."
    elem = elements[nth_result - 1]
    driver.execute_script("arguments[0].scrollIntoView(true);", elem)
    result += f"Focused on element {nth_result} of {len(elements)}"
    return result


@tool
def go_back() -> None:
    """Goes back to previous page."""
    driver.back()


@tool
def close_popups() -> str:
    """
    Closes any visible modal or pop-up on the page. Use this to dismiss pop-up windows!
    This does not work on cookie consent banners.
    """
    webdriver.ActionChains(driver).send_keys(Keys.ESCAPE).perform()


# Configure Chrome options
chrome_options = webdriver.ChromeOptions()
chrome_options.add_argument("--force-device-scale-factor=1")
chrome_options.add_argument("--window-size=1000,1350")
chrome_options.add_argument("--disable-pdf-viewer")
chrome_options.add_argument("--window-position=0,0")

# Initialize the browser
driver = helium.start_chrome(headless=False, options=chrome_options)


# Set up screenshot callback
def save_screenshot(memory_step: ActionStep, agent: CodeAgent) -> None:
    sleep(1.0)  # Let JavaScript animations happen before taking the screenshot
    driver = helium.get_driver()
    current_step = memory_step.step_number
    if driver is not None:
        for previous_memory_step in agent.memory.steps:
            # Remove previous screenshots for lean processing
            if (
                isinstance(previous_memory_step, ActionStep)
                and previous_memory_step.step_number <= current_step  # - 2
            ):
                previous_memory_step.observations_images = None
        png_bytes = driver.get_screenshot_as_png()
        image = Image.open(BytesIO(png_bytes))
        # Reduce image size to decrease token usage
        # Reduce image to be max 50 x 50 pixels
        recude_factor = max(image.size) / 50
        image = image.reduce(int(recude_factor))
        print(f"Captured a browser screenshot: {image.size} pixels")
        # Create a copy to ensure it persists in memory
        memory_step.observations_images = [image.copy()]

    # Update observations with current URL
    url_info = f"Current url: {driver.current_url}"
    memory_step.observations = (
        url_info
        if memory_step.observations is None
        else memory_step.observations + "\n" + url_info
    )


# Create the agent
agent = CodeAgent(
    tools=[
        go_back,
        close_popups,
        search_item_ctrl_f,
        get_github_issue_numbers,
        score_issues,
    ],
    model=model,
    additional_authorized_imports=["helium", "bs4", "requests"],
    step_callbacks=[save_screenshot],
    max_steps=20,
    verbosity_level=2,
)
agent.prompt_templates["system_prompt"] = Path("prompt.txt").read_text()


# Import helium for the agent
# scoring_agent.python_executor("from helium import *", scoring_agent.state)
agent.python_executor("from helium import *", agent.state)

helium_instructions = """
You can use helium to access websites. Don't bother about the helium driver, it's already managed.
We've already ran "from helium import *"
Then you can go to pages!
Code:
```py
go_to('github.com/trending')
```<end_code>

You can directly click clickable elements by inputting the text that appears on them.
Code:
```py
click("Top products")
```<end_code>

If it's a link:
Code:
```py
click(Link("Top products"))
```<end_code>

If you try to interact with an element and it's not found, you'll get a LookupError.
In general stop your action after each button click to see what happens on your screenshot.
Never try to login in a page.

To scroll up or down, use scroll_down or scroll_up with as an argument the number of pixels to scroll from.
Code:
```py
scroll_down(num_pixels=1200) # This will scroll one viewport down
```<end_code>

When you have pop-ups with a cross icon to close, don't try to click the close icon by finding its element or targeting an 'X' element (this most often fails).
Just use your built-in tool `close_popups` to close them:
Code:
```py
close_popups()
```<end_code>

You can use .exists() to check for the existence of an element. For example:
Code:
```py
if Text('Accept cookies?').exists():
    click('I accept')
```<end_code>

You can navigate back to the previous page with the built-in tool `go_back`:
Code:
```py
go_back()
```<end_code>
"""

search_request = """
Please navigate to https://github.com/huggingface/smolagents/issues?q=is%3Aissue and give me a list of top 5 issues sorted by the ease of implementation.
"""

try:
    agent_output = agent.run(search_request + helium_instructions)
    print("Final output:")
    print(agent_output)
except Exception as e:
    print(f"An error occurred: {e}")
finally:
    helium.kill_browser()
