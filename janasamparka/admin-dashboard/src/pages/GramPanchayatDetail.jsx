import { useParams, Link } from 'react-router-dom';
import { useQuery } from '@tanstack/react-query';
import { 
  ArrowLeft, 
  Building2, 
  Users, 
  MapPin, 
  Phone, 
  Mail,
  Calendar,
  Activity,
  Home,
  FileText,
  CheckCircle,
  Clock,
  Layers
} from 'lucide-react';
import { panchayatsAPI } from '../services/api';

function GramPanchayatDetail() {
  const { id } = useParams();

  const { data: gp, isLoading, error } = useQuery({
    queryKey: ['gram-panchayat', id],
    queryFn: async () => {
      const response = await panchayatsAPI.getGP(id);
      return response.data;
    },
  });

  if (isLoading) {
    return (
      <div className="p-6">
        <div className="animate-pulse">
          <div className="h-8 bg-gray-200 rounded w-1/4 mb-4"></div>
          <div className="h-64 bg-gray-200 rounded"></div>
        </div>
      </div>
    );
  }

  if (error || !gp) {
    return (
      <div className="p-6">
        <div className="bg-red-50 border border-red-200 rounded-lg p-4">
          <p className="text-red-800">Failed to load Gram Panchayat details</p>
        </div>
      </div>
    );
  }

  return (
    <div className="p-6 space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div className="flex items-center space-x-4">
          <Link
            to="/panchayats"
            className="p-2 hover:bg-gray-100 rounded-lg transition-colors"
          >
            <ArrowLeft className="h-5 w-5" />
          </Link>
          <div>
            <h1 className="text-2xl font-bold text-gray-900">{gp.name}</h1>
            <p className="text-sm text-gray-500">Gram Panchayat Details</p>
            <div className="flex items-center space-x-2 mt-1 text-xs text-gray-400">
              {gp.taluk_panchayat_name && (
                <>
                  <span className="flex items-center">
                    <Building2 className="h-3 w-3 mr-1" />
                    {gp.taluk_panchayat_name}
                  </span>
                  {gp.zilla_panchayat_name && (
                    <>
                      <span>→</span>
                      <span className="flex items-center">
                        <Layers className="h-3 w-3 mr-1" />
                        {gp.zilla_panchayat_name}
                      </span>
                    </>
                  )}
                </>
              )}
            </div>
          </div>
        </div>
        <div className={`px-3 py-1 rounded-full text-sm font-medium ${
          gp.is_active 
            ? 'bg-green-100 text-green-800' 
            : 'bg-gray-100 text-gray-800'
        }`}>
          {gp.is_active ? 'Active' : 'Inactive'}
        </div>
      </div>

      {/* Statistics Cards */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
        <div className="bg-gradient-to-br from-green-500 to-green-600 rounded-lg p-6 text-white">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-green-100 text-sm font-medium">Population</p>
              <p className="text-3xl font-bold mt-2">
                {gp.population?.toLocaleString() || 'N/A'}
              </p>
            </div>
            <Users className="h-12 w-12 text-green-200" />
          </div>
        </div>

        <div className="bg-gradient-to-br from-blue-500 to-blue-600 rounded-lg p-6 text-white">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-blue-100 text-sm font-medium">Households</p>
              <p className="text-3xl font-bold mt-2">
                {gp.households?.toLocaleString() || 'N/A'}
              </p>
            </div>
            <Home className="h-12 w-12 text-blue-200" />
          </div>
        </div>

        <div className="bg-gradient-to-br from-purple-500 to-purple-600 rounded-lg p-6 text-white">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-purple-100 text-sm font-medium">Total Users</p>
              <p className="text-3xl font-bold mt-2">
                {gp.total_users || '0'}
              </p>
            </div>
            <Users className="h-12 w-12 text-purple-200" />
          </div>
        </div>

        <div className="bg-gradient-to-br from-orange-500 to-orange-600 rounded-lg p-6 text-white">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-orange-100 text-sm font-medium">Submissions</p>
              <p className="text-3xl font-bold mt-2">
                {gp.total_submissions || '0'}
              </p>
              <p className="text-xs text-orange-100 mt-1">
                {gp.pending_submissions || '0'} pending
              </p>
            </div>
            <FileText className="h-12 w-12 text-orange-200" />
          </div>
        </div>
      </div>

      {/* Main Information */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Basic Details */}
        <div className="bg-white rounded-lg shadow p-6">
          <h2 className="text-lg font-semibold text-gray-900 mb-4 flex items-center">
            <Activity className="h-5 w-5 mr-2 text-green-600" />
            Basic Information
          </h2>
          <dl className="space-y-3">
            <div>
              <dt className="text-sm font-medium text-gray-500">Code</dt>
              <dd className="mt-1 text-sm text-gray-900 font-mono">{gp.code}</dd>
            </div>
            <div>
              <dt className="text-sm font-medium text-gray-500">Village Name</dt>
              <dd className="mt-1 text-sm text-gray-900">{gp.village_name || gp.name}</dd>
            </div>
            <div>
              <dt className="text-sm font-medium text-gray-500">Constituency</dt>
              <dd className="mt-1 text-sm text-gray-900">
                {gp.constituency_name || 'N/A'}
                {gp.mla_name && (
                  <span className="block text-xs text-gray-500 mt-1">
                    MLA: {gp.mla_name}
                  </span>
                )}
              </dd>
            </div>
            <div>
              <dt className="text-sm font-medium text-gray-500">Established</dt>
              <dd className="mt-1 text-sm text-gray-900 flex items-center">
                <Calendar className="h-4 w-4 mr-1 text-gray-400" />
                {gp.established_date ? new Date(gp.established_date).toLocaleDateString() : 'N/A'}
              </dd>
            </div>
          </dl>
        </div>

        {/* Leadership */}
        <div className="bg-white rounded-lg shadow p-6">
          <h2 className="text-lg font-semibold text-gray-900 mb-4 flex items-center">
            <Users className="h-5 w-5 mr-2 text-green-600" />
            Leadership
          </h2>
          <dl className="space-y-3">
            <div>
              <dt className="text-sm font-medium text-gray-500">President</dt>
              <dd className="mt-1 text-sm text-gray-900">{gp.president_name || 'N/A'}</dd>
            </div>
            <div>
              <dt className="text-sm font-medium text-gray-500">Vice President</dt>
              <dd className="mt-1 text-sm text-gray-900">{gp.vice_president_name || 'N/A'}</dd>
            </div>
            <div>
              <dt className="text-sm font-medium text-gray-500">PDO (Panchayat Development Officer)</dt>
              <dd className="mt-1 text-sm text-gray-900">{gp.pdo_name || 'N/A'}</dd>
            </div>
            <div>
              <dt className="text-sm font-medium text-gray-500">Village Accountant</dt>
              <dd className="mt-1 text-sm text-gray-900">{gp.village_accountant_name || 'N/A'}</dd>
            </div>
          </dl>
        </div>

        {/* Contact Information */}
        <div className="bg-white rounded-lg shadow p-6">
          <h2 className="text-lg font-semibold text-gray-900 mb-4 flex items-center">
            <Phone className="h-5 w-5 mr-2 text-green-600" />
            Contact Information
          </h2>
          <dl className="space-y-3">
            <div>
              <dt className="text-sm font-medium text-gray-500">Office Phone</dt>
              <dd className="mt-1 text-sm text-gray-900 flex items-center">
                <Phone className="h-4 w-4 mr-2 text-gray-400" />
                {gp.office_phone || 'N/A'}
              </dd>
            </div>
            <div>
              <dt className="text-sm font-medium text-gray-500">Email</dt>
              <dd className="mt-1 text-sm text-gray-900 flex items-center">
                <Mail className="h-4 w-4 mr-2 text-gray-400" />
                {gp.email || 'N/A'}
              </dd>
            </div>
            <div>
              <dt className="text-sm font-medium text-gray-500">Office Address</dt>
              <dd className="mt-1 text-sm text-gray-900 flex items-start">
                <MapPin className="h-4 w-4 mr-2 text-gray-400 mt-0.5" />
                <span>{gp.office_address || 'N/A'}</span>
              </dd>
            </div>
          </dl>
        </div>

        {/* Demographics & Statistics */}
        <div className="bg-white rounded-lg shadow p-6">
          <h2 className="text-lg font-semibold text-gray-900 mb-4 flex items-center">
            <Activity className="h-5 w-5 mr-2 text-green-600" />
            Demographics
          </h2>
          <dl className="space-y-3">
            <div>
              <dt className="text-sm font-medium text-gray-500">Total Wards</dt>
              <dd className="mt-1 text-sm text-gray-900">{gp.total_wards || 'N/A'}</dd>
            </div>
            <div>
              <dt className="text-sm font-medium text-gray-500">Area</dt>
              <dd className="mt-1 text-sm text-gray-900">
                {gp.area_sq_km ? `${gp.area_sq_km} km²` : 'N/A'}
              </dd>
            </div>
            <div>
              <dt className="text-sm font-medium text-gray-500">Literacy Rate</dt>
              <dd className="mt-1 text-sm text-gray-900">
                {gp.literacy_rate ? `${gp.literacy_rate}%` : 'N/A'}
              </dd>
            </div>
            <div>
              <dt className="text-sm font-medium text-gray-500">Male Population</dt>
              <dd className="mt-1 text-sm text-gray-900">
                {gp.male_population?.toLocaleString() || 'N/A'}
              </dd>
            </div>
            <div>
              <dt className="text-sm font-medium text-gray-500">Female Population</dt>
              <dd className="mt-1 text-sm text-gray-900">
                {gp.female_population?.toLocaleString() || 'N/A'}
              </dd>
            </div>
          </dl>
        </div>
      </div>

      {/* Activity Summary */}
      {(gp.total_submissions > 0 || gp.total_users > 0) && (
        <div className="bg-white rounded-lg shadow p-6">
          <h2 className="text-lg font-semibold text-gray-900 mb-4 flex items-center">
            <FileText className="h-5 w-5 mr-2 text-green-600" />
            Activity Summary
          </h2>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <div className="p-4 bg-blue-50 rounded-lg">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm text-blue-600 font-medium">Registered Users</p>
                  <p className="text-2xl font-bold text-blue-900 mt-1">
                    {gp.total_users || '0'}
                  </p>
                </div>
                <Users className="h-8 w-8 text-blue-400" />
              </div>
            </div>

            <div className="p-4 bg-green-50 rounded-lg">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm text-green-600 font-medium">Total Submissions</p>
                  <p className="text-2xl font-bold text-green-900 mt-1">
                    {gp.total_submissions || '0'}
                  </p>
                </div>
                <CheckCircle className="h-8 w-8 text-green-400" />
              </div>
            </div>

            <div className="p-4 bg-orange-50 rounded-lg">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm text-orange-600 font-medium">Pending</p>
                  <p className="text-2xl font-bold text-orange-900 mt-1">
                    {gp.pending_submissions || '0'}
                  </p>
                </div>
                <Clock className="h-8 w-8 text-orange-400" />
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}

export default GramPanchayatDetail;
