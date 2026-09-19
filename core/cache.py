import hashlib
import json
import time
from typing import Any


class PromptCache:
    def __init__(self, ttl_seconds: int = 3600):
        self.ttl_seconds = ttl_seconds
        self._cache: dict[str, tuple[float, Any]] = {}

    def _key(self, prompt: str, generator: str) -> str:
        raw = json.dumps(
            {
                "prompt": prompt.strip(),
                "generator": generator.lower().strip(),
            },
            sort_keys=True,
            ensure_ascii=False,
        )

        return hashlib.sha256(raw.encode("utf-8")).hexdigest()

    def get(self, prompt: str, generator: str):
        key = self._key(prompt, generator)

        entry = self._cache.get(key)

        if entry is None:
            return None

        created_at, value = entry

        if time.time() - created_at > self.ttl_seconds:
            del self._cache[key]
            return None

        return value

    def set(self, prompt: str, generator: str, value: Any):
        key = self._key(prompt, generator)
        self._cache[key] = (time.time(), value)

    def clear(self):
        self._cache.clear()
