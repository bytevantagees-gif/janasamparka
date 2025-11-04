"""
Seed script for multi-level administrative structure:
- 3 Constituencies (Puttur, Bantwal, Mangalore)
- 10 Wards per constituency (30 total)
- 3 Zilla Panchayats (Dakshina Kannada, Udupi, Uttara Kannada)
- 3 Taluk Panchayats per ZP (9 total)
- 3 Gram Panchayats per TP (27 total)

Run: docker exec janasamparka_backend python scripts/seed_multi_level_data.py
"""

import sys
import os
from pathlib import Path

# Add the parent directory to Python path
sys.path.append(str(Path(__file__).parent.parent))

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.models import (
    Constituency, Ward, 
    ZillaPanchayat, TalukPanchayat, GramPanchayat
)
from datetime import datetime, timezone
import random

# Database connection
DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://janasamparka:janasamparka123@db:5432/janasamparka")
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(bind=engine)

def seed_data():
    db = SessionLocal()
    
    try:
        print("=" * 80)
        print("SEEDING MULTI-LEVEL ADMINISTRATIVE DATA")
        print("=" * 80)
        
        # ===== 1. CREATE CONSTITUENCIES =====
        print("\n[1/5] Creating Constituencies...")
        constituencies_data = [
            {
                "name": "Puttur",
                "code": "PUT001",
                "district": "Dakshina Kannada",
                "state": "Karnataka",
                "description": "Puttur Assembly Constituency",
                "mla_name": "Shri Sanjeeva Matandoor",
                "mla_party": "BJP",
                "total_population": 185000,
                "total_wards": 10,
                "assembly_number": 176,
                "taluks": ["Puttur", "Kadaba"]
            },
            {
                "name": "Bantwal",
                "code": "BAN001",
                "district": "Dakshina Kannada",
                "state": "Karnataka",
                "description": "Bantwal Assembly Constituency",
                "mla_name": "Smt. Rajeshwari Naik",
                "mla_party": "INC",
                "total_population": 220000,
                "total_wards": 10,
                "assembly_number": 177,
                "taluks": ["Bantwal"]
            },
            {
                "name": "Mangalore City South",
                "code": "MNG001",
                "district": "Dakshina Kannada",
                "state": "Karnataka",
                "description": "Mangalore City South Assembly Constituency",
                "mla_name": "Shri Vedavyas Kamath",
                "mla_party": "BJP",
                "total_population": 156000,
                "total_wards": 10,
                "assembly_number": 178,
                "taluks": ["Mangalore"]
            }
        ]
        
        constituencies = []
        for const_data in constituencies_data:
            # Check if exists by name or code
            existing = db.query(Constituency).filter(
                (Constituency.code == const_data["code"]) | (Constituency.name == const_data["name"])
            ).first()
            if existing:
                print(f"  ✓ {const_data['name']} already exists")
                constituencies.append(existing)
            else:
                const = Constituency(**const_data)
                db.add(const)
                db.flush()
                constituencies.append(const)
                print(f"  + Created: {const_data['name']}")
        
        db.commit()
        print(f"✅ Created {len(constituencies)} constituencies")
        
        # ===== 2. CREATE WARDS (10 per constituency) =====
        print("\n[2/5] Creating Wards (10 per constituency)...")
        ward_names = [
            "Central Ward", "East Ward", "West Ward", "North Ward", "South Ward",
            "Market Ward", "Industrial Ward", "Residential Ward", "Commercial Ward", "Rural Ward"
        ]
        
        wards = []
        ward_count = 0
        for const in constituencies:
            const_taluk = const.taluks[0] if const.taluks else const.name
            for i, name in enumerate(ward_names, 1):
                # Check if exists by ward_number and constituency
                existing = db.query(Ward).filter(
                    Ward.constituency_id == const.id, 
                    Ward.ward_number == i
                ).first()
                if not existing:
                    ward = Ward(
                        name=f"{name}",
                        ward_number=i,
                        taluk=const_taluk,
                        constituency_id=const.id,
                        population=random.randint(8000, 25000)
                    )
                    db.add(ward)
                    wards.append(ward)
                    ward_count += 1
        
        db.commit()
        print(f"✅ Created {ward_count} wards (10 per constituency)")
        
        # ===== 3. CREATE ZILLA PANCHAYATS =====
        print("\n[3/5] Creating Zilla Panchayats (3 districts)...")
        zp_data = [
            {
                "name": "Dakshina Kannada Zilla Panchayat",
                "code": "DK_ZP",
                "district": "Dakshina Kannada",
                "state": "Karnataka",
                "president_name": "Smt. Meenakshi Shanthigodu",
                "chief_executive_officer_name": "Shri K. Ananda",
                "total_population": 2089649,
                "total_taluk_panchayats": 3,
                "total_gram_panchayats": 9,
                "office_phone": "+918242234567",
                "office_email": "dkzp@karnataka.gov.in",
                "office_address": "District Panchayat Office, Mangalore"
            },
            {
                "name": "Udupi Zilla Panchayat",
                "code": "UDU_ZP",
                "district": "Udupi",
                "state": "Karnataka",
                "president_name": "Shri Dinakar Babu",
                "chief_executive_officer_name": "Smt. Priya Acharya",
                "total_population": 1177361,
                "total_taluk_panchayats": 3,
                "total_gram_panchayats": 9,
                "office_phone": "+918202234567",
                "office_email": "udupizp@karnataka.gov.in",
                "office_address": "District Panchayat Office, Udupi"
            },
            {
                "name": "Uttara Kannada Zilla Panchayat",
                "code": "UK_ZP",
                "district": "Uttara Kannada",
                "state": "Karnataka",
                "president_name": "Smt. Lakshmi Hebbar",
                "chief_executive_officer_name": "Shri Nagesh Prabhu",
                "total_population": 1437169,
                "total_taluk_panchayats": 3,
                "total_gram_panchayats": 9,
                "office_phone": "+918382234567",
                "office_email": "ukzp@karnataka.gov.in",
                "office_address": "District Panchayat Office, Karwar"
            }
        ]
        
        zilla_panchayats = []
        for zp in zp_data:
            existing = db.query(ZillaPanchayat).filter(ZillaPanchayat.code == zp["code"]).first()
            if existing:
                print(f"  ✓ {zp['name']} already exists")
                zilla_panchayats.append(existing)
            else:
                zp_obj = ZillaPanchayat(**zp)
                db.add(zp_obj)
                db.flush()
                zilla_panchayats.append(zp_obj)
                print(f"  + Created: {zp['name']}")
        
        db.commit()
        print(f"✅ Created {len(zilla_panchayats)} Zilla Panchayats")
        
        # ===== 4. CREATE TALUK PANCHAYATS (3 per ZP) =====
        print("\n[4/5] Creating Taluk Panchayats (3 per ZP)...")
        
        # Get constituency IDs for reference (use the ones we just created/retrieved)
        # Use name-based lookup since existing constituencies may have different codes
        const_by_name = {c.name: c for c in constituencies}
        puttur_const = const_by_name.get("Puttur")
        bantwal_const = const_by_name.get("Bantwal")
        mng_const = const_by_name.get("Mangalore City South")
        
        print(f"  DEBUG: Puttur ID: {puttur_const.id if puttur_const else 'None'}")
        print(f"  DEBUG: Bantwal ID: {bantwal_const.id if bantwal_const else 'None'}")
        print(f"  DEBUG: Mangalore ID: {mng_const.id if mng_const else 'None'}")
        
        tp_data_by_zp = {
            "DK_ZP": [
                {
                    "name": "Puttur Taluk Panchayat",
                    "code": "DK_TP_PUT",
                    "taluk_name": "Puttur",
                    "district": "Dakshina Kannada",
                    "state": "Karnataka",
                    "president_name": "Shri Abdul Rasheed",
                    "executive_officer_name": "Smt. Rekha Rao",
                    "total_population": 295000,
                    "total_gram_panchayats": 3,
                    "constituency_id": puttur_const.id if puttur_const else None,
                    "office_phone": "+918252234567",
                    "office_email": "putturtp@karnataka.gov.in"
                },
                {
                    "name": "Bantwal Taluk Panchayat",
                    "code": "DK_TP_BAN",
                    "taluk_name": "Bantwal",
                    "district": "Dakshina Kannada",
                    "state": "Karnataka",
                    "president_name": "Smt. Vasanthi Shetty",
                    "executive_officer_name": "Shri Mohan Kumar",
                    "total_population": 378000,
                    "total_gram_panchayats": 3,
                    "constituency_id": bantwal_const.id if bantwal_const else None,
                    "office_phone": "+918252334567",
                    "office_email": "bantwaltp@karnataka.gov.in"
                },
                {
                    "name": "Belthangady Taluk Panchayat",
                    "code": "DK_TP_BEL",
                    "taluk_name": "Belthangady",
                    "district": "Dakshina Kannada",
                    "state": "Karnataka",
                    "president_name": "Shri Raviraj Hegde",
                    "executive_officer_name": "Smt. Lalitha Shetty",
                    "total_population": 182000,
                    "total_gram_panchayats": 3,
                    "constituency_id": puttur_const.id if puttur_const else None,
                    "office_phone": "+918252434567",
                    "office_email": "belthangadytp@karnataka.gov.in"
                }
            ],
            "UDU_ZP": [
                {
                    "name": "Udupi Taluk Panchayat",
                    "code": "UDU_TP_UDU",
                    "taluk_name": "Udupi",
                    "district": "Udupi",
                    "state": "Karnataka",
                    "president_name": "Smt. Geetha Wagle",
                    "executive_officer_name": "Shri Raghavendra Acharya",
                    "total_population": 512000,
                    "total_gram_panchayats": 3,
                    "constituency_id": mng_const.id if mng_const else None,
                    "office_phone": "+918202334567",
                    "office_email": "udupitp@karnataka.gov.in"
                },
                {
                    "name": "Kundapura Taluk Panchayat",
                    "code": "UDU_TP_KUN",
                    "taluk_name": "Kundapura",
                    "district": "Udupi",
                    "state": "Karnataka",
                    "president_name": "Shri Suresh Shettigar",
                    "executive_officer_name": "Smt. Savitha Hegde",
                    "total_population": 382000,
                    "total_gram_panchayats": 3,
                    "constituency_id": mng_const.id if mng_const else None,
                    "office_phone": "+918202434567",
                    "office_email": "kundapuratp@karnataka.gov.in"
                },
                {
                    "name": "Karkala Taluk Panchayat",
                    "code": "UDU_TP_KAR",
                    "taluk_name": "Karkala",
                    "district": "Udupi",
                    "state": "Karnataka",
                    "president_name": "Smt. Shailaja Nayak",
                    "executive_officer_name": "Shri Ganesh Bhat",
                    "total_population": 283000,
                    "total_gram_panchayats": 3,
                    "constituency_id": mng_const.id if mng_const else None,
                    "office_phone": "+918202534567",
                    "office_email": "karkalatp@karnataka.gov.in"
                }
            ],
            "UK_ZP": [
                {
                    "name": "Karwar Taluk Panchayat",
                    "code": "UK_TP_KAR",
                    "taluk_name": "Karwar",
                    "district": "Uttara Kannada",
                    "state": "Karnataka",
                    "president_name": "Shri Nagaraj Shetty",
                    "executive_officer_name": "Smt. Roopa Naik",
                    "total_population": 234000,
                    "total_gram_panchayats": 3,
                    "constituency_id": mng_const.id if mng_const else None,
                    "office_phone": "+918382334567",
                    "office_email": "karwartp@karnataka.gov.in"
                },
                {
                    "name": "Sirsi Taluk Panchayat",
                    "code": "UK_TP_SIR",
                    "taluk_name": "Sirsi",
                    "district": "Uttara Kannada",
                    "state": "Karnataka",
                    "president_name": "Smt. Lalitha Devadiga",
                    "executive_officer_name": "Shri Prakash Hegde",
                    "total_population": 312000,
                    "total_gram_panchayats": 3,
                    "constituency_id": mng_const.id if mng_const else None,
                    "office_phone": "+918382434567",
                    "office_email": "sirsitp@karnataka.gov.in"
                },
                {
                    "name": "Kumta Taluk Panchayat",
                    "code": "UK_TP_KUM",
                    "taluk_name": "Kumta",
                    "district": "Uttara Kannada",
                    "state": "Karnataka",
                    "president_name": "Shri Shekhar Naik",
                    "executive_officer_name": "Smt. Suma Kotian",
                    "total_population": 198000,
                    "total_gram_panchayats": 3,
                    "constituency_id": mng_const.id if mng_const else None,
                    "office_phone": "+918382534567",
                    "office_email": "kumtatp@karnataka.gov.in"
                }
            ]
        }
        
        taluk_panchayats = []
        tp_count = 0
        for zp in zilla_panchayats:
            tp_list = tp_data_by_zp.get(zp.code, [])
            for tp_data in tp_list:
                existing = db.query(TalukPanchayat).filter(TalukPanchayat.code == tp_data["code"]).first()
                if not existing:
                    tp = TalukPanchayat(
                        zilla_panchayat_id=zp.id,
                        **tp_data
                    )
                    db.add(tp)
                    db.flush()
                    taluk_panchayats.append(tp)
                    tp_count += 1
                    print(f"  + Created: {tp_data['name']} under {zp.name}")
                else:
                    taluk_panchayats.append(existing)
        
        db.commit()
        print(f"✅ Created {tp_count} Taluk Panchayats (3 per ZP)")
        
        # ===== 5. CREATE GRAM PANCHAYATS (3 per TP) =====
        print("\n[5/5] Creating Gram Panchayats (3 per TP)...")
        
        # Sample GP names for each taluk
        gp_names_by_taluk = {
            "Puttur": ["Kabaka", "Uppinangady", "Savanur"],
            "Bantwal": ["Vittal", "B.C. Road", "Panemangalore"],
            "Belthangady": ["Ujire", "Dharmasthala", "Venur"],
            "Udupi": ["Manipal", "Brahmavara", "Katapadi"],
            "Kundapura": ["Byndoor", "Gangolli", "Shankarnarayana"],
            "Karkala": ["Hebri", "Nitte", "Moodbidri"],
            "Karwar": ["Shirali", "Ankola", "Sadashivgad"],
            "Sirsi": ["Siddapur", "Yellapur", "Banavasi"],
            "Kumta": ["Gokarna", "Honavar", "Mirjan"]
        }
        
        gp_count = 0
        for tp in taluk_panchayats:
            gp_names = gp_names_by_taluk.get(tp.taluk_name, ["GP1", "GP2", "GP3"])
            for i, gp_name in enumerate(gp_names, 1):
                gp_code = f"{tp.code}_GP{i:02d}"
                existing = db.query(GramPanchayat).filter(GramPanchayat.code == gp_code).first()
                if not existing:
                    gp = GramPanchayat(
                        name=f"{gp_name} Gram Panchayat",
                        code=gp_code,
                        taluk_panchayat_id=tp.id,
                        constituency_id=tp.constituency_id,
                        taluk_name=tp.taluk_name,
                        district=tp.district,
                        state=tp.state,
                        president_name=f"Shri/Smt. {gp_name} President",
                        population=random.randint(5000, 25000),
                        households=random.randint(800, 5000),
                        villages_covered=random.randint(1, 5),
                        office_phone=f"+918{random.randint(200000000, 999999999)}"
                    )
                    db.add(gp)
                    gp_count += 1
                    print(f"  + Created: {gp_name} GP under {tp.name}")
        
        db.commit()
        print(f"✅ Created {gp_count} Gram Panchayats (3 per TP)")
        
        # ===== SUMMARY =====
        print("\n" + "=" * 80)
        print("SEEDING COMPLETE!")
        print("=" * 80)
        print(f"Constituencies: {db.query(Constituency).count()}")
        print(f"Wards: {db.query(Ward).count()}")
        print(f"Zilla Panchayats: {db.query(ZillaPanchayat).count()}")
        print(f"Taluk Panchayats: {db.query(TalukPanchayat).count()}")
        print(f"Gram Panchayats: {db.query(GramPanchayat).count()}")
        print("=" * 80)
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        db.rollback()
        raise
    finally:
        db.close()

if __name__ == "__main__":
    seed_data()
