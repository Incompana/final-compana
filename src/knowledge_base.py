from __future__ import annotations

import json
from functools import lru_cache
from pathlib import Path
from typing import Optional

BASE_DIR = Path(__file__).resolve().parents[1]
ROLES_FILE = BASE_DIR / "knowledge_base" / "roles.json"


@lru_cache(maxsize=1)
def load_roles() -> dict:
    with ROLES_FILE.open("r", encoding="utf-8") as file:
        payload = json.load(file)
    return payload.get("roles", {})


def get_role(role_key: str) -> Optional[dict]:
    return load_roles().get(role_key)


def list_roles() -> list[str]:
    return sorted(load_roles().keys())
