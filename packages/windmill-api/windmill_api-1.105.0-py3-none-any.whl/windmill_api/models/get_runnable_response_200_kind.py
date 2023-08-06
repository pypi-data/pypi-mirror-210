from enum import Enum


class GetRunnableResponse200Kind(str, Enum):
    SCRIPT = "script"
    FLOW = "flow"

    def __str__(self) -> str:
        return str(self.value)
