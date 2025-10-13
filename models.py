from pydantic import BaseModel

class CreateShip(BaseModel):
    name: str
    displacement: float
    port: str
    captain: str
    berth_num: int
    target: str

class Ship(CreateShip):
    id: int
    