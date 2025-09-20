from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from api.routers import inference, events
from api.config import settings

app = FastAPI(title="Duality Traffic Enforcement API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(inference.router, prefix="/inference", tags=["inference"])
app.include_router(events.router, prefix="/events", tags=["events"])

app.mount("/evidence", StaticFiles(directory="data/evidence"), name="evidence")

@app.get("/")
async def root():
    return {"status": "ok"}
