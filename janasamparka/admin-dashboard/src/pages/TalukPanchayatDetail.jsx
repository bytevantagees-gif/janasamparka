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
  TrendingUp,
  Layers
} from 'lucide-react';
import { panchayatsAPI } from '../services/api';

function TalukPanchayatDetail() {
  const { id } = useParams();

  const { data: tp, isLoading, error } = useQuery({
    queryKey: ['taluk-panchayat', id],
    queryFn: async () => {
      const response = await panchayatsAPI.getTP(id);
      return response.data;
    },
  });

  const { data: gpData } = useQuery({
    queryKey: ['gram-panchayats', id],
    queryFn: async () => {
      const response = await panchayatsAPI.getAllGP({ taluk_panchayat_id: id });
      return response.data;
    },
  });

  const gramPanchayats = gpData || [];

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

  if (error || !tp) {
    return (
      <div className="p-6">
        <div className="bg-red-50 border border-red-200 rounded-lg p-4">
          <p className="text-red-800">Failed to load Taluk Panchayat details</p>
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
            <h1 className="text-2xl font-bold text-gray-900">{tp.name}</h1>
            <p className="text-sm text-gray-500">Taluk Panchayat Details</p>
            {tp.zilla_panchayat_name && (
              <p className="text-xs text-gray-400 flex items-center mt-1">
                <Layers className="h-3 w-3 mr-1" />
                Under {tp.zilla_panchayat_name}
              </p>
            )}
          </div>
        </div>
        <div className={`px-3 py-1 rounded-full text-sm font-medium ${
          tp.is_active 
            ? 'bg-green-100 text-green-800' 
            : 'bg-gray-100 text-gray-800'
        }`}>
          {tp.is_active ? 'Active' : 'Inactive'}
        </div>
      </div>

      {/* Statistics Cards */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        <div className="bg-gradient-to-br from-blue-500 to-blue-600 rounded-lg p-6 text-white">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-blue-100 text-sm font-medium">Total Population</p>
              <p className="text-3xl font-bold mt-2">
                {tp.total_population?.toLocaleString() || 'N/A'}
              </p>
            </div>
            <Users className="h-12 w-12 text-blue-200" />
          </div>
        </div>

        <div className="bg-gradient-to-br from-green-500 to-green-600 rounded-lg p-6 text-white">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-green-100 text-sm font-medium">Gram Panchayats</p>
              <p className="text-3xl font-bold mt-2">
                {tp.gram_panchayats_count || gramPanchayats.length}
              </p>
            </div>
            <Home className="h-12 w-12 text-green-200" />
          </div>
        </div>

        <div className="bg-gradient-to-br from-orange-500 to-orange-600 rounded-lg p-6 text-white">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-orange-100 text-sm font-medium">Total Users</p>
              <p className="text-3xl font-bold mt-2">
                {tp.total_users || 'N/A'}
              </p>
            </div>
            <Users className="h-12 w-12 text-orange-200" />
          </div>
        </div>
      </div>

      {/* Main Information */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Basic Details */}
        <div className="bg-white rounded-lg shadow p-6">
          <h2 className="text-lg font-semibold text-gray-900 mb-4 flex items-center">
            <Activity className="h-5 w-5 mr-2 text-blue-600" />
            Basic Information
          </h2>
          <dl className="space-y-3">
            <div>
              <dt className="text-sm font-medium text-gray-500">Code</dt>
              <dd className="mt-1 text-sm text-gray-900 font-mono">{tp.code}</dd>
            </div>
            <div>
              <dt className="text-sm font-medium text-gray-500">Taluk Name</dt>
              <dd className="mt-1 text-sm text-gray-900">{tp.taluk_name}</dd>
            </div>
            <div>
              <dt className="text-sm font-medium text-gray-500">Constituency</dt>
              <dd className="mt-1 text-sm text-gray-900">
                {tp.constituency_name || 'N/A'}
                {tp.mla_name && (
                  <span className="block text-xs text-gray-500 mt-1">
                    MLA: {tp.mla_name}
                  </span>
                )}
              </dd>
            </div>
            <div>
              <dt className="text-sm font-medium text-gray-500">Established</dt>
              <dd className="mt-1 text-sm text-gray-900 flex items-center">
                <Calendar className="h-4 w-4 mr-1 text-gray-400" />
                {tp.established_date ? new Date(tp.established_date).toLocaleDateString() : 'N/A'}
              </dd>
            </div>
          </dl>
        </div>

        {/* Leadership */}
        <div className="bg-white rounded-lg shadow p-6">
          <h2 className="text-lg font-semibold text-gray-900 mb-4 flex items-center">
            <Users className="h-5 w-5 mr-2 text-blue-600" />
            Leadership
          </h2>
          <dl className="space-y-3">
            <div>
              <dt className="text-sm font-medium text-gray-500">President</dt>
              <dd className="mt-1 text-sm text-gray-900">{tp.president_name || 'N/A'}</dd>
            </div>
            <div>
              <dt className="text-sm font-medium text-gray-500">Vice President</dt>
              <dd className="mt-1 text-sm text-gray-900">{tp.vice_president_name || 'N/A'}</dd>
            </div>
            <div>
              <dt className="text-sm font-medium text-gray-500">Executive Officer</dt>
              <dd className="mt-1 text-sm text-gray-900">{tp.executive_officer_name || 'N/A'}</dd>
            </div>
          </dl>
        </div>

        {/* Contact Information */}
        <div className="bg-white rounded-lg shadow p-6">
          <h2 className="text-lg font-semibold text-gray-900 mb-4 flex items-center">
            <Phone className="h-5 w-5 mr-2 text-blue-600" />
            Contact Information
          </h2>
          <dl className="space-y-3">
            <div>
              <dt className="text-sm font-medium text-gray-500">Office Phone</dt>
              <dd className="mt-1 text-sm text-gray-900 flex items-center">
                <Phone className="h-4 w-4 mr-2 text-gray-400" />
                {tp.office_phone || 'N/A'}
              </dd>
            </div>
            <div>
              <dt className="text-sm font-medium text-gray-500">Email</dt>
              <dd className="mt-1 text-sm text-gray-900 flex items-center">
                <Mail className="h-4 w-4 mr-2 text-gray-400" />
                {tp.email || 'N/A'}
              </dd>
            </div>
            <div>
              <dt className="text-sm font-medium text-gray-500">Office Address</dt>
              <dd className="mt-1 text-sm text-gray-900 flex items-start">
                <MapPin className="h-4 w-4 mr-2 text-gray-400 mt-0.5" />
                <span>{tp.office_address || 'N/A'}</span>
              </dd>
            </div>
          </dl>
        </div>

        {/* Statistics */}
        <div className="bg-white rounded-lg shadow p-6">
          <h2 className="text-lg font-semibold text-gray-900 mb-4 flex items-center">
            <TrendingUp className="h-5 w-5 mr-2 text-blue-600" />
            Statistics
          </h2>
          <dl className="space-y-3">
            <div>
              <dt className="text-sm font-medium text-gray-500">Total Villages</dt>
              <dd className="mt-1 text-sm text-gray-900">{tp.total_villages || 'N/A'}</dd>
            </div>
            <div>
              <dt className="text-sm font-medium text-gray-500">Total Wards</dt>
              <dd className="mt-1 text-sm text-gray-900">{tp.total_wards || 'N/A'}</dd>
            </div>
            <div>
              <dt className="text-sm font-medium text-gray-500">Area</dt>
              <dd className="mt-1 text-sm text-gray-900">
                {tp.area_sq_km ? `${tp.area_sq_km} km²` : 'N/A'}
              </dd>
            </div>
          </dl>
        </div>
      </div>

      {/* Gram Panchayats List */}
      <div className="bg-white rounded-lg shadow">
        <div className="p-6 border-b border-gray-200">
          <h2 className="text-lg font-semibold text-gray-900 flex items-center">
            <Home className="h-5 w-5 mr-2 text-green-600" />
            Gram Panchayats ({gramPanchayats.length})
          </h2>
        </div>
        <div className="divide-y divide-gray-200">
          {gramPanchayats.length === 0 ? (
            <div className="p-6 text-center text-gray-500">
              No Gram Panchayats found
            </div>
          ) : (
            gramPanchayats.map((gp) => (
              <Link
                key={gp.id}
                to={`/panchayats/gram/${gp.id}`}
                className="p-6 hover:bg-gray-50 transition-colors block"
              >
                <div className="flex items-center justify-between">
                  <div className="flex items-center space-x-4">
                    <div className="p-3 bg-green-100 rounded-lg">
                      <Home className="h-6 w-6 text-green-600" />
                    </div>
                    <div>
                      <h3 className="text-sm font-semibold text-gray-900">{gp.name}</h3>
                      <div className="mt-1 flex items-center space-x-4 text-xs text-gray-500">
                        <span className="flex items-center">
                          <Users className="h-3 w-3 mr-1" />
                          {gp.population?.toLocaleString() || 'N/A'} people
                        </span>
                        <span>{gp.households?.toLocaleString() || 'N/A'} households</span>
                        {gp.president_name && (
                          <span>Pres: {gp.president_name}</span>
                        )}
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

export default TalukPanchayatDetail;
