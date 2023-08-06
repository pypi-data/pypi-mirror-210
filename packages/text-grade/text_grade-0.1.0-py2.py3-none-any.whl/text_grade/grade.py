from enum import Enum


class Grade(str, Enum):
    VERY_EASY: str = "very easy"
    EASY: str = "easy"
    FAIRLY_DIFFICULT: str = "fairly difficult"
    VERY_DIFFICULT: str = "very difficult"
    UNKNOWN: str = "unknown"

    def __str__(self) -> str:
        return str.__str__(self)
