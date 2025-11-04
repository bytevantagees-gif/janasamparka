# 🚀 Quick Start Guide - Panchayat Raj System

## Test User Login Credentials

### Gram Panchayat Level (Village)

**PDO (Panchayat Development Officer)**:
- Ramesh PDO: `+918242300001` → Bolwar GP
- Ganesh PDO: `+918242300003` → Kabaka GP  
- Mohan PDO: `+918242300004` → Parladka GP

**Village Accountant**:
- Suresh VA: `+918242300002` → Bolwar GP

**GP President** (Elected):
- Manoj Shetty: `+918242300005` → Bolwar GP

---

### Taluk Panchayat Level (Block)

**Taluk Panchayat Officer**:
- Kumar TP Officer: `+918242300100` → Puttur TP (oversees 3 GPs)

**TP President** (Elected):
- Rajesh Kumar: `+918242300101` → Puttur TP

---

### Zilla Panchayat Level (District)

**Zilla Panchayat Officer**:
- Dr. Kumar R.: `+918242300200` → Dakshina Kannada ZP (oversees 2 TPs, 5 GPs)

---

## Login Process

1. Open app: `http://localhost:3000`
2. Enter phone number (e.g., `+918242300001`)
3. Request OTP
4. Enter OTP code
5. Dashboard loads based on role

---

## Role-Based Dashboards

| Role | Dashboard | Key Features |
|------|-----------|--------------|
| **PDO** | PDO Dashboard | Village submissions, development works, scheme monitoring |
| **Village Accountant** | VA Dashboard | Certificate issuance, tax collection, revenue tracking |
| **GP President** | PDO Dashboard | Same as PDO (elected representative view) |
| **Taluk Officer** | TP Officer Dashboard | Multi-GP coordination, performance tracking |
| **TP President** | TP Officer Dashboard | Same as TP Officer (elected representative view) |
| **ZP Officer** | Admin Dashboard | District-wide view (full access) |
| **ZP President** | Admin Dashboard | Same as ZP Officer (elected representative view) |

---

## Panchayat Hierarchy

```
📍 Dakshina Kannada Zilla Panchayat
   ├─ 📍 Puttur Taluk Panchayat
   │    ├─ 🏘️ Bolwar Gram Panchayat (8,500 pop)
   │    │    ├─ Ramesh PDO
   │    │    ├─ Suresh VA
   │    │    └─ Manoj Shetty (President)
   │    ├─ 🏘️ Kabaka Gram Panchayat (6,200 pop)
   │    │    └─ Ganesh PDO
   │    └─ 🏘️ Parladka Gram Panchayat (5,800 pop)
   │         └─ Mohan PDO
   │
   └─ 📍 Kadaba Taluk Panchayat
        ├─ 🏘️ Nettanige Mudnur GP (7,200 pop)
        └─ 🏘️ Kodimbala GP (5,500 pop)
```

---

## API Endpoints

**Base URL**: `http://localhost:8000`

### Gram Panchayat
- `GET /api/panchayats/gram` - List all GPs (filtered by access)
- `GET /api/panchayats/gram/{gp_id}` - Get GP details + stats
- `POST /api/panchayats/gram` - Create GP (Admin only)
- `PATCH /api/panchayats/gram/{gp_id}` - Update GP

### Taluk Panchayat
- `GET /api/panchayats/taluk` - List all TPs
- `GET /api/panchayats/taluk/{tp_id}` - Get TP details + GP count

### Zilla Panchayat
- `GET /api/panchayats/zilla` - List all ZPs
- `GET /api/panchayats/zilla/{zp_id}` - Get ZP details + hierarchy

### Hierarchy
- `GET /api/panchayats/hierarchy/{constituency_id}` - Full ZP→TP→GP hierarchy

---

## Database Quick Reference

### Check Panchayats
```sql
-- Count by level
SELECT 'Zilla' as level, COUNT(*) FROM zilla_panchayats
UNION ALL SELECT 'Taluk', COUNT(*) FROM taluk_panchayats
UNION ALL SELECT 'Gram', COUNT(*) FROM gram_panchayats;

-- List all with hierarchy
SELECT gp.name, tp.name as taluk, zp.name as zilla
FROM gram_panchayats gp
LEFT JOIN taluk_panchayats tp ON gp.taluk_panchayat_id = tp.id
LEFT JOIN zilla_panchayats zp ON tp.zilla_panchayat_id = zp.id;
```

### Check Panchayat Officials
```sql
SELECT u.name, u.phone, u.role, 
       COALESCE(gp.name, tp.name, zp.name) as assignment
FROM users u
LEFT JOIN gram_panchayats gp ON u.gram_panchayat_id = gp.id
LEFT JOIN taluk_panchayats tp ON u.taluk_panchayat_id = tp.id
LEFT JOIN zilla_panchayats zp ON u.zilla_panchayat_id = zp.id
WHERE u.role LIKE '%panchayat%' OR u.role IN ('pdo', 'village_accountant', 'gp_president', 'tp_president', 'zp_president')
ORDER BY u.role;
```

---

## Docker Commands

```bash
# Check containers
docker ps --filter name=janasamparka

# View backend logs
docker logs janasamparka_backend --tail 50

# View frontend logs
docker logs janasamparka_frontend --tail 50

# Access database
docker exec -it janasamparka_db psql -U janasamparka -d janasamparka_db

# Restart backend
docker restart janasamparka_backend

# Restart frontend
docker restart janasamparka_frontend
```

---

## Testing Checklist

### PDO Dashboard Test
- [ ] Login as Ramesh PDO (+918242300001)
- [ ] See Bolwar GP statistics
- [ ] View recent submissions
- [ ] Check development works progress

### Village Accountant Test
- [ ] Login as Suresh VA (+918242300002)
- [ ] Navigate to Certificates tab
- [ ] Navigate to Tax Collection tab
- [ ] Check pending certificates count

### Taluk Officer Test
- [ ] Login as Kumar TP Officer (+918242300100)
- [ ] See 3 Gram Panchayats listed
- [ ] Check GP performance table
- [ ] View budget utilization per GP

### Zilla Officer Test
- [ ] Login as Dr. Kumar R. (+918242300200)
- [ ] Access admin dashboard
- [ ] View district-wide statistics

---

## Troubleshooting

### Issue: Dashboard not loading
**Solution**: Check role routing in SmartDashboard.jsx

### Issue: API returns 401 Unauthorized
**Solution**: User needs to login first (OTP authentication)

### Issue: No panchayat data shown
**Solution**: User not assigned to panchayat - check user.gram_panchayat_id

### Issue: Role not recognized
**Solution**: Check users.role column - should be VARCHAR(50)

---

## Summary

✅ **8 Test Users** across 3 panchayat levels  
✅ **3 Dashboards** (PDO, VA, TP Officer)  
✅ **5 Gram Panchayats** with sample data  
✅ **9 API Endpoints** for CRUD operations  
✅ **Complete Hierarchy** ZP → TP → GP  

**Status**: Production Ready 🚀

---

**Quick Login**: Use any phone number from above → Request OTP → Access dashboard
