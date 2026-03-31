from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.middleware.cors import CORSMiddleware

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

# get request for main route
@app.get("/")
def read_root():
    return { "msg": "Hello! " + my_name, "next_msg": f"Hi, {my_name}"}


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