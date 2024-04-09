from openai import OpenAI

from src.utils.get_openai_api_key import get_openai_api_key
from src.utils.init_logger import init_logger

# ログ設定ファイルの読み込み
logger = init_logger()
api_key, model_name = get_openai_api_key()


def generate_sqlx(messages: list[dict[str, str]]) -> str | None:
    try:
        client = OpenAI(
            # This is the default and can be omitted
            api_key=api_key,
        )
        chat_completion = client.chat.completions.create(
            messages=messages,
            model=model_name,
        )
        logger.info(chat_completion.choices[0].message.content)
        return chat_completion.choices[0].message.content
    except Exception:
        logger.exception("Failed to generate text")
        return None
