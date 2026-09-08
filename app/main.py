from fastapi import Depends, FastAPI, HTTPException
from sqlalchemy.orm import Session

from app.database import Base, engine, get_db
from app import models, schemas

Base.metadata.create_all(bind = engine)

app = FastAPI()

@app.get("/")
def root():
    return {"message": "EventForge API"}

@app.get("/events", response_model=list[schemas.EventResponse])
def get_events(db: Session = Depends(get_db)):
    events = db.query(models.Event).all()

    return events

@app.post("/events")
def create_event(event: schemas.EventCreate, db: Session = Depends(get_db)):
    venue = db.query(models.Venue).filter(models.Venue.id == event.venue_id).first()

    if venue is None:
        raise HTTPException(
            status_code = 404,
            detail = "Venue not found"
        )

    db_event =models.Event(
        name = event.name,
        venue_id = event.venue_id
    )
    db.add(db_event)
    db.commit()
    db.refresh(db_event)

    return db_event

@app.get("/venues")
def get_venues(db: Session = Depends(get_db)):
    venues = db.query(models.Venue).all()
    return venues

@app.post("/venues")
def create_venue(venue: schemas.VenueCreate, db: Session = Depends(get_db)):
    db_venue = models.Venue(
        name = venue.name,
        address = venue.address
    )
    db.add(db_venue)
    db.commit()
    db.refresh(db_venue)



    return db_venue

@app.get("/events/{event_id}/seats")
def get_seats(
    event_id: int,
    db: Session = Depends(get_db)
):
    event = db.query(models.Event).filter(models.Event.id == event_id).first()

    if event is None:
        raise HTTPException(
            status_code=404,
            detail="Event not found"
        )

    seats = db.query(models.Seat).filter(
        models.Seat.event_id == event_id
    ).all()

    return seats
@app.post("/events/{event_id/seats")
def create_seat(
        event_id: int,
        seat: schemas.SeatCreate,
        db: Session = Depends(get_db)
):
    event = db.query(models.Event).filter(models.Event.id == event_id).first()

    if event is None:
        raise HTTPException(
            status_code=404,
            detail = "Event not found"
        )

    db_seat = models.Seat(
        section = seat.section,
        row = seat.row,
        number = seat.number,
        event_id= event_id
    )

    db.add(db_seat)
    db.commit()
    db.refresh(db_seat)

    return db_seat
