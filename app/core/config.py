from __future__ import annotations
import os, yaml
from pydantic import BaseModel
from typing import Optional

class OverridesConfig(BaseModel):
    enabled: bool = False

class TocConfig(BaseModel):
    source: str = "json_only"
    path_pattern: str = "manuals/{manual}/00_目次.json"
    hierarchical_default: bool = False
    use_loc: bool = False
    overrides: OverridesConfig = OverridesConfig()

class LoggingConfig(BaseModel):
    level: str = "INFO"

class Settings(BaseModel):
    manuals_root: str = "manuals"
    toc: TocConfig = TocConfig()
    validation_mode: str = "relaxed"  # relaxed / strict
    logging: LoggingConfig = LoggingConfig()

def load_settings(path: str = "config.yaml") -> Settings:
    data = {}
    if os.path.exists(path):
        with open(path, "r", encoding="utf-8") as f:
            data = yaml.safe_load(f) or {}
    # 環境変数の簡易オーバーライド（必要最小限）
    mr = os.getenv("MANUALS_ROOT")
    if mr:
        data.setdefault("manuals_root", mr)
    return Settings(**data)
