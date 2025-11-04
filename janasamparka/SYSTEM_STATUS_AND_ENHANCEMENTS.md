# 🚀 Janasamparka System Status & Enhancement Plan

**Date**: October 30, 2025  
**Document**: Comprehensive System Status and Enhancement Requirements  
**Status**: Production-Ready MVP with Critical Enhancements Needed

---

## 📊 **CURRENT SYSTEM STATUS**

### ✅ **What's Complete and Working**

#### 1. **Multi-Tenancy Architecture** (100% Complete)
- ✅ Constituency-based data isolation
- ✅ Role-based access control (9 roles)
- ✅ Cross-constituency analytics for admins
- ✅ Auto-filtering by user constituency

#### 2. **Panchayat Raj Integration** (100% Complete - Just Completed!)
- ✅ 3-tier hierarchy (Zilla → Taluk → Gram Panchayats)
- ✅ 7 new panchayat roles (PDO, VA, TP Officer, etc.)
- ✅ Complete API endpoints with role-based filtering
- ✅ 3 frontend dashboards (PDO, VA, TP Officer)
- ✅ 8 test users created across all levels
- ✅ Sample data for Dakshina Kannada district

#### 3. **Core Complaint Management** (95% Complete)
- ✅ Complaint submission (web + mobile)
- ✅ AI-powered department routing
- ✅ Status tracking and lifecycle management
- ✅ Media uploads (photos, videos)
- ✅ Before/after photo workflow
- ✅ Department assignment and reassignment
- ✅ Work approval/rejection workflow
- ✅ Citizen rating system (Phase 5.5)
- ⚠️ **MISSING**: Internal notes visible only to officials

#### 4. **Analytics & Reporting** (85% Complete)
- ✅ Real-time dashboard with key metrics
- ✅ Trend analysis (daily, weekly, monthly)
- ✅ Department performance tracking
- ✅ SLA compliance monitoring
- ✅ CSV/JSON export functionality
- ✅ Category and priority breakdowns
- ⚠️ **MISSING**: MLA performance dashboard with comparative analytics
- ⚠️ **MISSING**: Side-by-side comparison of wards/GPs/taluks
- ⚠️ **MISSING**: Citizen satisfaction index aggregation

#### 5. **Role-Based Dashboards** (60% Complete)
- ✅ Admin Dashboard (95% complete)
- ✅ MLA Dashboard (85% complete - needs personalization)
- ✅ Moderator Dashboard (70% complete)
- ✅ Officer Dashboard (60% complete - needs personalization)
- ✅ Auditor Dashboard (complete)
- ✅ PDO Dashboard (complete)
- ✅ Village Accountant Dashboard (complete)
- ✅ Taluk Panchayat Officer Dashboard (complete)
- ❌ **MISSING**: Citizen Portal (20% complete)

#### 6. **Authentication & Security** (90% Complete)
- ✅ OTP-based login (phone number only)
- ✅ JWT token management
- ✅ Role-based middleware
- ✅ Multi-constituency access control
- ⚠️ **MISSING**: Backup login mechanism (when phone is broken)

#### 7. **GIS & Mapping** (100% Complete)
- ✅ Interactive map with complaint pins
- ✅ Ward boundary visualization
- ✅ Geo-tagged media uploads
- ✅ Location-based complaint filtering
- ✅ Cluster visualization

#### 8. **Polls & Citizen Engagement** (90% Complete)
- ✅ Poll creation by MLA/Moderators
- ✅ Multiple poll types
- ✅ Results visualization
- ✅ Date-based activation
- ⚠️ **MISSING**: Citizen voting interface in main dashboard

#### 9. **Mobile App** (75% Complete)
- ✅ Complaint submission with photos
- ✅ Location capture
- ✅ Status tracking
- ⚠️ **MISSING**: Role-specific screens
- ⚠️ **MISSING**: Officer field tools

---

## 🎯 **NEW REQUIREMENTS - PRIORITY CLASSIFICATION**

### 🔴 **CRITICAL PRIORITY (P0) - Must Implement Immediately**

#### 1. **MLA Performance Dashboard with Comparative Analytics**

**What's Needed**:
```
MLA should be able to:
✅ Choose comparison units from dropdown:
   - Wards (urban areas)
   - Gram Panchayats (rural villages)
   - Taluks (block level)
   - Zilla Panchayats (district level)
   - Departments

✅ View side-by-side comparison:
   - Resolution rates
   - Average resolution times
   - Active complaints
   - Citizen satisfaction index
   - Budget utilization
   - Officer performance

✅ Visual representations:
   - Bar charts (comparison)
   - Line graphs (trends over time)
   - Heatmaps (geographic performance)
   - Leaderboards (top/bottom performers)

✅ Insights and recommendations:
   - Areas lacking behind (red flags)
   - Areas exceeding expectations (green stars)
   - Suggestions for resource allocation
   - Predicted issues based on trends
```

**Implementation Required**:

**Backend API Endpoint**:
```python
# /backend/app/routers/analytics.py

@router.get("/mla/performance-comparison")
async def get_mla_performance_comparison(
    unit_type: str = Query(..., description="ward, gram_panchayat, taluk, department"),
    unit_ids: Optional[List[UUID]] = Query(None, description="Specific units to compare"),
    date_from: Optional[date] = None,
    date_to: Optional[date] = None,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Compare performance across multiple units (wards, GPs, taluks, departments)
    Returns side-by-side metrics for MLA decision-making
    """
    # Verify MLA role
    if current_user.role not in [UserRole.MLA, UserRole.ADMIN]:
        raise HTTPException(403, "Only MLAs can access performance comparison")
    
    # Get user's constituency
    constituency_id = current_user.constituency_id
    
    # Fetch units based on type
    if unit_type == "ward":
        units = db.query(Ward).filter(
            Ward.constituency_id == constituency_id
        )
        if unit_ids:
            units = units.filter(Ward.id.in_(unit_ids))
        units = units.all()
        
        # Calculate metrics for each ward
        comparison_data = []
        for ward in units:
            metrics = calculate_ward_metrics(db, ward.id, date_from, date_to)
            comparison_data.append({
                "id": str(ward.id),
                "name": ward.name,
                "type": "ward",
                "metrics": metrics,
                "insights": generate_insights(metrics)
            })
    
    elif unit_type == "gram_panchayat":
        units = db.query(GramPanchayat).filter(
            GramPanchayat.constituency_id == constituency_id
        )
        if unit_ids:
            units = units.filter(GramPanchayat.id.in_(unit_ids))
        units = units.all()
        
        comparison_data = []
        for gp in units:
            metrics = calculate_gp_metrics(db, gp.id, date_from, date_to)
            comparison_data.append({
                "id": str(gp.id),
                "name": gp.village,
                "type": "gram_panchayat",
                "metrics": metrics,
                "insights": generate_insights(metrics)
            })
    
    # Similar for taluk, department, etc.
    
    # Calculate constituency average for comparison
    constituency_avg = calculate_constituency_average(db, constituency_id, date_from, date_to)
    
    return {
        "unit_type": unit_type,
        "comparison": comparison_data,
        "constituency_average": constituency_avg,
        "best_performer": max(comparison_data, key=lambda x: x["metrics"]["resolution_rate"]),
        "needs_attention": [unit for unit in comparison_data if unit["metrics"]["resolution_rate"] < 70],
        "date_range": {
            "from": date_from,
            "to": date_to
        }
    }


def calculate_ward_metrics(db: Session, ward_id: UUID, date_from, date_to):
    """Calculate comprehensive metrics for a ward"""
    query = db.query(Complaint).filter(Complaint.ward_id == ward_id)
    
    if date_from:
        query = query.filter(Complaint.created_at >= date_from)
    if date_to:
        query = query.filter(Complaint.created_at <= date_to)
    
    total = query.count()
    resolved = query.filter(Complaint.status.in_([ComplaintStatus.RESOLVED, ComplaintStatus.CLOSED])).count()
    avg_rating = db.query(func.avg(Complaint.citizen_rating)).filter(
        Complaint.ward_id == ward_id,
        Complaint.citizen_rating.isnot(None)
    ).scalar() or 0
    
    # Calculate average resolution time
    resolved_complaints = query.filter(
        Complaint.status.in_([ComplaintStatus.RESOLVED, ComplaintStatus.CLOSED]),
        Complaint.resolved_at.isnot(None)
    ).all()
    
    if resolved_complaints:
        total_days = sum((c.resolved_at - c.created_at).days for c in resolved_complaints)
        avg_resolution_days = total_days / len(resolved_complaints)
    else:
        avg_resolution_days = None
    
    return {
        "total_complaints": total,
        "resolved": resolved,
        "pending": total - resolved,
        "resolution_rate": round((resolved / total * 100), 1) if total > 0 else 0,
        "avg_resolution_days": round(avg_resolution_days, 1) if avg_resolution_days else None,
        "citizen_satisfaction": round(avg_rating, 2),
        "active_cases": total - resolved,
        "overdue_cases": query.filter(
            Complaint.status.not_in([ComplaintStatus.RESOLVED, ComplaintStatus.CLOSED]),
            Complaint.created_at < (datetime.utcnow() - timedelta(days=7))
        ).count()
    }


def generate_insights(metrics: dict) -> dict:
    """Generate AI-like insights from metrics"""
    insights = {
        "performance_level": "good",
        "recommendations": [],
        "red_flags": [],
        "green_stars": []
    }
    
    # Resolution rate analysis
    if metrics["resolution_rate"] < 60:
        insights["performance_level"] = "poor"
        insights["red_flags"].append("Low resolution rate - needs immediate attention")
        insights["recommendations"].append("Increase officer assignment or investigate bottlenecks")
    elif metrics["resolution_rate"] > 85:
        insights["green_stars"].append("Excellent resolution rate!")
    
    # Citizen satisfaction analysis
    if metrics["citizen_satisfaction"] < 3.0:
        insights["red_flags"].append("Low citizen satisfaction - quality of work may be poor")
        insights["recommendations"].append("Review completed work quality and officer training")
    elif metrics["citizen_satisfaction"] > 4.0:
        insights["green_stars"].append("High citizen satisfaction!")
    
    # Resolution time analysis
    if metrics["avg_resolution_days"] and metrics["avg_resolution_days"] > 7:
        insights["red_flags"].append("Slow resolution time exceeding 7-day SLA")
        insights["recommendations"].append("Review officer workload and resource allocation")
    
    # Overdue cases analysis
    if metrics["overdue_cases"] > 5:
        insights["red_flags"].append(f"{metrics['overdue_cases']} cases are overdue")
        insights["recommendations"].append("Escalate overdue cases to department heads")
    
    return insights
```

**Frontend Component**:
```jsx
// /admin-dashboard/src/pages/mla/PerformanceDashboard.jsx

import React, { useState } from 'react';
import { useQuery } from '@tanstack/react-query';
import {
  BarChart, Bar, LineChart, Line, XAxis, YAxis, CartesianGrid, 
  Tooltip, Legend, ResponsiveContainer, RadarChart, PolarGrid,
  PolarAngleAxis, PolarRadiusAxis, Radar
} from 'recharts';
import { TrendingUp, TrendingDown, AlertCircle, Award, Filter } from 'lucide-react';

export default function MLAPerformanceDashboard() {
  const [unitType, setUnitType] = useState('ward'); // ward, gram_panchayat, taluk, department
  const [selectedUnits, setSelectedUnits] = useState([]);
  const [dateRange, setDateRange] = useState('last_30_days');

  // Fetch comparison data
  const { data: comparison, isLoading } = useQuery({
    queryKey: ['mla-performance-comparison', unitType, selectedUnits, dateRange],
    queryFn: async () => {
      const params = new URLSearchParams({
        unit_type: unitType,
        ...getDateRangeParams(dateRange)
      });
      
      if (selectedUnits.length > 0) {
        selectedUnits.forEach(id => params.append('unit_ids', id));
      }
      
      const response = await analyticsAPI.getMLAPerformanceComparison(params);
      return response.data;
    }
  });

  return (
    <div className="space-y-6">
      {/* Header with Filters */}
      <div className="bg-white rounded-lg shadow p-6">
        <h1 className="text-2xl font-bold mb-6">Performance Comparison Dashboard</h1>
        
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          {/* Unit Type Selector */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Compare By
            </label>
            <select
              value={unitType}
              onChange={(e) => setUnitType(e.target.value)}
              className="w-full rounded-md border-gray-300 shadow-sm"
            >
              <option value="ward">Wards</option>
              <option value="gram_panchayat">Gram Panchayats</option>
              <option value="taluk">Taluks</option>
              <option value="department">Departments</option>
            </select>
          </div>

          {/* Date Range Selector */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Time Period
            </label>
            <select
              value={dateRange}
              onChange={(e) => setDateRange(e.target.value)}
              className="w-full rounded-md border-gray-300 shadow-sm"
            >
              <option value="last_7_days">Last 7 Days</option>
              <option value="last_30_days">Last 30 Days</option>
              <option value="last_3_months">Last 3 Months</option>
              <option value="last_6_months">Last 6 Months</option>
              <option value="last_year">Last Year</option>
            </select>
          </div>

          {/* Unit Selector (Multi-select) */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Specific Units (Optional)
            </label>
            <button className="w-full px-4 py-2 border rounded-md text-left">
              <Filter className="inline h-4 w-4 mr-2" />
              {selectedUnits.length === 0 ? 'All' : `${selectedUnits.length} selected`}
            </button>
          </div>
        </div>
      </div>

      {isLoading ? (
        <div className="flex justify-center items-center h-64">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
        </div>
      ) : (
        <>
          {/* Key Insights Cards */}
          <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
            {/* Best Performer */}
            <div className="bg-gradient-to-br from-green-500 to-green-600 rounded-lg shadow p-6 text-white">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm opacity-90">Best Performer</p>
                  <p className="text-2xl font-bold mt-1">
                    {comparison?.best_performer?.name}
                  </p>
                  <p className="text-sm mt-2">
                    {comparison?.best_performer?.metrics?.resolution_rate}% Resolution Rate
                  </p>
                </div>
                <Award className="h-12 w-12 opacity-80" />
              </div>
            </div>

            {/* Constituency Average */}
            <div className="bg-gradient-to-br from-blue-500 to-blue-600 rounded-lg shadow p-6 text-white">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm opacity-90">Constituency Average</p>
                  <p className="text-2xl font-bold mt-1">
                    {comparison?.constituency_average?.resolution_rate}%
                  </p>
                  <p className="text-sm mt-2">
                    {comparison?.constituency_average?.total_complaints} Total Cases
                  </p>
                </div>
                <TrendingUp className="h-12 w-12 opacity-80" />
              </div>
            </div>

            {/* Needs Attention */}
            <div className="bg-gradient-to-br from-red-500 to-red-600 rounded-lg shadow p-6 text-white">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm opacity-90">Needs Attention</p>
                  <p className="text-2xl font-bold mt-1">
                    {comparison?.needs_attention?.length || 0}
                  </p>
                  <p className="text-sm mt-2">
                    Units Below 70% Resolution Rate
                  </p>
                </div>
                <AlertCircle className="h-12 w-12 opacity-80" />
              </div>
            </div>
          </div>

          {/* Side-by-Side Comparison Chart */}
          <div className="bg-white rounded-lg shadow p-6">
            <h2 className="text-xl font-bold mb-6">Resolution Rate Comparison</h2>
            <ResponsiveContainer width="100%" height={400}>
              <BarChart data={comparison?.comparison || []}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis dataKey="name" angle={-45} textAnchor="end" height={100} />
                <YAxis />
                <Tooltip />
                <Legend />
                <Bar dataKey="metrics.resolution_rate" name="Resolution Rate (%)" fill="#3B82F6" />
                <Bar dataKey="metrics.citizen_satisfaction" name="Satisfaction (×20)" fill="#10B981" />
              </BarChart>
            </ResponsiveContainer>
          </div>

          {/* Citizen Satisfaction Index Chart */}
          <div className="bg-white rounded-lg shadow p-6">
            <h2 className="text-xl font-bold mb-6">Citizen Satisfaction Index</h2>
            <ResponsiveContainer width="100%" height={400}>
              <LineChart data={comparison?.comparison || []}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis dataKey="name" angle={-45} textAnchor="end" height={100} />
                <YAxis domain={[0, 5]} />
                <Tooltip />
                <Legend />
                <Line 
                  type="monotone" 
                  dataKey="metrics.citizen_satisfaction" 
                  name="Satisfaction Rating" 
                  stroke="#F59E0B" 
                  strokeWidth={2}
                />
              </LineChart>
            </ResponsiveContainer>
          </div>

          {/* Detailed Comparison Table */}
          <div className="bg-white rounded-lg shadow overflow-hidden">
            <h2 className="text-xl font-bold p-6 border-b">Detailed Metrics</h2>
            <div className="overflow-x-auto">
              <table className="min-w-full divide-y divide-gray-200">
                <thead className="bg-gray-50">
                  <tr>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">
                      {unitType === 'ward' ? 'Ward' : 
                       unitType === 'gram_panchayat' ? 'Gram Panchayat' :
                       unitType === 'taluk' ? 'Taluk' : 'Department'}
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">
                      Total Cases
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">
                      Resolved
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">
                      Resolution Rate
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">
                      Avg Time (days)
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">
                      Satisfaction
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">
                      Status
                    </th>
                  </tr>
                </thead>
                <tbody className="bg-white divide-y divide-gray-200">
                  {comparison?.comparison?.map((unit) => (
                    <tr key={unit.id} className="hover:bg-gray-50">
                      <td className="px-6 py-4 whitespace-nowrap font-medium text-gray-900">
                        {unit.name}
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-gray-700">
                        {unit.metrics.total_complaints}
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-gray-700">
                        {unit.metrics.resolved}
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap">
                        <div className="flex items-center">
                          <span className={`font-semibold ${
                            unit.metrics.resolution_rate >= 80 ? 'text-green-600' :
                            unit.metrics.resolution_rate >= 60 ? 'text-yellow-600' :
                            'text-red-600'
                          }`}>
                            {unit.metrics.resolution_rate}%
                          </span>
                          {unit.metrics.resolution_rate >= comparison.constituency_average.resolution_rate ? (
                            <TrendingUp className="ml-2 h-4 w-4 text-green-600" />
                          ) : (
                            <TrendingDown className="ml-2 h-4 w-4 text-red-600" />
                          )}
                        </div>
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-gray-700">
                        {unit.metrics.avg_resolution_days?.toFixed(1) || 'N/A'}
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap">
                        <div className="flex items-center">
                          <span className="text-yellow-500">★</span>
                          <span className="ml-1 font-medium">
                            {unit.metrics.citizen_satisfaction?.toFixed(1) || 'N/A'}
                          </span>
                        </div>
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap">
                        {unit.insights.red_flags.length > 0 ? (
                          <span className="px-2 py-1 text-xs font-semibold rounded-full bg-red-100 text-red-800">
                            Needs Attention
                          </span>
                        ) : unit.insights.green_stars.length > 0 ? (
                          <span className="px-2 py-1 text-xs font-semibold rounded-full bg-green-100 text-green-800">
                            Excellent
                          </span>
                        ) : (
                          <span className="px-2 py-1 text-xs font-semibold rounded-full bg-blue-100 text-blue-800">
                            Good
                          </span>
                        )}
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>

          {/* Insights & Recommendations */}
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            {/* Areas Excelling */}
            <div className="bg-white rounded-lg shadow p-6">
              <h3 className="text-lg font-bold text-green-800 mb-4">
                🌟 Areas Excelling
              </h3>
              <div className="space-y-3">
                {comparison?.comparison
                  ?.filter(unit => unit.insights.green_stars.length > 0)
                  .map(unit => (
                    <div key={unit.id} className="border-l-4 border-green-500 pl-4">
                      <p className="font-semibold text-gray-900">{unit.name}</p>
                      {unit.insights.green_stars.map((star, idx) => (
                        <p key={idx} className="text-sm text-gray-600">• {star}</p>
                      ))}
                    </div>
                  ))}
              </div>
            </div>

            {/* Areas Needing Attention */}
            <div className="bg-white rounded-lg shadow p-6">
              <h3 className="text-lg font-bold text-red-800 mb-4">
                ⚠️ Areas Needing Attention
              </h3>
              <div className="space-y-3">
                {comparison?.comparison
                  ?.filter(unit => unit.insights.red_flags.length > 0)
                  .map(unit => (
                    <div key={unit.id} className="border-l-4 border-red-500 pl-4">
                      <p className="font-semibold text-gray-900">{unit.name}</p>
                      {unit.insights.red_flags.map((flag, idx) => (
                        <p key={idx} className="text-sm text-gray-600">• {flag}</p>
                      ))}
                      <div className="mt-2">
                        <p className="text-xs font-semibold text-gray-700">Recommendations:</p>
                        {unit.insights.recommendations.map((rec, idx) => (
                          <p key={idx} className="text-xs text-gray-600">→ {rec}</p>
                        ))}
                      </div>
                    </div>
                  ))}
              </div>
            </div>
          </div>
        </>
      )}
    </div>
  );
}

function getDateRangeParams(range) {
  const today = new Date();
  let date_from;
  
  switch (range) {
    case 'last_7_days':
      date_from = new Date(today.setDate(today.getDate() - 7));
      break;
    case 'last_30_days':
      date_from = new Date(today.setDate(today.getDate() - 30));
      break;
    case 'last_3_months':
      date_from = new Date(today.setMonth(today.getMonth() - 3));
      break;
    case 'last_6_months':
      date_from = new Date(today.setMonth(today.getMonth() - 6));
      break;
    case 'last_year':
      date_from = new Date(today.setFullYear(today.getFullYear() - 1));
      break;
    default:
      date_from = new Date(today.setDate(today.getDate() - 30));
  }
  
  return {
    date_from: date_from.toISOString().split('T')[0],
    date_to: new Date().toISOString().split('T')[0]
  };
}
```

**Implementation Time**: 3-4 days

---

#### 2. **Citizen Satisfaction Index Aggregation**

**What's Currently There**:
- ✅ Individual complaint ratings (1-5 stars)
- ✅ `citizen_rating` field in complaints table
- ✅ `citizen_feedback` text field

**What's Missing**:
- ❌ Aggregated satisfaction score per ward/GP
- ❌ Trend analysis of satisfaction over time
- ❌ Identification of consistently unhappy citizens
- ❌ Moderator intervention workflow

**Implementation Required**:

**Backend**:
```python
# /backend/app/routers/analytics.py

@router.get("/satisfaction/aggregated")
async def get_aggregated_satisfaction(
    unit_type: str = Query(..., description="ward, gram_panchayat, department"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get aggregated citizen satisfaction index
    Identifies areas with low satisfaction for moderator intervention
    """
    constituency_id = current_user.constituency_id
    
    if unit_type == "ward":
        units = db.query(Ward).filter(Ward.constituency_id == constituency_id).all()
        
        results = []
        for ward in units:
            # Get all rated complaints in this ward
            ratings_query = db.query(
                func.avg(Complaint.citizen_rating).label('avg_rating'),
                func.count(Complaint.id).label('total_ratings'),
                func.sum(case((Complaint.citizen_rating <= 2, 1), else_=0)).label('unhappy_count')
            ).filter(
                Complaint.ward_id == ward.id,
                Complaint.citizen_rating.isnot(None)
            ).first()
            
            # Get list of unhappy citizens (rating <= 2)
            unhappy_citizens = db.query(
                User.id, User.name, User.phone,
                Complaint.id.label('complaint_id'),
                Complaint.title,
                Complaint.citizen_rating,
                Complaint.citizen_feedback,
                Complaint.rating_submitted_at
            ).join(Complaint, Complaint.user_id == User.id).filter(
                Complaint.ward_id == ward.id,
                Complaint.citizen_rating <= 2
            ).all()
            
            results.append({
                "ward_id": str(ward.id),
                "ward_name": ward.name,
                "satisfaction_index": round(ratings_query.avg_rating or 0, 2),
                "total_ratings": ratings_query.total_ratings or 0,
                "unhappy_count": ratings_query.unhappy_count or 0,
                "unhappy_citizens": [
                    {
                        "user_id": str(uc.id),
                        "name": uc.name,
                        "phone": uc.phone,
                        "complaint_id": str(uc.complaint_id),
                        "complaint_title": uc.title,
                        "rating": uc.citizen_rating,
                        "feedback": uc.citizen_feedback,
                        "submitted_at": uc.rating_submitted_at.isoformat()
                    }
                    for uc in unhappy_citizens
                ],
                "status": get_satisfaction_status(ratings_query.avg_rating or 0)
            })
        
        return {
            "unit_type": "ward",
            "results": sorted(results, key=lambda x: x["satisfaction_index"]),
            "constituency_average": sum(r["satisfaction_index"] for r in results) / len(results) if results else 0
        }


def get_satisfaction_status(avg_rating: float) -> str:
    """Determine satisfaction status"""
    if avg_rating >= 4.0:
        return "excellent"
    elif avg_rating >= 3.5:
        return "good"
    elif avg_rating >= 3.0:
        return "fair"
    else:
        return "needs_intervention"
```

**Moderator Intervention Workflow**:
```python
# /backend/app/routers/moderator.py

@router.post("/satisfaction/intervene")
async def create_satisfaction_intervention(
    intervention: SatisfactionInterventionCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Moderator creates intervention for unhappy citizen
    Tracks call/follow-up to convert unhappy to happy
    """
    if current_user.role != UserRole.MODERATOR:
        raise HTTPException(403, "Only moderators can create interventions")
    
    # Create intervention record
    intervention_record = SatisfactionIntervention(
        complaint_id=intervention.complaint_id,
        citizen_id=intervention.citizen_id,
        moderator_id=current_user.id,
        intervention_type=intervention.intervention_type,  # call, visit, follow_up
        notes=intervention.notes,
        scheduled_at=intervention.scheduled_at
    )
    
    db.add(intervention_record)
    db.commit()
    
    # Create case note
    case_note = CaseNote(
        complaint_id=intervention.complaint_id,
        note=f"Moderator intervention scheduled: {intervention.intervention_type}",
        note_type=NoteType.GENERAL,
        created_by=current_user.id,
        is_public=False  # Internal only
    )
    
    db.add(case_note)
    db.commit()
    
    return {"message": "Intervention created successfully", "id": str(intervention_record.id)}


@router.put("/satisfaction/intervene/{intervention_id}/complete")
async def complete_satisfaction_intervention(
    intervention_id: UUID,
    completion: InterventionCompletion,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Mark intervention as complete with outcome
    """
    intervention = db.query(SatisfactionIntervention).filter(
        SatisfactionIntervention.id == intervention_id
    ).first()
    
    if not intervention:
        raise HTTPException(404, "Intervention not found")
    
    intervention.completed_at = datetime.utcnow()
    intervention.outcome = completion.outcome  # resolved, escalated, needs_follow_up
    intervention.completion_notes = completion.notes
    intervention.citizen_now_happy = completion.citizen_now_happy
    
    db.commit()
    
    # Create case note
    case_note = CaseNote(
        complaint_id=intervention.complaint_id,
        note=f"Moderator intervention completed. Outcome: {completion.outcome}. Citizen satisfaction improved: {completion.citizen_now_happy}",
        note_type=NoteType.GENERAL,
        created_by=current_user.id,
        is_public=False
    )
    
    db.add(case_note)
    db.commit()
    
    return {"message": "Intervention marked complete"}
```

**Database Migration**:
```sql
-- /backend/migrations/add_satisfaction_intervention.sql

CREATE TABLE satisfaction_interventions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    complaint_id UUID NOT NULL REFERENCES complaints(id) ON DELETE CASCADE,
    citizen_id UUID NOT NULL REFERENCES users(id),
    moderator_id UUID NOT NULL REFERENCES users(id),
    intervention_type VARCHAR(50) NOT NULL, -- call, visit, follow_up
    notes TEXT,
    scheduled_at TIMESTAMP,
    completed_at TIMESTAMP,
    outcome VARCHAR(50), -- resolved, escalated, needs_follow_up
    completion_notes TEXT,
    citizen_now_happy BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX idx_satisfaction_interventions_complaint ON satisfaction_interventions(complaint_id);
CREATE INDEX idx_satisfaction_interventions_citizen ON satisfaction_interventions(citizen_id);
CREATE INDEX idx_satisfaction_interventions_moderator ON satisfaction_interventions(moderator_id);
```

**Implementation Time**: 2-3 days

---

#### 3. **Internal Notes for Officials Only**

**Current State**:
- ✅ `case_notes` table exists with `is_public` field
- ✅ Notes can be marked public or internal
- ⚠️ **MISSING**: UI to create internal notes
- ⚠️ **MISSING**: UI to view internal notes (hidden from citizens)

**Implementation Required**:

**Backend** (Already exists, just verify):
```python
# case_notes table already has is_public field
# Just need to ensure API filters correctly

# /backend/app/routers/complaints.py

@router.get("/{complaint_id}/notes")
async def get_complaint_notes(
    complaint_id: UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get notes for a complaint
    Citizens see only public notes
    Officials/MLA see all notes
    """
    query = db.query(CaseNote).filter(CaseNote.complaint_id == complaint_id)
    
    # Filter based on role
    if current_user.role == UserRole.CITIZEN:
        # Citizens only see public notes
        query = query.filter(CaseNote.is_public == True)
    # Officials, moderators, MLA, admin see ALL notes
    
    notes = query.order_by(CaseNote.created_at.desc()).all()
    
    return {
        "notes": [
            {
                "id": str(note.id),
                "note": note.note,
                "note_type": note.note_type,
                "created_by_name": note.creator.name,
                "created_by_role": note.creator.role,
                "is_public": note.is_public,
                "created_at": note.created_at.isoformat()
            }
            for note in notes
        ]
    }


@router.post("/{complaint_id}/notes")
async def create_complaint_note(
    complaint_id: UUID,
    note_data: CaseNoteCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Create a note on a complaint
    Officials can mark as internal (is_public=False)
    """
    # Verify user has access to this complaint
    complaint = db.query(Complaint).filter(Complaint.id == complaint_id).first()
    if not complaint:
        raise HTTPException(404, "Complaint not found")
    
    # Citizens can only create public notes
    is_public = note_data.is_public
    if current_user.role == UserRole.CITIZEN:
        is_public = True
    
    note = CaseNote(
        complaint_id=complaint_id,
        note=note_data.note,
        note_type=note_data.note_type,
        created_by=current_user.id,
        is_public=is_public
    )
    
    db.add(note)
    db.commit()
    db.refresh(note)
    
    return {"message": "Note created", "id": str(note.id)}
```

**Frontend Component**:
```jsx
// /admin-dashboard/src/components/InternalNotesSection.jsx

import React, { useState } from 'react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { Lock, MessageSquare, Send } from 'lucide-react';
import { complaintsAPI } from '../services/api';
import { useAuth } from '../contexts/AuthContext';

export default function InternalNotesSection({ complaintId }) {
  const { user } = useAuth();
  const [newNote, setNewNote] = useState('');
  const [isInternal, setIsInternal] = useState(true);
  const queryClient = useQueryClient();

  const isOfficial = ['department_officer', 'moderator', 'mla', 'admin', 'pdo', 
                      'village_accountant', 'taluk_panchayat_officer'].includes(user?.role);

  // Fetch notes
  const { data: notesData } = useQuery({
    queryKey: ['complaint-notes', complaintId],
    queryFn: async () => {
      const response = await complaintsAPI.getNotes(complaintId);
      return response.data;
    }
  });

  // Create note mutation
  const createNoteMutation = useMutation({
    mutationFn: async (noteData) => {
      return complaintsAPI.createNote(complaintId, noteData);
    },
    onSuccess: () => {
      queryClient.invalidateQueries(['complaint-notes', complaintId]);
      setNewNote('');
    }
  });

  const handleSubmit = (e) => {
    e.preventDefault();
    if (!newNote.trim()) return;

    createNoteMutation.mutate({
      note: newNote,
      note_type: 'general',
      is_public: !isInternal
    });
  };

  const notes = notesData?.notes || [];
  const internalNotes = notes.filter(n => !n.is_public);
  const publicNotes = notes.filter(n => n.is_public);

  return (
    <div className="space-y-6">
      {/* Internal Notes Section - Officials Only */}
      {isOfficial && (
        <div className="bg-yellow-50 border-2 border-yellow-200 rounded-lg p-6">
          <div className="flex items-center gap-2 mb-4">
            <Lock className="h-5 w-5 text-yellow-700" />
            <h3 className="text-lg font-bold text-yellow-900">
              Internal Notes (Officials Only)
            </h3>
          </div>
          
          <p className="text-sm text-yellow-800 mb-4">
            These notes are visible only to officials, moderators, and MLA. Citizens cannot see them.
          </p>

          {/* Note Input Form */}
          <form onSubmit={handleSubmit} className="mb-6">
            <textarea
              value={newNote}
              onChange={(e) => setNewNote(e.target.value)}
              placeholder="Add internal note for officials..."
              className="w-full px-4 py-2 border rounded-lg focus:ring-2 focus:ring-yellow-500"
              rows={3}
            />
            <div className="mt-2 flex items-center justify-between">
              <label className="flex items-center gap-2 text-sm">
                <input
                  type="checkbox"
                  checked={isInternal}
                  onChange={(e) => setIsInternal(e.target.checked)}
                  className="rounded"
                />
                <span className="text-gray-700">
                  {isInternal ? (
                    <>
                      <Lock className="inline h-4 w-4 mr-1" />
                      Internal (Officials Only)
                    </>
                  ) : (
                    <>
                      <MessageSquare className="inline h-4 w-4 mr-1" />
                      Public (Visible to Citizen)
                    </>
                  )}
                </span>
              </label>
              <button
                type="submit"
                disabled={createNoteMutation.isLoading || !newNote.trim()}
                className="px-4 py-2 bg-yellow-600 text-white rounded-lg hover:bg-yellow-700 disabled:opacity-50 flex items-center gap-2"
              >
                <Send className="h-4 w-4" />
                Add Note
              </button>
            </div>
          </form>

          {/* Internal Notes List */}
          <div className="space-y-3">
            {internalNotes.length === 0 ? (
              <p className="text-sm text-gray-500 text-center py-4">
                No internal notes yet
              </p>
            ) : (
              internalNotes.map((note) => (
                <div key={note.id} className="bg-white rounded-lg p-4 border border-yellow-300">
                  <div className="flex items-start justify-between">
                    <div className="flex-1">
                      <div className="flex items-center gap-2 mb-1">
                        <span className="font-semibold text-gray-900">
                          {note.created_by_name}
                        </span>
                        <span className="text-xs px-2 py-0.5 rounded-full bg-gray-100 text-gray-600">
                          {note.created_by_role.replace('_', ' ')}
                        </span>
                        <Lock className="h-4 w-4 text-yellow-600" />
                      </div>
                      <p className="text-gray-700 whitespace-pre-wrap">{note.note}</p>
                    </div>
                    <span className="text-xs text-gray-500 ml-4">
                      {new Date(note.created_at).toLocaleString()}
                    </span>
                  </div>
                </div>
              ))
            )}
          </div>
        </div>
      )}

      {/* Public Communication Timeline */}
      <div className="bg-white border rounded-lg p-6">
        <h3 className="text-lg font-bold text-gray-900 mb-4">
          <MessageSquare className="inline h-5 w-5 mr-2" />
          Communication Timeline
        </h3>
        
        <div className="space-y-3">
          {publicNotes.length === 0 ? (
            <p className="text-sm text-gray-500 text-center py-4">
              No public updates yet
            </p>
          ) : (
            publicNotes.map((note) => (
              <div key={note.id} className="bg-gray-50 rounded-lg p-4 border border-gray-200">
                <div className="flex items-start justify-between">
                  <div className="flex-1">
                    <div className="flex items-center gap-2 mb-1">
                      <span className="font-semibold text-gray-900">
                        {note.created_by_name}
                      </span>
                      <span className="text-xs px-2 py-0.5 rounded-full bg-blue-100 text-blue-600">
                        {note.created_by_role.replace('_', ' ')}
                      </span>
                    </div>
                    <p className="text-gray-700 whitespace-pre-wrap">{note.note}</p>
                  </div>
                  <span className="text-xs text-gray-500 ml-4">
                    {new Date(note.created_at).toLocaleString()}
                  </span>
                </div>
              </div>
            ))
          )}
        </div>
      </div>
    </div>
  );
}
```

**Implementation Time**: 1 day (mostly frontend work, backend exists)

---

#### 4. **Backup Login Mechanism (Phone Broken)**

**Current Problem**:
- ✅ System uses phone number + OTP for login
- ❌ If phone is lost/broken, users cannot login
- ❌ No backup authentication method
- ❌ No admin override mechanism

**Solution Options**:

**Option 1: Email Backup**
```python
# Add email field to users table
ALTER TABLE users ADD COLUMN email VARCHAR(255);
CREATE INDEX idx_users_email ON users(email);

# Allow login with email + OTP sent to email
@router.post("/auth/login-email")
async def login_with_email(
    email: str = Body(...),
    db: Session = Depends(get_db)
):
    """
    Send OTP to email for backup login
    """
    user = db.query(User).filter(User.email == email).first()
    if not user:
        raise HTTPException(404, "User not found")
    
    # Generate OTP
    otp = generate_otp()
    
    # Store OTP in Redis/cache
    cache.set(f"email_otp:{email}", otp, ex=300)  # 5 min expiry
    
    # Send email
    send_email(
        to=email,
        subject="Janasamparka Login OTP",
        body=f"Your OTP is: {otp}. Valid for 5 minutes."
    )
    
    return {"message": "OTP sent to email"}
```

**Option 2: Admin Override/Reset**
```python
# Admin can generate temporary password for user
@router.post("/admin/users/{user_id}/reset-access")
async def admin_reset_user_access(
    user_id: UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Admin generates temporary access code for user with broken phone
    """
    if current_user.role != UserRole.ADMIN:
        raise HTTPException(403, "Admin only")
    
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(404, "User not found")
    
    # Generate temporary 6-digit code
    temp_code = str(random.randint(100000, 999999))
    
    # Store in database with expiry
    temp_access = TemporaryAccess(
        user_id=user_id,
        code=temp_code,
        expires_at=datetime.utcnow() + timedelta(hours=24),
        created_by=current_user.id
    )
    
    db.add(temp_access)
    db.commit()
    
    return {
        "message": "Temporary access code generated",
        "code": temp_code,
        "expires_at": temp_access.expires_at.isoformat(),
        "instructions": "User can login with this code at /login-with-code"
    }


@router.post("/auth/login-with-code")
async def login_with_temporary_code(
    phone: str = Body(...),
    code: str = Body(...),
    db: Session = Depends(get_db)
):
    """
    Login using admin-generated temporary code
    """
    user = db.query(User).filter(User.phone == phone).first()
    if not user:
        raise HTTPException(404, "User not found")
    
    # Check temporary access
    temp_access = db.query(TemporaryAccess).filter(
        TemporaryAccess.user_id == user.id,
        TemporaryAccess.code == code,
        TemporaryAccess.expires_at > datetime.utcnow(),
        TemporaryAccess.used_at.is_(None)
    ).first()
    
    if not temp_access:
        raise HTTPException(401, "Invalid or expired code")
    
    # Mark as used
    temp_access.used_at = datetime.utcnow()
    db.commit()
    
    # Generate JWT token
    token = create_access_token({"user_id": str(user.id)})
    
    return {
        "access_token": token,
        "token_type": "bearer",
        "user": user_to_dict(user)
    }
```

**Database Migration**:
```sql
-- Add email field
ALTER TABLE users ADD COLUMN email VARCHAR(255);
CREATE INDEX idx_users_email ON users(email);

-- Create temporary access table
CREATE TABLE temporary_access (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    code VARCHAR(10) NOT NULL,
    expires_at TIMESTAMP NOT NULL,
    used_at TIMESTAMP,
    created_by UUID NOT NULL REFERENCES users(id),
    created_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX idx_temporary_access_user ON temporary_access(user_id);
CREATE INDEX idx_temporary_access_code ON temporary_access(code);
```

**Frontend - Admin UI**:
```jsx
// /admin-dashboard/src/pages/Users.jsx

function UserResetAccessButton({ user }) {
  const [showModal, setShowModal] = useState(false);
  const [tempCode, setTempCode] = useState(null);

  const resetMutation = useMutation({
    mutationFn: async (userId) => {
      const response = await adminAPI.resetUserAccess(userId);
      return response.data;
    },
    onSuccess: (data) => {
      setTempCode(data.code);
    }
  });

  return (
    <>
      <button
        onClick={() => setShowModal(true)}
        className="text-sm text-blue-600 hover:text-blue-800"
      >
        Reset Access
      </button>

      {showModal && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
          <div className="bg-white rounded-lg p-6 max-w-md">
            <h3 className="text-lg font-bold mb-4">
              Reset Access for {user.name}
            </h3>
            
            {!tempCode ? (
              <>
                <p className="text-sm text-gray-600 mb-4">
                  This will generate a temporary code that {user.name} can use to login 
                  if their phone is lost or broken. The code is valid for 24 hours.
                </p>
                <div className="flex gap-2">
                  <button
                    onClick={() => resetMutation.mutate(user.id)}
                    className="px-4 py-2 bg-blue-600 text-white rounded hover:bg-blue-700"
                  >
                    Generate Code
                  </button>
                  <button
                    onClick={() => setShowModal(false)}
                    className="px-4 py-2 border rounded hover:bg-gray-50"
                  >
                    Cancel
                  </button>
                </div>
              </>
            ) : (
              <>
                <div className="bg-green-50 border-2 border-green-200 rounded-lg p-4 mb-4">
                  <p className="text-sm text-gray-700 mb-2">
                    Temporary Access Code:
                  </p>
                  <p className="text-3xl font-bold text-green-800 text-center tracking-wider">
                    {tempCode}
                  </p>
                  <p className="text-xs text-gray-600 mt-2 text-center">
                    Valid for 24 hours
                  </p>
                </div>
                
                <p className="text-sm text-gray-600 mb-4">
                  Share this code with {user.name}. They can login at:
                  <br />
                  <strong className="text-blue-600">
                    https://janasamparka.app/login-with-code
                  </strong>
                </p>
                
                <button
                  onClick={() => {
                    navigator.clipboard.writeText(tempCode);
                    alert('Code copied to clipboard!');
                  }}
                  className="w-full px-4 py-2 bg-blue-600 text-white rounded hover:bg-blue-700 mb-2"
                >
                  Copy Code
                </button>
                
                <button
                  onClick={() => {
                    setShowModal(false);
                    setTempCode(null);
                  }}
                  className="w-full px-4 py-2 border rounded hover:bg-gray-50"
                >
                  Close
                </button>
              </>
            )}
          </div>
        </div>
      )}
    </>
  );
}
```

**Implementation Time**: 2-3 days

---

### 🟠 **HIGH PRIORITY (P1) - Should Implement Soon**

#### 5. **Complete Citizen Portal** (20% → 100%)

**Currently Missing**:
- Citizen-specific dashboard
- My Complaints page
- Poll voting interface
- Ward information page
- Rating interface for completed work

**Implementation**: Follow the detailed guide in `IMPLEMENTATION_GUIDE_ROLE_PORTALS.md`

**Implementation Time**: 3-4 days

---

#### 6. **Officer Dashboard Personalization** (60% → 100%)

**Currently Missing**:
- Personal performance metrics (not system-wide)
- Leaderboard position among peers
- My stats vs department average
- Field officer tools

**Implementation**: Follow the detailed guide in `IMPLEMENTATION_GUIDE_ROLE_PORTALS.md`

**Implementation Time**: 2-3 days

---

### 🟡 **MEDIUM PRIORITY (P2) - Future Enhancements**

#### 7. **Moderator Triage Center** (70% → 100%)
- Bulk assignment interface
- Duplicate detection alerts
- Quality review workflow

**Implementation Time**: 2-3 days

#### 8. **Advanced Analytics**
- Predictive analytics for complaint trends
- Resource allocation recommendations
- Seasonal forecasting

**Implementation Time**: 3-4 days

#### 9. **Mobile App Enhancements**
- Role-specific screens
- Officer field tools
- Offline mode

**Implementation Time**: 5-7 days

---

## 📅 **RECOMMENDED IMPLEMENTATION ROADMAP**

### **Week 1-2: Critical Features (P0)**
- Days 1-4: MLA Performance Dashboard with Comparative Analytics
- Days 5-6: Citizen Satisfaction Index + Moderator Intervention
- Day 7: Internal Notes UI
- Days 8-10: Backup Login Mechanism

### **Week 3-4: High Priority Features (P1)**
- Days 1-4: Complete Citizen Portal
- Days 5-7: Officer Dashboard Personalization
- Days 8-10: Testing & Bug Fixes

### **Week 5+: Medium Priority (P2)**
- Moderator Triage Center
- Advanced Analytics
- Mobile App Enhancements

---

## 📊 **SYSTEM HEALTH SUMMARY**

**Overall Status**: **85% Production Ready**

### **What Works Well** ✅
- Multi-tenancy architecture (100%)
- Panchayat Raj integration (100%)
- Core complaint management (95%)
- Authentication & security (90%)
- GIS & mapping (100%)
- Analytics & reporting (85%)

### **What Needs Attention** ⚠️
- MLA performance dashboard (needs comparative analytics)
- Citizen satisfaction tracking (needs aggregation + intervention workflow)
- Internal notes (backend ready, needs UI)
- Backup login (critical for phone loss scenarios)
- Citizen portal (only 20% complete)
- Officer personalization (only 60% complete)

### **System Stability**: **STABLE** ✅
- All 3 Docker containers healthy
- Backend responding correctly
- Frontend HMR active
- 40 test users created
- Database migrations complete

---

## 🎯 **NEXT STEPS**

1. ✅ **Read** this document completely
2. ✅ **Review** IMPLEMENTATION_GUIDE_ROLE_PORTALS.md for citizen/officer portals
3. ✅ **Prioritize** which features to implement first (recommend P0)
4. ✅ **Start** with MLA Performance Dashboard (highest impact)
5. ✅ **Test** thoroughly with existing test users
6. ✅ **Deploy** to staging after each major feature

---

## 📞 **SUPPORT**

For questions or clarifications on this document:
- **Backend Issues**: Check `/backend/app/routers/` and `/backend/app/models/`
- **Frontend Issues**: Check `/admin-dashboard/src/pages/` and `/admin-dashboard/src/components/`
- **Database Issues**: Check `/backend/migrations/`
- **Documentation**: All `.md` files in project root

---

**Document Version**: 1.0  
**Last Updated**: October 30, 2025  
**Status**: Ready for Implementation  
**Next Review**: After P0 features completion
