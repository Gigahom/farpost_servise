from pydantic import BaseModel

from datetime import datetime

class CountSchema(BaseModel):
    count: int


class PositeonTimeSchema(BaseModel):
    positeon: list[int]
    time: list[datetime]
    
class PositeonTimeALLSchema(BaseModel):
    positeon: int
    time: datetime
    
class PositeonTimeALL(BaseModel):
    positeon_time: PositeonTimeALLSchema
