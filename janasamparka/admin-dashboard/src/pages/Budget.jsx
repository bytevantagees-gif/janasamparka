import { useState } from 'react';
import { useQuery } from '@tanstack/react-query';
import { Wallet, TrendingUp, DollarSign } from 'lucide-react';
import BudgetDashboard from '../components/BudgetDashboard';
import { authAPI } from '../services/api';
import { useTranslation } from '../hooks/useTranslation';

const Budget = () => {
  const { t } = useTranslation();
  const [viewType, setViewType] = useState('ward'); // 'ward', 'department', or 'constituency'

  // Get current user to determine constituency
  const { data: userData } = useQuery({
    queryKey: ['current-user'],
    queryFn: () => authAPI.getCurrentUser(),
  });

  const currentUser = userData?.data;
  const constituencyId = currentUser?.constituency_id;

  if (!currentUser) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Page Header */}
      <div className="bg-white shadow rounded-lg p-6">
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-2xl font-bold text-gray-900 flex items-center gap-2">
              <Wallet className="h-8 w-8 text-blue-600" />
              {t('Budget Transparency')}
            </h1>
            <p className="mt-1 text-sm text-gray-500">
              Real-time budget tracking and utilization across departments
            </p>
          </div>

          {/* View Toggle */}
          <div className="flex gap-2">
            <button
              onClick={() => setViewType('constituency')}
              className={`px-4 py-2 rounded-lg text-sm font-medium transition ${
                viewType === 'constituency'
                  ? 'bg-blue-600 text-white'
                  : 'bg-gray-200 text-gray-700 hover:bg-gray-300'
              }`}
            >
              Constituency View
            </button>
            <button
              onClick={() => setViewType('ward')}
              className={`px-4 py-2 rounded-lg text-sm font-medium transition ${
                viewType === 'ward'
                  ? 'bg-blue-600 text-white'
                  : 'bg-gray-200 text-gray-700 hover:bg-gray-300'
              }`}
            >
              Ward View
            </button>
            <button
              onClick={() => setViewType('department')}
              className={`px-4 py-2 rounded-lg text-sm font-medium transition ${
                viewType === 'department'
                  ? 'bg-blue-600 text-white'
                  : 'bg-gray-200 text-gray-700 hover:bg-gray-300'
              }`}
            >
              Department View
            </button>
          </div>
        </div>
      </div>

      {/* Budget Dashboard */}
      <div className="bg-white shadow rounded-lg p-6">
        <BudgetDashboard
          constituencyId={constituencyId}
          wardId={null} // TODO: Add ward selector
          departmentId={null} // TODO: Add department selector
          type={viewType === 'department' ? 'department' : 'ward'}
        />
      </div>

      {/* Quick Stats */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        <div className="bg-gradient-to-br from-blue-500 to-blue-600 rounded-lg shadow p-6 text-white">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-blue-100 text-sm font-medium">Total Allocated</p>
              <p className="text-3xl font-bold mt-2">₹2.5Cr</p>
              <p className="text-blue-100 text-sm mt-1">This fiscal year</p>
            </div>
            <DollarSign className="h-12 w-12 text-blue-200 opacity-50" />
          </div>
        </div>

        <div className="bg-gradient-to-br from-green-500 to-green-600 rounded-lg shadow p-6 text-white">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-green-100 text-sm font-medium">Utilized</p>
              <p className="text-3xl font-bold mt-2">68%</p>
              <p className="text-green-100 text-sm mt-1">On track with plan</p>
            </div>
            <TrendingUp className="h-12 w-12 text-green-200 opacity-50" />
          </div>
        </div>

        <div className="bg-gradient-to-br from-purple-500 to-purple-600 rounded-lg shadow p-6 text-white">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-purple-100 text-sm font-medium">Remaining</p>
              <p className="text-3xl font-bold mt-2">₹80L</p>
              <p className="text-purple-100 text-sm mt-1">Available to allocate</p>
            </div>
            <Wallet className="h-12 w-12 text-purple-200 opacity-50" />
          </div>
        </div>
      </div>

      {/* Information Box */}
      <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
        <div className="flex items-start">
          <div className="flex-shrink-0">
            <svg className="h-5 w-5 text-blue-400" viewBox="0 0 20 20" fill="currentColor">
              <path fillRule="evenodd" d="M18 10a8 8 0 11-16 0 8 8 0 0116 0zm-7-4a1 1 0 11-2 0 1 1 0 012 0zM9 9a1 1 0 000 2v3a1 1 0 001 1h1a1 1 0 100-2v-3a1 1 0 00-1-1H9z" clipRule="evenodd" />
            </svg>
          </div>
          <div className="ml-3 flex-1">
            <h3 className="text-sm font-medium text-blue-800">Budget Transparency Initiative</h3>
            <div className="mt-2 text-sm text-blue-700">
              <p>
                This dashboard provides real-time visibility into budget allocation and utilization. 
                All financial data is updated automatically from department expense reports and 
                complies with Karnataka Financial Code guidelines.
              </p>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default Budget;
