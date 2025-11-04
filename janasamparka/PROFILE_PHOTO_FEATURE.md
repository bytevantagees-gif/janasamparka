# User Profile Photo Upload Feature

## ✅ Implementation Complete

### Database Changes
1. **Added `profile_photo` column to users table**
   - Type: `VARCHAR(500)`
   - Nullable: Yes
   - Stores relative URL path: `/uploads/profile_photos/{uuid}.{ext}`

2. **All tables now in Docker database**
   - Database: `janasamparka_db` in Docker container
   - 17 tables confirmed: users, complaints, constituencies, departments, wards, polls, media, status_logs, case_notes, complaint_escalations, department_routing, budget_transactions, ward_budgets, department_budgets, faq_solutions, poll_options, votes
   - No external PostgreSQL dependencies

### Backend API Endpoints

#### 1. Upload Profile Photo
**Endpoint:** `POST /api/auth/me/profile-photo`

**Headers:**
```
Authorization: Bearer {access_token}
Content-Type: multipart/form-data
```

**Request Body:**
```
file: (binary image file)
```

**Validations:**
- File type: JPEG, JPG, PNG, GIF, WEBP only
- Max size: 5MB
- Authenticated user required

**Response:**
```json
{
  "id": "uuid",
  "name": "User Name",
  "phone": "+919999999999",
  "role": "citizen",
  "locale_pref": "kn",
  "profile_photo": "/uploads/profile_photos/abc123.jpg",
  "constituency_id": "uuid",
  "is_active": "true",
  "created_at": "2025-10-30T...",
  "updated_at": "2025-10-30T..."
}
```

**Features:**
- Generates unique UUID-based filename
- Deletes old profile photo on new upload
- Creates `/uploads/profile_photos/` directory automatically
- Returns updated user object

#### 2. Update User Profile
**Endpoint:** `PUT /api/auth/me`

**Headers:**
```
Authorization: Bearer {access_token}
Content-Type: application/json
```

**Request Body:**
```json
{
  "name": "Updated Name",
  "locale_pref": "en",
  "profile_photo": "/uploads/profile_photos/new.jpg"
}
```

**Note:** All fields optional - only send fields you want to update

### Frontend Implementation

#### 1. Settings Page (`/settings`)
**Location:** `admin-dashboard/src/pages/Settings.jsx`

**Features:**
- Profile photo preview (24x24 circular avatar)
- Camera icon overlay for quick upload
- "Upload Photo" button with file picker
- Real-time preview on file selection
- Shows loading spinner during upload
- File validation (type & size)
- Success/error alerts

**UI Components:**
- Large circular avatar (96x96) with ring border
- Fallback to User icon if no photo
- Camera icon button (absolute positioned)
- File input (hidden, triggered by buttons)
- Upload button with Upload icon

**Upload Flow:**
1. User clicks camera icon or "Upload Photo" button
2. File picker opens (accepts images only)
3. Frontend validates file size (<5MB)
4. Shows preview immediately
5. Uploads to API via FormData
6. Updates user context on success
7. Displays success/error message

#### 2. Dashboard Page (`/`)
**Location:** `admin-dashboard/src/pages/Dashboard.jsx`

**Features:**
- Profile photo in "Mission Ready" banner
- Displays next to welcome message
- Size: 48x48 circular with white ring
- Falls back to User icon if no photo

**Location:**
```jsx
<h1>
  <img src={profile_photo} /> 
  Welcome back, {name} — ...
</h1>
```

#### 3. Layout Component (Top Navigation)
**Location:** `admin-dashboard/src/components/Layout.jsx`

**Features:**
- Profile photo in top-right corner
- Circular avatar (40x40)
- Falls back to UI-Avatars with user initials
- Consistent across all pages

**Implementation:**
```jsx
const profilePhotoUrl = useMemo(() => {
  if (user?.profile_photo) {
    return `${API_URL}${user.profile_photo}`;
  }
  return `https://ui-avatars.com/api/?background=2563eb&color=fff&name=${user.name}`;
}, [user?.profile_photo, user?.name]);
```

### File Storage

**Directory Structure:**
```
janasamparka/
  backend/
    uploads/
      media/              # Complaint media files
      profile_photos/     # User profile photos ✨ NEW
```

**Backend Static File Serving:**
```python
app.mount("/uploads", StaticFiles(directory="uploads"), name="uploads")
```

**Access URL:**
```
http://localhost:8000/uploads/profile_photos/abc123.jpg
```

### Configuration Updates

**backend/app/core/config.py:**
```python
# Database (Docker defaults - override in .env for local development)
DATABASE_URL: str = "postgresql://janasamparka:janasamparka123@db:5432/janasamparka_db"
POSTGRES_SERVER: str = "db"  # Docker service name
```

**backend/.env:**
```env
DATABASE_URL=postgresql://janasamparka:janasamparka123@localhost:5433/janasamparka_db
# localhost:5433 maps to Docker container db:5432
```

### Docker Setup

**All database operations within Docker:**
- Container: `janasamparka_db`
- Image: `postgis/postgis:15-3.3`
- Port mapping: `5433:5432` (host:container)
- Database: `janasamparka_db`
- No external PostgreSQL required

**Verify:**
```bash
docker-compose ps
docker-compose exec db psql -U janasamparka -d janasamparka_db -c "\d users" | grep profile_photo
```

## Testing the Feature

### 1. Backend API Test
```bash
# Login first to get token
curl -X POST http://localhost:8000/api/auth/request-otp \
  -H "Content-Type: application/json" \
  -d '{"phone": "+919999999999"}'

curl -X POST http://localhost:8000/api/auth/verify-otp \
  -H "Content-Type: application/json" \
  -d '{"phone": "+919999999999", "otp": "123456"}'

# Upload profile photo
curl -X POST http://localhost:8000/api/auth/me/profile-photo \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN" \
  -F "file=@/path/to/photo.jpg"

# Get current user (verify profile_photo field)
curl -X GET http://localhost:8000/api/auth/me \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"
```

### 2. Frontend Test
1. Open http://localhost:3000
2. Login with test account
3. Navigate to Settings page
4. Click camera icon or "Upload Photo" button
5. Select an image file
6. Verify upload success message
7. Navigate to Dashboard
8. Verify profile photo appears in:
   - Mission Ready banner (next to welcome message)
   - Top-right navigation (circular avatar)

### 3. Database Verification
```bash
docker-compose exec db psql -U janasamparka -d janasamparka_db \
  -c "SELECT id, name, phone, profile_photo FROM users WHERE profile_photo IS NOT NULL;"
```

## Features & Validations

### Frontend Validations
- ✅ File type: Only image/* MIME types
- ✅ File size: Maximum 5MB
- ✅ Preview before upload
- ✅ Loading state during upload
- ✅ Error handling with alerts

### Backend Validations
- ✅ File type: JPEG, JPG, PNG, GIF, WEBP only
- ✅ File size: Maximum 5MB (checked via file.file.tell())
- ✅ Authentication required
- ✅ Unique filename generation (UUID)
- ✅ Old photo deletion on new upload

### Security
- ✅ JWT authentication required for all photo operations
- ✅ Users can only upload/update their own photos
- ✅ File type validation prevents malicious uploads
- ✅ File size limit prevents DoS attacks
- ✅ Unique filenames prevent overwrites

## File Structure Summary

```
backend/
  app/
    routers/
      auth.py                 # Added profile photo endpoints
    models/
      user.py                # Added profile_photo field
    schemas/
      user.py                # Added profile_photo to UserResponse & UserUpdate
    core/
      config.py              # Updated DATABASE_URL defaults to Docker
    main.py                  # Added profile_photos directory creation
  uploads/
    profile_photos/          # Photo storage directory

admin-dashboard/
  src/
    pages/
      Settings.jsx           # Profile photo upload UI
      Dashboard.jsx          # Profile photo in Mission Ready banner
    components/
      Layout.jsx            # Profile photo in top-right navigation
```

## Next Steps

### Recommended Enhancements
1. **Image Optimization**
   - Resize images to standard sizes (200x200, 400x400)
   - Convert to WebP for better compression
   - Generate thumbnails for different contexts

2. **CDN Integration**
   - Upload photos to S3/Cloud Storage
   - Serve via CDN for better performance
   - Implement signed URLs for security

3. **Image Cropping**
   - Add cropping tool in frontend
   - Allow users to adjust photo before upload
   - Ensure circular crop matches avatar display

4. **Profile Completion**
   - Show profile completion percentage
   - Encourage users to upload photos
   - Add achievement/gamification

## Troubleshooting

### Profile photo not displaying
1. Check backend logs: `docker-compose logs backend`
2. Verify file exists: `docker-compose exec backend ls -la /app/uploads/profile_photos/`
3. Check API response includes profile_photo field
4. Verify frontend constructs correct URL with API base URL

### Upload fails with 413 (Payload Too Large)
- File exceeds 5MB limit
- Check file size before upload
- Consider compressing image

### Upload fails with 400 (Bad Request)
- Invalid file type (not an image)
- Check file MIME type
- Ensure file is JPEG, PNG, or GIF

### Database connection issues
- Verify Docker containers running: `docker-compose ps`
- Check .env file DATABASE_URL
- Restart containers: `docker-compose restart backend db`

## Documentation

- API Docs: http://localhost:8000/docs (Swagger UI)
- ReDoc: http://localhost:8000/redoc
- Test with Swagger: Click "Try it out" on POST /api/auth/me/profile-photo

---

## Summary

✅ **Database:** All tables in Docker (janasamparka_db), no external dependencies  
✅ **Backend:** Profile photo upload API with validation & file storage  
✅ **Frontend:** Upload UI in Settings, display in Dashboard & Layout  
✅ **Docker:** Full containerization, proper port mapping  
✅ **Testing:** All components tested and verified

**Status:** 🎉 **Feature Complete & Production Ready**
