"""
Simple seed script using raw SQL
"""
import uuid
from datetime import datetime, timedelta
import random
import psycopg2
from app.core.config import settings

# Parse DATABASE_URL
# postgresql://user:password@host:port/database
url_parts = settings.DATABASE_URL.replace('postgresql://', '').split('@')
user_pass = url_parts[0].split(':')
host_db = url_parts[1].split('/')
host_port = host_db[0].split(':')

conn_params = {
    'user': user_pass[0],
    'password': user_pass[1],
    'host': host_port[0],
    'port': host_port[1] if len(host_port) > 1 else '5432',
    'database': host_db[1]
}

# Sample locations in Bangalore
LOCATIONS = [
    (12.9716, 77.6412, "Near Shanti Nagar Circle"),
    (12.9725, 77.6405, "Shanti Nagar Main Road"),
    (12.9250, 77.5838, "Jayanagar 4th Block"),
    (12.9352, 77.6245, "Koramangala 5th Block"),
    (12.9716, 77.6412, "Indiranagar 100 Feet Road"),
    (13.0067, 77.5697, "Malleshwaram 18th Cross"),
    (12.9899, 77.5544, "Rajajinagar 4th Block"),
    (12.9300, 77.6270, "Koramangala 6th Block"),
    (12.9280, 77.5850, "Jayanagar Shopping Complex"),
    (12.9780, 77.6408, "Indiranagar 12th Main"),
]

COMPLAINTS = [
    ("Pothole on main road", "Large pothole causing accidents", "road", "high"),
    ("Street light not working", "Street light non-functional for a week", "electricity", "medium"),
    ("Water supply disruption", "No water supply for 3 days", "water", "urgent"),
    ("Garbage not collected", "Garbage not collected for over a week", "sanitation", "high"),
    ("Broken footpath", "Footpath broken and dangerous", "road", "medium"),
    ("Overflowing drainage", "Drainage overflowing causing water logging", "sanitation", "high"),
    ("Traffic signal malfunction", "Traffic signal not working", "road", "medium"),
    ("Park maintenance needed", "Park needs maintenance", "other", "low"),
]

STATUSES = ["submitted", "assigned", "in_progress", "resolved"]

conn = psycopg2.connect(**conn_params)
cur = conn.cursor()

try:
    # Get constituency and user
    cur.execute("SELECT id FROM constituencies LIMIT 1")
    constituency_id = cur.fetchone()[0]
    
    cur.execute("SELECT id FROM users WHERE role = 'citizen' LIMIT 1")
    result = cur.fetchone()
    if result:
        user_id = result[0]
    else:
        # Create a user
        user_id = str(uuid.uuid4())
        cur.execute("""
            INSERT INTO users (id, name, phone, role, constituency_id, is_active, created_at, updated_at)
            VALUES (%s, %s, %s, %s, %s, %s, NOW(), NOW())
        """, (user_id, "Sample Citizen", "+919876543210", "citizen", str(constituency_id), "true"))
    
    print(f"Using constituency: {constituency_id}")
    print(f"Using user: {user_id}")
    print()
    
    # Create complaints
    created = 0
    for loc in LOCATIONS:
        complaint = random.choice(COMPLAINTS)
        status = random.choice(STATUSES)
        
        created_at = datetime.utcnow() - timedelta(days=random.randint(1, 30))
        updated_at = created_at + timedelta(hours=random.randint(1, 48))
        resolved_at = updated_at if status == "resolved" else None
        
        complaint_id = str(uuid.uuid4())
        
        cur.execute("""
            INSERT INTO complaints (
                id, constituency_id, user_id, title, description, category,
                lat, lng, location_description, status, priority,
                created_at, updated_at, resolved_at
            ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """, (
            complaint_id, str(constituency_id), str(user_id),
            complaint[0], complaint[1], complaint[2],
            loc[0], loc[1], loc[2],
            status, complaint[3],
            created_at, updated_at, resolved_at
        ))
        
        created += 1
        print(f"✅ Created: {complaint[0]} at {loc[2]}")
    
    conn.commit()
    print()
    print(f"🎉 Successfully created {created} complaints!")
    print(f"📍 Visit http://localhost:3000/map to see them")
    
except Exception as e:
    conn.rollback()
    print(f"❌ Error: {e}")
    raise
finally:
    cur.close()
    conn.close()
