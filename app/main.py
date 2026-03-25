from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse

app = FastAPI()

my_name = "Jay"

# get request for main route
@app.get("/")
def read_root():
    return { "msg": "Hello! " + my_name, "next_msg": f"Hi, {my_name}"}

@app.get("/items/{id}")
def read_item(item_id: int, q: str = None):
    return {"id": id, "q": q}

@app.get("/api/ip")
def read_root(request: Request):
    client_host = request.client.host
    return { "msg": f"Your public IP is {client_host}"}

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
async def read_root(request: Request):
    ip = request.client.host
    return generate_html_response(ip)