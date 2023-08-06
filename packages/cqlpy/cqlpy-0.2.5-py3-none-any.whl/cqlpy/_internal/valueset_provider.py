from typing import Any, Optional, Protocol


class ValueSetProvider(Protocol):
    def get_valueset(self, name: str, scope: Optional[str]) -> dict[str, Any]:
        ...
