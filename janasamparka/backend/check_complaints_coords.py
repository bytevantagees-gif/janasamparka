"""Check complaints with coordinates"""
from app.core.database import engine
from sqlalchemy import text

with engine.connect() as conn:
    result = conn.execute(text('''
        SELECT 
            COUNT(*) as total_complaints,
            COUNT(CASE WHEN lat IS NOT NULL AND lng IS NOT NULL THEN 1 END) as with_coords,
            c2.name as constituency_name,
            COUNT(CASE WHEN c.constituency_id = c2.id THEN 1 END) as in_puttur
        FROM complaints c
        LEFT JOIN constituencies c2 ON c2.name = 'Puttur'
        GROUP BY c2.name
    '''))
    row = result.fetchone()
    if row:
        print(f'Total complaints: {row[0]}')
        print(f'With coordinates: {row[1]}')
        print(f'Constituency: {row[2]}')
    else:
        print('No complaints found')
    
    # Get sample complaints with coords
    result2 = conn.execute(text('''
        SELECT c.id, c.title, c.lat, c.lng, con.name as constituency
        FROM complaints c
        JOIN constituencies con ON c.constituency_id = con.id
        WHERE c.lat IS NOT NULL AND c.lng IS NOT NULL
        LIMIT 5
    '''))
    print('\nSample complaints with coordinates:')
    for row in result2:
        print(f'  {row[1]}: lat={row[2]}, lng={row[3]}, constituency={row[4]}')
