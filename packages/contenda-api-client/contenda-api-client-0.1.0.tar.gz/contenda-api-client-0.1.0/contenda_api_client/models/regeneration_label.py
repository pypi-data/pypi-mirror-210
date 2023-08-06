from enum import Enum


class RegenerationLabel(str, Enum):
    DECLINE_TO_LABEL = "decline to label"
    DIDNT_MAKE_SENSE = "didn't make sense"
    INACCURATE = "inaccurate"
    INCOMPLETE = "incomplete"
    STYLE = "style"

    def __str__(self) -> str:
        return str(self.value)
