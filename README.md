# Delay Management Application - Backend API

A community-driven public transport delay management system built with FastAPI and SQLite.

## Features

- 📝 User-reported incidents with point rewards
- ✅ Community verification system
- 🚇 Support for multiple transport types (train, bus, tram)
- 📊 Real-time incident tracking and statistics
- 🗺️ Location-based incident reporting
- 🎯 Automatic incident status management

## Project Structure

```
delay-management/
├── main.py              # FastAPI application and endpoints
├── database.py          # SQLAlchemy models and database setup
├── schemas.py           # Pydantic schemas for validation
├── crud.py              # Database operations
├── seed_data.py         # Mock data generator
├── requirements.txt     # Python dependencies
└── README.md           # This file
```

## Setup Instructions

### 1. Create Virtual Environment

```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

### 2. Install Dependencies

```bash
pip install -r requirements.txt
```

### 3. Seed Database with Mock Data

```bash
python seed_data.py
```

This will create:
- 8 users with varying points
- 9 transport routes (trains, buses, trams)
- 12 stops with coordinates
- 35 incidents with different statuses
- Random verifications from users

### 4. Run the Application

```bash
python main.py
```

Or using uvicorn directly:

```bash
uvicorn main:app --reload
```

The API will be available at: `http://localhost:8000`

## API Documentation

Once the server is running, visit:
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

## API Endpoints

### Users
- `POST /users` - Create new user
- `GET /users/{user_id}` - Get user details and points

### Routes
- `GET /routes` - List all routes with incident counts
- `GET /routes/{route_id}` - Get specific route details
- `GET /routes/{route_id}/incidents` - Get all incidents for a route

### Stops
- `GET /stops` - List all stops with nearby incident counts
- `GET /stops/{stop_id}` - Get specific stop details

### Incidents
- `POST /incidents` - Report new incident (awards 10 points)
- `GET /incidents` - List all incidents (filter by status)
- `GET /incidents/{incident_id}` - Get incident details
- `PUT /incidents/{incident_id}/status` - Update incident status

### Verifications
- `POST /verifications` - Verify or dispute an incident (awards 2 points)
- `GET /incidents/{incident_id}/verifications` - Get all verifications for incident

### Statistics
- `GET /stats` - Get incident statistics

## Usage Examples

### Report a New Incident

```bash
curl -X POST "http://localhost:8000/incidents" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Train delayed at Central Station",
    "description": "Train running 15 minutes behind schedule",
    "incident_type": "delay",
    "severity": "medium",
    "route_id": 1,
    "stop_id": 1,
    "reporter_id": 1,
    "delay_minutes": 15
  }'
```

### Get Active Incidents

```bash
curl "http://localhost:8000/incidents?status=active"
```

### Verify an Incident

```bash
curl -X POST "http://localhost:8000/verifications" \
  -H "Content-Type: application/json" \
  -d '{
    "incident_id": 1,
    "user_id": 2,
    "is_verified": true,
    "comment": "Confirmed, I am at the location"
  }'
```

### Get Statistics

```bash
curl "http://localhost:8000/stats"
```

## Data Model

### Incident Types
- `delay` - Service running behind schedule
- `cancellation` - Service cancelled
- `breakdown` - Vehicle malfunction
- `crowding` - Overcrowding issues
- `other` - Other incidents

### Severity Levels
- `low` - Minor inconvenience
- `medium` - Moderate delay
- `high` - Significant disruption
- `critical` - Service severely affected

### Incident Status
- `active` - Currently ongoing
- `verified` - Confirmed by 3+ users
- `disputed` - Disputed by 3+ users
- `resolved` - No longer active

## Point System

- Report incident: **+10 points**
- Verify incident: **+2 points**
- Auto-verification: 3+ confirmations
- Auto-dispute: 3+ disputes

## For Jury Presentation

The seeded database includes:
- Realistic incident scenarios across different routes and stops
- Mix of active, verified, and resolved incidents
- Community engagement through verifications
- Point rewards system in action
- Various incident types and severity levels

You can demonstrate:
1. Real-time incident reporting
2. Community verification workflow
3. Route and stop impact visualization
4. User engagement and rewards
5. Statistical insights

## Next Steps (Future Enhancements)

- Integration with dispatcher systems
- Predictive analytics for future delays
- Real-time push notifications
- Interactive map visualization
- Mobile application
- Machine learning for incident validation
- Historical pattern analysis

## License

This is a demonstration project for educational purposes.