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
  TrendingUp
} from 'lucide-react';
import { panchayatsAPI } from '../services/api';

function ZillaPanchayatDetail() {
  const { id } = useParams();

  const { data: zp, isLoading, error } = useQuery({
    queryKey: ['zilla-panchayat', id],
    queryFn: async () => {
      const response = await panchayatsAPI.getZP(id);
      return response.data;
    },
  });

  const { data: tpData } = useQuery({
    queryKey: ['taluk-panchayats', id],
    queryFn: async () => {
      const response = await panchayatsAPI.getAllTP({ zilla_panchayat_id: id });
      return response.data;
    },
  });

  const talukPanchayats = tpData || [];

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

  if (error || !zp) {
    return (
      <div className="p-6">
        <div className="bg-red-50 border border-red-200 rounded-lg p-4">
          <p className="text-red-800">Failed to load Zilla Panchayat details</p>
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
            <h1 className="text-2xl font-bold text-gray-900">{zp.name}</h1>
            <p className="text-sm text-gray-500">Zilla Panchayat Details</p>
          </div>
        </div>
        <div className={`px-3 py-1 rounded-full text-sm font-medium ${
          zp.is_active 
            ? 'bg-green-100 text-green-800' 
            : 'bg-gray-100 text-gray-800'
        }`}>
          {zp.is_active ? 'Active' : 'Inactive'}
        </div>
      </div>

      {/* Statistics Cards */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
        <div className="bg-gradient-to-br from-purple-500 to-purple-600 rounded-lg p-6 text-white">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-purple-100 text-sm font-medium">Total Population</p>
              <p className="text-3xl font-bold mt-2">
                {zp.total_population?.toLocaleString() || 'N/A'}
              </p>
            </div>
            <Users className="h-12 w-12 text-purple-200" />
          </div>
        </div>

        <div className="bg-gradient-to-br from-blue-500 to-blue-600 rounded-lg p-6 text-white">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-blue-100 text-sm font-medium">Taluk Panchayats</p>
              <p className="text-3xl font-bold mt-2">
                {zp.taluk_panchayats_count || talukPanchayats.length}
              </p>
            </div>
            <Building2 className="h-12 w-12 text-blue-200" />
          </div>
        </div>

        <div className="bg-gradient-to-br from-green-500 to-green-600 rounded-lg p-6 text-white">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-green-100 text-sm font-medium">Gram Panchayats</p>
              <p className="text-3xl font-bold mt-2">
                {zp.gram_panchayats_count || 'N/A'}
              </p>
            </div>
            <Home className="h-12 w-12 text-green-200" />
          </div>
        </div>

        <div className="bg-gradient-to-br from-orange-500 to-orange-600 rounded-lg p-6 text-white">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-orange-100 text-sm font-medium">Area</p>
              <p className="text-3xl font-bold mt-2">
                {zp.area_sq_km ? `${zp.area_sq_km} km²` : 'N/A'}
              </p>
            </div>
            <MapPin className="h-12 w-12 text-orange-200" />
          </div>
        </div>
      </div>

      {/* Main Information */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Basic Details */}
        <div className="bg-white rounded-lg shadow p-6">
          <h2 className="text-lg font-semibold text-gray-900 mb-4 flex items-center">
            <Activity className="h-5 w-5 mr-2 text-purple-600" />
            Basic Information
          </h2>
          <dl className="space-y-3">
            <div>
              <dt className="text-sm font-medium text-gray-500">Code</dt>
              <dd className="mt-1 text-sm text-gray-900 font-mono">{zp.code}</dd>
            </div>
            <div>
              <dt className="text-sm font-medium text-gray-500">District</dt>
              <dd className="mt-1 text-sm text-gray-900">{zp.district}</dd>
            </div>
            <div>
              <dt className="text-sm font-medium text-gray-500">Headquarters</dt>
              <dd className="mt-1 text-sm text-gray-900">{zp.headquarters || 'N/A'}</dd>
            </div>
            <div>
              <dt className="text-sm font-medium text-gray-500">Established</dt>
              <dd className="mt-1 text-sm text-gray-900 flex items-center">
                <Calendar className="h-4 w-4 mr-1 text-gray-400" />
                {zp.established_date ? new Date(zp.established_date).toLocaleDateString() : 'N/A'}
              </dd>
            </div>
          </dl>
        </div>

        {/* Leadership */}
        <div className="bg-white rounded-lg shadow p-6">
          <h2 className="text-lg font-semibold text-gray-900 mb-4 flex items-center">
            <Users className="h-5 w-5 mr-2 text-purple-600" />
            Leadership
          </h2>
          <dl className="space-y-3">
            <div>
              <dt className="text-sm font-medium text-gray-500">President</dt>
              <dd className="mt-1 text-sm text-gray-900">{zp.president_name || 'N/A'}</dd>
            </div>
            <div>
              <dt className="text-sm font-medium text-gray-500">Vice President</dt>
              <dd className="mt-1 text-sm text-gray-900">{zp.vice_president_name || 'N/A'}</dd>
            </div>
            <div>
              <dt className="text-sm font-medium text-gray-500">Chief Executive Officer</dt>
              <dd className="mt-1 text-sm text-gray-900">{zp.ceo_name || 'N/A'}</dd>
            </div>
          </dl>
        </div>

        {/* Contact Information */}
        <div className="bg-white rounded-lg shadow p-6">
          <h2 className="text-lg font-semibold text-gray-900 mb-4 flex items-center">
            <Phone className="h-5 w-5 mr-2 text-purple-600" />
            Contact Information
          </h2>
          <dl className="space-y-3">
            <div>
              <dt className="text-sm font-medium text-gray-500">Office Phone</dt>
              <dd className="mt-1 text-sm text-gray-900 flex items-center">
                <Phone className="h-4 w-4 mr-2 text-gray-400" />
                {zp.office_phone || 'N/A'}
              </dd>
            </div>
            <div>
              <dt className="text-sm font-medium text-gray-500">Email</dt>
              <dd className="mt-1 text-sm text-gray-900 flex items-center">
                <Mail className="h-4 w-4 mr-2 text-gray-400" />
                {zp.email || 'N/A'}
              </dd>
            </div>
            <div>
              <dt className="text-sm font-medium text-gray-500">Office Address</dt>
              <dd className="mt-1 text-sm text-gray-900 flex items-start">
                <MapPin className="h-4 w-4 mr-2 text-gray-400 mt-0.5" />
                <span>{zp.office_address || 'N/A'}</span>
              </dd>
            </div>
          </dl>
        </div>

        {/* Statistics */}
        <div className="bg-white rounded-lg shadow p-6">
          <h2 className="text-lg font-semibold text-gray-900 mb-4 flex items-center">
            <TrendingUp className="h-5 w-5 mr-2 text-purple-600" />
            Demographics
          </h2>
          <dl className="space-y-3">
            <div>
              <dt className="text-sm font-medium text-gray-500">Total Villages</dt>
              <dd className="mt-1 text-sm text-gray-900">{zp.total_villages || 'N/A'}</dd>
            </div>
            <div>
              <dt className="text-sm font-medium text-gray-500">Literacy Rate</dt>
              <dd className="mt-1 text-sm text-gray-900">
                {zp.literacy_rate ? `${zp.literacy_rate}%` : 'N/A'}
              </dd>
            </div>
            <div>
              <dt className="text-sm font-medium text-gray-500">Total Wards</dt>
              <dd className="mt-1 text-sm text-gray-900">{zp.total_wards || 'N/A'}</dd>
            </div>
          </dl>
        </div>
      </div>

      {/* Taluk Panchayats List */}
      <div className="bg-white rounded-lg shadow">
        <div className="p-6 border-b border-gray-200">
          <h2 className="text-lg font-semibold text-gray-900 flex items-center">
            <Building2 className="h-5 w-5 mr-2 text-blue-600" />
            Taluk Panchayats ({talukPanchayats.length})
          </h2>
        </div>
        <div className="divide-y divide-gray-200">
          {talukPanchayats.length === 0 ? (
            <div className="p-6 text-center text-gray-500">
              No Taluk Panchayats found
            </div>
          ) : (
            talukPanchayats.map((tp) => (
              <Link
                key={tp.id}
                to={`/panchayats/taluk/${tp.id}`}
                className="p-6 hover:bg-gray-50 transition-colors block"
              >
                <div className="flex items-center justify-between">
                  <div className="flex items-center space-x-4">
                    <div className="p-3 bg-blue-100 rounded-lg">
                      <Building2 className="h-6 w-6 text-blue-600" />
                    </div>
                    <div>
                      <h3 className="text-sm font-semibold text-gray-900">{tp.name}</h3>
                      <div className="mt-1 flex items-center space-x-4 text-xs text-gray-500">
                        <span className="flex items-center">
                          <MapPin className="h-3 w-3 mr-1" />
                          {tp.taluk_name || 'N/A'}
                        </span>
                        <span className="flex items-center">
                          <Users className="h-3 w-3 mr-1" />
                          {tp.total_population?.toLocaleString() || 'N/A'} people
                        </span>
                      </div>
                    </div>
                  </div>
                  <div className="text-sm text-primary-600 font-medium">
                    View Details →
                  </div>
                </div>
              </Link>
            ))
          )}
        </div>
      </div>
    </div>
  );
}

export default ZillaPanchayatDetail;
