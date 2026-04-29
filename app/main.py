from fastapi import FastAPI, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy import text
from sqlalchemy.orm import Session

from app.db import get_db, init_db, Room

app = FastAPI()

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