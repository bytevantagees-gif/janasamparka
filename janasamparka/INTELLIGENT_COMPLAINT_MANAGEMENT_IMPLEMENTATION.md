# Intelligent Complaint Management - Implementation Guide

## 📋 Overview

This document outlines the intelligent complaint management system implemented to prevent bureaucratic overload in Indian constituencies. The system uses **priority scoring**, **geographic clustering**, **duplicate detection**, and **smart resource allocation** to handle high complaint volumes efficiently.

---

## 🎯 Problem Addressed

**Challenge**: In India, a single MLA constituency serves 200,000-300,000 citizens. If even 1% file complaints, that's 2,000-3,000 complaints potentially overwhelming officials with limited budgets and staff.

**Solution**: Intelligent triage, batching, and resource optimization to maximize impact with available resources.

---

## ✅ Implemented Features

### 1. **Priority Scoring System** ✓

**File**: `backend/app/services/priority_service.py`

**Algorithm**:
```python
Priority Score = (Severity × 0.4) + (Population × 0.25) + (Urgency × 0.15) + (Recurrence × 0.1) + (Vulnerability × 0.1)
```

**Features**:
- **Severity Detection**: Keywords like "broken", "collapsed", "danger", "hazard"
- **Emergency Detection**: "emergency", "urgent", "immediately", "critical"
- **High Impact**: "entire area", "whole street", "multiple", "many people"
- **Vulnerable Populations**: "children", "elderly", "disabled", "pregnant", "hospital", "school"
- **Recurrence Detection**: Checks for similar complaints in same area

**Output**: Score 0-1, priority level (urgent/high/medium/low), is_emergency flag, affected_population_estimate

**Key Methods**:
- `calculate_priority_score()`: Main priority calculation
- `detect_nearby_duplicates()`: Find similar complaints within 200m
- `calculate_queue_position()`: Rank complaint in constituency queue
- `get_sla_for_category()`: Get expected resolution timeline

**SLA Configuration** (Resolution Times):
```python
{
    "water": {"min_days": 7, "max_days": 14},      # 1-2 weeks
    "roads": {"min_days": 30, "max_days": 45},     # 1-1.5 months
    "electricity": {"min_days": 3, "max_days": 7}, # 3-7 days
    "sanitation": {"min_days": 7, "max_days": 14}, # 1-2 weeks
    "streetlight": {"min_days": 3, "max_days": 7}, # 3-7 days
    "drainage": {"min_days": 14, "max_days": 30},  # 2-4 weeks
    "default": {"min_days": 14, "max_days": 30}    # 2-4 weeks
}
```

---

### 2. **Geographic Clustering for Batch Resolution** ✓

**File**: `backend/app/services/clustering_service.py`

**Purpose**: Group nearby complaints for batch resolution, saving 30-40% on costs.

**Features**:
- **Cluster Detection**: Finds groups of 3+ complaints within 500m radius
- **Cost Estimation**: Calculates individual vs. batch resolution costs
- **Savings Calculation**: Estimates 35% cost reduction through batch work
- **Project Generation**: Creates batch project proposals with timelines

**Example Cost Estimates** (per complaint):
```python
{
    "roads": ₹50,000,        # Pothole repair
    "water": ₹25,000,        # Water supply fix
    "electricity": ₹15,000,  # Electrical issue
    "sanitation": ₹20,000,   # Sanitation work
    "streetlight": ₹8,000,   # Streetlight repair
    "drainage": ₹40,000      # Drainage system
}
```

**API Endpoints**:
- `GET /api/v1/case-management/constituencies/{constituency_id}/clusters`
  - Parameters: `category`, `min_cluster_size`, `max_radius_meters`
  - Returns: List of clusters with savings calculations
  
- `GET /api/v1/case-management/clusters/{cluster_id}/batch-project`
  - Returns: Detailed batch project proposal

**Batch Project Output**:
```json
{
  "project_id": "roads_12345_67890",
  "project_name": "Road Repair Project: Near Main Street Area",
  "category": "roads",
  "location": {
    "center_lat": 12.9716,
    "center_lng": 77.5946,
    "radius_meters": 350.5,
    "description": "Near main street area"
  },
  "complaints": {
    "count": 5,
    "ids": ["uuid1", "uuid2", ...]
  },
  "cost": {
    "individual_total": 250000,
    "batch_total": 162500,
    "savings": 87500,
    "savings_percentage": 35.0,
    "currency": "INR"
  },
  "timeline": {
    "estimated_days": 10,
    "estimated_completion": "10 days from start"
  },
  "benefits": [
    "Resolves 5 complaints at once",
    "Saves ₹87,500",
    "35% cost reduction",
    "Single project coordination",
    "Comprehensive area coverage"
  ]
}
```

---

### 3. **Database Schema Enhancements** ✓

**File**: `backend/app/models/complaint.py`

**New Fields**:
```python
# Priority Management
priority_score = Column(Float, default=0.0)
is_emergency = Column(Boolean, default=False)
affected_population_estimate = Column(Integer, default=1)
last_activity_at = Column(DateTime(timezone=True), default=func.now())

# Duplicate Detection
is_duplicate = Column(Boolean, default=False)
parent_complaint_id = Column(UUID(as_uuid=True), ForeignKey("complaints.id"), nullable=True)
duplicate_count = Column(Integer, default=0)

# Department Selection
suggested_dept_id = Column(UUID(as_uuid=True), ForeignKey("departments.id"), nullable=True)
citizen_selected_dept = Column(Boolean, default=False)
```

**Relationships**:
```python
duplicates = relationship("Complaint", backref=backref("parent_complaint", remote_side=[id]))
```

---

## 🚧 Pending Implementation

### 4. **Priority Scoring Integration** (Next Step)

**Action Required**: Modify `backend/app/routers/complaints.py`

**Implementation**:
```python
from app.services.priority_service import PriorityCalculationService

@router.post("/complaints", response_model=ComplaintResponse)
async def create_complaint(
    complaint_data: ComplaintCreate,
    db: AsyncSession = Depends(get_db)
):
    # Create complaint first
    complaint = Complaint(**complaint_data.dict())
    db.add(complaint)
    await db.flush()
    
    # Calculate priority
    priority_service = PriorityCalculationService(db)
    priority_result = await priority_service.calculate_priority_score(
        description=complaint.description,
        category=complaint.category,
        location=(complaint.lat, complaint.lng),
        constituency_id=complaint.constituency_id,
        location_description=complaint.location_description
    )
    
    # Update complaint with priority data
    complaint.priority_score = priority_result["score"]
    complaint.is_emergency = priority_result["is_emergency"]
    complaint.affected_population_estimate = priority_result["affected_population"]
    
    await db.commit()
    return complaint
```

**Expected Impact**:
- Automatic priority assignment on every complaint
- Emergency complaints flagged immediately
- Queue position calculated automatically

---

### 5. **Duplicate Detection Workflow**

**API Endpoint** (To be created):
```python
@router.post("/api/v1/complaints/{complaint_id}/mark-duplicate")
async def mark_as_duplicate(
    complaint_id: UUID,
    parent_complaint_id: UUID,
    db: AsyncSession = Depends(get_db)
):
    """Mark complaint as duplicate and link to parent."""
    complaint = await db.get(Complaint, complaint_id)
    parent = await db.get(Complaint, parent_complaint_id)
    
    complaint.is_duplicate = True
    complaint.parent_complaint_id = parent_complaint_id
    parent.duplicate_count += 1
    
    await db.commit()
    return {"message": "Marked as duplicate", "parent_id": parent_complaint_id}
```

**Frontend Integration**:
- Show "Possible Duplicates" section when creating complaint
- Use `PriorityCalculationService.detect_nearby_duplicates()` to find similar complaints
- Allow officer to link duplicates with one click

---

### 6. **Budget Tracking System**

**Models to Create**:
```python
# backend/app/models/budget.py

class WardBudget(Base):
    __tablename__ = "ward_budgets"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    ward_id = Column(UUID(as_uuid=True), ForeignKey("wards.id"))
    financial_year = Column(String)
    category = Column(String)
    allocated = Column(Integer)  # Total budget
    spent = Column(Integer, default=0)
    committed = Column(Integer, default=0)  # Allocated to projects
    remaining = Column(Integer)  # Calculated field
    
class DepartmentBudget(Base):
    __tablename__ = "department_budgets"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    department_id = Column(UUID(as_uuid=True), ForeignKey("departments.id"))
    financial_year = Column(String)
    category = Column(String)
    allocated = Column(Integer)
    spent = Column(Integer, default=0)
    committed = Column(Integer, default=0)
    remaining = Column(Integer)
```

**API Endpoints Needed**:
- `GET /api/v1/budgets/wards/{ward_id}` - View ward budget
- `GET /api/v1/budgets/departments/{dept_id}` - View department budget
- `POST /api/v1/budgets/allocate` - Allocate budget to project
- `GET /api/v1/budgets/transparency` - Public budget dashboard

**Expected Impact**:
- Officers see available budget before approving work
- Citizens see budget transparency
- Prevents over-commitment

---

### 7. **FAQ / Knowledge Base System**

**Models to Create**:
```python
# backend/app/models/faq.py

class FAQSolution(Base):
    __tablename__ = "faq_solutions"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    category = Column(String, nullable=False)
    title = Column(String, nullable=False)
    solution_text = Column(Text, nullable=False)
    success_rate = Column(Float, default=0.0)
    prevented_complaints = Column(Integer, default=0)
    created_at = Column(DateTime(timezone=True), default=func.now())
```

**API Endpoints Needed**:
- `GET /api/v1/faqs/search?q={query}&category={category}` - Search solutions
- `POST /api/v1/faqs/{faq_id}/mark-helpful` - Track success rate
- `GET /api/v1/faqs/top-solutions` - Most helpful solutions

**Frontend Integration**:
- Show relevant FAQs before complaint submission
- "Did this solve your problem?" button
- Track prevented complaints

---

## 📊 Expected System Performance

### Without Intelligent Management:
- 2,000 complaints filed
- 2,000 individual resolutions needed
- Random priority → critical issues delayed
- Budget exhausted in 2-3 months
- System overload → citizen frustration

### With Intelligent Management:
- 2,000 complaints filed
- **30% marked as duplicates** → 1,400 unique issues
- **20% resolved via FAQ** → 1,120 requiring action
- **40% clustered for batch resolution** → 672 individual + 448 in batches (savings: ₹5-10 lakhs)
- **Priority scoring** → emergencies handled first
- **Budget tracking** → strategic allocation throughout year

**Net Effect**: 
- Handle same volume with 60% less resources
- Better outcomes (emergencies prioritized)
- Increased citizen satisfaction (self-service FAQs)
- Budget transparency and accountability

---

## 🎨 Frontend Integration Guide

### Priority Display Component
```jsx
function PriorityBadge({ priorityScore, isEmergency }) {
  const level = isEmergency ? 'urgent' : 
                priorityScore > 0.7 ? 'high' :
                priorityScore > 0.4 ? 'medium' : 'low';
  
  const colors = {
    urgent: 'bg-red-600',
    high: 'bg-orange-500',
    medium: 'bg-yellow-500',
    low: 'bg-green-500'
  };
  
  return (
    <span className={`px-3 py-1 rounded-full text-white ${colors[level]}`}>
      {isEmergency && '🚨 '}{level.toUpperCase()}
    </span>
  );
}
```

### SLA Timeline Component
```jsx
function SLATimeline({ category, createdAt }) {
  const sla = getSLAForCategory(category);
  const daysElapsed = daysSince(createdAt);
  const progress = (daysElapsed / sla.max_days) * 100;
  
  return (
    <div className="w-full bg-gray-200 rounded">
      <div 
        className={`h-2 rounded ${progress > 80 ? 'bg-red-500' : 'bg-blue-500'}`}
        style={{ width: `${Math.min(progress, 100)}%` }}
      />
      <p className="text-sm mt-1">
        Day {daysElapsed} of {sla.max_days} (SLA: {sla.min_days}-{sla.max_days} days)
      </p>
    </div>
  );
}
```

### Cluster Map View
```jsx
function ClusterMapView({ clusters }) {
  return (
    <Map>
      {clusters.map(cluster => (
        <CircleMarker
          center={[cluster.center_lat, cluster.center_lng]}
          radius={cluster.radius_meters}
          color="blue"
          fillOpacity={0.3}
        >
          <Popup>
            <h3>{cluster.category} Cluster</h3>
            <p>{cluster.complaint_count} complaints</p>
            <p>Savings: ₹{cluster.savings}</p>
            <button onClick={() => viewBatchProject(cluster.cluster_id)}>
              View Batch Project
            </button>
          </Popup>
        </CircleMarker>
      ))}
    </Map>
  );
}
```

---

## 🔧 Testing the System

### Test Priority Scoring
```python
# In backend terminal
python -c "
from app.services.priority_service import PriorityCalculationService
import asyncio

async def test():
    # Mock high-priority complaint
    result = await priority_service.calculate_priority_score(
        description='EMERGENCY: Entire street water pipeline burst. Many elderly residents affected.',
        category='water',
        location=(12.9716, 77.5946),
        constituency_id='uuid-here'
    )
    print('Priority Result:', result)

asyncio.run(test())
"
```

### Test Clustering API
```bash
# Get clusters for constituency
curl http://localhost:8000/api/v1/case-management/constituencies/{id}/clusters?category=roads

# Get batch project for cluster
curl http://localhost:8000/api/v1/case-management/clusters/{cluster_id}/batch-project
```

---

## 📈 Next Steps

1. **✅ DONE**: Priority scoring service created
2. **✅ DONE**: Clustering service created
3. **🔄 IN PROGRESS**: Integrate priority scoring into complaint creation
4. **⏳ TODO**: Add duplicate detection endpoints
5. **⏳ TODO**: Create budget tracking models and APIs
6. **⏳ TODO**: Build FAQ/knowledge base system
7. **⏳ TODO**: Frontend UI components for priority, clusters, SLA timelines
8. **⏳ TODO**: Mobile app integration for citizen self-service

---

## 🎓 Key Learnings

### Why This Approach Works for India:
1. **Accepts Reality**: Cannot resolve every complaint immediately with limited resources
2. **Maximizes Impact**: Priority scoring ensures critical issues handled first
3. **Optimizes Costs**: Batch resolution saves 35% through economies of scale
4. **Reduces Load**: FAQs and duplicate detection prevent unnecessary complaints
5. **Builds Trust**: Transparency (queue position, budget, SLA) manages expectations
6. **Cultural Fit**: Queue position aligns with Indian understanding of waiting systems

### Why Traditional Systems Fail:
- ❌ First-come-first-served → minor issues block critical ones
- ❌ No duplicate detection → wasted resources on same problem
- ❌ No batching → 3x more expensive
- ❌ Hidden budget → citizens think government ignoring them
- ❌ No self-service → every issue needs human intervention

---

## 📞 Support & Documentation

- **API Documentation**: `http://localhost:8000/docs`
- **Database Schema**: See migration file `add_case_notes_routing_escalations.py`
- **Service Files**: 
  - `backend/app/services/priority_service.py`
  - `backend/app/services/clustering_service.py`
  - `backend/app/services/department_suggestion.py`

---

**Last Updated**: December 2024  
**Status**: Core services implemented, integration in progress  
**Next Session**: Complete priority scoring integration and duplicate detection
