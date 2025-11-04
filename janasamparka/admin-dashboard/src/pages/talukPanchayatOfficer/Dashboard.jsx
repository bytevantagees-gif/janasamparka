import React, { useState, useEffect } from 'react';
import { 
  BarChart3, Users, FileText, CheckCircle, AlertCircle, 
  TrendingUp, Calendar, Award, MapPin, Building2 
} from 'lucide-react';
import { useAuth } from '../../contexts/AuthContext';

/**
 * Taluk Panchayat Officer Dashboard
 * 
 * Responsibilities:
 * - Coordinate all Gram Panchayats in taluk
 * - Monitor PDOs and Village Accountants
 * - Implement taluk-level schemes
 * - Budget preparation and allocation
 * - Revenue supervision
 * - Report to Zilla Panchayat
 */

const Dashboard = () => {
  const { user } = useAuth();
  const [stats, setStats] = useState({
    totalGramPanchayats: 0,
    totalPDOs: 0,
    totalVAs: 0,
    activeSchemes: 0,
    budgetUtilization: 0,
    pendingApprovals: 0
  });
  const [gramPanchayats, setGramPanchayats] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    loadDashboardData();
  }, []);

  const loadDashboardData = async () => {
    try {
      setLoading(true);

      // TODO: Fetch real data from API
      setStats({
        totalGramPanchayats: 25,
        totalPDOs: 25,
        totalVAs: 30,
        activeSchemes: 12,
        budgetUtilization: 68,
        pendingApprovals: 8
      });

      setGramPanchayats([
        {
          id: 1,
          name: 'Bolwar GP',
          code: 'GP-PUT-001',
          population: 8500,
          pdoName: 'Ramesh',
          submissions: { total: 45, pending: 12, resolved: 33 },
          budgetUtilization: 75,
          performance: 'good'
        },
        {
          id: 2,
          name: 'Kabaka GP',
          code: 'GP-PUT-002',
          population: 6200,
          pdoName: 'Ganesh',
          submissions: { total: 32, pending: 8, resolved: 24 },
          budgetUtilization: 62,
          performance: 'average'
        },
        {
          id: 3,
          name: 'Parladka GP',
          code: 'GP-PUT-003',
          population: 5800,
          pdoName: 'Mohan',
          submissions: { total: 28, pending: 15, resolved: 13 },
          budgetUtilization: 45,
          performance: 'needs_attention'
        }
      ]);

    } catch (error) {
      console.error('Error loading dashboard:', error);
    } finally {
      setLoading(false);
    }
  };

  const getPerformanceColor = (performance) => {
    const colors = {
      good: 'bg-green-100 text-green-800',
      average: 'bg-yellow-100 text-yellow-800',
      needs_attention: 'bg-red-100 text-red-800'
    };
    return colors[performance] || 'bg-gray-100 text-gray-800';
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center h-screen">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-indigo-600 mx-auto"></div>
          <p className="mt-4 text-gray-600">Loading dashboard...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <div className="bg-white shadow">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-6">
          <div className="flex items-center justify-between">
            <div>
              <h1 className="text-3xl font-bold text-gray-900">
                Taluk Panchayat Officer Dashboard
              </h1>
              <p className="mt-1 text-sm text-gray-600">
                {user?.talukPanchayatName || 'Puttur Taluk Panchayat'} • Coordinating {stats.totalGramPanchayats} Gram Panchayats
              </p>
            </div>
            <div className="flex items-center space-x-4">
              <div className="text-right">
                <p className="text-sm font-medium text-gray-900">{user?.name}</p>
                <p className="text-xs text-gray-500">{user?.phone}</p>
              </div>
            </div>
          </div>
        </div>
      </div>

      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* Stats Grid */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6 mb-8">
          <div className="bg-white rounded-lg shadow p-6">
            <div className="flex items-center">
              <div className="flex-shrink-0">
                <Building2 className="h-8 w-8 text-indigo-600" />
              </div>
              <div className="ml-4">
                <p className="text-sm font-medium text-gray-600">Gram Panchayats</p>
                <p className="text-2xl font-bold text-gray-900">{stats.totalGramPanchayats}</p>
              </div>
            </div>
          </div>

          <div className="bg-white rounded-lg shadow p-6">
            <div className="flex items-center">
              <div className="flex-shrink-0">
                <Users className="h-8 w-8 text-purple-600" />
              </div>
              <div className="ml-4">
                <p className="text-sm font-medium text-gray-600">PDOs / VAs</p>
                <p className="text-2xl font-bold text-gray-900">
                  {stats.totalPDOs} / {stats.totalVAs}
                </p>
              </div>
            </div>
          </div>

          <div className="bg-white rounded-lg shadow p-6">
            <div className="flex items-center">
              <div className="flex-shrink-0">
                <Award className="h-8 w-8 text-green-600" />
              </div>
              <div className="ml-4">
                <p className="text-sm font-medium text-gray-600">Active Schemes</p>
                <p className="text-2xl font-bold text-gray-900">{stats.activeSchemes}</p>
              </div>
            </div>
          </div>

          <div className="bg-white rounded-lg shadow p-6">
            <div className="flex items-center">
              <div className="flex-shrink-0">
                <TrendingUp className="h-8 w-8 text-blue-600" />
              </div>
              <div className="ml-4">
                <p className="text-sm font-medium text-gray-600">Budget Utilization</p>
                <p className="text-2xl font-bold text-gray-900">{stats.budgetUtilization}%</p>
              </div>
            </div>
          </div>

          <div className="bg-white rounded-lg shadow p-6">
            <div className="flex items-center">
              <div className="flex-shrink-0">
                <AlertCircle className="h-8 w-8 text-yellow-600" />
              </div>
              <div className="ml-4">
                <p className="text-sm font-medium text-gray-600">Pending Approvals</p>
                <p className="text-2xl font-bold text-gray-900">{stats.pendingApprovals}</p>
              </div>
            </div>
          </div>

          <div className="bg-white rounded-lg shadow p-6">
            <div className="flex items-center">
              <div className="flex-shrink-0">
                <BarChart3 className="h-8 w-8 text-indigo-600" />
              </div>
              <div className="ml-4">
                <p className="text-sm font-medium text-gray-600">Performance Score</p>
                <p className="text-2xl font-bold text-gray-900">8.2/10</p>
              </div>
            </div>
          </div>
        </div>

        {/* Gram Panchayats Overview */}
        <div className="bg-white rounded-lg shadow mb-8">
          <div className="px-6 py-4 border-b border-gray-200">
            <h2 className="text-lg font-semibold text-gray-900">Gram Panchayats Performance</h2>
            <p className="mt-1 text-sm text-gray-600">
              Monitor performance and progress of all GPs in your taluk
            </p>
          </div>
          <div className="overflow-x-auto">
            <table className="min-w-full divide-y divide-gray-200">
              <thead className="bg-gray-50">
                <tr>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Gram Panchayat
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    PDO
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Population
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Submissions
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Budget Utilization
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Performance
                  </th>
                  <th className="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Actions
                  </th>
                </tr>
              </thead>
              <tbody className="bg-white divide-y divide-gray-200">
                {gramPanchayats.map((gp) => (
                  <tr key={gp.id} className="hover:bg-gray-50">
                    <td className="px-6 py-4 whitespace-nowrap">
                      <div>
                        <div className="text-sm font-medium text-gray-900">{gp.name}</div>
                        <div className="text-xs text-gray-500">{gp.code}</div>
                      </div>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                      {gp.pdoName}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                      {gp.population.toLocaleString()}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap">
                      <div className="text-sm text-gray-900">
                        {gp.submissions.total} total
                      </div>
                      <div className="text-xs text-gray-500">
                        {gp.submissions.pending} pending • {gp.submissions.resolved} resolved
                      </div>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap">
                      <div className="flex items-center">
                        <div className="w-20 bg-gray-200 rounded-full h-2 mr-2">
                          <div 
                            className={`h-2 rounded-full ${
                              gp.budgetUtilization >= 70 ? 'bg-green-600' : 
                              gp.budgetUtilization >= 50 ? 'bg-yellow-600' : 
                              'bg-red-600'
                            }`}
                            style={{ width: `${gp.budgetUtilization}%` }}
                          ></div>
                        </div>
                        <span className="text-sm text-gray-900">{gp.budgetUtilization}%</span>
                      </div>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap">
                      <span className={`px-3 py-1 inline-flex text-xs leading-5 font-semibold rounded-full ${getPerformanceColor(gp.performance)}`}>
                        {gp.performance.replace('_', ' ')}
                      </span>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-right text-sm font-medium">
                      <button className="text-indigo-600 hover:text-indigo-900 mr-3">
                        View Details
                      </button>
                      <button className="text-gray-600 hover:text-gray-900">
                        Reports
                      </button>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>

        {/* Quick Actions Grid */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
          <button className="bg-white rounded-lg shadow p-6 hover:shadow-md transition-shadow text-left">
            <FileText className="h-8 w-8 text-indigo-600 mb-3" />
            <h3 className="text-lg font-semibold text-gray-900">Taluk Report</h3>
            <p className="mt-1 text-sm text-gray-600">
              Generate consolidated report for Zilla Panchayat
            </p>
          </button>

          <button className="bg-white rounded-lg shadow p-6 hover:shadow-md transition-shadow text-left">
            <Calendar className="h-8 w-8 text-green-600 mb-3" />
            <h3 className="text-lg font-semibold text-gray-900">Schedule Review</h3>
            <p className="mt-1 text-sm text-gray-600">
              Plan review meetings with PDOs and VAs
            </p>
          </button>

          <button className="bg-white rounded-lg shadow p-6 hover:shadow-md transition-shadow text-left">
            <CheckCircle className="h-8 w-8 text-purple-600 mb-3" />
            <h3 className="text-lg font-semibold text-gray-900">Approve Budgets</h3>
            <p className="mt-1 text-sm text-gray-600">
              Review and approve GP budget proposals
            </p>
          </button>
        </div>
      </div>
    </div>
  );
};

export default Dashboard;
