from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from pymongo import MongoClient


app = FastAPI(
    title="Event Service",
    description="Microservice responsible for event management",
    version="1.0.0"
)


client = MongoClient("mongodb://localhost:27017")

db = client["event_db"]
events_collection = db["events"]


class EventCreate(BaseModel):
    name: str
    description: str
    location: str


@app.get("/")
def root():
    return {
        "message": "Event Service is running",
        "service": "event-service"
    }


@app.get("/health")
def health_check():
    try:
        client.admin.command("ping")

        return {
            "status": "healthy",
            "database": "connected",
            "service": "event-service"
        }

    except Exception:
        return {
            "status": "unhealthy",
            "database": "disconnected",
            "service": "event-service"
        }


@app.post("/events")
def create_event(event: EventCreate):

    result = events_collection.insert_one(
        event.model_dump()
    )

    return {
        "message": "Event created successfully",
        "event_id": str(result.inserted_id)
    }


@app.get("/events")
def get_events():

    events = []

    for event in events_collection.find():

        events.append({
            "id": str(event["_id"]),
            "name": event["name"],
            "description": event["description"],
            "location": event["location"]
        })

    return events


@app.get("/events/{event_id}")
def get_event(event_id: str):

    from bson import ObjectId

    try:
        event = events_collection.find_one(
            {"_id": ObjectId(event_id)}
        )
    except Exception:
        raise HTTPException(
            status_code=400,
            detail="Invalid event ID"
        )

    if not event:
        raise HTTPException(
            status_code=404,
            detail="Event not found"
        )

    return {
        "id": str(event["_id"]),
        "name": event["name"],
        "description": event["description"],
        "location": event["location"]
    }