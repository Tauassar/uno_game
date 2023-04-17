from typing import Optional

from pydantic import BaseModel

from . import enums


class UnoCardModel(BaseModel):
    color: Optional[enums.CardColors]
    suit: Optional[enums.CardSuits]
    new_color: Optional[enums.CardColors]
