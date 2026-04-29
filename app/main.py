from fastapi import FastAPI, Depends, HTTPException
from fastapi.security import APIKeyHeader
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from sqlalchemy import text, func
from sqlalchemy.orm import Session
from datetime import date

from app.db import get_db, init_db, Room, Booking, Guest, BookingView

app = FastAPI()

origins = [
    "*", # Allow all origins

    "https://web-communication-git-web-communitation.2.rahtiapp.fi",
    "http://localhost",

    "http://127.0.0.1:5500",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

my_name = "Jay"

@app.on_event("startup")
def startup():
    init_db()

# Pydantic schema for POST
class RoomCreate(BaseModel):
    room_number: int
    room_type: str
    price: float


@app.get("/")
def default_endpoint(db: Session = Depends(get_db)):
    result = db.execute(text("SELECT version()"))
    return { "version": result.scalar(), "endpoints": "rooms/" }


@app.post("/rooms")
def create_room(payload: RoomCreate, db: Session = Depends(get_db)):
    # We need to map the incoming data object (pydantic RoomCreate) with the SQLAlchemy Data model
    room = Room(
        room_number=payload.room_number,
        room_type=payload.room_type,
        price=payload.price
    )
    # If we have the same field names, we could also just do:
    #room = Room(**payload.model_dump())

    # Prepare object for insert
    db.add(room)

    # Actually execute SQL INSERT
    db.commit()

    # If you need the updated data (like for returning), you need to refresh
    db.refresh(room)
    return room


@app.get("/rooms")
def get_rooms(db: Session = Depends(get_db)):
    # ORM equivalent of:
    #   SELECT * FROM rooms ORDER BY id DESC
    return db.query(Room).order_by(Room.id.desc()).all()


@app.get("/rooms/{id}")
def get_room(id: int, db: Session = Depends(get_db)):
    # ORM equivalent of:
    #   SELECT * FROM rooms WHERE id = %s
    room = db.query(Room).filter(Room.id == id).first()

    if not room:
        raise HTTPException(404, "Room not found")

    return room


@app.delete("/rooms/{id}")
def delete_room(id: int, db: Session = Depends(get_db)):
    # ORM loads the object first
    room = db.query(Room).filter(Room.id == id).first()

    if not room:
        raise HTTPException(404, "Room not found")

    # ORM tracks deletion instead of raw DELETE SQL
    db.delete(room)
    db.commit()

    return {"deleted": id}



# Assume validate_key is defined elsewhere in your file
# from auth import validate_key

api_key_header = APIKeyHeader(name="X-API-Key", auto_error=False)

def validate_key(
    api_key: str = Depends(api_key_header),
    db: Session = Depends(get_db) # Inject the DB session here
):
    if not api_key:
        raise HTTPException(status_code=401, detail="API key is missing") # Note: FastAPI detail usually takes a string

    # Query the guest using SQLAlchemy ORM
    guest = db.query(Guest).filter(Guest.api_key == api_key).first()

    if not guest:
        raise HTTPException(status_code=401, detail="Invalid API key")

    return guest
# ---------------------------------------------------
# Pydantic Schemas
# ---------------------------------------------------
class BookingCreate(BaseModel):
    room_id: int
    guest_id: int
    datefrom: date
    dateto: date
    addinfo: str | None = None

class Stars(BaseModel):
    stars: int

# ---------------------------------------------------
# Endpoints
# ---------------------------------------------------

@app.get("/bookings")
def get_bookings(guest: Guest = Depends(validate_key), db: Session = Depends(get_db)):
    bookings = db.query(BookingView).filter(
        BookingView.guest_id == guest.id
    ).order_by(BookingView.datefrom.asc()).all()

    return bookings


@app.post("/bookings")
def create_booking(booking: BookingCreate, db: Session = Depends(get_db)):
    new_booking = Booking(
        room_id=booking.room_id,
        guest_id=booking.guest_id,
        datefrom=booking.datefrom,
        dateto=booking.dateto,
        addinfo=booking.addinfo
    )

    db.add(new_booking)
    db.commit()
    db.refresh(new_booking)

    return {"message": "Booking created!", "booking_id": new_booking.id}


@app.put("/bookings/{id}")
def put_bookings(id: int, stars: Stars, guest: Guest = Depends(validate_key), db: Session = Depends(get_db)):
    booking = db.query(Booking).filter(
        Booking.id == id,
        Booking.guest_id == guest.id
    ).first()

    if not booking:
        raise HTTPException(
            status_code=404,
            detail=f"Booking {id} not found or you don't have permission to update this booking."
        )

    booking.stars = stars.stars
    db.commit()
    db.refresh(booking)

    return booking


@app.get("/guests")
def get_guests(db: Session = Depends(get_db)):
    # Create the subquery for 'previous_visits'
    visits_subquery = (
        db.query(func.count(Booking.id))
        .filter(Booking.guest_id == Guest.id)
        .filter(Booking.dateto < func.current_date())
        .scalar_subquery()
    )

    # Query Guests and attach the subquery as a column
    results = db.query(
        Guest.id,
        Guest.firstname,
        Guest.lastname,
        visits_subquery.label("previous_visits")
    ).all()

    # Format the results into a list of dictionaries
    guests = [
        {
            "id": row.id,
            "firstname": row.firstname,
            "lastname": row.lastname,
            "previous_visits": row.previous_visits
        }
        for row in results
    ]

    return {"guests": guests}


@app.get("/guests/{id}")
def get_guests_id(id: int, db: Session = Depends(get_db)):
    # Count the previous visits directly
    visit_count = db.query(func.count(Booking.id)).filter(
        Booking.guest_id == id,
        Booking.dateto < func.current_date()
    ).scalar()

    return {"count": visit_count}