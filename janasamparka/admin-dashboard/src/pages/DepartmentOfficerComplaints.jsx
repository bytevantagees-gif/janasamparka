import { useState } from 'react';
import { useQuery } from '@tanstack/react-query';
import { Link } from 'react-router-dom';
import {
  MessageSquare,
  Filter,
  Search,
  Clock,
  CheckCircle,
  XCircle,
  AlertCircle,
  MapPin,
  User,
  Calendar,
  UserCheck,
  ArrowRight
} from 'lucide-react';
import { complaintsAPI } from '../services/api';
import { useTranslation } from '../hooks/useTranslation';

const STATUS_CONFIG = {
  submitted: { color: 'blue', icon: Clock, label: 'Submitted' },
  assigned: { color: 'yellow', icon: AlertCircle, label: 'Assigned' },
  in_progress: { color: 'purple', icon: Clock, label: 'In Progress' },
  resolved: { color: 'green', icon: CheckCircle, label: 'Resolved' },
  closed: { color: 'gray', icon: CheckCircle, label: 'Closed' },
  rejected: { color: 'red', icon: XCircle, label: 'Rejected' },
};

const CATEGORY_LABELS = {
  road: 'Road & Infrastructure',
  water: 'Water Supply',
  electricity: 'Electricity',
  health: 'Health',
  education: 'Education',
  sanitation: 'Sanitation',
  other: 'Other',
};

function DepartmentOfficerComplaints() {
  const { t } = useTranslation();
  const [filters, setFilters] = useState({
    status: '',
    category: '',
    search: '',
  });

  const { data, isLoading, error } = useQuery({
    queryKey: ['my-assigned-complaints', filters],
    queryFn: () => complaintsAPI.getMyAssigned(filters),
  });

  const complaints = data?.data?.complaints || [];

  const handleFilterChange = (key, value) => {
    setFilters(prev => ({ ...prev, [key]: value }));
  };

  if (error) {
    return (
      <div className="rounded-md bg-red-50 p-4">
        <p className="text-sm text-red-800">Error loading complaints: {error.message}</p>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">{t('myAssignedComplaints')}</h1>
          <p className="mt-1 text-sm text-gray-500">
            {t('manageAssignedComplaints')}
          </p>
        </div>
        <div className="flex space-x-3">
          <Link
            to="/complaints"
            className="inline-flex items-center px-4 py-2 border border-gray-300 shadow-sm text-sm font-medium rounded-md text-gray-700 bg-white hover:bg-gray-50"
          >
            {t('viewAllComplaints')}
          </Link>
        </div>
      </div>

      {/* Quick Stats */}
      <div className="grid grid-cols-1 gap-5 sm:grid-cols-2 lg:grid-cols-4">
        <div className="bg-white overflow-hidden shadow rounded-lg">
          <div className="p-5">
            <div className="flex items-center">
              <div className="flex-shrink-0">
                <MessageSquare className="h-6 w-6 text-gray-400" />
              </div>
              <div className="ml-5 w-0 flex-1">
                <dl>
                  <dt className="text-sm font-medium text-gray-500 truncate">{t('totalAssigned')}</dt>
                  <dd className="text-lg font-semibold text-gray-900">{complaints.length}</dd>
                </dl>
              </div>
            </div>
          </div>
        </div>

        <div className="bg-white overflow-hidden shadow rounded-lg">
          <div className="p-5">
            <div className="flex items-center">
              <div className="flex-shrink-0">
                <Clock className="h-6 w-6 text-yellow-500" />
              </div>
              <div className="ml-5 w-0 flex-1">
                <dl>
                  <dt className="text-sm font-medium text-gray-500 truncate">{t('pending')}</dt>
                  <dd className="text-lg font-semibold text-gray-900">
                    {complaints.filter(c => ['submitted', 'assigned'].includes(c.status)).length}
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
                <AlertCircle className="h-6 w-6 text-purple-500" />
              </div>
              <div className="ml-5 w-0 flex-1">
                <dl>
                  <dt className="text-sm font-medium text-gray-500 truncate">{t('inProgress')}</dt>
                  <dd className="text-lg font-semibold text-gray-900">
                    {complaints.filter(c => c.status === 'in_progress').length}
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
                <CheckCircle className="h-6 w-6 text-green-500" />
              </div>
              <div className="ml-5 w-0 flex-1">
                <dl>
                  <dt className="text-sm font-medium text-gray-500 truncate">{t('completed')}</dt>
                  <dd className="text-lg font-semibold text-gray-900">
                    {complaints.filter(c => ['resolved', 'closed'].includes(c.status)).length}
                  </dd>
                </dl>
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Filters */}
      <div className="bg-white rounded-lg shadow p-4">
        <div className="flex items-center space-x-4">
          <Filter className="h-5 w-5 text-gray-400" />

          {/* Search */}
          <div className="flex-1">
            <div className="relative">
              <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 h-5 w-5 text-gray-400" />
              <input
                type="text"
                placeholder={t('searchComplaints')}
                value={filters.search}
                onChange={(e) => handleFilterChange('search', e.target.value)}
                className="w-full pl-10 pr-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent"
              />
            </div>
          </div>

          {/* Status Filter */}
          <select
            value={filters.status}
            onChange={(e) => handleFilterChange('status', e.target.value)}
            className="px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent"
          >
            <option value="">{t('allStatuses')}</option>
            {Object.entries(STATUS_CONFIG).map(([key, config]) => (
              <option key={key} value={key}>{config.label}</option>
            ))}
          </select>

          {/* Category Filter */}
          <select
            value={filters.category}
            onChange={(e) => handleFilterChange('category', e.target.value)}
            className="px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent"
          >
            <option value="">{t('allCategories')}</option>
            {Object.entries(CATEGORY_LABELS).map(([key, label]) => (
              <option key={key} value={key}>{label}</option>
            ))}
          </select>
        </div>
      </div>

      {/* Complaints List */}
      {isLoading ? (
        <div className="text-center py-12">
          <div className="inline-block animate-spin rounded-full h-8 w-8 border-b-2 border-primary-600"></div>
          <p className="mt-2 text-sm text-gray-500">Loading your assigned complaints...</p>
        </div>
      ) : complaints.length === 0 ? (
        <div className="text-center py-12 bg-white rounded-lg shadow">
          <UserCheck className="mx-auto h-12 w-12 text-gray-400" />
          <h3 className="mt-2 text-sm font-medium text-gray-900">No assigned complaints</h3>
          <p className="mt-1 text-sm text-gray-500">
            {filters.status || filters.category || filters.search
              ? 'No complaints match your filters.'
              : 'You have no complaints assigned to you at the moment.'}
          </p>
        </div>
      ) : (
        <div className="bg-white shadow overflow-hidden sm:rounded-md">
          <ul className="divide-y divide-gray-200">
            {complaints.map((complaint) => {
              const StatusIcon = STATUS_CONFIG[complaint.status]?.icon || AlertCircle;
              const statusColor = STATUS_CONFIG[complaint.status]?.color || 'gray';

              return (
                <li key={complaint.id}>
                  <div className="px-4 py-4 sm:px-6">
                    <div className="flex items-center justify-between">
                      <div className="flex-1 min-w-0">
                        <p className="text-sm font-medium text-primary-600 truncate">
                          {complaint.title}
                        </p>
                        <p className="mt-1 text-sm text-gray-600 line-clamp-2">
                          {complaint.description}
                        </p>
                      </div>
                      <div className="ml-4 flex-shrink-0 flex items-center space-x-2">
                        <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-${statusColor}-100 text-${statusColor}-800`}>
                          <StatusIcon className="mr-1 h-3 w-3" />
                          {STATUS_CONFIG[complaint.status]?.label || complaint.status}
                        </span>
                        <Link
                          to={`/complaints/${complaint.id}`}
                          className="inline-flex items-center px-3 py-1 border border-transparent text-sm leading-4 font-medium rounded-md text-primary-700 bg-primary-100 hover:bg-primary-200"
                        >
                          {t('viewDetails')}
                          <ArrowRight className="ml-1 h-4 w-4" />
                        </Link>
                      </div>
                    </div>

                    <div className="mt-2 sm:flex sm:justify-between">
                      <div className="sm:flex space-x-4">
                        <p className="flex items-center text-sm text-gray-500">
                          <User className="flex-shrink-0 mr-1.5 h-4 w-4 text-gray-400" />
                          {complaint.user_name || 'Anonymous'}
                        </p>
                        {complaint.category && (
                          <p className="flex items-center text-sm text-gray-500">
                            <MessageSquare className="flex-shrink-0 mr-1.5 h-4 w-4 text-gray-400" />
                            {CATEGORY_LABELS[complaint.category] || complaint.category}
                          </p>
                        )}
                        {complaint.location_description && (
                          <p className="flex items-center text-sm text-gray-500">
                            <MapPin className="flex-shrink-0 mr-1.5 h-4 w-4 text-gray-400" />
                            {complaint.location_description}
                          </p>
                        )}
                      </div>
                      <div className="mt-2 flex items-center text-sm text-gray-500 sm:mt-0">
                        <Calendar className="flex-shrink-0 mr-1.5 h-4 w-4 text-gray-400" />
                        <p>
                          {new Date(complaint.created_at).toLocaleDateString('en-IN', {
                            day: 'numeric',
                            month: 'short',
                            year: 'numeric',
                          })}
                        </p>
                      </div>
                    </div>
                  </div>
                </li>
              );
            })}
          </ul>
        </div>
      )}
    </div>
  );
}

export default DepartmentOfficerComplaints;