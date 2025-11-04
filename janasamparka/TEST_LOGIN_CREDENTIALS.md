# 🔑 TEST LOGIN CREDENTIALS

## Overview

This document contains all test login credentials for the MLA Janasamparka Connect system. All test accounts use **OTP: 123456** for authentication.

---

## 📱 Quick Reference

| Role | Count | Description |
|------|-------|-------------|
| **Admin** | 1 | Super admin with access to all constituencies |
| **MLA** | 3 | One per constituency (Puttur, Mangalore North, Udupi) |
| **Moderator** | 6 | Two per constituency |
| **Department Officer** | 9 | Three per constituency (PWD, Water, MESCOM) |
| **Auditor** | 3 | One per constituency |
| **Citizen** | 6 | Two per constituency |
| **TOTAL** | **28** | Comprehensive role coverage |

---

## 🔐 Authentication

### Request OTP
```bash
POST /api/v1/auth/request-otp
Content-Type: application/json

{
  "phone": "+919999999999"
}
```

### Verify OTP
```bash
POST /api/v1/auth/verify-otp
Content-Type: application/json

{
  "phone": "+919999999999",
  "otp": "123456"
}
```

**Response:**
```json
{
  "access_token": "eyJ0eXAiOiJKV1QiLCJhbGc...",
  "token_type": "bearer",
  "user": {
    "id": "uuid",
    "name": "System Administrator",
    "phone": "+919999999999",
    "role": "admin"
  }
}
```

---

## 👔 SYSTEM ADMIN

### Admin User
- **Phone:** `+919999999999`
- **Name:** System Administrator
- **Role:** `admin`
- **Constituency:** All (no restriction)
- **Access:** Can view and manage all constituencies
- **Use Case:** System administration, cross-constituency reports

**Test Scenarios:**
- ✅ View complaints from all constituencies
- ✅ Access analytics across all regions
- ✅ Manage system-wide settings
- ✅ Generate consolidated reports

---

## 📍 PUTTUR CONSTITUENCY

### MLA
- **Phone:** `+918242226666`
- **Name:** Ashok Kumar Rai
- **Party:** Indian National Congress
- **Role:** `mla`
- **Email:** ashok.rai@karnataka.gov.in

**Test Scenarios:**
- ✅ View Puttur constituency dashboard
- ✅ Review complaint analytics for Puttur
- ✅ Monitor department performance
- ✅ Access budget information

---

### Moderators

#### Moderator 1
- **Phone:** `+918242226001`
- **Name:** Puttur Moderator 1
- **Role:** `moderator`

**Test Scenarios:**
- ✅ Review and approve citizen complaints
- ✅ Assign complaints to departments
- ✅ Update complaint status
- ✅ Moderate citizen feedback

#### Moderator 2
- **Phone:** `+918242226002`
- **Name:** Puttur Moderator 2
- **Role:** `moderator`

---

### Department Officers

#### PWD Officer
- **Phone:** `+918242226101`
- **Name:** PWD Officer - Puttur
- **Role:** `department_officer`
- **Department:** Public Works Department

**Test Scenarios:**
- ✅ View assigned road/infrastructure complaints
- ✅ Update work progress
- ✅ Upload completion photos
- ✅ Mark complaints as resolved

#### Water Supply Officer
- **Phone:** `+918242226102`
- **Name:** Water Officer - Puttur
- **Role:** `department_officer`
- **Department:** Water Supply & Drainage

**Test Scenarios:**
- ✅ View water-related complaints
- ✅ Respond to drainage issues
- ✅ Update work status

#### Electricity Officer
- **Phone:** `+918242226103`
- **Name:** MESCOM Officer - Puttur
- **Role:** `department_officer`
- **Department:** MESCOM

**Test Scenarios:**
- ✅ View electricity complaints
- ✅ Coordinate power outage responses
- ✅ Update resolution status

---

### Auditor
- **Phone:** `+918242226201`
- **Name:** Audit Officer - Puttur
- **Role:** `auditor`

**Test Scenarios:**
- ✅ Review complaint processing timelines
- ✅ Audit budget utilization
- ✅ Generate compliance reports
- ✅ Monitor SLA adherence

---

### Citizens

#### Citizen 1
- **Phone:** `+918242226301`
- **Name:** Citizen - Puttur Ward 1
- **Role:** `citizen`
- **Ward:** Ward 1 - Market Area

**Test Scenarios:**
- ✅ Submit new complaints
- ✅ Upload photos/videos
- ✅ Track complaint status
- ✅ Rate MLA performance
- ✅ Provide feedback

#### Citizen 2
- **Phone:** `+918242226302`
- **Name:** Citizen - Puttur Ward 2
- **Role:** `citizen`
- **Ward:** Ward 2 - Bus Stand

---

## 📍 MANGALORE NORTH CONSTITUENCY

### MLA
- **Phone:** `+918242227777`
- **Name:** B.A. Mohiuddin Bava
- **Party:** Indian National Congress
- **Role:** `mla`
- **Email:** bava@karnataka.gov.in
- **Assembly Number:** 129

**Test Scenarios:**
- ✅ View Mangalore North constituency dashboard
- ✅ Monitor 45 wards
- ✅ Review analytics for 180,000 population
- ✅ Access seasonal forecasts

---

### Moderators

#### Moderator 1
- **Phone:** `+918242227001`
- **Name:** Mangalore Moderator 1
- **Role:** `moderator`

#### Moderator 2
- **Phone:** `+918242227002`
- **Name:** Mangalore Moderator 2
- **Role:** `moderator`

---

### Department Officers

#### PWD Officer
- **Phone:** `+918242227101`
- **Name:** PWD Officer - Mangalore
- **Role:** `department_officer`

#### Water Supply Officer
- **Phone:** `+918242227102`
- **Name:** Water Officer - Mangalore
- **Role:** `department_officer`

#### Electricity Officer
- **Phone:** `+918242227103`
- **Name:** MESCOM Officer - Mangalore
- **Role:** `department_officer`

---

### Auditor
- **Phone:** `+918242227201`
- **Name:** Audit Officer - Mangalore
- **Role:** `auditor`

---

### Citizens

#### Citizen 1
- **Phone:** `+918242227301`
- **Name:** Citizen - Mangalore Kadri
- **Role:** `citizen`
- **Ward:** Ward 1 - Kadri

#### Citizen 2
- **Phone:** `+918242227302`
- **Name:** Citizen - Mangalore Pandeshwar
- **Role:** `citizen`
- **Ward:** Ward 2 - Pandeshwar

---

## 📍 UDUPI CONSTITUENCY

### MLA
- **Phone:** `+918252255555`
- **Name:** Yashpal A. Suvarna
- **Party:** Bharatiya Janata Party
- **Role:** `mla`
- **Email:** yashpal.suvarna@karnataka.gov.in
- **Assembly Number:** 156

**Test Scenarios:**
- ✅ View Udupi constituency dashboard
- ✅ Monitor temple area complaints
- ✅ Review educational institution issues
- ✅ Coastal area specific concerns

---

### Moderators

#### Moderator 1
- **Phone:** `+918252255001`
- **Name:** Udupi Moderator 1
- **Role:** `moderator`

#### Moderator 2
- **Phone:** `+918252255002`
- **Name:** Udupi Moderator 2
- **Role:** `moderator`

---

### Department Officers

#### PWD Officer
- **Phone:** `+918252255101`
- **Name:** PWD Officer - Udupi
- **Role:** `department_officer`

#### Water Supply Officer
- **Phone:** `+918252255102`
- **Name:** Water Officer - Udupi
- **Role:** `department_officer`

#### Electricity Officer
- **Phone:** `+918252255103`
- **Name:** MESCOM Officer - Udupi
- **Role:** `department_officer`

---

### Auditor
- **Phone:** `+918252255201`
- **Name:** Audit Officer - Udupi
- **Role:** `auditor`

---

### Citizens

#### Citizen 1
- **Phone:** `+918252255301`
- **Name:** Citizen - Udupi Car Street
- **Role:** `citizen`
- **Ward:** Ward 1 - Car Street

#### Citizen 2
- **Phone:** `+918252255302`
- **Name:** Citizen - Udupi Temple Area
- **Role:** `citizen`
- **Ward:** Ward 2 - Temple Area

---

## 🔒 Role Permissions

### Admin
- ✅ View all constituencies
- ✅ Manage system settings
- ✅ Access all reports
- ✅ User management
- ✅ Budget oversight across constituencies

### MLA
- ✅ View constituency dashboard
- ✅ Review all complaints
- ✅ Access analytics & forecasts
- ✅ Monitor department performance
- ✅ View budget information
- ✅ Generate reports

### Moderator
- ✅ Review complaints
- ✅ Assign to departments
- ✅ Update complaint status
- ✅ Moderate citizen feedback
- ✅ Basic analytics

### Department Officer
- ✅ View assigned complaints (by category)
- ✅ Update work status
- ✅ Upload completion photos
- ✅ Mark resolved
- ✅ Add internal notes

### Auditor
- ✅ View all complaints (read-only)
- ✅ Access budget reports
- ✅ Generate audit trails
- ✅ Monitor SLA compliance
- ✅ Export data

### Citizen
- ✅ Submit complaints
- ✅ Upload media
- ✅ Track own complaints
- ✅ Rate MLA
- ✅ Provide feedback
- ❌ View other citizens' complaints

---

## 🧪 Testing Multi-Tenancy

### Test Case 1: Constituency Isolation
1. Login as **Puttur Moderator** (+918242226001)
2. Try to view complaints - should only see Puttur data
3. Login as **Mangalore Moderator** (+918242227001)
4. Verify different data set (Mangalore only)

### Test Case 2: Admin Cross-Access
1. Login as **Admin** (+919999999999)
2. View complaints - should see ALL constituencies
3. Switch constituency filter in dashboard
4. Verify access to all 3 constituencies

### Test Case 3: Department Filtering
1. Login as **PWD Officer - Puttur** (+918242226101)
2. Should see only road/infrastructure complaints
3. Login as **Water Officer - Puttur** (+918242226102)
4. Should see only water-related complaints

### Test Case 4: Citizen Privacy
1. Login as **Citizen 1** (+918242226301)
2. Submit a complaint
3. Login as **Citizen 2** (+918242226302)
4. Verify cannot view Citizen 1's complaint

---

## 📊 Quick Start Testing Guide

### Step 1: Start Backend
```bash
cd backend
.venv/bin/python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### Step 2: Test Authentication
```bash
curl -X POST http://localhost:8000/api/v1/auth/request-otp \
  -H "Content-Type: application/json" \
  -d '{"phone": "+919999999999"}'

curl -X POST http://localhost:8000/api/v1/auth/verify-otp \
  -H "Content-Type: application/json" \
  -d '{"phone": "+919999999999", "otp": "123456"}'
```

### Step 3: Make Authenticated Request
```bash
curl -X GET http://localhost:8000/api/v1/complaints \
  -H "Authorization: Bearer YOUR_TOKEN_HERE"
```

### Step 4: Test Different Roles
Repeat Steps 2-3 with different phone numbers to test role-based access control.

---

## 🔧 Troubleshooting

### Issue: User not found
**Solution:** Run `python create_all_test_users.py` to create all test users

### Issue: OTP not working
**Solution:** Development OTP is hardcoded as `123456` in auth service

### Issue: Permission denied
**Solution:** Check user role matches required permission for endpoint

### Issue: No data visible
**Solution:** Verify user's constituency_id matches data. Admin can see all.

---

## 📝 Notes

- **Development OTP:** Always `123456` for all users
- **Phone Format:** Must include country code (+91)
- **Token Expiry:** JWT tokens expire after 7 days
- **Multi-tenancy:** Enforced at database query level via middleware
- **Admin Override:** Admin users bypass constituency filtering

---

**Last Updated:** October 30, 2025  
**Total Test Users:** 28  
**Constituencies:** 3 (Puttur, Mangalore North, Udupi)  
**Role Distribution:** 1 Admin, 3 MLAs, 6 Moderators, 9 Officers, 3 Auditors, 6 Citizens
