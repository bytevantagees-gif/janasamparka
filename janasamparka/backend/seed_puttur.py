"""
Seed script with actual Puttur (Dakshina Kannada) coordinates
Puttur is at approximately 12.7593° N, 75.2114° E
"""
import uuid
from datetime import datetime, timedelta
import random
import psycopg2
from app.core.config import settings

# Parse DATABASE_URL
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

# Sample locations in and around Puttur town, Dakshina Kannada
# Puttur center: 12.7593° N, 75.2114° E
LOCATIONS = [
    (12.7593, 75.2114, "Puttur Town - Main Road"),
    (12.7620, 75.2140, "Puttur Bus Stand Area"),
    (12.7560, 75.2090, "Puttur Market Area"),
    (12.7650, 75.2100, "Puttur Hospital Road"),
    (12.7580, 75.2150, "Puttur College Road"),
    (12.7540, 75.2130, "Puttur Railway Station Road"),
    (12.7600, 75.2080, "Puttur Circle"),
    (12.7570, 75.2170, "Puttur Residential Area"),
    (12.7610, 75.2050, "Puttur Government Office Area"),
    (12.7590, 75.2190, "Puttur School Zone"),
    (12.7630, 75.2120, "Puttur Temple Street"),
    (12.7550, 75.2100, "Puttur Industrial Area"),
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
    ("Bus stop shed damaged", "Bus stop shed needs repair", "road", "medium"),
    ("Public toilet not maintained", "Public toilet in unhygienic condition", "sanitation", "high"),
]

STATUSES = ["submitted", "assigned", "in_progress", "resolved"]

conn = psycopg2.connect(**conn_params)
cur = conn.cursor()

try:
    # Get Puttur constituency
    cur.execute("SELECT id FROM constituencies WHERE name = 'Puttur'")
    result = cur.fetchone()
    if not result:
        print("❌ Puttur constituency not found!")
        exit(1)
    constituency_id = result[0]
    
    cur.execute("SELECT id FROM users WHERE role = 'citizen' LIMIT 1")
    result = cur.fetchone()
    if result:
        user_id = result[0]
    else:
        # Create a user
        user_id = str(uuid.uuid4())
        cur.execute("""
            INSERT INTO users (id, name, phone, role, locale_pref, constituency_id, is_active, created_at, updated_at)
            VALUES (%s, %s, %s, %s, %s, %s, %s, NOW(), NOW())
        """, (user_id, "Puttur Citizen", "+918242223333", "citizen", "kn", str(constituency_id), "true"))
    
    print(f"Using Puttur constituency: {constituency_id}")
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
                is_emergency, is_duplicate, created_at, updated_at, resolved_at
            ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """, (
            complaint_id, str(constituency_id), str(user_id),
            complaint[0], complaint[1], complaint[2],
            loc[0], loc[1], loc[2],
            status, complaint[3],
            False,  # is_emergency
            False,  # is_duplicate
            created_at, updated_at, resolved_at
        ))
        
        created += 1
        print(f"✅ Created: {complaint[0]} at {loc[2]}")
    
    conn.commit()
    print()
    print(f"🎉 Successfully created {created} complaints in Puttur!")
    print(f"📍 Visit http://localhost:3000/map to see them in Puttur, Dakshina Kannada")
    
except Exception as e:
    conn.rollback()
    print(f"❌ Error: {e}")
    raise
finally:
    cur.close()
    conn.close()
