"""
Create test users for different roles and constituencies
"""
import uuid
import psycopg2
from passlib.context import CryptContext
from app.core.config import settings

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

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

conn = psycopg2.connect(**conn_params)
cur = conn.cursor()

try:
    # Get constituencies
    cur.execute("SELECT id, name FROM constituencies ORDER BY name")
    constituencies = cur.fetchall()
    
    if not constituencies:
        print("❌ No constituencies found! Run setup first.")
        exit(1)
    
    print("Available constituencies:")
    for const in constituencies:
        print(f"  - {const[1]} ({const[0]})")
    print()
    
    # Create test users for each constituency
    test_users = [
        {
            "name": "Admin User",
            "phone": "+919876543210",
            "role": "admin",
            "constituency_id": constituencies[0][0],  # Admins still need a constituency
            "description": "System admin - can see all constituencies"
        },
        {
            "name": "Puttur MLA",
            "phone": "+919876543211",
            "role": "mla",
            "constituency_id": None,  # Will set to Puttur
            "description": "MLA for Puttur - sees only Puttur data"
        },
        {
            "name": "Puttur Moderator",
            "phone": "+919876543212",
            "role": "moderator",
            "constituency_id": None,  # Will set to Puttur
            "description": "Moderator for Puttur - sees only Puttur data"
        },
        {
            "name": "Mangalore Moderator",
            "phone": "+919876543213",
            "role": "moderator",
            "constituency_id": None,  # Will set to Mangalore North
            "description": "Moderator for Mangalore - sees only Mangalore data"
        },
        {
            "name": "Puttur Citizen",
            "phone": "+919876543214",
            "role": "citizen",
            "constituency_id": None,  # Will set to Puttur
            "description": "Citizen from Puttur"
        }
    ]
    
    # Set constituency IDs
    puttur_id = next((c[0] for c in constituencies if 'Puttur' in c[1]), constituencies[0][0])
    mangalore_id = next((c[0] for c in constituencies if 'Mangalore' in c[1]), constituencies[1][0] if len(constituencies) > 1 else constituencies[0][0])
    
    test_users[1]["constituency_id"] = puttur_id
    test_users[2]["constituency_id"] = puttur_id
    test_users[3]["constituency_id"] = mangalore_id
    test_users[4]["constituency_id"] = puttur_id
    
    print("Creating test users:")
    print("=" * 80)
    
    for user_data in test_users:
        # Check if user exists
        cur.execute("SELECT id FROM users WHERE phone = %s", (user_data["phone"],))
        existing = cur.fetchone()
        
        if existing:
            print(f"✓ User already exists: {user_data['name']} ({user_data['phone']})")
            continue
        
        user_id = str(uuid.uuid4())
        cur.execute("""
            INSERT INTO users (id, name, phone, role, constituency_id, is_active, created_at, updated_at)
            VALUES (%s, %s, %s, %s, %s, %s, NOW(), NOW())
        """, (
            user_id,
            user_data["name"],
            user_data["phone"],
            user_data["role"],
            str(user_data["constituency_id"]),
            "true"
        ))
        
        print(f"✅ Created: {user_data['name']}")
        print(f"   Phone: {user_data['phone']}")
        print(f"   Role: {user_data['role']}")
        print(f"   Description: {user_data['description']}")
        print()
    
    conn.commit()
    
    print("=" * 80)
    print("📱 Test Users Created!")
    print()
    print("Login Credentials (use OTP: 123456 for all):")
    print("-" * 80)
    for user in test_users:
        print(f"Phone: {user['phone']} | Role: {user['role']:15} | {user['description']}")
    print()
    print("Note: Multi-tenancy is now active!")
    print("- Admin sees all complaints")
    print("- Other roles see only their constituency's data")
    
except Exception as e:
    conn.rollback()
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()
finally:
    cur.close()
    conn.close()
