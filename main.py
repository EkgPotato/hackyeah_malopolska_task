from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from typing import List, Optional
from database import get_db, init_db
import crud
import schemas

app = FastAPI(
    title="Delay Management API",
    description="Community-driven public transport delay reporting system",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",  # T3 app default port
        "http://localhost:8000"
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize database on startup
@app.on_event("startup")
def startup_event():
    init_db()


# Health check
@app.get("/")
def read_root():
    return {
        "message": "Delay Management API",
        "status": "running",
        "version": "1.0.0"
    }


# User endpoints
@app.get("/users/{user_id}", response_model=schemas.UserResponse)
def get_user(user_id: int, db: Session = Depends(get_db)):
    user = crud.get_user(db, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user


@app.post("/users", response_model=schemas.UserResponse, status_code=201)
def create_user(user: schemas.UserCreate, db: Session = Depends(get_db)):
    existing_user = crud.get_user_by_username(db, user.username)
    if existing_user:
        raise HTTPException(status_code=400, detail="Username already exists")
    return crud.create_user(db, user.username)


# Route endpoints
@app.get("/routes", response_model=List[schemas.RouteWithIncidents])
def get_routes(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    routes_with_counts = crud.get_routes_with_incident_counts(db)
    return [
        schemas.RouteWithIncidents(
            id=route.id,
            route_number=route.route_number,
            route_name=route.route_name,
            transport_type=route.transport_type,
            active_incidents=count
        )
        for route, count in routes_with_counts
    ]


@app.get("/routes/{route_id}", response_model=schemas.RouteResponse)
def get_route(route_id: int, db: Session = Depends(get_db)):
    route = crud.get_route(db, route_id)
    if not route:
        raise HTTPException(status_code=404, detail="Route not found")
    return route


@app.get("/routes/{route_id}/incidents", response_model=List[schemas.IncidentResponse])
def get_route_incidents(route_id: int, db: Session = Depends(get_db)):
    route = crud.get_route(db, route_id)
    if not route:
        raise HTTPException(status_code=404, detail="Route not found")
    return crud.get_incidents_by_route(db, route_id)


# Stop endpoints
@app.get("/stops", response_model=List[schemas.StopWithIncidents])
def get_stops(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    stops_with_counts = crud.get_stops_with_incident_counts(db)
    return [
        schemas.StopWithIncidents(
            id=stop.id,
            stop_name=stop.stop_name,
            latitude=stop.latitude,
            longitude=stop.longitude,
            nearby_incidents=count
        )
        for stop, count in stops_with_counts
    ]


@app.get("/stops/{stop_id}", response_model=schemas.StopResponse)
def get_stop(stop_id: int, db: Session = Depends(get_db)):
    stop = crud.get_stop(db, stop_id)
    if not stop:
        raise HTTPException(status_code=404, detail="Stop not found")
    return stop


# Incident endpoints
@app.post("/incidents", response_model=schemas.IncidentResponse, status_code=201)
def create_incident(incident: schemas.IncidentCreate, db: Session = Depends(get_db)):
    # Validate route exists
    route = crud.get_route(db, incident.route_id)
    if not route:
        raise HTTPException(status_code=404, detail="Route not found")

    # Validate stop exists if provided
    if incident.stop_id:
        stop = crud.get_stop(db, incident.stop_id)
        if not stop:
            raise HTTPException(status_code=404, detail="Stop not found")

    # Validate user exists
    user = crud.get_user(db, incident.reporter_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    return crud.create_incident(db, incident)


@app.get("/incidents", response_model=List[schemas.IncidentResponse])
def get_incidents(
        skip: int = 0,
        limit: int = 100,
        status: Optional[str] = None,
        db: Session = Depends(get_db)
):
    return crud.get_incidents(db, skip, limit, status)


@app.get("/incidents/{incident_id}", response_model=schemas.IncidentDetailResponse)
def get_incident(incident_id: int, db: Session = Depends(get_db)):
    incident = crud.get_incident(db, incident_id)
    if not incident:
        raise HTTPException(status_code=404, detail="Incident not found")
    return incident


@app.put("/incidents/{incident_id}/status")
def update_incident_status(
        incident_id: int,
        status: str,
        db: Session = Depends(get_db)
):
    valid_statuses = ["active", "resolved", "verified", "disputed"]
    if status not in valid_statuses:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid status. Must be one of: {', '.join(valid_statuses)}"
        )

    incident = crud.update_incident_status(db, incident_id, status)
    if not incident:
        raise HTTPException(status_code=404, detail="Incident not found")
    return {"message": "Status updated successfully", "incident": incident}


# Verification endpoints
@app.post("/verifications", response_model=schemas.VerificationResponse, status_code=201)
def create_verification(verification: schemas.VerificationCreate, db: Session = Depends(get_db)):
    # Validate incident exists
    incident = crud.get_incident(db, verification.incident_id)
    if not incident:
        raise HTTPException(status_code=404, detail="Incident not found")

    # Validate user exists
    user = crud.get_user(db, verification.user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    # Create verification
    db_verification = crud.create_verification(db, verification)
    if not db_verification:
        raise HTTPException(
            status_code=400,
            detail="User has already verified this incident"
        )

    return db_verification


@app.get("/incidents/{incident_id}/verifications", response_model=List[schemas.VerificationResponse])
def get_incident_verifications(incident_id: int, db: Session = Depends(get_db)):
    incident = crud.get_incident(db, incident_id)
    if not incident:
        raise HTTPException(status_code=404, detail="Incident not found")
    return crud.get_verifications_by_incident(db, incident_id)


# Statistics endpoint
@app.get("/stats", response_model=schemas.IncidentStats)
def get_stats(db: Session = Depends(get_db)):
    return crud.get_incident_stats(db)


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)