# Predictive Planning Implementation - Multilingual Support

## 🎯 Overview

Implemented **predictive planning** with full **Kannada and English support** to handle:
- ✅ Transliterated Kannada (raste, niru, bandi, guddi)
- ✅ Poor English grammar and spelling mistakes
- ✅ Seasonal trend predictions (monsoon, summer patterns)
- ✅ Budget forecasting
- ✅ Proactive maintenance suggestions

---

## 🗣️ Multilingual NLP Features

### **MultilingualNormalizer** (`backend/app/services/predictive_planning_service.py`)

Handles real-world Indian citizen complaints with poor language quality.

#### **Supported Kannada Transliterations**:
```python
{
    # Infrastructure
    "raste": "road",
    "bandi": "road",
    "niru": "water",
    "jala": "water",
    "bavi": "well",
    "current": "electricity",
    "light": "light",
    "gutter": "drainage",
    "kachada": "garbage",
    
    # Issues
    "guddi": "hole",
    "kodilla": "not working",
    "illa": "no",
    
    # Severity
    "bega": "urgent",
    "sikkantu": "urgent",
    
    # Locations
    "mane": "house"
}
```

#### **Common Misspelling Corrections**:
```python
{
    "watter": "water",
    "watr": "water",
    "rodd": "road",
    "rode": "road",
    "elctricity": "electricity",
    "lihgt": "light",
    "garbge": "garbage",
    "drainge": "drainage",
    "brokan": "broken",
    "urgant": "urgent",
    "emergancy": "emergency",
    "problm": "problem"
}
```

#### **Levenshtein Distance Matching**:
For severe misspellings (edit distance ≤ 2), automatically corrects to known words.

---

## 📊 Predictive Planning Features

### 1. **Seasonal Trend Prediction**

**API Endpoint**: `GET /api/v1/case-management/constituencies/{id}/seasonal-forecast?months_ahead=3`

**What it does**: Predicts complaint volumes 3-6 months ahead based on:
- Historical data (last 3 years)
- Seasonal patterns (monsoon, summer, winter)
- India-specific adjustments

**Seasonal Factors**:

**Monsoon (June-September)**:
- Drainage: **+150%** increase
- Roads: **+80%** (potholes after rain)
- Sanitation: **+50%** (garbage disposal issues)
- Water: **-20%** (sufficient water)
- Electricity: **+20%** (lightning damage)

**Summer (March-May)**:
- Water: **+100%** (shortages)
- Electricity: **+50%** (AC usage)
- Sanitation: **+20%** (faster decomposition)

**Winter/Festival Season (October-February)**:
- Streetlights: **+40%** (darker earlier)
- Roads: **+30%** (festival travel)
- Sanitation: **+30%** (festival waste)

**Response Example**:
```json
{
  "constituency_id": "uuid",
  "forecast_period": "Next 3 months",
  "predictions": [
    {
      "month": 6,
      "month_name": "June",
      "predicted_complaints": {
        "drainage": 45,
        "roads": 30,
        "water": 15
      },
      "total_predicted": 90,
      "recommendations": [
        "Clean all drainage systems before monsoon",
        "Inspect and repair roads to prevent monsoon damage",
        "Check water storage facilities"
      ]
    }
  ]
}
```

---

### 2. **Budget Forecasting**

**API Endpoint**: `GET /api/v1/case-management/constituencies/{id}/budget-forecast?months_ahead=6`

**What it does**: Forecasts budget needs based on predicted complaints and average resolution costs.

**Cost Estimates** (per complaint):
- Roads: ₹50,000
- Drainage: ₹40,000
- Water: ₹25,000
- Sanitation: ₹20,000
- Electricity: ₹15,000
- Streetlight: ₹8,000

**Response Example**:
```json
{
  "period": "Next 6 months",
  "total_budget_needed": 12500000,
  "monthly_average": 2083333,
  "by_category": {
    "roads": 5000000,
    "drainage": 3500000,
    "water": 2000000
  },
  "monthly_breakdown": [
    {
      "month": "June",
      "total_budget": 3000000,
      "by_category": {
        "drainage": 1800000,
        "roads": 900000
      }
    }
  ],
  "critical_months": ["June", "July", "August"]
}
```

**Critical Months**: Months requiring >150% of average budget.

---

### 3. **Proactive Maintenance Suggestions**

**API Endpoint**: `GET /api/v1/case-management/constituencies/{id}/proactive-maintenance`

**What it does**: Identifies recurring issues (3+ complaints in same area in last 6 months) and suggests preventive fixes.

**Response Example**:
```json
{
  "constituency_id": "uuid",
  "suggestions": [
    {
      "priority": "HIGH",
      "category": "roads",
      "location": "Near MG Road Circle",
      "coordinates": {"lat": 12.9716, "lng": 77.5946},
      "complaint_count": 7,
      "recommendation": "Schedule comprehensive road resurfacing. 7 repairs done already - permanent fix needed.",
      "estimated_cost": 140000,
      "expected_benefit": "Prevents 14 future complaints"
    }
  ],
  "total_suggestions": 15
}
```

**Cost Estimation**:
- **Reactive approach**: Fix each complaint individually
- **Preventive cost**: 40% of total reactive cost
- **Savings**: 60% reduction + prevents future issues

---

### 4. **Complaint Text Analysis**

**API Endpoint**: `POST /api/v1/case-management/analyze-complaint-text?title={title}&description={desc}`

**What it does**: Real-time NLP analysis of citizen input (Kannada/English mix).

**Input Examples**:
```
Title: "Raste mele guddi ide bega fix maadi"
Description: "Main rode near circle broken from many days urgant fix needed"
```

**Response**:
```json
{
  "original_title": "Raste mele guddi ide bega fix maadi",
  "original_description": "Main rode near circle broken from many days urgant fix needed",
  "normalized_title": "road on hole urgent fix",
  "normalized_description": "main road near circle broken from many days urgent fix needed",
  "detected_category": "roads",
  "is_urgent": true,
  "has_location_context": true,
  "language_quality": "multilingual",
  "suggested_improvements": [
    "Mention when the problem started: 'since yesterday' or 'last week'"
  ]
}
```

---

## 🚀 Integration into Complaint Creation

**File**: `backend/app/routers/complaints.py` (lines 257-330)

When a citizen submits a complaint:

1. **Category Detection**: Automatically detects category from Kannada/English text
   ```python
   normalizer = MultilingualNormalizer()
   detected_category = normalizer.detect_category(f"{title} {description}")
   category = payload.category or detected_category or "other"
   ```

2. **Emergency Detection**: Checks for Kannada + English keywords
   ```python
   emergency_keywords = ["emergency", "urgent", "immediately", "bega", "sikkantu"]
   complaint.is_emergency = any(keyword in desc_lower for keyword in emergency_keywords)
   ```

3. **Impact Estimation**: Detects high-impact issues
   ```python
   impact_keywords = ["entire", "whole", "all", "many", "multiple"]
   affected_pop = 10 if any(kw in desc for kw in impact_keywords) else 1
   ```

4. **Priority Score Calculation**:
   - Emergency: 0.9 (90% priority)
   - High impact (>5 people): 0.7 (70% priority)
   - Normal: 0.5 (50% priority)

---

## 📝 Example User Flows

### **Scenario 1: Kannada Speaker with Poor English**
```
Input: "niru pipeline brokan near mane bega fix maadi water waste"
↓
Normalized: "water pipeline broken near house urgent fix water waste"
↓
Detected: category=water, is_urgent=true, affected_pop=1
↓
Priority Score: 0.9 (emergency)
```

### **Scenario 2: English with Terrible Spelling**
```
Input: "rood hole very big problm many vehical crash urgant"
↓
Normalized: "road hole very big problem many vehicle crash urgent"
↓
Detected: category=roads, is_urgent=true, affected_pop=10
↓
Priority Score: 0.9 (emergency + high impact)
```

### **Scenario 3: Seasonal Prediction in Action**
**April**: System predicts water shortage complaints will spike in May
↓
**MLA Dashboard**: Shows "Prepare ₹5 lakhs for water tankers in May"
↓
**May 1st**: Water complaints start coming, but budget already allocated
↓
**Result**: Quick response, citizens satisfied

---

## 🎯 API Endpoints Summary

| Endpoint | Method | Purpose |
|----------|--------|---------|
| `/constituencies/{id}/seasonal-forecast` | GET | Predict complaint trends 3-6 months ahead |
| `/constituencies/{id}/budget-forecast` | GET | Forecast budget needs based on trends |
| `/constituencies/{id}/proactive-maintenance` | GET | Identify recurring issues needing permanent fix |
| `/analyze-complaint-text` | POST | Real-time NLP analysis of complaint text |
| `/clusters/{cluster_id}/batch-project` | GET | Batch resolution project suggestions |

---

## 📚 Technical Details

### **Files Created/Modified**:

**New Files**:
- `backend/app/services/predictive_planning_service.py` (469 lines)
  - `MultilingualNormalizer` class
  - `PredictivePlanningService` class
  - Seasonal factors, recommendations, budget calculations

**Modified Files**:
- `backend/app/routers/case_management.py`
  - Added 4 new predictive planning endpoints
  
- `backend/app/routers/complaints.py`
  - Integrated category detection and priority scoring
  - Auto-detect emergency from Kannada keywords

---

## 🧪 Testing

### **Test Category Detection**:
```bash
curl -X POST "http://localhost:8000/api/v1/case-management/analyze-complaint-text" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -d "title=raste guddi&description=Main rode brokan bega fix"
```

### **Test Seasonal Forecast**:
```bash
curl "http://localhost:8000/api/v1/case-management/constituencies/{UUID}/seasonal-forecast?months_ahead=3" \
  -H "Authorization: Bearer YOUR_TOKEN"
```

### **Test Budget Forecast**:
```bash
curl "http://localhost:8000/api/v1/case-management/constituencies/{UUID}/budget-forecast?months_ahead=6" \
  -H "Authorization: Bearer YOUR_TOKEN"
```

### **Test Proactive Maintenance**:
```bash
curl "http://localhost:8000/api/v1/case-management/constituencies/{UUID}/proactive-maintenance" \
  -H "Authorization: Bearer YOUR_TOKEN"
```

---

## 🌟 Key Benefits

1. **No Language Barrier**: Citizens can type in Kannada, English, or mix
2. **Spelling Doesn't Matter**: Automatic correction handles mistakes
3. **Predictive Power**: MLAs can plan 3-6 months ahead
4. **Cost Optimization**: Identifies where preventive fixes save money
5. **Seasonal Awareness**: Prepares for monsoon drainage issues, summer water shortages
6. **Cultural Fit**: Understands Indian context (festivals, monsoon, local terms)

---

## 🚀 Next Steps

1. ✅ **DONE**: Multilingual NLP
2. ✅ **DONE**: Seasonal predictions
3. ✅ **DONE**: Budget forecasting
4. ✅ **DONE**: Proactive maintenance
5. ⏳ **TODO**: Frontend dashboard showing predictions
6. ⏳ **TODO**: SMS notifications in Kannada
7. ⏳ **TODO**: Voice complaint support (Kannada speech-to-text)

---

**Status**: ✅ Backend implementation complete, backend restarted successfully  
**Next**: Build duplicate detection workflow and budget tracking system
