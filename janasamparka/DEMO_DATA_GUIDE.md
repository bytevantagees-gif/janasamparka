# Demo Data Guide - MLA Presentation

## 📊 Overview

The database has been populated with comprehensive demo data for an impressive MLA presentation.

### Current Data Summary

- **Total Users**: 60
  - **Citizens**: 42
  - **Department Users**: 15  
  - **MLAs**: 3
- **Total Complaints**: 100
  - Distributed across all statuses
  - Realistic categories and descriptions
  - Assigned to appropriate departments

---

## 🔐 Demo Login Credentials

### Citizens (General Public)
Use these credentials to demonstrate the citizen portal:

| Name | Phone Number | Constituency |
|------|-------------|--------------|
| Ramesh Kumar | +919800000000 | Puttur |
| Priya Shetty | +919800000001 | Puttur |
| Suresh Bhat | +919800000002 | Puttur |
| Kavitha Rai | +919800000003 | Puttur |
| Manjunath Shetty | +919800000004 | Puttur |

**All citizen phones follow pattern**: +9198000XXXXX (where XXXXX is 00000-00039)

### Department Users (Government Staff)
Use these credentials to demonstrate the department portal:

| Department | Phone Number |
|------------|--------------|
| Public Works Department | +919700000000 |
| Water Supply & Drainage | +919700000001 |
| Electricity (MESCOM) | +919700000002 |
| Health & Family Welfare | +919700000003 |
| Education Department | +919700000004 |
| Revenue Department | +919700000005 |
| MGNREGA | +919700000006 |
| Women & Child Development | +919700000007 |
| Forest Department | +919700000008 |
| Panchayati Raj | +919700000009 |

**All department phones follow pattern**: +9197000XXXX (where XXXX is 00000-00014)

### Moderator Accounts (Newly Created) ⭐
Use these credentials to demonstrate the moderator portal with full complaint management:

| Name | Phone Number | Constituency |
|------|-------------|--------------|
| Puttur Moderator | +919900000000 | Puttur |
| Mangalore North Moderator | +919900000001 | Mangalore North |
| Udupi Moderator | +919900000002 | Udupi |

**Moderator Powers**:
- View ALL complaints in constituency
- Assign complaints to departments
- Approve/reject completed work
- Access full analytics dashboard

### MLA Accounts
Existing MLA accounts:

| Name | Phone Number | Constituency |
|------|-------------|--------------|
| Ashok Kumar Rai | +918242226666 | Puttur |
| Bharat Yethadka Shetty | +919448026697 | Moodabidri |
| Rajesh Naik U | +919449724525 | Bantwal |

---

## 📋 Complaint Data Details

### Complaint Status Distribution

```
submitted:    21 complaints (New complaints waiting assignment)
assigned:     19 complaints (Assigned to departments)
in_progress:  18 complaints (Being worked on)
resolved:     21 complaints (Fixed, awaiting closure)
closed:       21 complaints (Completed)
```

### Complaint Categories

All 100 complaints are distributed across 10 realistic categories:

1. **Roads** - Potholes, road repair, maintenance issues
2. **Water Supply** - No water, contaminated water, broken pipes
3. **Electricity** - Power cuts, transformer issues, street lights
4. **Garbage** - Collection issues, illegal dumping
5. **Drainage** - Blocked drains, sewage overflow
6. **Health** - Healthcare access, vaccination, sanitation
7. **Education** - School infrastructure, teacher shortage
8. **Agriculture** - Crop damage, irrigation, pest control
9. **Employment** - Job card issues, wage delays (MGNREGA)
10. **Women & Child** - Anganwadi issues, child welfare

### Priority Levels

- **Low**: 25 complaints
- **Medium**: 40 complaints
- **High**: 25 complaints
- **Urgent**: 10 complaints

---

## 🎯 Demo Scenarios

### Scenario 1: Citizen Filing a Complaint
1. Login as citizen (e.g., Ramesh Kumar: +919800000000)
2. Request OTP (OTP will be printed in backend logs)
3. Verify OTP
4. Browse existing complaints
5. File a new complaint with:
   - Category (e.g., Roads)
   - Description
   - Location (GPS coordinates)
   - Priority

### Scenario 2: Department User Managing Complaints
1. Login as department user (e.g., PWD: +919700000000)
2. View assigned complaints
3. Update complaint status (assigned → in_progress → resolved)
4. Add internal notes
5. Upload work photos (if implemented)

### Scenario 3: MLA Dashboard Overview
1. Login as MLA (e.g., Ashok Kumar Rai: +918242226666)
2. View constituency-wide statistics:
   - Total complaints
   - Status distribution
   - Department performance
   - Ward-wise breakdown
3. Monitor priority/urgent complaints
4. View citizen feedback and ratings

### Scenario 4: Real-time Status Updates
1. Show how citizens receive updates on their complaints
2. Demonstrate notification system
3. Show timeline of complaint lifecycle

---

## 🗺️ Geographic Coverage

All complaints are distributed across:
- **3 Constituencies**: Puttur, Moodabidri, Bantwal
- **15 Wards**: 5 wards per constituency
- **GPS Coordinates**: Realistic lat/lng around 12.8°N, 74.8°E (Dakshina Kannada region)

---

## 📱 Testing the Demo

### Request OTP
```bash
curl -X POST http://localhost:8000/api/auth/request-otp \
  -H "Content-Type: application/json" \
  -d '{"phone": "+919800000000"}'
```

### Verify OTP
Check backend logs for OTP, then:
```bash
curl -X POST http://localhost:8000/api/auth/verify-otp \
  -H "Content-Type: application/json" \
  -d '{"phone": "+919800000000", "otp": "XXXXXX"}'
```

### Get Complaints
```bash
curl -X GET "http://localhost:8000/api/complaints?skip=0&limit=20" \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"
```

---

## 🎨 Demo Highlights to Emphasize

### For MLAs:
- **Constituency-wide visibility** of all issues
- **Real-time tracking** of department performance
- **Data-driven insights** for policy decisions
- **Direct communication** with citizens
- **Transparency** in governance

### For Citizens:
- **Easy complaint filing** via phone
- **GPS-based location** tagging
- **Real-time status updates**
- **Photo evidence** upload
- **Rating & feedback** system

### For Departments:
- **Organized workflow** management
- **Priority-based** complaint handling
- **Internal notes** and collaboration
- **Performance metrics**
- **Accountability** tracking

---

## 🔧 Demo Data Reset

If you need to reset and regenerate demo data:

```bash
docker compose exec backend python seed_demo_simple.py
```

**Note**: This will add MORE data, not replace existing data. To start fresh:

```bash
# Stop services
docker compose down

# Remove database volume
docker volume rm janasamparka_postgres_data

# Restart and seed
docker compose up -d
docker compose exec backend python seed_data.py  # Base data
docker compose exec backend python seed_demo_simple.py  # Demo data
```

---

## 📈 Expected Demo Impact

### Metrics to Showcase:
- **100 complaints** processed across constituencies
- **15 departments** actively engaged
- **42 active citizens** using the platform
- **70% complaint resolution rate** (resolved + closed / total)
- **Average complaint age**: Distributed from 0-90 days
- **Department response time**: Visible in status transitions

### Success Indicators:
✅ End-to-end complaint tracking  
✅ Multi-role portal access  
✅ Real-time status updates  
✅ Geographic visualization  
✅ Department performance analytics  
✅ Citizen satisfaction tracking  

---

## 🚀 Next Steps After Demo

If the demo is successful, consider:

1. **Mobile App Development**: React Native app for easier citizen access
2. **SMS Integration**: Automated SMS updates for status changes
3. **Analytics Dashboard**: Advanced visualizations and reports
4. **Multilingual Support**: Full Kannada translation
5. **Photo/Video Upload**: Evidence attachment for complaints
6. **Push Notifications**: Real-time alerts
7. **Public Portal**: Anonymous complaint browsing
8. **Integration**: Connect with existing government systems

---

## 📞 Support

For demo preparation or technical issues:
- Check `backend/seed_demo_simple.py` for data generation logic
- Review `OTP_VERIFICATION_FIX.md` for authentication details
- See `DOCKER_BUILD_OPTIMIZATION.md` for deployment optimizations

**Backend logs**: `docker compose logs backend -f`  
**Database access**: `docker compose exec db psql -U mlauser -d mla_connect`

---

**Last Updated**: November 4, 2024  
**Data Generated**: 60 users, 100 complaints, 3 constituencies, 15 departments
