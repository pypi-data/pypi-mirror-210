from .grade import Grade


class Score:
    __slots__ = ("_value", "_grade")

    def __init__(self, value: int) -> None:
        self._value = value
        self._grade = self._calculate_grade(value)

    @property
    def value(self) -> int:
        return self._value

    @property
    def grade(self) -> Grade:
        return self._grade

    @property
    def grade_description(self) -> str:
        return str(self._grade)

    def _calculate_grade(self, value: int) -> Grade:
        if value > 75:
            return Grade.VERY_EASY
        elif value <= 75 and value > 50:
            return Grade.EASY
        elif value <= 50 and value > 25:
            return Grade.FAIRLY_DIFFICULT
        elif value <= 25 and value >= 0:
            return Grade.VERY_DIFFICULT
        else:
            return Grade.UNKNOWN

    def __str__(self) -> str:
        return self._grade

    def __repr__(self) -> str:
        return f"Score(value={self._value}, grade='{self.grade_description}')"
