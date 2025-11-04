# Test Login Credentials

## 🔐 Login Credentials by Role

Use these phone numbers to test different user roles:

### 👨‍💼 **ADMIN**
| Name | Phone | Email | Notes |
|------|-------|-------|-------|
| Admin User | `+919999999999` | - | Primary admin account |
| System Administrator | `+919900000001` | admin@janasamparka.gov.in | Secondary admin |

**Permissions:** Full system access, all constituencies

---

### 🏛️ **MLA**
| Name | Phone | Email | Constituency |
|------|-------|-------|--------------|
| MLA Puttur | `+91991000001` | mla.puttur@janasamparka.gov.in | Puttur |
| MLA Bantwal | `+91991000002` | mla.bantwal@janasamparka.gov.in | Bantwal |
| MLA Mangalore City South | `+91991000003` | mla.mangalore.city.south@janasamparka.gov.in | Mangalore |
| Ashok Kumar Rai | `+918242226666` | mla.test@janasamparka.gov.in | Puttur |

**Permissions:** View all complaints in constituency, manage conferences, approve budgets

---

### 👮 **MODERATOR**
| Name | Phone | Email | Constituency |
|------|-------|-------|--------------|
| Rajesh Kumar | `+919876543211` | - | Puttur |
| Vijay Shetty | `+919876543224` | - | Puttur |
| Shanta Acharya | `+919876543225` | - | Puttur |

**Permissions:** Moderate complaints, approve chat messages, manage citizen engagement

---

### 👥 **CITIZENS**
| Name | Phone | Notes |
|------|-------|-------|
| Lakshmi Bhat | `+919876543214` | Regular citizen |
| Kavitha Nayak | `+919876543216` | Regular citizen |
| Harish Bhandary | `+919876543219` | Regular citizen |
| Anitha Hegde | `+919876543222` | Regular citizen |

**Permissions:** Submit complaints, participate in polls, chat in conferences

---

### 🏢 **DEPARTMENT OFFICERS**
Department officers are automatically assigned. Check database for specific credentials.

**Permissions:** Manage complaints assigned to their department

---

### 🏘️ **WARD OFFICERS**
Ward officers are automatically assigned to specific wards.

**Permissions:** Manage complaints in their ward

---

## 🧪 Testing Different Roles

### Test as ADMIN:
```
Phone: +919999999999
Password: admin123 (if using default seed)
```
**What you'll see:**
- Full dashboard with all constituencies
- All admin features
- Conference management
- Budget management

---

### Test as MLA:
```
Phone: +918242226666
Password: mla123 (if using default seed)
```
**What you'll see:**
- Constituency-specific dashboard
- Complaint management
- Video conference hosting
- Citizen engagement features

---

### Test as MODERATOR:
```
Phone: +919876543211
Password: moderator123 (if using default seed)
```
**What you'll see:**
- Moderator dashboard
- Chat moderation panel (yellow pending messages)
- Complaint review features
- Constituency-scoped data

---

### Test as CITIZEN:
```
Phone: +919876543214
Password: citizen123 (if using default seed)
```
**What you'll see:**
- Citizen dashboard with MLA achievements
- Submit complaint option
- Book video call with MLA
- Agricultural support
- My complaints

---

## ⚠️ Common Login Issues

### Issue 1: "Logged in as wrong role"
**Problem:** Using citizen phone number when trying to test moderator
**Solution:** Use the correct phone from table above

### Issue 2: "User not found"
**Problem:** Phone number not in database
**Solution:** Check if you've run all seed scripts

### Issue 3: "Multiple users with same name"
**Problem:** Seed scripts created duplicate test users
**Solution:** Use phone number, not name, to login

---

## 🔧 Verify Your Login

After logging in, check the browser console:
```javascript
console.log("User logged in:", {
  name: user.name,
  role: user.role,
  constituency_id: user.constituency_id
});
```

**Expected output for MODERATOR:**
```
User logged in: {
  name: "Rajesh Kumar",
  role: "moderator",
  constituency_id: "4eb94d2e-8ec5-48e8-b151-1928c5cad78b"
}
```

---

## 📊 Check Database

To see all available users:
```bash
docker exec janasamparka_db psql -U janasamparka -d janasamparka_db -c "SELECT name, phone, role FROM users WHERE role IN ('admin', 'mla', 'moderator') ORDER BY role, name;"
```

---

## 🐛 If Still Having Issues

1. **Clear browser cache and localStorage**
   ```javascript
   localStorage.clear();
   // Then refresh page
   ```

2. **Check backend logs**
   ```bash
   docker logs janasamparka_backend --tail 50
   ```

3. **Verify user exists**
   ```bash
   docker exec janasamparka_db psql -U janasamparka -d janasamparka_db -c "SELECT * FROM users WHERE phone = '+919876543211';"
   ```

4. **Check auth token**
   - Open browser DevTools → Application → Local Storage
   - Find `token` key
   - Decode at jwt.io to see role

---

## ✅ Quick Test Matrix

| Role | Phone | Expected Dashboard |
|------|-------|-------------------|
| Admin | +919999999999 | Full admin panel |
| MLA | +918242226666 | MLA performance dashboard |
| Moderator | +919876543211 | Moderator features + chat moderation |
| Citizen | +919876543214 | Citizen dashboard + MLA achievements |

---

**Last Updated:** Nov 1, 2025
