from pydantic import BaseModel, Field
from datetime import datetime


class Checkpoint(BaseModel):
    check_dt: datetime = Field(default_factory=datetime.now)
    data: dict = Field(default_factory=dict)
    next_scheduled: int = None
    position: int = None
    active: bool = True
