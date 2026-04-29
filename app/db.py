import os
from sqlalchemy import create_engine, Column, Integer, String, Date, Numeric, TIMESTAMP, ForeignKey, func, text
from sqlalchemy.orm import declarative_base, sessionmaker

# ---------------------------------------------------
# DATABASE SETUP
# ---------------------------------------------------
# SQLAlchemy uses an "engine" instead of manual psycopg connections.
# The engine manages connection pooling automatically.
DATABASE_URL = os.getenv("DATABASE_URL").replace(
    "postgresql://", "postgresql+psycopg://"
)

engine = create_engine(DATABASE_URL, future=True)

# Session = unit of work (similar to a psycopg connection + cursor combined,
# but with ORM tracking of objects)
SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False, future=True)

Base = declarative_base()


# ---------------------------------------------------
# ORM MODEL: ROOMS
# ---------------------------------------------------
# This class represents a TABLE in the database.
# Each attribute = column.
class Room(Base):
    __tablename__ = "rooms"

    # PRIMARY KEY (like SERIAL PRIMARY KEY in raw SQL)
    id = Column(Integer, primary_key=True)

    # NOT NULL constraint
    room_number = Column(Integer, nullable=False)

    # VARCHAR column (string in Python maps to SQL VARCHAR/TEXT)
    room_type = Column(String)

    # NUMERIC column (good for money; avoids float precision issues)
    price = Column(Numeric)

    # server_default runs in PostgreSQL (not Python)
    created_at = Column(TIMESTAMP, server_default=func.now())

# ---------------------------------------------------
# ORM MODEL: GUESTS
# ---------------------------------------------------
class Guest(Base):
    __tablename__ = "guests"

    id = Column(Integer, primary_key=True)

    firstname = Column(String, nullable=False)
    lastname = Column(String, nullable=False)
    address = Column(String)
    created_at = Column(TIMESTAMP, server_default=func.now())

# ---------------------------------------------------
# ORM MODEL: BOOKINGS
# ---------------------------------------------------
class Booking(Base):
    __tablename__ = "bookings"

    id = Column(Integer, primary_key=True)

    # Foreign keys
    guest_id = Column(Integer, ForeignKey("guests.id"))
    room_id = Column(Integer, ForeignKey("rooms.id"))

    # Start date of booking with default today
    datefrom = Column(Date, nullable=False, server_default=func.current_date())

    # End date of booking, SQLAlchemy doesn't have now()+1 so we need to use text() to pass raw SQL:
    dateto = Column(Date, nullable=False, server_default=text("(now() + interval '1 day')::date)"))

    info = Column(String)
    created_at = Column(TIMESTAMP, server_default=func.now())

# ---------------------------------------------------
# Create SQLAlchemy session (similar to the previous db_conn() function)
# ---------------------------------------------------
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# ---------------------------------------------------
# Create schema (run on app startup)
# ---------------------------------------------------
def init_db():
    Base.metadata.create_all(bind=engine)
  