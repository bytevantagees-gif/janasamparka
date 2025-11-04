import { useParams } from 'react-router-dom';
import { useQuery } from '@tanstack/react-query';
import { MapPin, Users, Phone, Mail } from 'lucide-react';
import { constituenciesAPI } from '../services/api';

function ConstituencyDetail() {
  const { id } = useParams();

  const { data, isLoading, error } = useQuery({
    queryKey: ['constituency', id],
    queryFn: () => constituenciesAPI.getById(id),
  });

  const constituency = data?.data;
  const stats = constituency?.statistics || {};

  if (isLoading) {
    return <div className="flex items-center justify-center h-64">Loading...</div>;
  }

  if (error) {
    return <div className="text-red-600">Error loading constituency</div>;
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="bg-white shadow">
        <div className="px-6 py-4">
          <div className="flex items-center justify-between">
            <div>
              <h1 className="text-2xl font-bold text-gray-900">{constituency.name}</h1>
              <p className="mt-1 text-sm text-gray-500">{constituency.code}</p>
            </div>
            <span className={`
              inline-flex items-center px-3 py-1 rounded-full text-sm font-medium
              ${constituency.is_active ? 'bg-green-100 text-green-800' : 'bg-gray-100 text-gray-800'}
            `}>
              {constituency.is_active ? 'Active' : 'Inactive'}
            </span>
          </div>
        </div>
      </div>

      {/* MLA Info */}
      <div className="bg-white shadow rounded-lg p-6">
        <h2 className="text-lg font-medium text-gray-900 mb-4">MLA Information</h2>
        <div className="space-y-3">
          <div className="flex items-center text-sm">
            <Users className="mr-3 h-5 w-5 text-gray-400" />
            <span className="font-medium text-gray-900">{constituency.mla_name}</span>
            <span className="ml-2 text-gray-500">({constituency.mla_party})</span>
          </div>
          {constituency.mla_contact_phone && (
            <div className="flex items-center text-sm text-gray-600">
              <Phone className="mr-3 h-5 w-5 text-gray-400" />
              {constituency.mla_contact_phone}
            </div>
          )}
          {constituency.mla_contact_email && (
            <div className="flex items-center text-sm text-gray-600">
              <Mail className="mr-3 h-5 w-5 text-gray-400" />
              {constituency.mla_contact_email}
            </div>
          )}
        </div>
      </div>

      {/* Statistics */}
      <div className="grid grid-cols-1 gap-5 sm:grid-cols-2 lg:grid-cols-4">
        <div className="bg-white overflow-hidden shadow rounded-lg">
          <div className="p-5">
            <dt className="text-sm font-medium text-gray-500 truncate">Total Users</dt>
            <dd className="mt-1 text-3xl font-semibold text-gray-900">{stats.total_users || 0}</dd>
          </div>
        </div>
        <div className="bg-white overflow-hidden shadow rounded-lg">
          <div className="p-5">
            <dt className="text-sm font-medium text-gray-500 truncate">Total Wards</dt>
            <dd className="mt-1 text-3xl font-semibold text-gray-900">{stats.total_wards || 0}</dd>
          </div>
        </div>
        <div className="bg-white overflow-hidden shadow rounded-lg">
          <div className="p-5">
            <dt className="text-sm font-medium text-gray-500 truncate">Complaints</dt>
            <dd className="mt-1 text-3xl font-semibold text-gray-900">{stats.total_complaints || 0}</dd>
          </div>
        </div>
        <div className="bg-white overflow-hidden shadow rounded-lg">
          <div className="p-5">
            <dt className="text-sm font-medium text-gray-500 truncate">Resolution Rate</dt>
            <dd className="mt-1 text-3xl font-semibold text-gray-900">{stats.resolution_rate || 0}%</dd>
          </div>
        </div>
      </div>

      {/* Additional Details */}
      <div className="bg-white shadow rounded-lg p-6">
        <h2 className="text-lg font-medium text-gray-900 mb-4">Details</h2>
        <dl className="grid grid-cols-1 gap-x-4 gap-y-6 sm:grid-cols-2">
          <div>
            <dt className="text-sm font-medium text-gray-500">District</dt>
            <dd className="mt-1 text-sm text-gray-900">{constituency.district}</dd>
          </div>
          <div>
            <dt className="text-sm font-medium text-gray-500">State</dt>
            <dd className="mt-1 text-sm text-gray-900">{constituency.state}</dd>
          </div>
          <div>
            <dt className="text-sm font-medium text-gray-500">Assembly Number</dt>
            <dd className="mt-1 text-sm text-gray-900">{constituency.assembly_number}</dd>
          </div>
          <div>
            <dt className="text-sm font-medium text-gray-500">Subscription Tier</dt>
            <dd className="mt-1">
              <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-blue-100 text-blue-800">
                {constituency.subscription_tier}
              </span>
            </dd>
          </div>
          <div className="sm:col-span-2">
            <dt className="text-sm font-medium text-gray-500">Description</dt>
            <dd className="mt-1 text-sm text-gray-900">{constituency.description || 'No description available'}</dd>
          </div>
        </dl>
      </div>
    </div>
  );
}

export default ConstituencyDetail;
