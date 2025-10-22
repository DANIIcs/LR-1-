from __future__ import annotations
from dataclasses import dataclass

@dataclass
class Token:
    type: str
    text: str

    def __str__(self) -> str:
        return f"<{self.type}, {self.text}>"
