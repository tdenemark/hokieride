from fastapi import FastAPI, Request, Form, Depends, HTTPException
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel
from datetime import datetime
import os
from supabase import create_client, Client
from dotenv import load_dotenv

load_dotenv()

app = FastAPI(title="HokieRide 🦃")
templates = Jinja2Templates(directory="templates")
app.mount("/static", StaticFiles(directory="static", html=True), name="static")

supabase: Client = create_client(os.getenv("SUPABASE_URL"), os.getenv("SUPABASE_ANON_KEY"))

# Temporary auth – real version uses Supabase JWT (we’ll upgrade after launch)
async def get_current_user(request: Request):
    user = {"id": "test-driver-001", "email": "tdenemark@vt.edu"}  # replace with real auth later
    if not user["email"].endswith("@vt.edu"):
        raise HTTPException(403, "Only VT emails allowed")
    return user

@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

@app.get("/offer", response_class=HTMLResponse)
async def offer_form(request: Request):
    return templates.TemplateResponse("offer.html", {"request": request})

@app.post("/offer")
async def create_ride(
    direction: str = Form(...),
    date_time: str = Form(...),
    pickup: str = Form(...),
    dropoff: str = Form(...),
    seats: int = Form(...),
    price: float = Form(30.0),
    notes: str = Form(""),
    venmo: str = Form(""),
    user = Depends(get_current_user)
):
    data = {
        "driver_id": user["id"],
        "direction": direction,
        "date_time": date_time,
        "pickup": pickup,
        "dropoff": dropoff,
        "seats": seats,
        "seats_left": seats,
        "price": price,
        "notes": notes,
        "venmo": venmo
    }
    supabase.table("rides").insert(data).execute()
    return RedirectResponse("/", status_code=303)

@app.get("/find", response_class=HTMLResponse)
async def find_rides(request: Request, direction: str = "To NOVA"):
    rides = supabase.table("rides").select("*").eq("direction", direction).order("date_time", desc=False).execute().data
    return templates.TemplateResponse("find.html", {"request": request, "rides": rides, "direction": direction})

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
