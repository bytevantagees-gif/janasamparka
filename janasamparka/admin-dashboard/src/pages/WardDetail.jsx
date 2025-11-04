import { useParams, Link } from 'react-router-dom';
import { useQuery } from '@tanstack/react-query';
import { 
  ArrowLeft, 
  MapPin, 
  Users, 
  Building2,
  TrendingUp,
  AlertCircle,
  Edit2,
  Map as MapIcon,
  BarChart3
} from 'lucide-react';

function WardDetail() {
  const { id } = useParams();

  // Mock data - replace with actual API call
  const { data, isLoading } = useQuery({
    queryKey: ['ward', id],
    queryFn: async () => {
      return {
        data: {
          id: id,
          ward_number: 1,
          ward_name: 'MG Road Ward',
          locality: 'MG Road, City Center',
          total_population: 12500,
          total_households: 3200,
          area_sq_km: 2.5,
          constituency_name: 'Puttur',
          constituency_id: 'const-1',
          description: 'Central ward covering the main commercial area including MG Road, shopping complexes, and office buildings.',
          
          // Demographics
          demographics: {
            male_population: 6300,
            female_population: 6200,
            age_0_18: 3200,
            age_19_35: 4500,
            age_36_60: 3800,
            age_above_60: 1000,
          },

          // Infrastructure
          infrastructure: {
            schools: 3,
            hospitals: 2,
            police_stations: 1,
            fire_stations: 1,
            parks: 5,
            community_centers: 2,
          },

          // Complaints Statistics
          complaints_stats: {
            total: 45,
            submitted: 12,
            under_review: 8,
            in_progress: 15,
            resolved: 8,
            rejected: 2,
          },

          // Category-wise complaints
          complaints_by_category: [
            { category: 'Road & Infrastructure', count: 15 },
            { category: 'Water Supply', count: 10 },
            { category: 'Electricity', count: 8 },
            { category: 'Sanitation', count: 7 },
            { category: 'Other', count: 5 },
          ],

          // Recent activities
          recent_complaints: [
            {
              id: 'c1',
              title: 'Pothole on MG Road',
              status: 'in_progress',
              created_at: '2025-10-25T10:30:00',
            },
            {
              id: 'c2',
              title: 'Street light not working',
              status: 'submitted',
              created_at: '2025-10-26T15:45:00',
            },
            {
              id: 'c3',
              title: 'Water leakage',
              status: 'under_review',
              created_at: '2025-10-27T09:20:00',
            },
          ],

          // Boundaries (for map)
          boundary: {
            type: 'Polygon',
            coordinates: [[12.7644, 75.4088], [12.7655, 75.4099]],
          },
        },
      };
    },
  });

  const ward = data?.data;

  if (isLoading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="text-center">
          <div className="inline-block animate-spin rounded-full h-8 w-8 border-b-2 border-primary-600"></div>
          <p className="mt-2 text-sm text-gray-500">Loading ward details...</p>
        </div>
      </div>
    );
  }

  if (!ward) {
    return (
      <div className="space-y-4">
        <Link
          to="/wards"
          className="inline-flex items-center text-sm font-medium text-gray-500 hover:text-gray-700"
        >
          <ArrowLeft className="mr-2 h-4 w-4" />
          Back to Wards
        </Link>
        <div className="rounded-md bg-red-50 p-4">
          <p className="text-sm text-red-800">Ward not found</p>
        </div>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Back Button */}
      <Link
        to="/wards"
        className="inline-flex items-center text-sm font-medium text-gray-500 hover:text-gray-700"
      >
        <ArrowLeft className="mr-2 h-4 w-4" />
        Back to Wards
      </Link>

      {/* Header */}
      <div className="bg-white shadow rounded-lg p-6">
        <div className="flex items-start justify-between">
          <div className="flex items-center">
            <div className="flex-shrink-0 h-16 w-16 bg-primary-100 rounded-lg flex items-center justify-center">
              <span className="text-2xl font-bold text-primary-700">{ward.ward_number}</span>
            </div>
            <div className="ml-4">
              <h1 className="text-2xl font-bold text-gray-900">{ward.ward_name}</h1>
              <p className="mt-1 text-sm text-gray-500">{ward.constituency_name}</p>
              <div className="mt-2 flex items-center text-sm text-gray-600">
                <MapPin className="mr-1 h-4 w-4 text-gray-400" />
                {ward.locality}
              </div>
            </div>
          </div>
          <button className="inline-flex items-center px-4 py-2 border border-gray-300 shadow-sm text-sm font-medium rounded-md text-gray-700 bg-white hover:bg-gray-50">
            <Edit2 className="mr-2 h-4 w-4" />
            Edit Ward
          </button>
        </div>

        {ward.description && (
          <p className="mt-4 text-gray-600">{ward.description}</p>
        )}
      </div>

      {/* Statistics Grid */}
      <div className="grid grid-cols-1 gap-5 sm:grid-cols-2 lg:grid-cols-4">
        <div className="bg-white overflow-hidden shadow rounded-lg">
          <div className="p-5">
            <div className="flex items-center">
              <div className="flex-shrink-0">
                <Users className="h-6 w-6 text-blue-600" />
              </div>
              <div className="ml-5 w-0 flex-1">
                <dl>
                  <dt className="text-sm font-medium text-gray-500 truncate">Population</dt>
                  <dd className="text-lg font-semibold text-gray-900">
                    {ward.total_population.toLocaleString('en-IN')}
                  </dd>
                </dl>
              </div>
            </div>
          </div>
        </div>

        <div className="bg-white overflow-hidden shadow rounded-lg">
          <div className="p-5">
            <div className="flex items-center">
              <div className="flex-shrink-0">
                <Building2 className="h-6 w-6 text-green-600" />
              </div>
              <div className="ml-5 w-0 flex-1">
                <dl>
                  <dt className="text-sm font-medium text-gray-500 truncate">Households</dt>
                  <dd className="text-lg font-semibold text-gray-900">
                    {ward.total_households.toLocaleString('en-IN')}
                  </dd>
                </dl>
              </div>
            </div>
          </div>
        </div>

        <div className="bg-white overflow-hidden shadow rounded-lg">
          <div className="p-5">
            <div className="flex items-center">
              <div className="flex-shrink-0">
                <MapIcon className="h-6 w-6 text-purple-600" />
              </div>
              <div className="ml-5 w-0 flex-1">
                <dl>
                  <dt className="text-sm font-medium text-gray-500 truncate">Area</dt>
                  <dd className="text-lg font-semibold text-gray-900">{ward.area_sq_km} km²</dd>
                </dl>
              </div>
            </div>
          </div>
        </div>

        <div className="bg-white overflow-hidden shadow rounded-lg">
          <div className="p-5">
            <div className="flex items-center">
              <div className="flex-shrink-0">
                <TrendingUp className="h-6 w-6 text-yellow-600" />
              </div>
              <div className="ml-5 w-0 flex-1">
                <dl>
                  <dt className="text-sm font-medium text-gray-500 truncate">Complaints</dt>
                  <dd className="text-lg font-semibold text-gray-900">
                    {ward.complaints_stats.total}
                  </dd>
                </dl>
              </div>
            </div>
          </div>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Main Content */}
        <div className="lg:col-span-2 space-y-6">
          {/* Demographics */}
          <div className="bg-white shadow rounded-lg p-6">
            <h2 className="text-lg font-medium text-gray-900 mb-4 flex items-center">
              <Users className="mr-2 h-5 w-5 text-gray-400" />
              Demographics
            </h2>
            <div className="grid grid-cols-2 gap-4">
              <div>
                <p className="text-sm text-gray-500">Male</p>
                <p className="text-lg font-semibold text-gray-900">
                  {ward.demographics.male_population.toLocaleString('en-IN')}
                </p>
              </div>
              <div>
                <p className="text-sm text-gray-500">Female</p>
                <p className="text-lg font-semibold text-gray-900">
                  {ward.demographics.female_population.toLocaleString('en-IN')}
                </p>
              </div>
              <div>
                <p className="text-sm text-gray-500">Age 0-18</p>
                <p className="text-lg font-semibold text-gray-900">
                  {ward.demographics.age_0_18.toLocaleString('en-IN')}
                </p>
              </div>
              <div>
                <p className="text-sm text-gray-500">Age 19-35</p>
                <p className="text-lg font-semibold text-gray-900">
                  {ward.demographics.age_19_35.toLocaleString('en-IN')}
                </p>
              </div>
              <div>
                <p className="text-sm text-gray-500">Age 36-60</p>
                <p className="text-lg font-semibold text-gray-900">
                  {ward.demographics.age_36_60.toLocaleString('en-IN')}
                </p>
              </div>
              <div>
                <p className="text-sm text-gray-500">Above 60</p>
                <p className="text-lg font-semibold text-gray-900">
                  {ward.demographics.age_above_60.toLocaleString('en-IN')}
                </p>
              </div>
            </div>
          </div>

          {/* Infrastructure */}
          <div className="bg-white shadow rounded-lg p-6">
            <h2 className="text-lg font-medium text-gray-900 mb-4 flex items-center">
              <Building2 className="mr-2 h-5 w-5 text-gray-400" />
              Infrastructure
            </h2>
            <div className="grid grid-cols-3 gap-4">
              {Object.entries(ward.infrastructure).map(([key, value]) => (
                <div key={key}>
                  <p className="text-sm text-gray-500 capitalize">{key.replace(/_/g, ' ')}</p>
                  <p className="text-lg font-semibold text-gray-900">{value}</p>
                </div>
              ))}
            </div>
          </div>

          {/* Complaints by Category */}
          <div className="bg-white shadow rounded-lg p-6">
            <h2 className="text-lg font-medium text-gray-900 mb-4 flex items-center">
              <BarChart3 className="mr-2 h-5 w-5 text-gray-400" />
              Complaints by Category
            </h2>
            <div className="space-y-3">
              {ward.complaints_by_category.map((item) => (
                <div key={item.category}>
                  <div className="flex items-center justify-between mb-1">
                    <span className="text-sm text-gray-600">{item.category}</span>
                    <span className="text-sm font-semibold text-gray-900">{item.count}</span>
                  </div>
                  <div className="w-full bg-gray-200 rounded-full h-2">
                    <div
                      className="bg-primary-600 h-2 rounded-full"
                      style={{ 
                        width: `${(item.count / ward.complaints_stats.total) * 100}%` 
                      }}
                    ></div>
                  </div>
                </div>
              ))}
            </div>
          </div>
        </div>

        {/* Sidebar */}
        <div className="space-y-6">
          {/* Complaints Status */}
          <div className="bg-white shadow rounded-lg p-6">
            <h2 className="text-lg font-medium text-gray-900 mb-4">Complaint Status</h2>
            <div className="space-y-3">
              <div className="flex justify-between items-center">
                <span className="text-sm text-gray-600">Submitted</span>
                <span className="text-sm font-semibold text-blue-600">
                  {ward.complaints_stats.submitted}
                </span>
              </div>
              <div className="flex justify-between items-center">
                <span className="text-sm text-gray-600">Under Review</span>
                <span className="text-sm font-semibold text-yellow-600">
                  {ward.complaints_stats.under_review}
                </span>
              </div>
              <div className="flex justify-between items-center">
                <span className="text-sm text-gray-600">In Progress</span>
                <span className="text-sm font-semibold text-purple-600">
                  {ward.complaints_stats.in_progress}
                </span>
              </div>
              <div className="flex justify-between items-center">
                <span className="text-sm text-gray-600">Resolved</span>
                <span className="text-sm font-semibold text-green-600">
                  {ward.complaints_stats.resolved}
                </span>
              </div>
              <div className="flex justify-between items-center">
                <span className="text-sm text-gray-600">Rejected</span>
                <span className="text-sm font-semibold text-red-600">
                  {ward.complaints_stats.rejected}
                </span>
              </div>
            </div>
          </div>

          {/* Recent Complaints */}
          <div className="bg-white shadow rounded-lg p-6">
            <h2 className="text-lg font-medium text-gray-900 mb-4">Recent Complaints</h2>
            <div className="space-y-3">
              {ward.recent_complaints.map((complaint) => (
                <Link
                  key={complaint.id}
                  to={`/complaints/${complaint.id}`}
                  className="block p-3 hover:bg-gray-50 rounded-lg transition-colors"
                >
                  <p className="text-sm font-medium text-gray-900">{complaint.title}</p>
                  <div className="mt-1 flex items-center justify-between">
                    <span className="text-xs text-gray-500">
                      {new Date(complaint.created_at).toLocaleDateString('en-IN', {
                        month: 'short',
                        day: 'numeric',
                      })}
                    </span>
                    <span className={`text-xs px-2 py-0.5 rounded-full ${
                      complaint.status === 'resolved' ? 'bg-green-100 text-green-800' :
                      complaint.status === 'in_progress' ? 'bg-purple-100 text-purple-800' :
                      complaint.status === 'under_review' ? 'bg-yellow-100 text-yellow-800' :
                      'bg-blue-100 text-blue-800'
                    }`}>
                      {complaint.status.replace('_', ' ')}
                    </span>
                  </div>
                </Link>
              ))}
            </div>
            <Link
              to={`/complaints?ward=${ward.id}`}
              className="mt-4 block text-center text-sm font-medium text-primary-600 hover:text-primary-700"
            >
              View All Complaints →
            </Link>
          </div>

          {/* Quick Actions */}
          <div className="bg-white shadow rounded-lg p-6">
            <h2 className="text-lg font-medium text-gray-900 mb-4">Quick Actions</h2>
            <div className="space-y-2">
              <button className="w-full px-4 py-2 bg-primary-600 text-white rounded-lg hover:bg-primary-700">
                View on Map
              </button>
              <button className="w-full px-4 py-2 bg-white text-gray-700 border border-gray-300 rounded-lg hover:bg-gray-50">
                Export Data
              </button>
              <button className="w-full px-4 py-2 bg-white text-gray-700 border border-gray-300 rounded-lg hover:bg-gray-50">
                Generate Report
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}

export default WardDetail;
