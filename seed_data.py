from database import SessionLocal, User, Route, Stop, Incident, Verification, init_db
from datetime import datetime, timedelta
import random


def seed_database():
    init_db()
    db = SessionLocal()

    # Clear existing data
    db.query(Verification).delete()
    db.query(Incident).delete()
    db.query(Stop).delete()
    db.query(Route).delete()
    db.query(User).delete()
    db.commit()

    print("Creating users...")
    users = [
        User(username="john_traveler", points=150),
        User(username="mary_commuter", points=280),
        User(username="david_daily", points=95),
        User(username="sarah_student", points=420),
        User(username="mike_manager", points=180),
        User(username="emma_explorer", points=310),
        User(username="alex_analyst", points=75),
        User(username="lisa_local", points=520),
    ]
    db.add_all(users)
    db.commit()
    print(f"Created {len(users)} users")

    print("Creating routes...")
    routes = [
        Route(route_number="M1", route_name="Central Line", transport_type="train"),
        Route(route_number="M2", route_name="East-West Line", transport_type="train"),
        Route(route_number="M3", route_name="North Circle", transport_type="train"),
        Route(route_number="B15", route_name="City Express", transport_type="bus"),
        Route(route_number="B27", route_name="Airport Shuttle", transport_type="bus"),
        Route(route_number="B42", route_name="Suburban Loop", transport_type="bus"),
        Route(route_number="B88", route_name="Night Bus", transport_type="bus"),
        Route(route_number="T1", route_name="Downtown Tram", transport_type="tram"),
        Route(route_number="T5", route_name="Park Line", transport_type="tram"),
    ]
    db.add_all(routes)
    db.commit()
    print(f"Created {len(routes)} routes")

    print("Creating stops...")
    stops = [
        Stop(stop_name="Kraków Główny", latitude=50.0677, longitude=19.9447),  # Main Railway Station
        Stop(stop_name="Rynek Główny", latitude=50.0619, longitude=19.9369),  # Main Market Square
        Stop(stop_name="Wawel Castle", latitude=50.0544, longitude=19.9356),  # Wawel Royal Castle
        Stop(stop_name="Kazimierz", latitude=50.0520, longitude=19.9467),  # Jewish Quarter
        Stop(stop_name="Nowa Huta", latitude=50.0715, longitude=20.0350),  # Industrial District
        Stop(stop_name="AGH University", latitude=50.0657, longitude=19.9189),  # AGH University of Science
        Stop(stop_name="Jagiellonian University", latitude=50.0638, longitude=19.9326),  # Jagiellonian University
        Stop(stop_name="Kraków Airport", latitude=50.0777, longitude=19.7848),  # Balice Airport
        Stop(stop_name="Galeria Krakowska", latitude=50.0684, longitude=19.9467),  # Shopping Mall
        Stop(stop_name="Tauron Arena", latitude=50.0682, longitude=19.9906),  # Sports & Concert Arena
        Stop(stop_name="University Hospital", latitude=50.0703, longitude=19.9534),  # Hospital
        Stop(stop_name="Błonia Park", latitude=50.0587, longitude=19.9159),  # Large Park
    ]

    db.add_all(stops)
    db.commit()
    print(f"Created {len(stops)} stops")

    print("Creating incidents...")
    incident_titles = [
        "Severe delay on {}",
        "Train breakdown at {}",
        "Overcrowding reported",
        "Signal failure causing delays",
        "Bus running 20 minutes late",
        "Accident blocking route",
        "Technical issues at {}",
        "Service temporarily suspended",
        "Unexpected delay at {}",
        "Vehicle malfunction",
        "Track maintenance delay",
        "Power outage affecting service",
    ]

    incident_descriptions = [
        "Multiple passengers reported significant delays. Service is running behind schedule due to unforeseen circumstances.",
        "Vehicle experiencing technical difficulties. Passengers are being asked to use alternative routes.",
        "Heavy congestion and overcrowding observed. Consider taking next service.",
        "Infrastructure issues causing service disruptions. Engineers are working to resolve the problem.",
        "Delays expected for the next hour due to operational problems.",
        "Emergency services on site. Traffic is being diverted.",
        "System experiencing technical glitches. Estimated resolution time is 30-45 minutes.",
        "Service interruption due to maintenance work that ran over schedule.",
        "Unexpected incident causing delays. Staff are working to minimize disruption.",
        "Weather conditions affecting normal operations.",
    ]

    incidents = []
    now = datetime.utcnow()

    # Create mix of active, verified, and resolved incidents
    for i in range(35):
        route = random.choice(routes)
        reporter = random.choice(users)
        stop = random.choice(stops) if random.random() > 0.3 else None

        incident_type = random.choice(["delay", "delay", "delay", "cancellation", "breakdown", "crowding", "other"])
        severity = random.choice(["low", "medium", "medium", "high", "critical"])

        # Most incidents are recent, some are older
        hours_ago = random.randint(1, 72) if random.random() > 0.3 else random.randint(1, 8)
        reported_at = now - timedelta(hours=hours_ago)

        # Status based on age and verifications
        if hours_ago > 48:
            status = "resolved"
            resolved_at = reported_at + timedelta(hours=random.randint(2, 24))
        elif random.random() > 0.7:
            status = "verified"
            resolved_at = None
        elif random.random() > 0.9:
            status = "disputed"
            resolved_at = None
        else:
            status = "active"
            resolved_at = None

        title = random.choice(incident_titles).format(stop.stop_name if stop else route.route_name)

        incident = Incident(
            title=title,
            description=random.choice(incident_descriptions),
            incident_type=incident_type,
            severity=severity,
            status=status,
            route_id=route.id,
            stop_id=stop.id if stop else None,
            reporter_id=reporter.id,
            delay_minutes=random.randint(5, 90) if incident_type == "delay" else None,
            reported_at=reported_at,
            resolved_at=resolved_at,
            verification_count=0,
            dispute_count=0
        )
        incidents.append(incident)

    db.add_all(incidents)
    db.commit()
    print(f"Created {len(incidents)} incidents")

    print("Creating verifications...")
    verifications = []

    for incident in incidents:
        # Add random verifications to incidents
        num_verifications = random.randint(0, 5)

        # Get random users excluding the reporter
        available_users = [u for u in users if u.id != incident.reporter_id]
        verifiers = random.sample(available_users, min(num_verifications, len(available_users)))

        for verifier in verifiers:
            is_verified = random.random() > 0.15  # 85% verification rate
            verification = Verification(
                incident_id=incident.id,
                user_id=verifier.id,
                is_verified=is_verified,
                comment=random.choice([
                    "Confirmed, I'm at the location now",
                    "Yes, experiencing the same issue",
                    "Can verify this is accurate",
                    "Still ongoing as of now",
                    None,
                    None
                ]) if is_verified else random.choice([
                    "This seems resolved now",
                    "Cannot confirm this",
                    "Situation appears normal",
                    None
                ]),
                verified_at=incident.reported_at + timedelta(minutes=random.randint(5, 120))
            )
            verifications.append(verification)

            # Update incident counts
            if is_verified:
                incident.verification_count += 1
            else:
                incident.dispute_count += 1

    db.add_all(verifications)
    db.commit()
    print(f"Created {len(verifications)} verifications")

    # Update incident statuses based on verification counts
    for incident in incidents:
        if incident.status == "active":
            if incident.verification_count >= 3:
                incident.status = "verified"
            elif incident.dispute_count >= 3:
                incident.status = "disputed"

    db.commit()

    print("\n=== Database seeded successfully! ===")
    print(f"Users: {len(users)}")
    print(f"Routes: {len(routes)}")
    print(f"Stops: {len(stops)}")
    print(f"Incidents: {len(incidents)}")
    print(f"Verifications: {len(verifications)}")
    print("\nActive incidents:", len([i for i in incidents if i.status == "active"]))
    print("Verified incidents:", len([i for i in incidents if i.status == "verified"]))
    print("Resolved incidents:", len([i for i in incidents if i.status == "resolved"]))
    print("Disputed incidents:", len([i for i in incidents if i.status == "disputed"]))

    db.close()


if __name__ == "__main__":
    seed_database()
