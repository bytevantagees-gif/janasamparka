# 🔑 QUICK TEST LOGIN REFERENCE

**OTP for all users: `123456`**

---

## 📋 QUICK ACCESS

| Role | Phone | Name | Constituency |
|------|-------|------|--------------|
| 👑 **Admin** | `+919999999999` | System Administrator | All |
| 👔 **MLA** | `+918242226666` | Ashok Kumar Rai | Puttur |
| 👔 **MLA** | `+918242227777` | B.A. Mohiuddin Bava | Mangalore North |
| 👔 **MLA** | `+918252255555` | Yashpal A. Suvarna | Udupi |

---

## 🏛️ PUTTUR USERS

| Role | Phone |
|------|-------|
| 🛡️ Moderator 1 | `+918242226001` |
| 🛡️ Moderator 2 | `+918242226002` |
| 👷 PWD Officer | `+918242226101` |
| 👷 Water Officer | `+918242226102` |
| 👷 MESCOM Officer | `+918242226103` |
| 📊 Auditor | `+918242226201` |
| 👤 Citizen Ward 1 | `+918242226301` |
| 👤 Citizen Ward 2 | `+918242226302` |

---

## 🏛️ MANGALORE NORTH USERS

| Role | Phone |
|------|-------|
| 🛡️ Moderator 1 | `+918242227001` |
| 🛡️ Moderator 2 | `+918242227002` |
| 👷 PWD Officer | `+918242227101` |
| 👷 Water Officer | `+918242227102` |
| 👷 MESCOM Officer | `+918242227103` |
| 📊 Auditor | `+918242227201` |
| 👤 Citizen Kadri | `+918242227301` |
| 👤 Citizen Pandeshwar | `+918242227302` |

---

## 🏛️ UDUPI USERS

| Role | Phone |
|------|-------|
| 🛡️ Moderator 1 | `+918252255001` |
| 🛡️ Moderator 2 | `+918252255002` |
| 👷 PWD Officer | `+918252255101` |
| 👷 Water Officer | `+918252255102` |
| 👷 MESCOM Officer | `+918252255103` |
| 📊 Auditor | `+918252255201` |
| 👤 Citizen Car Street | `+918252255301` |
| 👤 Citizen Temple Area | `+918252255302` |

---

## 🔄 Quick Login

```bash
# Request OTP
curl -X POST http://localhost:8000/api/v1/auth/request-otp \
  -H "Content-Type: application/json" \
  -d '{"phone": "+919999999999"}'

# Verify OTP
curl -X POST http://localhost:8000/api/v1/auth/verify-otp \
  -H "Content-Type: application/json" \
  -d '{"phone": "+919999999999", "otp": "123456"}'
```

---

## 📊 Role Summary

- **1** Admin (all access)
- **3** MLAs (one per constituency)
- **6** Moderators (two per constituency)
- **9** Department Officers (three per constituency)
- **3** Auditors (one per constituency)
- **6** Citizens (two per constituency)

**Total: 28 test users**

---

**See [TEST_LOGIN_CREDENTIALS.md](TEST_LOGIN_CREDENTIALS.md) for detailed documentation**
