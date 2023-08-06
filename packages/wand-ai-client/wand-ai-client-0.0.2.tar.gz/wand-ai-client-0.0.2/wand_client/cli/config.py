import json
from pathlib import Path
from typing import Any, Dict, Optional, Sequence

from pydantic import BaseSettings

CONFIG_PATH = Path("~/.wand/config.json")


def json_config_settings_source(settings: BaseSettings) -> Dict[str, Any]:
    encoding = settings.__config__.env_file_encoding
    if CONFIG_PATH.exists():
        return json.loads(CONFIG_PATH.read_text(encoding))
    return {}


class WandCliSettings(BaseSettings):
    WAND_API_URL: Optional[str] = None
    WAND_TOKEN: Optional[str] = None

    def check_complete(self) -> None:
        if self.WAND_API_URL is None:
            raise ValueError("Settings WAND_API_URL is not set")
        if self.WAND_TOKEN is None:
            raise ValueError("Settings WAND_TOKEN is not set")

    class Config:
        env_file_encoding = "utf-8"

        @classmethod
        def customise_sources(
            cls,
            init_settings: Any,
            env_settings: Any,
            file_secret_settings: Any,
        ) -> Sequence[Any]:
            return (
                init_settings,
                env_settings,
                json_config_settings_source,
            )
