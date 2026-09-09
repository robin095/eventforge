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
def get_venues(
        db: Session = Depends(get_db)
):
    venues = db.query(models.Venue).all()
    return venues

@app.post("/venues")
def create_venue(
        venue: schemas.VenueCreate,
        db: Session = Depends(get_db)
):
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
@app.post("/events/{event_id}/seats")
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


@app.get("/users")
def get_users(db: Session = Depends(get_db)):
    users = db.query(models.User).all()
    return users


@app.post("/users")
def create_user(
        user: schemas.UserCreate,
        db: Session = Depends(get_db)
):
    db_user = models.User(
        name = user.name,
        email = user.email
    )

    db.add(db_user)
    db.commit()
    db.refresh(db_user)

    return db_user

@app.post("/reservations")
def create_reservation(
        reservation: schemas.ReservationCreate,
        db: Session = Depends(get_db)
):
    user = (
        db.query(models.User)
        .filter(models.User.id == reservation.user_id)
        .first()
    )

    if user is None:
        raise HTTPException(
            status_code=404,
            detail="User not found"
        )

    event =(
        db.query(models.Event)
        .filter(models.Event.id == reservation.event_id)
        .first()
    )

    if event is None:
        raise HTTPException(
            status_code=404,
            detail="Event not found"
        )

    seat = (
        db.query(models.Seat)
        .filter(models.Seat.id == reservation.seat_id)
        .first()
    )

    if seat is None:
        raise HTTPException(
            status_code=404,
            detail="Seat not found"
        )

    if seat.event_id != reservation.event_id:
        raise HTTPException(
            status_code=400,
            detail="Seat does not belong to this event"
        )

    existing_reservation = (
        db.query(models.Reservation)
        .filter(models.Reservation.seat_id == reservation.seat_id,
                models.Reservation.event_id == reservation.event_id)
        .first()
    )

    if existing_reservation is not None:
        raise HTTPException(
            status_code=400,
            detail="Seat is already reserved"
        )
    db_reservation = models.Reservation(
        user_id = reservation.user_id,
        event_id= reservation.event_id,
        seat_id = reservation.seat_id
    )

    db.add(db_reservation)
    db.commit()
    db.refresh(db_reservation)

    return db_reservation