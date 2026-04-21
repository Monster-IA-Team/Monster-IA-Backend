from enum import Enum

class TasteProfileEnum(str, Enum):
    sweet = "sweet"
    sour = "sour"
    moderate = "moderate"

class IsSugarFreeEnum(str, Enum):
    yes = "yes"
    no = "no"
    no_preference = "no_preference"