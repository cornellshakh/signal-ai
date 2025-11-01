import yaml
import structlog
from jinja2 import Template
from typing import Any

log = structlog.get_logger()


class PromptManager:
    def __init__(self, file_path: str = "src/signal_ai/prompts.yaml"):
        try:
            with open(file_path, "r") as f:
                self._prompts = yaml.safe_load(f)
        except FileNotFoundError:
            log.critical("prompt.file.not_found", file_path=file_path)
            self._prompts = {}

    def get(self, key: str, **kwargs: Any) -> str:
        """
        Retrieves a prompt by its key and renders it with the given variables.
        """
        if key not in self._prompts:
            log.error("prompt.key.not_found", key=key)
            raise ValueError(f"Prompt key '{key}' not found.")

        template = Template(self._prompts[key])
        return template.render(**kwargs)
