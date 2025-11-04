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
  Calendar
} from 'lucide-react';
import { complaintsAPI, authAPI } from '../services/api';
import { useTranslation } from '../hooks/useTranslation';
import { useAuth } from '../contexts/AuthContext';

const STATUS_CONFIG = {
  submitted: { color: 'blue', icon: Clock, label: 'Submitted' },
  under_review: { color: 'yellow', icon: AlertCircle, label: 'Under Review' },
  in_progress: { color: 'purple', icon: Clock, label: 'In Progress' },
  resolved: { color: 'green', icon: CheckCircle, label: 'Resolved' },
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

function ComplaintsList() {
  const { t } = useTranslation();
  const { user: currentUser } = useAuth();
  const [filters, setFilters] = useState({
    status: '',
    category: '',
    search: '',
  });

  // Fetch current user details
  const { data: userData } = useQuery({
    queryKey: ['currentUser'],
    queryFn: authAPI.getCurrentUser,
    staleTime: 5 * 60 * 1000, // 5 minutes
  });

  const { data, isLoading, error } = useQuery({
    queryKey: ['complaints', filters, currentUser?.id],
    queryFn: async () => {
      console.log('Fetching complaints with filters:', filters);
      console.log('Current user role:', currentUser?.role);
      console.log('Current user constituency:', currentUser?.constituency_id);
      
      const params = {};
      
      // Add filters as query parameters
      if (filters.status) params.status = filters.status;
      if (filters.category) params.category = filters.category;
      if (filters.search) params.search = filters.search;
      
      // Add constituency_id as a query parameter for non-admin users
      if (currentUser?.role !== 'admin' && currentUser?.constituency_id) {
        params.constituency_id = currentUser.constituency_id;
      }
      
      console.log('API Request Params:', params);
      const response = await complaintsAPI.getAll(params);
      console.log('API Response:', response);
      
      if (!response?.data) {
        console.warn('No data in API response');
        return { complaints: [] };
      }
      
      console.log(`Found ${response.data.complaints?.length || 0} complaints`);
      return response.data;
    },
    enabled: !!currentUser, // Only run the query when we have the current user
  });

  // The response data is already the complaints object, not nested under data
  const complaints = data?.complaints || [];

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
          <h1 className="text-2xl font-bold text-gray-900">{t('complaints')}</h1>
          <p className="mt-1 text-sm text-gray-500">
            {t('filterComplaints')}
          </p>
        </div>
        <Link
          to="/complaints/new"
          className="inline-flex items-center px-4 py-2 border border-transparent shadow-sm text-sm font-medium rounded-md text-white bg-primary-600 hover:bg-primary-700"
        >
          <MessageSquare className="mr-2 h-4 w-4" />
          {t('createComplaint')}
        </Link>
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

      {/* Stats */}
      <div className="grid grid-cols-1 gap-5 sm:grid-cols-2 lg:grid-cols-4">
        <div className="bg-white overflow-hidden shadow rounded-lg">
          <div className="p-5">
            <div className="flex items-center">
              <div className="flex-shrink-0">
                <MessageSquare className="h-6 w-6 text-gray-400" />
              </div>
              <div className="ml-5 w-0 flex-1">
                <dl>
                  <dt className="text-sm font-medium text-gray-500 truncate">{t('total')}</dt>
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
                    {complaints.filter(c => c.status === 'submitted').length}
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
                  <dt className="text-sm font-medium text-gray-500 truncate">{t('resolved')}</dt>
                  <dd className="text-lg font-semibold text-gray-900">
                    {complaints.filter(c => c.status === 'resolved').length}
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
      </div>

      {/* Complaints List */}
      {isLoading ? (
        <div className="text-center py-12">
          <div className="inline-block animate-spin rounded-full h-8 w-8 border-b-2 border-primary-600"></div>
          <p className="mt-2 text-sm text-gray-500">Loading complaints...</p>
        </div>
      ) : complaints.length === 0 ? (
        <div className="text-center py-12 bg-white rounded-lg shadow">
          <MessageSquare className="mx-auto h-12 w-12 text-gray-400" />
          <h3 className="mt-2 text-sm font-medium text-gray-900">No complaints</h3>
          <p className="mt-1 text-sm text-gray-500">
            {filters.status || filters.category || filters.search
              ? 'No complaints match your filters.'
              : 'Get started by creating a new complaint.'}
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
                  <Link
                    to={`/complaints/${complaint.id}`}
                    className="block hover:bg-gray-50 transition-colors"
                  >
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
                        <div className="ml-4 flex-shrink-0">
                          <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-${statusColor}-100 text-${statusColor}-800`}>
                            <StatusIcon className="mr-1 h-3 w-3" />
                            {STATUS_CONFIG[complaint.status]?.label || complaint.status}
                          </span>
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
                  </Link>
                </li>
              );
            })}
          </ul>
        </div>
      )}
    </div>
  );
}

export default ComplaintsList;
