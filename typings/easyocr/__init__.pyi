from __future__ import annotations

from typing import Any, Iterable, List, Sequence

__all__ = ["Reader"]


class Reader:
    def __init__(self, languages: Sequence[str], **kwargs: Any) -> None: ...

    def readtext(
        self,
        *args: Any,
        detail: int = 1,
        paragraph: bool = False,
        **kwargs: Any,
    ) -> List[str]: ...
