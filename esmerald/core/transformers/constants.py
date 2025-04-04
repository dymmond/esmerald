from inspect import Signature as InspectSignature

from esmerald.typing import Undefined

UNDEFINED = {Undefined, InspectSignature.empty}
CLASS_SPECIAL_WORDS = {"self", "cls"}
VALIDATION_NAMES = {"request", "socket", "state"}
