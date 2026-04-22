from enum import Enum

class IsSugarFreeEnum(str, Enum):
    yes = "yes"
    no = "no"
    no_preference = "no_preference"