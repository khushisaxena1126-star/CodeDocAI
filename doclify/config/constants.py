from dataclasses import dataclass

@dataclass
class LiteLLMConfig:
    DEFAULT_MODEL: str = "qwen/qwen3.6-27b"