from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
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

# get request for main route
@app.get("/")
def read_root():
    with get_conn() as conn, conn.cursor() as cur:
        cur.execute("SELECT 'Hello, postgres!' AS message")
        result = cur.fetchone()
        create_schema()
    return { "msg": f"Hotel API", "db_api": result}


@app.get("/items/{id}")
def read_item(item_id: int, q: str = None):
    return {"id": id, "q": q}

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


@app.get("/rooms")
def read():
    return { "rooms": my_rooms}

# Create a class to represent your JSON body
class Booking(BaseModel):
    room_id: int
    name: str
    start_date: str
    end_date: str

@app.post("/bookings")
def create_booking(booking: Booking):
    # Access data using booking.room_id or booking.name
    return {"message": f"Booking created for {booking.name} in room {booking.room_id}"}