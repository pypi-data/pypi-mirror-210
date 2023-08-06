from enum import Enum


class BlogSegmentType(str, Enum):
    BODY = "body"
    CODE = "code"
    HEADING = "heading"
    IMAGE = "image"
    QUESTION = "question"
    USER_BODY = "user_body"
    USER_CODE = "user_code"
    USER_HEADING = "user_heading"

    def __str__(self) -> str:
        return str(self.value)
