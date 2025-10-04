from sqlalchemy import create_engine, Column, Integer, String, Float, DateTime, ForeignKey, Boolean, Text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
from datetime import datetime

SQLALCHEMY_DATABASE_URL = "sqlite:///./delay_management.db"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True)
    points = Column(Integer, default=0)
    created_at = Column(DateTime, default=datetime.utcnow)

    incidents = relationship("Incident", back_populates="reporter")
    verifications = relationship("Verification", back_populates="user")


class Route(Base):
    __tablename__ = "routes"

    id = Column(Integer, primary_key=True, index=True)
    route_number = Column(String, unique=True, index=True)
    route_name = Column(String)
    transport_type = Column(String)  # bus, train, tram

    incidents = relationship("Incident", back_populates="route")


class Stop(Base):
    __tablename__ = "stops"

    id = Column(Integer, primary_key=True, index=True)
    stop_name = Column(String, index=True)
    latitude = Column(Float)
    longitude = Column(Float)

    incidents = relationship("Incident", back_populates="stop")


class Incident(Base):
    __tablename__ = "incidents"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, index=True)
    description = Column(Text)
    incident_type = Column(String)  # delay, cancellation, breakdown, crowding, other
    severity = Column(String)  # low, medium, high, critical
    status = Column(String, default="active")  # active, resolved, verified, disputed

    route_id = Column(Integer, ForeignKey("routes.id"))
    stop_id = Column(Integer, ForeignKey("stops.id"), nullable=True)
    reporter_id = Column(Integer, ForeignKey("users.id"))

    delay_minutes = Column(Integer, nullable=True)
    reported_at = Column(DateTime, default=datetime.utcnow)
    resolved_at = Column(DateTime, nullable=True)

    verification_count = Column(Integer, default=0)
    dispute_count = Column(Integer, default=0)

    route = relationship("Route", back_populates="incidents")
    stop = relationship("Stop", back_populates="incidents")
    reporter = relationship("User", back_populates="incidents")
    verifications = relationship("Verification", back_populates="incident")


class Verification(Base):
    __tablename__ = "verifications"

    id = Column(Integer, primary_key=True, index=True)
    incident_id = Column(Integer, ForeignKey("incidents.id"))
    user_id = Column(Integer, ForeignKey("users.id"))
    is_verified = Column(Boolean)  # True for verify, False for dispute
    comment = Column(String, nullable=True)
    verified_at = Column(DateTime, default=datetime.utcnow)

    incident = relationship("Incident", back_populates="verifications")
    user = relationship("User", back_populates="verifications")


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def init_db():
    Base.metadata.create_all(bind=engine)