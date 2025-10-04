from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional


class UserBase(BaseModel):
    username: str


class UserCreate(UserBase):
    pass


class UserResponse(UserBase):
    id: int
    points: int
    created_at: datetime

    class Config:
        from_attributes = True


class RouteBase(BaseModel):
    route_number: str
    route_name: str
    transport_type: str


class RouteResponse(RouteBase):
    id: int

    class Config:
        from_attributes = True


class RouteWithIncidents(RouteResponse):
    active_incidents: int


class StopBase(BaseModel):
    stop_name: str
    latitude: float
    longitude: float


class StopResponse(StopBase):
    id: int

    class Config:
        from_attributes = True


class StopWithIncidents(StopResponse):
    nearby_incidents: int


class IncidentCreate(BaseModel):
    title: str = Field(..., min_length=5, max_length=200)
    description: str = Field(..., min_length=10)
    incident_type: str = Field(..., pattern="^(delay|cancellation|breakdown|crowding|other)$")
    severity: str = Field(..., pattern="^(low|medium|high|critical)$")
    route_id: int
    stop_id: Optional[int] = None
    reporter_id: int
    delay_minutes: Optional[int] = Field(None, ge=0, le=999)


class IncidentResponse(BaseModel):
    id: int
    title: str
    description: str
    incident_type: str
    severity: str
    status: str
    route_id: int
    stop_id: Optional[int]
    reporter_id: int
    delay_minutes: Optional[int]
    reported_at: datetime
    resolved_at: Optional[datetime]
    verification_count: int
    dispute_count: int

    class Config:
        from_attributes = True


class IncidentDetailResponse(IncidentResponse):
    route: RouteResponse
    stop: Optional[StopResponse]
    reporter: UserResponse


class VerificationCreate(BaseModel):
    incident_id: int
    user_id: int
    is_verified: bool
    comment: Optional[str] = None


class VerificationResponse(BaseModel):
    id: int
    incident_id: int
    user_id: int
    is_verified: bool
    comment: Optional[str]
    verified_at: datetime

    class Config:
        from_attributes = True


class IncidentStats(BaseModel):
    total_incidents: int
    active_incidents: int
    resolved_incidents: int
    by_type: dict
    by_severity: dict