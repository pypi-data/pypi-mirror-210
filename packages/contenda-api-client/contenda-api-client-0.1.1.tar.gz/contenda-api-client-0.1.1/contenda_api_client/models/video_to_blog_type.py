from enum import Enum


class VideoToBlogType(str, Enum):
    PRESENTATION = "presentation"
    TUTORIAL = "tutorial"

    def __str__(self) -> str:
        return str(self.value)
