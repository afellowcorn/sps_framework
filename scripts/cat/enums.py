from __future__ import annotations

from strenum import Enum, StrEnum


class CatAgeEnum(StrEnum):
    NEWBORN = "newborn"
    KITTEN = "kitten"
    ADOLESCENT = "adolescent"
    YOUNG_ADULT = "young adult"
    ADULT = "adult"
    SENIOR_ADULT = "senior adult"
    SENIOR = "senior"
