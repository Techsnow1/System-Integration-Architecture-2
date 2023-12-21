from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import sqlite3

app = FastAPI()

# Pydantic model for input validation
class EventCreate(BaseModel):
    title: str
    description: str
    date: str

# Pydantic model for response
class Event(EventCreate):
    id: int

# SQLite database setup
def create_connection():
    connection = sqlite3.connect("events.db")
    return connection

def create_table():
    connection = create_connection()
    cursor = connection.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS events (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            description TEXT NOT NULL,
            date TEXT NOT NULL
        )
    """)
    connection.commit()
    connection.close()

create_table()

# CRUD functions
def create_event(event: EventCreate):
    connection = create_connection()
    cursor = connection.cursor()
    cursor.execute("INSERT INTO events (title, description, date) VALUES (?, ?, ?)",
                   (event.title, event.description, event.date))
    connection.commit()
    event_id = cursor.lastrowid
    connection.close()
    return event_id

def read_events(skip: int = 0, limit: int = 10):
    connection = create_connection()
    cursor = connection.cursor()
    cursor.execute("SELECT * FROM events LIMIT ? OFFSET ?", (limit, skip))
    events = cursor.fetchall()
    connection.close()
    return events

def read_event(event_id: int):
    connection = create_connection()
    cursor = connection.cursor()
    cursor.execute("SELECT * FROM events WHERE id = ?", (event_id,))
    event = cursor.fetchone()
    connection.close()
    return event

def update_event(event_id: int, event: EventCreate):
    connection = create_connection()
    cursor = connection.cursor()
    cursor.execute("UPDATE events SET title = ?, description = ?, date = ? WHERE id = ?",
                   (event.title, event.description, event.date, event_id))
    connection.commit()
    connection.close()

def delete_event(event_id: int):
    connection = create_connection()
    cursor = connection.cursor()
    cursor.execute("DELETE FROM events WHERE id = ?", (event_id,))
    connection.commit()
    connection.close()

# FastAPI endpoints
@app.post("/events/", response_model=Event)
def create_event_endpoint(event: EventCreate):
    event_id = create_event(event)
    return {"id": event_id, **event.dict()}

@app.get("/events/", response_model=list[Event])
def read_events_endpoint(skip: int = 0, limit: int = 10):
    return read_events(skip=skip, limit=limit)

@app.get("/events/{event_id}", response_model=Event)
def read_event_endpoint(event_id: int):
    event = read_event(event_id)
    if event:
        return dict(zip(["id", "title", "description", "date"], event))
    raise HTTPException(status_code=404, detail="Event not found")

@app.put("/events/{event_id}")
def update_event_endpoint(event_id: int, event: EventCreate):
    existing_event = read_event(event_id)
    if existing_event:
        update_event(event_id, event)
        return {"message": "Event updated successfully"}
    raise HTTPException(status_code=404, detail="Event not found")

@app.delete("/events/{event_id}")
def delete_event_endpoint(event_id: int):
    existing_event = read_event(event_id)
    if existing_event:
        delete_event(event_id)
        return {"message": "Event deleted successfully"}
    raise HTTPException(status_code=404, detail="Event not found")
