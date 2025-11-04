# EXIF GPS Location Capture Implementation

## Problem Statement

**Issue**: When citizens submit complaints with photos taken earlier at the problem location, but submit the complaint from home later, the location is captured from where they submit (home), not where the photo was taken (actual problem site).

**Result**: Inaccurate complaint mapping and misplaced markers on the map.

---

## Solution Implemented

### **Approach**: EXIF Metadata GPS Extraction

Automatically extract GPS coordinates from photo EXIF metadata as the **primary** location source, with manual GPS capture as fallback.

---

## Changes Made

### 1. Mobile App (`mobile-app/app/(tabs)/submit.js`)

#### Added Helper Functions

```javascript
// Convert EXIF GPS coordinates from DMS to decimal degrees
const convertExifToDecimal = (coordinate, ref) => {
  const degrees = coordinate[0];
  const minutes = coordinate[1];
  const seconds = coordinate[2];
  
  let decimal = degrees + minutes / 60 + seconds / 3600;
  
  if (ref === 'S' || ref === 'W') {
    decimal = -decimal;
  }
  
  return decimal;
};

// Extract GPS from EXIF data
const extractGPSFromExif = (exif) => {
  if (!exif) return null;
  
  const latitude = convertExifToDecimal(exif.GPSLatitude, exif.GPSLatitudeRef);
  const longitude = convertExifToDecimal(exif.GPSLongitude, exif.GPSLongitudeRef);
  
  if (latitude !== null && longitude !== null) {
    return { latitude, longitude };
  }
  
  return null;
};
```

#### Updated Photo Capture

**Before**:
```javascript
const result = await ImagePicker.launchCameraAsync({
  mediaTypes: ImagePicker.MediaTypeOptions.Images,
  allowsEditing: true,
  quality: 0.8,
});
```

**After**:
```javascript
const result = await ImagePicker.launchCameraAsync({
  mediaTypes: ImagePicker.MediaTypeOptions.Images,
  allowsEditing: true,
  quality: 0.8,
  exif: true, // ✅ Request EXIF data
});

// Extract GPS from photo
const gpsFromExif = extractGPSFromExif(asset.exif);

if (gpsFromExif && !formData.latitude) {
  // Auto-set location from photo
  setFormData({
    ...formData,
    images: [...formData.images, asset],
    latitude: gpsFromExif.latitude,
    longitude: gpsFromExif.longitude,
  });
  setLocationSource('exif');
  Alert.alert('Photo captured with GPS location from image metadata');
}
```

#### User Experience

- **If photo has GPS**: Automatically extracts and uses it
- **If photo has GPS but location already set**: Asks user which to use
- **If photo has no GPS**: Prompts user to use "Capture Location" button
- **Shows indicator**: "Location from photo metadata" or "Location from device GPS"

---

### 2. Backend (`backend/app/routers/media.py`)

#### Import EXIF Extraction

```python
from app.core.image_processing import (
    optimize_image, 
    create_thumbnail, 
    is_image_file, 
    extract_exif_data  # ✅ Added
)
```

#### EXIF GPS Extraction During Upload

```python
# Initialize GPS variables
exif_gps_lat = None
exif_gps_lng = None

if is_image_file(file.filename):
    # Extract EXIF before optimization (optimization strips EXIF)
    exif_data = extract_exif_data(contents)
    
    if exif_data and 'gps' in exif_data:
        gps_info = exif_data['gps']
        
        # GPSInfo tag 2 = latitude, tag 4 = longitude
        if 2 in gps_info and 4 in gps_info:
            lat = gps_info[2]
            lat_ref = gps_info.get(1, 'N')
            lng = gps_info[4]
            lng_ref = gps_info.get(3, 'E')
            
            # Convert DMS to decimal
            if isinstance(lat, (list, tuple)) and len(lat) == 3:
                exif_gps_lat = float(lat[0]) + float(lat[1])/60 + float(lat[2])/3600
                if lat_ref == 'S':
                    exif_gps_lat = -exif_gps_lat
            
            if isinstance(lng, (list, tuple)) and len(lng) == 3:
                exif_gps_lng = float(lng[0]) + float(lng[1])/60 + float(lng[2])/3600
                if lng_ref == 'W':
                    exif_gps_lng = -exif_gps_lng
```

#### Store GPS with Media Record

```python
new_media = Media(
    complaint_id=complaint_id,
    url=f"/uploads/media/{unique_filename}",
    media_type=media_type,
    photo_type=photo_type,
    caption=caption,
    lat=exif_gps_lat,  # ✅ From EXIF
    lng=exif_gps_lng,  # ✅ From EXIF
)
```

#### Auto-Update Complaint Location

```python
# If first media has GPS and complaint doesn't, update complaint
if exif_gps_lat and exif_gps_lng and len(uploaded_media) == 1:
    complaint = db.query(Complaint).filter(Complaint.id == complaint_id).first()
    if complaint and (not complaint.lat or not complaint.lng):
        from decimal import Decimal
        complaint.lat = Decimal(str(exif_gps_lat))
        complaint.lng = Decimal(str(exif_gps_lng))
        print(f"Updated complaint {complaint_id} with GPS from photo EXIF")
```

---

## Technical Details

### EXIF GPS Data Format

- **GPSLatitude (Tag 2)**: Array of 3 values [degrees, minutes, seconds]
- **GPSLatitudeRef (Tag 1)**: 'N' (North) or 'S' (South)
- **GPSLongitude (Tag 4)**: Array of 3 values [degrees, minutes, seconds]
- **GPSLongitudeRef (Tag 3)**: 'E' (East) or 'W' (West)

### Conversion Formula

```
Decimal Degrees = Degrees + (Minutes / 60) + (Seconds / 3600)

If hemisphere is South or West, multiply by -1
```

### Example

```
Photo EXIF:
  GPSLatitude: [12, 45, 33.48]  (12°45'33.48")
  GPSLatitudeRef: N
  GPSLongitude: [75, 12, 41.04]  (75°12'41.04")
  GPSLongitudeRef: E

Converts to:
  Latitude: 12.7593 (12 + 45/60 + 33.48/3600)
  Longitude: 75.2114 (75 + 12/60 + 41.04/3600)
```

---

## Location Priority Logic

### Mobile App

1. **Photo with EXIF GPS** (First Priority)
   - If photo has GPS and no location set → Auto-use EXIF GPS
   - If photo has GPS but location already set → Ask user

2. **Manual GPS Capture** (Fallback)
   - User presses "Capture Location" button
   - Gets current device GPS

3. **Validation**
   - Complaint cannot be submitted without location
   - Shows clear indicator of location source

### Backend

1. **Media Upload**: Extract EXIF GPS from each photo
2. **Store**: Save GPS with media record (`media.lat`, `media.lng`)
3. **Update Complaint**: If complaint has no GPS but first photo does → auto-update complaint

---

## Benefits

✅ **Accurate Location**: Complaint marked at actual problem site, not where citizen submits from
✅ **Automatic**: No manual coordination needed - works transparently
✅ **Backwards Compatible**: Falls back to manual GPS if photo has no EXIF
✅ **User Control**: User can override if needed
✅ **Timestamp Aware**: Could add validation (photo date vs submission date)

---

## Future Enhancements

### 1. **Timestamp Validation**
```javascript
// Warn if photo is old
const photoDate = new Date(asset.exif?.DateTime);
const daysSincePhoto = (Date.now() - photoDate) / (1000 * 60 * 60 * 24);

if (daysSincePhoto > 7) {
  Alert.alert('Old Photo', 'This photo was taken over a week ago. Is the issue still present?');
}
```

### 2. **Multiple Photos - Average GPS**
```javascript
// If multiple photos with different GPS, use average or first
const avgLat = photos.reduce((sum, p) => sum + p.exif.lat, 0) / photos.length;
const avgLng = photos.reduce((sum, p) => sum + p.exif.lng, 0) / photos.length;
```

### 3. **GPS Accuracy Indicator**
```javascript
// EXIF includes HDOP (Horizontal Dilution of Precision)
if (asset.exif?.GPSDOP) {
  const accuracy = asset.exif.GPSDOP < 5 ? 'High' : 'Medium';
  showAccuracyIndicator(accuracy);
}
```

### 4. **Offline Support**
- Store photos with EXIF locally
- Extract GPS when online
- Submit with accurate location even if delayed

---

## Testing Checklist

### Mobile App Testing

- [ ] Take photo at location A, submit from location A → Uses EXIF GPS
- [ ] Take photo at location A, move to location B, submit → Uses EXIF GPS from location A
- [ ] Take photo without GPS enabled → Prompts for manual capture
- [ ] Select old photo from gallery with EXIF → Extracts GPS correctly
- [ ] Take photo, then manually capture GPS → Asks which to use
- [ ] Submit complaint → Shows correct location indicator

### Backend Testing

- [ ] Upload photo with EXIF GPS → Media record has lat/lng
- [ ] Upload photo without EXIF → Media record lat/lng is null
- [ ] First photo has GPS, complaint doesn't → Complaint updated
- [ ] First photo has GPS, complaint already has GPS → Complaint not updated
- [ ] Multiple photos → Each has own GPS stored

### Integration Testing

- [ ] Submit complaint with EXIF GPS → Shows on map correctly
- [ ] Submit complaint with manual GPS → Shows on map correctly
- [ ] View complaint details → Shows location source
- [ ] Filter by constituency → Shows only relevant complaints

---

## Deployment Notes

### Mobile App
1. Update `mobile-app/app/(tabs)/submit.js`
2. Test with different phone models (iOS/Android handle EXIF differently)
3. Ensure camera permissions include location access

### Backend
1. Update `backend/app/routers/media.py`
2. Restart backend service
3. Verify PIL/Pillow is installed (already in requirements.txt)

### No Database Changes Required
- `media` table already has `lat` and `lng` columns
- `complaints` table already has `lat` and `lng` columns
- No migrations needed ✅

---

## Commands to Test

### 1. Test Mobile App
```bash
cd mobile-app
npx expo start
```

### 2. Test Backend
```bash
# Check if running
docker ps | grep janasamparka_backend

# Restart backend with new code
docker restart janasamparka_backend

# Check logs
docker logs -f janasamparka_backend
```

### 3. Test EXIF Extraction (Python)
```python
from PIL import Image
img = Image.open('test_photo.jpg')
exif = img._getexif()
print(exif.get(34853))  # GPS info
```

---

## Summary

This implementation solves the critical issue of location accuracy by:

1. **Mobile App**: Automatically extracts GPS from photo EXIF data
2. **Backend**: Stores GPS with each media item and updates complaint if needed
3. **User Experience**: Transparent operation with fallback to manual GPS

**Result**: Complaints are now accurately geotagged to the actual problem location, regardless of where/when the citizen submits the complaint.

---

**Status**: ✅ **Implementation Complete**
**Testing**: 🟡 **Pending Manual Testing**
**Documentation**: ✅ **Complete**
