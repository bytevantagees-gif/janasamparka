"""
Create comprehensive test users for all roles and constituencies
Run this after seed_data.py: python create_all_test_users.py
"""
import uuid
import psycopg2
from app.core.config import settings

# Parse DATABASE_URL
url_parts = settings.DATABASE_URL.replace('postgresql://', '').replace('postgres://', '').split('@')
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

print("🔗 Connecting to database...")
conn = psycopg2.connect(**conn_params)
cur = conn.cursor()

try:
    # Get all constituencies
    cur.execute("SELECT id, name FROM constituencies ORDER BY name")
    constituencies = cur.fetchall()
    
    if not constituencies:
        print("❌ No constituencies found! Run 'python seed_data.py' first.")
        exit(1)
    
    print(f"\n📍 Found {len(constituencies)} constituencies:")
    constituency_map = {}
    for const in constituencies:
        print(f"   - {const[1]}")
        constituency_map[const[1]] = const[0]
    print()
    
    # Define all test users with proper role distribution
    test_users = [
        # ========================================
        # SYSTEM ADMIN
        # ========================================
        {
            "name": "System Administrator",
            "phone": "+919999999999",
            "role": "admin",
            "constituency": None,  # Admin sees all
            "description": "Super Admin - Access to all constituencies"
        },
        
        # ========================================
        # PUTTUR CONSTITUENCY USERS
        # ========================================
        {
            "name": "Ashok Kumar Rai",
            "phone": "+918242226666",
            "role": "mla",
            "constituency": "Puttur",
            "description": "MLA for Puttur constituency"
        },
        {
            "name": "Puttur Moderator 1",
            "phone": "+918242226001",
            "role": "moderator",
            "constituency": "Puttur",
            "description": "Moderator - Puttur constituency"
        },
        {
            "name": "Puttur Moderator 2",
            "phone": "+918242226002",
            "role": "moderator",
            "constituency": "Puttur",
            "description": "Moderator - Puttur constituency"
        },
        {
            "name": "PWD Officer - Puttur",
            "phone": "+918242226101",
            "role": "department_officer",
            "constituency": "Puttur",
            "description": "Department Officer - PWD Puttur"
        },
        {
            "name": "Water Officer - Puttur",
            "phone": "+918242226102",
            "role": "department_officer",
            "constituency": "Puttur",
            "description": "Department Officer - Water Supply Puttur"
        },
        {
            "name": "MESCOM Officer - Puttur",
            "phone": "+918242226103",
            "role": "department_officer",
            "constituency": "Puttur",
            "description": "Department Officer - MESCOM Puttur"
        },
        {
            "name": "Audit Officer - Puttur",
            "phone": "+918242226201",
            "role": "auditor",
            "constituency": "Puttur",
            "description": "Auditor - Puttur constituency"
        },
        {
            "name": "Citizen - Puttur Ward 1",
            "phone": "+918242226301",
            "role": "citizen",
            "constituency": "Puttur",
            "description": "Citizen from Puttur Ward 1"
        },
        {
            "name": "Citizen - Puttur Ward 2",
            "phone": "+918242226302",
            "role": "citizen",
            "constituency": "Puttur",
            "description": "Citizen from Puttur Ward 2"
        },
        
        # ========================================
        # MANGALORE NORTH CONSTITUENCY USERS
        # ========================================
        {
            "name": "B.A. Mohiuddin Bava",
            "phone": "+918242227777",
            "role": "mla",
            "constituency": "Mangalore North",
            "description": "MLA for Mangalore North constituency"
        },
        {
            "name": "Mangalore Moderator 1",
            "phone": "+918242227001",
            "role": "moderator",
            "constituency": "Mangalore North",
            "description": "Moderator - Mangalore North constituency"
        },
        {
            "name": "Mangalore Moderator 2",
            "phone": "+918242227002",
            "role": "moderator",
            "constituency": "Mangalore North",
            "description": "Moderator - Mangalore North constituency"
        },
        {
            "name": "PWD Officer - Mangalore",
            "phone": "+918242227101",
            "role": "department_officer",
            "constituency": "Mangalore North",
            "description": "Department Officer - PWD Mangalore"
        },
        {
            "name": "Water Officer - Mangalore",
            "phone": "+918242227102",
            "role": "department_officer",
            "constituency": "Mangalore North",
            "description": "Department Officer - Water Supply Mangalore"
        },
        {
            "name": "MESCOM Officer - Mangalore",
            "phone": "+918242227103",
            "role": "department_officer",
            "constituency": "Mangalore North",
            "description": "Department Officer - MESCOM Mangalore"
        },
        {
            "name": "Audit Officer - Mangalore",
            "phone": "+918242227201",
            "role": "auditor",
            "constituency": "Mangalore North",
            "description": "Auditor - Mangalore North constituency"
        },
        {
            "name": "Citizen - Mangalore Kadri",
            "phone": "+918242227301",
            "role": "citizen",
            "constituency": "Mangalore North",
            "description": "Citizen from Mangalore Kadri Ward"
        },
        {
            "name": "Citizen - Mangalore Pandeshwar",
            "phone": "+918242227302",
            "role": "citizen",
            "constituency": "Mangalore North",
            "description": "Citizen from Mangalore Pandeshwar Ward"
        },
        
        # ========================================
        # UDUPI CONSTITUENCY USERS
        # ========================================
        {
            "name": "Yashpal A. Suvarna",
            "phone": "+918252255555",
            "role": "mla",
            "constituency": "Udupi",
            "description": "MLA for Udupi constituency"
        },
        {
            "name": "Udupi Moderator 1",
            "phone": "+918252255001",
            "role": "moderator",
            "constituency": "Udupi",
            "description": "Moderator - Udupi constituency"
        },
        {
            "name": "Udupi Moderator 2",
            "phone": "+918252255002",
            "role": "moderator",
            "constituency": "Udupi",
            "description": "Moderator - Udupi constituency"
        },
        {
            "name": "PWD Officer - Udupi",
            "phone": "+918252255101",
            "role": "department_officer",
            "constituency": "Udupi",
            "description": "Department Officer - PWD Udupi"
        },
        {
            "name": "Water Officer - Udupi",
            "phone": "+918252255102",
            "role": "department_officer",
            "constituency": "Udupi",
            "description": "Department Officer - Water Supply Udupi"
        },
        {
            "name": "MESCOM Officer - Udupi",
            "phone": "+918252255103",
            "role": "department_officer",
            "constituency": "Udupi",
            "description": "Department Officer - MESCOM Udupi"
        },
        {
            "name": "Audit Officer - Udupi",
            "phone": "+918252255201",
            "role": "auditor",
            "constituency": "Udupi",
            "description": "Auditor - Udupi constituency"
        },
        {
            "name": "Citizen - Udupi Car Street",
            "phone": "+918252255301",
            "role": "citizen",
            "constituency": "Udupi",
            "description": "Citizen from Udupi Car Street Ward"
        },
        {
            "name": "Citizen - Udupi Temple Area",
            "phone": "+918252255302",
            "role": "citizen",
            "constituency": "Udupi",
            "description": "Citizen from Udupi Temple Area Ward"
        },
    ]
    
    print("=" * 100)
    print("👥 CREATING TEST USERS")
    print("=" * 100)
    
    created_count = 0
    existing_count = 0
    
    for user_data in test_users:
        # Get constituency ID
        constituency_id = None
        if user_data["constituency"]:
            constituency_id = constituency_map.get(user_data["constituency"])
            if not constituency_id:
                print(f"⚠️  Warning: Constituency '{user_data['constituency']}' not found, skipping user {user_data['name']}")
                continue
        
        # Check if user exists
        cur.execute("SELECT id FROM users WHERE phone = %s", (user_data["phone"],))
        existing = cur.fetchone()
        
        if existing:
            existing_count += 1
            print(f"✓ Already exists: {user_data['name']:30} | {user_data['phone']:15} | {user_data['role']:20}")
            continue
        
        # Create new user
        user_id = str(uuid.uuid4())
        cur.execute("""
            INSERT INTO users (id, name, phone, role, constituency_id, is_active, locale_pref, created_at, updated_at)
            VALUES (%s, %s, %s, %s, %s, %s, %s, NOW(), NOW())
        """, (
            user_id,
            user_data["name"],
            user_data["phone"],
            user_data["role"],
            str(constituency_id) if constituency_id else None,
            "true",
            "kn" if user_data["role"] != "admin" else "en"
        ))
        
        created_count += 1
        print(f"✅ Created: {user_data['name']:30} | {user_data['phone']:15} | {user_data['role']:20}")
    
    conn.commit()
    
    print("\n" + "=" * 100)
    print("🎉 USER CREATION COMPLETE!")
    print("=" * 100)
    print(f"\n📊 Summary:")
    print(f"   ✅ Created: {created_count} new users")
    print(f"   ✓ Existing: {existing_count} users")
    print(f"   📱 Total: {created_count + existing_count} test users available")
    
    print("\n" + "=" * 100)
    print("🔑 TEST LOGIN CREDENTIALS")
    print("=" * 100)
    print("\n📱 Use OTP: 123456 for all test logins\n")
    
    print("┌" + "─" * 98 + "┐")
    print("│ SYSTEM ADMIN" + " " * 85 + "│")
    print("├" + "─" * 98 + "┤")
    for user in test_users:
        if user["role"] == "admin":
            print(f"│ 📱 {user['phone']:15} │ {user['name']:30} │ {user['description']:40} │")
    
    print("├" + "─" * 98 + "┤")
    print("│ PUTTUR CONSTITUENCY" + " " * 78 + "│")
    print("├" + "─" * 98 + "┤")
    for user in test_users:
        if user["constituency"] == "Puttur":
            role_emoji = {
                "mla": "👔",
                "moderator": "🛡️",
                "department_officer": "👷",
                "auditor": "📊",
                "citizen": "👤"
            }.get(user["role"], "👤")
            print(f"│ {role_emoji} {user['phone']:15} │ {user['name']:30} │ {user['description']:40} │")
    
    print("├" + "─" * 98 + "┤")
    print("│ MANGALORE NORTH CONSTITUENCY" + " " * 69 + "│")
    print("├" + "─" * 98 + "┤")
    for user in test_users:
        if user["constituency"] == "Mangalore North":
            role_emoji = {
                "mla": "👔",
                "moderator": "🛡️",
                "department_officer": "👷",
                "auditor": "📊",
                "citizen": "👤"
            }.get(user["role"], "👤")
            print(f"│ {role_emoji} {user['phone']:15} │ {user['name']:30} │ {user['description']:40} │")
    
    print("├" + "─" * 98 + "┤")
    print("│ UDUPI CONSTITUENCY" + " " * 79 + "│")
    print("├" + "─" * 98 + "┤")
    for user in test_users:
        if user["constituency"] == "Udupi":
            role_emoji = {
                "mla": "👔",
                "moderator": "🛡️",
                "department_officer": "👷",
                "auditor": "📊",
                "citizen": "👤"
            }.get(user["role"], "👤")
            print(f"│ {role_emoji} {user['phone']:15} │ {user['name']:30} │ {user['description']:40} │")
    
    print("└" + "─" * 98 + "┘")
    
    print("\n" + "=" * 100)
    print("📋 ROLE BREAKDOWN")
    print("=" * 100)
    
    role_counts = {}
    for user in test_users:
        role = user["role"]
        role_counts[role] = role_counts.get(role, 0) + 1
    
    role_names = {
        "admin": "System Administrators",
        "mla": "MLAs",
        "moderator": "Moderators",
        "department_officer": "Department Officers",
        "auditor": "Auditors",
        "citizen": "Citizens"
    }
    
    for role, count in sorted(role_counts.items()):
        print(f"   {role_names.get(role, role):25} : {count:2} users")
    
    print("\n" + "=" * 100)
    print("🚀 NEXT STEPS")
    print("=" * 100)
    print("\n1. Start the backend server:")
    print("   cd backend && .venv/bin/python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000")
    print("\n2. Test authentication:")
    print("   - Visit: http://localhost:8000/docs")
    print("   - Use endpoint: POST /api/v1/auth/request-otp")
    print("   - Enter any phone number from the list above")
    print("   - Use OTP: 123456")
    print("\n3. Test multi-tenancy:")
    print("   - Login as different roles")
    print("   - Verify data filtering by constituency")
    print("   - Admin should see all data")
    print("   - Others see only their constituency")
    print("\n" + "=" * 100)
    
except Exception as e:
    conn.rollback()
    print(f"\n❌ Error creating test users: {e}")
    import traceback
    traceback.print_exc()
finally:
    cur.close()
    conn.close()
