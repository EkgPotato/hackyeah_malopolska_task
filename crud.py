from sqlalchemy.orm import Session
from sqlalchemy import func
from database import User, Route, Stop, Incident, Verification
from schemas import IncidentCreate, VerificationCreate
from datetime import datetime


# User operations
def get_user(db: Session, user_id: int):
    return db.query(User).filter(User.id == user_id).first()


def get_user_by_username(db: Session, username: str):
    return db.query(User).filter(User.username == username).first()


def create_user(db: Session, username: str):
    db_user = User(username=username)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user


def update_user_points(db: Session, user_id: int, points: int):
    user = get_user(db, user_id)
    if user:
        user.points += points
        db.commit()
        db.refresh(user)
    return user


# Route operations
def get_routes(db: Session, skip: int = 0, limit: int = 100):
    return db.query(Route).offset(skip).limit(limit).all()


def get_route(db: Session, route_id: int):
    return db.query(Route).filter(Route.id == route_id).first()


def get_routes_with_incident_counts(db: Session):
    return db.query(
        Route,
        func.count(Incident.id).label('active_incidents')
    ).outerjoin(
        Incident,
        (Incident.route_id == Route.id) & (Incident.status == 'active')
    ).group_by(Route.id).all()


# Stop operations
def get_stops(db: Session, skip: int = 0, limit: int = 100):
    return db.query(Stop).offset(skip).limit(limit).all()


def get_stop(db: Session, stop_id: int):
    return db.query(Stop).filter(Stop.id == stop_id).first()


def get_stops_with_incident_counts(db: Session):
    return db.query(
        Stop,
        func.count(Incident.id).label('nearby_incidents')
    ).outerjoin(
        Incident,
        (Incident.stop_id == Stop.id) & (Incident.status == 'active')
    ).group_by(Stop.id).all()


# Incident operations
def create_incident(db: Session, incident: IncidentCreate):
    db_incident = Incident(**incident.model_dump())
    db.add(db_incident)
    db.commit()
    db.refresh(db_incident)

    # Award points to reporter
    update_user_points(db, incident.reporter_id, 10)

    return db_incident


def get_incidents(db: Session, skip: int = 0, limit: int = 100, status: str = None):
    query = db.query(Incident)
    if status:
        query = query.filter(Incident.status == status)
    return query.order_by(Incident.reported_at.desc()).offset(skip).limit(limit).all()


def get_incident(db: Session, incident_id: int):
    return db.query(Incident).filter(Incident.id == incident_id).first()


def update_incident_status(db: Session, incident_id: int, status: str):
    incident = get_incident(db, incident_id)
    if incident:
        incident.status = status
        if status == "resolved":
            incident.resolved_at = datetime.utcnow()
        db.commit()
        db.refresh(incident)
    return incident


def get_incidents_by_route(db: Session, route_id: int):
    return db.query(Incident).filter(
        Incident.route_id == route_id,
        Incident.status == 'active'
    ).all()


# Verification operations
def create_verification(db: Session, verification: VerificationCreate):
    # Check if user already verified this incident
    existing = db.query(Verification).filter(
        Verification.incident_id == verification.incident_id,
        Verification.user_id == verification.user_id
    ).first()

    if existing:
        return None

    db_verification = Verification(**verification.model_dump())
    db.add(db_verification)

    # Update incident counts
    incident = get_incident(db, verification.incident_id)
    if incident:
        if verification.is_verified:
            incident.verification_count += 1
            # Award points for helpful verification
            update_user_points(db, verification.user_id, 2)
        else:
            incident.dispute_count += 1

        # Auto-verify if enough confirmations
        if incident.verification_count >= 3:
            incident.status = "verified"
        # Auto-dispute if too many disputes
        elif incident.dispute_count >= 3:
            incident.status = "disputed"

    db.commit()
    db.refresh(db_verification)
    return db_verification


def get_verifications_by_incident(db: Session, incident_id: int):
    return db.query(Verification).filter(Verification.incident_id == incident_id).all()


# Statistics
def get_incident_stats(db: Session):
    total = db.query(func.count(Incident.id)).scalar()
    active = db.query(func.count(Incident.id)).filter(Incident.status == 'active').scalar()
    resolved = db.query(func.count(Incident.id)).filter(Incident.status == 'resolved').scalar()

    by_type = {}
    type_stats = db.query(Incident.incident_type, func.count(Incident.id)).group_by(Incident.incident_type).all()
    for incident_type, count in type_stats:
        by_type[incident_type] = count

    by_severity = {}
    severity_stats = db.query(Incident.severity, func.count(Incident.id)).group_by(Incident.severity).all()
    for severity, count in severity_stats:
        by_severity[severity] = count

    return {
        "total_incidents": total,
        "active_incidents": active,
        "resolved_incidents": resolved,
        "by_type": by_type,
        "by_severity": by_severity
    }