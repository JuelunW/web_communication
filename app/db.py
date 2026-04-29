import os
from sqlalchemy import create_engine, Column, Integer, String, Date, Numeric, TIMESTAMP, ForeignKey, func, text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import declarative_base, sessionmaker

DATABASE_URL = os.getenv("DATABASE_URL", "").replace(
    "postgresql://", "postgresql+psycopg://"
)

engine = create_engine(DATABASE_URL, future=True)
SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False, future=True)
Base = declarative_base()

class Room(Base):
    __tablename__ = "hotel_rooms"

    id = Column(Integer, primary_key=True)
    room_number = Column(Integer, nullable=False)
    # Removed room_type as it is not in the DB
    price = Column(Integer) # Changed to Integer to match DB
    created_at = Column(TIMESTAMP, server_default=func.now())

class Guest(Base):
    __tablename__ = "hotel_guests"

    id = Column(Integer, primary_key=True)
    firstname = Column(String, nullable=False)
    lastname = Column(String, nullable=False)
    address = Column(String)
    created_at = Column(TIMESTAMP, server_default=func.now())
    api_key = Column(UUID(as_uuid=True)) # Added missing column

class Booking(Base):
    __tablename__ = "hotel_bookings"

    id = Column(Integer, primary_key=True)
    # Fixed Foreign Key table references
    guest_id = Column(Integer, ForeignKey("hotel_guests.id"))
    room_id = Column(Integer, ForeignKey("hotel_rooms.id"))

    datefrom = Column(Date, nullable=False, server_default=func.current_date())
    # Changed to nullable=True to match DB
    dateto = Column(Date, nullable=True, server_default=text("now() + interval '1 day'"))

    # Renamed 'info' to 'addinfo' and added 'stars'
    addinfo = Column(String)
    stars = Column(Integer)
    created_at = Column(TIMESTAMP, server_default=func.now())

class BookingView(Base):
    __tablename__ = "bookings_view"

    # SQLAlchemy requires at least one primary_key=True to map the ORM object,
    # even for views where the database itself might say "NULL".
    id = Column(Integer, primary_key=True)

    firstname = Column(String)
    room_id = Column(Integer)
    room_number = Column(Integer)
    datefrom = Column(Date)
    stays = Column(Integer)
    gross_price = Column(Integer)
    total_price = Column(Numeric)
    addinfo = Column(String)
    stars = Column(Integer)
    guest_id = Column(Integer)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def init_db():
    Base.metadata.create_all(bind=engine)