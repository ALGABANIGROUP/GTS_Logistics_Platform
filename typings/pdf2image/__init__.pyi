from __future__ import annotations

from typing import Any, List

__all__ = ["convert_from_path", "convert_from_bytes"]


def convert_from_path(path: str, **kwargs: Any) -> List[Any]: ...


def convert_from_bytes(data: bytes, **kwargs: Any) -> List[Any]: ...
