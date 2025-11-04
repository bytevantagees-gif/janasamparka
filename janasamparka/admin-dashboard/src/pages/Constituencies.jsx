import { useState } from 'react';
import { useQuery, useQueryClient } from '@tanstack/react-query';
import { Link } from 'react-router-dom';
import { MapPin, Users, MessageSquare, TrendingUp, Plus } from 'lucide-react';
import { constituenciesAPI } from '../services/api';
import ConstituencyCreateModal from '../components/ConstituencyCreateModal';
import { useTranslation } from '../hooks/useTranslation';

function Constituencies() {
  const { t } = useTranslation();
  const [activeOnly, setActiveOnly] = useState(true);
  const [searchTerm, setSearchTerm] = useState('');
  const [isCreateModalOpen, setIsCreateModalOpen] = useState(false);
  const queryClient = useQueryClient();

  const { data, isLoading, error } = useQuery({
    queryKey: ['constituencies', activeOnly],
    queryFn: () => constituenciesAPI.getAll(activeOnly),
  });

  const constituencies = data?.data?.constituencies || [];

  if (isLoading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="text-gray-500">Loading constituencies...</div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="rounded-md bg-red-50 p-4">
        <p className="text-sm text-red-800">Error loading constituencies: {error.message}</p>
      </div>
    );
  }

  const handleCreateConstituency = async (constituencyData) => {
    // TODO: Implement actual API call
    console.log('Creating constituency:', constituencyData);
    
    // Mock success
    await new Promise(resolve => setTimeout(resolve, 1000));
    
    // Invalidate queries
    queryClient.invalidateQueries(['constituencies']);
    
    alert('Constituency created successfully!');
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">{t('constituencies')}</h1>
          <p className="mt-1 text-sm text-gray-500">
            {t('constituencyManagement')}
          </p>
        </div>
        <button 
          onClick={() => setIsCreateModalOpen(true)}
          className="inline-flex items-center px-4 py-2 border border-transparent shadow-sm text-sm font-medium rounded-md text-white bg-primary-600 hover:bg-primary-700"
        >
          <Plus className="mr-2 h-4 w-4" />
          Add Constituency
        </button>
      </div>

      {/* Filters */}
      <div className="flex items-center space-x-4">
        <label className="flex items-center">
          <input
            type="checkbox"
            checked={activeOnly}
            onChange={(e) => setActiveOnly(e.target.checked)}
            className="h-4 w-4 text-primary-600 focus:ring-primary-500 border-gray-300 rounded"
          />
          <span className="ml-2 text-sm text-gray-700">Show active only</span>
        </label>
      </div>

      {/* Stats Summary */}
      <div className="grid grid-cols-1 gap-5 sm:grid-cols-2 lg:grid-cols-4">
        <div className="bg-white overflow-hidden shadow rounded-lg">
          <div className="p-5">
            <div className="flex items-center">
              <div className="flex-shrink-0">
                <MapPin className="h-6 w-6 text-gray-400" />
              </div>
              <div className="ml-5 w-0 flex-1">
                <dl>
                  <dt className="text-sm font-medium text-gray-500 truncate">Total Constituencies</dt>
                  <dd className="text-lg font-semibold text-gray-900">{constituencies.length}</dd>
                </dl>
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Constituencies Grid */}
      <div className="grid grid-cols-1 gap-6 sm:grid-cols-2 lg:grid-cols-3">
        {constituencies.map((constituency) => (
          <Link
            key={constituency.id}
            to={`/constituencies/${constituency.id}`}
            className="bg-white overflow-hidden shadow rounded-lg hover:shadow-lg transition-shadow"
          >
            <div className="p-6">
              {/* Header */}
              <div className="flex items-start justify-between">
                <div className="flex-1">
                  <h3 className="text-lg font-medium text-gray-900">{constituency.name}</h3>
                  <p className="text-sm text-gray-500">{constituency.code}</p>
                </div>
                <span className={`
                  inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium
                  ${constituency.is_active ? 'bg-green-100 text-green-800' : 'bg-gray-100 text-gray-800'}
                `}>
                  {constituency.is_active ? 'Active' : 'Inactive'}
                </span>
              </div>

              {/* MLA Info */}
              <div className="mt-4 space-y-2">
                <div className="flex items-center text-sm text-gray-600">
                  <Users className="mr-2 h-4 w-4" />
                  <span className="font-medium">{constituency.mla_name || 'No MLA assigned'}</span>
                </div>
                {constituency.mla_party && (
                  <p className="text-xs text-gray-500 ml-6">{constituency.mla_party}</p>
                )}
              </div>

              {/* Location */}
              <div className="mt-3">
                <p className="text-sm text-gray-500">
                  <MapPin className="inline h-3 w-3 mr-1" />
                  {constituency.district}, {constituency.state}
                </p>
              </div>

              {/* Tier Badge */}
              <div className="mt-4 pt-4 border-t border-gray-200">
                <span className="inline-flex items-center px-2.5 py-0.5 rounded-md text-xs font-medium bg-blue-100 text-blue-800">
                  {constituency.subscription_tier}
                </span>
              </div>
            </div>
          </Link>
        ))}
      </div>

      {/* Empty State */}
      {constituencies.length === 0 && (
        <div className="text-center py-12">
          <MapPin className="mx-auto h-12 w-12 text-gray-400" />
          <h3 className="mt-2 text-sm font-medium text-gray-900">No constituencies</h3>
          <p className="mt-1 text-sm text-gray-500">
            Get started by adding a new constituency.
          </p>
          <div className="mt-6">
            <button 
              onClick={() => setIsCreateModalOpen(true)}
              className="inline-flex items-center px-4 py-2 border border-transparent shadow-sm text-sm font-medium rounded-md text-white bg-primary-600 hover:bg-primary-700"
            >
              <Plus className="mr-2 h-4 w-4" />
              Add Constituency
            </button>
          </div>
        </div>
      )}

      {/* Constituency Create Modal */}
      <ConstituencyCreateModal
        isOpen={isCreateModalOpen}
        onClose={() => setIsCreateModalOpen(false)}
        onCreate={handleCreateConstituency}
      />
    </div>
  );
}

export default Constituencies;
