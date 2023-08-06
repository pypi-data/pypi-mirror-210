from enum import Enum


class RegenerationFnName(str, Enum):
    LENGTH_UNDER_200 = "length_under_200"
    SVR_REGENERATION_SCORE = "svr_regeneration_score"

    def __str__(self) -> str:
        return str(self.value)
