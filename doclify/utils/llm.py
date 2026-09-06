from dotenv import load_dotenv
import json
import os
import re
from typing import Optional, Any, Union, Dict, List

from groq import Groq
load_dotenv()

from doclify.utils.utils import get_prompt
from doclify.utils.logger import get_logger
from doclify.schema.schema import LLMConfig
from doclify.config.constants import LiteLLMConfig

logger = get_logger(__name__)


def get_chat_model(llm_config: Optional[LLMConfig] = None) -> str:
    raw_model = llm_config.model if llm_config else LiteLLMConfig.DEFAULT_MODEL

    if not raw_model:
        raw_model = "qwen/qwen3.6-27b"

    logger.info(f"Targeting Groq model: {raw_model}")
    return raw_model


def generate_doc(
    code_content: str,
    prompt_type: str,
    llm_config: Optional[LLMConfig] = None,
    metadata: Optional[dict] = None
) -> str:

    try:
        model_name = get_chat_model(llm_config)

        prompt_text = get_prompt(prompt_type)

        if prompt_type == "final_summary":
            project_name = (
                metadata.get("project_name", os.path.basename(os.getcwd()))
                if metadata
                else os.path.basename(os.getcwd())
            )

            try:
                prompt_text = prompt_text.format(project_name=project_name)
            except (KeyError, ValueError):
                prompt_text = prompt_text.replace(
                    "{project_name}",
                    project_name
                )

        content = (
            f"{prompt_text}\n\n"
            f"[FILE CONTENT START]\n"
            f"{code_content}\n"
            f"[FILE CONTENT END]"
        )

        api_key = os.environ.get("GROQ_API_KEY", "").strip()

        if not api_key:
            raise ValueError(
                "Missing GROQ_API_KEY. Please ensure your .env file is set up correctly."
            )

        client = Groq(api_key=api_key)

        kwargs = {
            "model": model_name,
            "messages": [
                {
                    "role": "user",
                    "content": content
                }
            ],
            "stream": True,
            "temperature": 0,
            "max_tokens": 900,
            "reasoning_format": "hidden",
            "reasoning_effort": "none"
        }

        logger.info(
            f"Sending request to Groq API with model {model_name}"
        )

        response = client.chat.completions.create(**kwargs)

        message_content = ""

        for chunk in response:
            if getattr(chunk.choices[0].delta, "content", None) is not None:
                message_content += chunk.choices[0].delta.content

        # Remove <think>...</think> reasoning blocks.
        message_content = re.sub(
            r"<think>.*?</think>",
            "",
            message_content,
            flags=re.DOTALL
        ).strip()

        # For README generation, remove any plain-text reasoning
        # that appears before the actual Markdown document.
        if prompt_type == "final_summary":
            markdown_start = re.search(
                r"(?m)^#\s+",
                message_content
            )

            if markdown_start:
                message_content = (
                    message_content[markdown_start.start():]
                    .strip()
                )

        return message_content

    except Exception as e:
        err_str = str(e)

        logger.error(
            f"Failed to generate documentation using Groq: {err_str}",
            exc_info=True
        )

        raise ValueError(
            f"Failed to generate documentation: {err_str}"
        )