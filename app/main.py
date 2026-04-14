from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from datetime import date
from app.db import *

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

my_rooms = [
    {"id": 1, "name": "Room A", "price": 110,},
    {"id": 2, "name": "Room B", "price": 120,},
    {"id": 3, "name": "Room C", "price": 130,},
]

### IP
# get request for main route
@app.get("/")
def read_root():
    with get_conn() as conn, conn.cursor() as cur:
        cur.execute("SELECT 'Hello, postgres!' AS message")
        result = cur.fetchone()
        create_schema()
    return { "msg": f"Hotel API", "db_api": result}

@app.get("/api/ip")
def api_ip(request: Request):
    client_host = request.client.host
    return { "ip": client_host}

def generate_html_response(ip):

    html_content = f"""
    <html>
        <head>
            <title>Some HTML in here</title>
        </head>
        <body>
            <h1>Your public IP is {ip}</h1>
        </body>
    </html>
    """
    return HTMLResponse(content=html_content, status_code=200)

@app.get("/ip", response_class=HTMLResponse)
async def html_ip(request: Request):
    ip = request.client.host
    return generate_html_response(ip)

### Hotel
@app.get("/rooms")
def read():
    return { "rooms": my_rooms}

@app.get("/rooms/{id}")
def get_one_room(id: int):
    with get_conn() as conn, conn.cursor() as cur:
        cur.execute("""
            SELECT *
            FROM hotel_rooms
            WHERE id = %s
        """, (id,)) # <- tuple, list is also fine: [id]
        room = cur.fetchone()
    return room

@app.get("/bookings")
def get_bookings():
    with get_conn() as conn, conn.cursor() as cur:
        cur.execute("""
            SELECT
                g.firstname,
                b.room_id,
                r.room_number,
                b.datefrom
            FROM hotel_guests AS g
            INNER JOIN hotel_bookings AS b
                ON g.id = b.guest_id
            INNER JOIN hotel_rooms AS r
                ON r.id = b.room_id
            ORDER BY b.datefrom
        """)
        room = cur.fetchall()
    return room

# Create a class to represent your JSON body
class Booking(BaseModel):
    room_id: int
    guest_id: int
    datefrom: date
    dateto: date
    addinfo: str | None = None

@app.post("/bookings")
def create_booking(booking: Booking):
    with get_conn() as conn, conn.cursor() as cur:
        cur.execute("""
                    INSERT INTO hotel_bookings (room_id, guest_id, datefrom, dateto)
                    VALUES (%s, %s, %s, %s)
                    RETURNING id
                    """, [booking.room_id, booking.guest_id, booking.datefrom, booking.dateto])
        booking_id = cur.fetchone()
    return {"message": "Booking created!", "booking_id": booking_id}

### Other
@app.get("/items/{id}")
def read_item(id: int, q: str = ''):
    return {"id": id, "q": q}

@app.get("/if/{term}")
def if_term(term: str):
    if term == "hello" or term == "hi" or term == "hey":
        return {"message": "Hello there!"}
    elif term == "goodbye":
        return {"message": "Goodbye!"}
    else:
        return {"message": f"Term '{term}' not recognized."}