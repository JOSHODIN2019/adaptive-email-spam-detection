"""Key-value storage abstraction for state that must survive across
process restarts on platforms with no persistent filesystem.

Local file writes (the original design) work fine on a continuously-
running process, but both of our cloud deployments periodically reset
their filesystem out from under the app: Vercel serverless functions
have no persistent disk at all (every cold start reloads from the
git-committed baseline), and Render's free plan spins the instance down
after inactivity, which has the same effect. This meant a feedback
correction could vanish the next time the user checked back - not a
bug in how the correction was applied, but in where it was kept.

KVStore gives the adaptive model, ADWIN detector, and in-flight
prediction lookups somewhere durable to live: Upstash Redis, reachable
over HTTPS from any environment (not tied to either platform's
filesystem), when KV_REST_API_URL/KV_REST_API_TOKEN are configured.
Falls back to local files - the original behavior, unchanged - when
they are not, so local development needs no database at all.
"""

import base64
import json
from abc import ABC, abstractmethod
from pathlib import Path
from typing import Optional


class KVStore(ABC):
    @abstractmethod
    def get_bytes(self, key: str) -> Optional[bytes]: ...

    @abstractmethod
    def set_bytes(self, key: str, data: bytes) -> None: ...

    @abstractmethod
    def get_json(self, key: str) -> Optional[dict]: ...

    @abstractmethod
    def set_json(self, key: str, data: dict, ttl_seconds: Optional[int] = None) -> None: ...

    @abstractmethod
    def delete(self, key: str) -> None: ...


class LocalFileKVStore(KVStore):
    """Original behavior: each key is a file under base_dir. No TTL
    support - local dev/Render's free-tier reset window is short enough
    that unbounded local growth was never the concern `ttl_seconds` on
    the Redis backend exists for."""

    def __init__(self, base_dir: Path) -> None:
        self._base_dir = base_dir
        self._base_dir.mkdir(parents=True, exist_ok=True)

    def _path(self, key: str) -> Path:
        return self._base_dir / key

    def get_bytes(self, key: str) -> Optional[bytes]:
        path = self._path(key)
        return path.read_bytes() if path.exists() else None

    def set_bytes(self, key: str, data: bytes) -> None:
        self._path(key).write_bytes(data)

    def get_json(self, key: str) -> Optional[dict]:
        path = self._path(key)
        return json.loads(path.read_text()) if path.exists() else None

    def set_json(self, key: str, data: dict, ttl_seconds: Optional[int] = None) -> None:
        self._path(key).write_text(json.dumps(data))

    def delete(self, key: str) -> None:
        path = self._path(key)
        if path.exists():
            path.unlink()


class UpstashKVStore(KVStore):
    """Binary values are base64-encoded, since Redis/Upstash's REST API
    is JSON-over-HTTP - raw bytes aren't a natively transportable value
    type there the way they are in a local file write."""

    def __init__(self, url: str, token: str) -> None:
        from upstash_redis import Redis

        self._client = Redis(url=url, token=token)

    def get_bytes(self, key: str) -> Optional[bytes]:
        value = self._client.get(key)
        return base64.b64decode(value) if value is not None else None

    def set_bytes(self, key: str, data: bytes) -> None:
        self._client.set(key, base64.b64encode(data).decode("ascii"))

    def get_json(self, key: str) -> Optional[dict]:
        value = self._client.get(key)
        return json.loads(value) if value is not None else None

    def set_json(self, key: str, data: dict, ttl_seconds: Optional[int] = None) -> None:
        self._client.set(key, json.dumps(data), ex=ttl_seconds)

    def delete(self, key: str) -> None:
        self._client.delete(key)
