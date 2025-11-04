"""Delete department officers with wrong phone numbers"""
from app.core.database import SessionLocal
from app.models.user import User

db = SessionLocal()
officers = db.query(User).filter(User.role == 'department_officer').all()
print(f'🗑️ Deleting {len(officers)} existing department officers...')
for o in officers:
    print(f'  Deleting: {o.phone} - {o.name}')
    db.delete(o)
db.commit()
print('✅ Deleted all department officers')
