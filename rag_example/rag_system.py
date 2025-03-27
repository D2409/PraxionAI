import openai
import logging
import os
import sys
from requests.adapters import HTTPAdapter
from requests.sessions import Session
from urllib3.util.retry import Retry

# Ensure UTF-8 encoding for all output
sys.stdout = os.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
sys.stderr = os.TextIOWrapper(sys.stderr.buffer, encoding="utf-8", errors="replace")

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Set OpenAI API Key
openai.api_key = os.getenv("OPENAI_API_KEY", "sk-proj-batjcE88WHH0MаTRvbIyLFFRLWoZEXPi0W5hdUJvj4Ij8uGsjNuw8PxHZ_HyADkV-VWjRh5b1_T3BIbkFJEp6qlJ4BscapNLeISsnuVEUHuXeOXTVzHIDI8fH1Etj3As7kwI-7vYn9X@ka5mGRiMmf1tA7gAl")  # Replace with your actual API key if not using env vars

# Custom session to enforce UTF-8 compatibility
class UTF8Session(Session):
    def __init__(self):
        super().__init__()
        adapter = HTTPAdapter(
            max_retries=Retry(total=5, backoff_factor=1, status_forcelist=[500, 502, 503, 504])
        )
        self.mount("http://", adapter)
        self.mount("https://", adapter)

# Patch OpenAI's HTTP session
openai._openai_http_session = UTF8Session()

def generate_response(user_input, relevant_document):
    """
    Generates a recommendation based on the user input and the retrieved document
    using ChatGPT-4.
    """
    try:
        # Construct the prompt
        prompt = f"""
        You are a bot that makes recommendations for activities. You answer in very short sentences and do not include extra information.
        This is the recommended activity: {relevant_document}
        The user input is: {user_input}
        Compile a recommendation to the user based on the recommended activity and the user input.
        """

        # Ensure prompt is UTF-8 safe
        prompt = prompt.encode('utf-8', 'replace').decode('utf-8')

        logger.info("Sending prompt to OpenAI:")
        logger.info(prompt.strip())

        # Call OpenAI ChatCompletion for GPT-4
        response = openai.ChatCompletion.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": "You are a helpful assistant."},
                {"role": "user", "content": prompt.strip()}
            ],
            max_tokens=150,
            temperature=0.7
        )

        # Extract and return the generated content
        result = response["choices"][0]["message"]["content"].strip()
        logger.info("OpenAI Response: %s", result)
        return result

    except Exception as e:
        logger.error("Error in generate_response: %s", str(e))
        return "I apologize, but I encountered an error. Please try again with your request."
