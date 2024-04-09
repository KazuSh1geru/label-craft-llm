import os

from dotenv import load_dotenv

load_dotenv()

MODEL_NAME = "gpt-4"
# MODEL_NAME = "gpt-3.5-turbo"


def get_openai_api_key() -> tuple[str, str]:
    return os.getenv("OPENAI_API_KEY"), MODEL_NAME
