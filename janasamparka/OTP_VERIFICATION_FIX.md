# OTP Verification Fix Summary

## Issues Fixed

### 1. ❌ **Backend Crash - Missing Monitoring Packages**
**Error:** `ModuleNotFoundError: No module named 'pythonjsonlogger'`

**Root Cause:** Backend code imports monitoring/logging packages that weren't in requirements.txt

**Solution:** Added missing packages to `backend/requirements.txt`:
```python
python-json-logger==4.0.0  # JSON logging support
prometheus-client==0.23.1  # Prometheus metrics
opentelemetry-api==1.38.0  # OpenTelemetry API
opentelemetry-sdk==1.38.0  # OpenTelemetry SDK
```

### 2. ❌ **OTP Verification Schema Mismatch**
**Error:** `pydantic_core.ValidationError: is_active - Input should be a valid string [type=string_type, input_value=True, input_type=bool]`

**Root Cause:** UserResponse schema defined `is_active` as `str` but database stores it as `bool`

**Solution:** Fixed `backend/app/schemas/user.py` line 39:
```python
# Before:
is_active: str

# After:
is_active: bool
```

### 3. ⚠️ **Frontend API Path Mismatch**
**Issue:** Frontend was calling `/api/v1/auth/*` but backend routes are at `/api/auth/*`

**Backend Routes:**
- ✅ `/api/auth/request-otp` - Request OTP
- ✅ `/api/auth/verify-otp` - Verify OTP
- ✅ `/api/auth/refresh` - Refresh token
- ✅ `/api/auth/me` - Get current user

**Action Required:** Update frontend to use correct API paths (without `/v1`)

## Verification Tests

### ✅ Test 1: Request OTP
```bash
curl -X POST http://localhost:8000/api/auth/request-otp \
  -H "Content-Type: application/json" \
  -d '{"phone": "+918242226666"}'
```

**Result:**
```json
{
  "message": "OTP sent successfully",
  "phone": "+918242226666",
  "otp": "314268",
  "expires_in_minutes": 5
}
```

### ✅ Test 2: Verify OTP
```bash
curl -X POST http://localhost:8000/api/auth/verify-otp \
  -H "Content-Type: application/json" \
  -d '{
    "phone": "+918242226666",
    "otp": "314268"
  }'
```

**Result:**
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer",
  "user": {
    "name": "Ashok Kumar Rai",
    "phone": "+918242226666",
    "locale_pref": "kn",
    "id": "76360541-ca87-4581-adc2-ce2cf2f43584",
    "role": "mla",
    "constituency_id": "f534fd68-b380-47dd-bb26-8d8dd48badbf",
    "ward_id": null,
    "is_active": true,
    "profile_photo": null,
    "created_at": "2025-11-04T10:32:45.978121",
    "updated_at": "2025-11-04T10:32:45.978126"
  }
}
```

## Test Users (From Seed Data)

| Name | Phone | Role | Constituency |
|------|-------|------|--------------|
| Ashok Kumar Rai | +918242226666 | MLA | Puttur |
| Mohiuddin Bava | +918242227777 | MLA | Mangalore North |
| K Raghupati Bhat | +918252255555 | MLA | Udupi |
| Admin User | +919999999999 | Admin | Puttur |

## Backend Status

✅ **All containers running:**
```
NAME                   STATUS              PORTS
janasamparka_backend   Up 10 minutes       0.0.0.0:8000->8000/tcp
janasamparka_db        Up 10 minutes       0.0.0.0:5433->5432/tcp
janasamparka_frontend  Up 10 minutes       0.0.0.0:3000->3000/tcp
```

✅ **Backend logs show:**
```
INFO:     Application startup complete.
Metrics collection initialized
```

## Next Steps for Frontend

1. **Update API base URL configuration:**
   - Change from: `http://localhost:8000/api/v1/auth`
   - Change to: `http://localhost:8000/api/auth`

2. **Test OTP flow in browser:**
   - Go to http://localhost:3000/login
   - Enter phone: `+918242226666`
   - Request OTP (check backend logs for OTP code in dev mode)
   - Enter OTP code
   - Should receive access token and be logged in

3. **Update all API endpoints:**
   - Remove `/v1` from all API calls
   - Use `/api/auth/`, `/api/complaints/`, `/api/users/`, etc.

## Files Modified

1. ✅ `backend/requirements.txt` - Added monitoring packages
2. ✅ `backend/app/schemas/user.py` - Fixed `is_active` type
3. ✅ `backend/Dockerfile` - Optimized for BuildKit caching
4. ✅ `rebuild-backend-fast.sh` - Created fast rebuild script

## Development Notes

- **OTP in Development Mode:** OTP is printed in backend logs (not sent via SMS)
- **Token Expiry:** Access token: 30 days, Refresh token: 60 days
- **API Documentation:** http://localhost:8000/docs (Swagger UI)
- **Database:** PostgreSQL+PostGIS on port 5433

## Troubleshooting

### Backend not responding?
```bash
docker compose logs backend --tail 50
```

### Need to restart backend?
```bash
docker compose restart backend
```

### Check if OTP was generated?
```bash
docker compose logs backend | grep -i otp
```

### Database connection issues?
```bash
docker compose exec db psql -U janasamparka -d janasamparka -c "SELECT count(*) FROM users;"
```
