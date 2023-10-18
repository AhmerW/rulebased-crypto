from pydantic import BaseModel, Field
from datetime import datetime


class Checkpoint(BaseModel):
    check_dt: datetime = Field(default_factory=datetime.now)
    data: dict = Field(default_factory=dict)

    position: int = 0  # in what position should it continue from?
    active: bool = True
