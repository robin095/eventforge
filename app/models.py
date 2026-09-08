from sqlalchemy import Column, ForeignKey, Integer, String
from sqlalchemy.orm import relationship
from app.database import Base

class Venue(Base):
    __tablename__ = "venues"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    address = Column(String, nullable=False)

    events = relationship("Event", back_populates="venue")

class Event(Base):
    __tablename__ = "events"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    venue_id = Column(Integer, ForeignKey("venues.id"), nullable=False)

    venue = relationship("Venue", back_populates="events")
    seats = relationship("Seat", back_populates="event")

class Seat(Base):
    __tablename__ = "seats"

    id = Column(Integer, primary_key=True, index=True)
    section = Column (String, nullable=False)
    row = Column (String, nullable=False)
    number = Column (Integer, nullable=False)
    event_id = Column (Integer, ForeignKey("events.id"), nullable=False)

    event = relationship("Event", back_populates="seats")