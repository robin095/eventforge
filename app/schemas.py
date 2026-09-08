from pydantic import BaseModel, ConfigDict


class VenueCreate(BaseModel):
    name: str
    address: str

class EventCreate(BaseModel):
    name: str
    venue_id: int

class SeatCreate(BaseModel):
    section: str
    row: str
    number: int

class VenueResponse(BaseModel):
    id: int
    name: str
    address: str

    model_config = ConfigDict(from_attributes=True)

class EventResponse(BaseModel):
    id: int
    name: str
    venue: VenueResponse
    model_config = ConfigDict(from_attributes=True)

