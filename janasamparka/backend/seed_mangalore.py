"""
Seed script for Mangalore North constituency
Mangalore is at approximately 12.9141° N, 74.8560° E
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

# Sample locations in Mangalore North
LOCATIONS = [
    (12.9141, 74.8560, "Mangalore - Lighthouse Hill Road"),
    (12.9200, 74.8600, "Mangalore - Kadri Hills"),
    (12.9180, 74.8520, "Mangalore - Bejai"),
    (12.9160, 74.8580, "Mangalore - Pandeshwar"),
    (12.9220, 74.8540, "Mangalore - Kankanady"),
    (12.9100, 74.8590, "Mangalore - Valencia"),
    (12.9190, 74.8610, "Mangalore - Balmatta Road"),
    (12.9150, 74.8500, "Mangalore - Kodialbail"),
]

COMPLAINTS = [
    ("Beach erosion issue", "Coastal erosion affecting beach area", "other", "urgent"),
    ("Streetlight not working", "Multiple street lights out in the area", "electricity", "high"),
    ("Road damage due to rain", "Heavy rains damaged the road surface", "road", "high"),
    ("Water logging", "Water logging during monsoon season", "sanitation", "medium"),
    ("Bus shelter damaged", "Bus shelter needs repair after storm", "road", "medium"),
    ("Garbage collection irregular", "Garbage not collected regularly", "sanitation", "high"),
    ("Tree fallen on road", "Fallen tree blocking traffic", "road", "urgent"),
    ("Drainage clogged", "Storm water drain clogged", "sanitation", "high"),
]

STATUSES = ["submitted", "assigned", "in_progress", "resolved"]

conn = psycopg2.connect(**conn_params)
cur = conn.cursor()

try:
    # Get Mangalore North constituency
    cur.execute("SELECT id FROM constituencies WHERE name LIKE '%Mangalore%'")
    result = cur.fetchone()
    if not result:
        print("❌ Mangalore North constituency not found!")
        exit(1)
    constituency_id = result[0]
    
    cur.execute("SELECT id FROM users WHERE phone = '+919876543213'")
    result = cur.fetchone()
    if result:
        user_id = result[0]
    else:
        # Use any citizen
        cur.execute("SELECT id FROM users WHERE role = 'citizen' LIMIT 1")
        user_id = cur.fetchone()[0]
    
    print(f"Using Mangalore North constituency: {constituency_id}")
    print(f"Using user: {user_id}")
    print()
    
    # Create complaints
    created = 0
    for loc in LOCATIONS:
        complaint = random.choice(COMPLAINTS)
        status = random.choice(STATUSES)
        
        created_at = datetime.utcnow() - timedelta(days=random.randint(1, 20))
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
    print(f"🎉 Successfully created {created} complaints in Mangalore North!")
    
except Exception as e:
    conn.rollback()
    print(f"❌ Error: {e}")
    raise
finally:
    cur.close()
    conn.close()
