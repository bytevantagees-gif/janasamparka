import React, { useState, useEffect } from 'react';
import { 
  Users, FileText, AlertCircle, CheckCircle, Clock, 
  MapPin, TrendingUp, Calendar, PhoneCall, FileCheck 
} from 'lucide-react';
import { useAuth } from '../../contexts/AuthContext';

/**
 * PDO (Panchayat Development Officer) Dashboard
 * 
 * Responsibilities:
 * - Overall administration of Gram Panchayat
 * - Monitor development works and scheme implementation
 * - Coordinate with departments and citizens
 * - Oversee Village Accountant and other GP staff
 * - Generate reports for Taluk Panchayat
 */

const Dashboard = () => {
  const { user } = useAuth();
  const [stats, setStats] = useState({
    totalSubmissions: 0,
    pendingSubmissions: 0,
    inProgress: 0,
    resolved: 0,
    totalCitizens: 0,
    schemesActive: 0
  });
  const [recentSubmissions, setRecentSubmissions] = useState([]);
  const [developmentWorks, setDevelopmentWorks] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    loadDashboardData();
  }, []);

  const loadDashboardData = async () => {
    try {
      setLoading(true);

      // TODO: Fetch real data from API
      // For now, using mock data
      setStats({
        totalSubmissions: 45,
        pendingSubmissions: 12,
        inProgress: 8,
        resolved: 25,
        totalCitizens: 8500,
        schemesActive: 6
      });

      setRecentSubmissions([
        {
          id: 1,
          title: 'Road repair needed near school',
          category: 'Infrastructure',
          status: 'submitted',
          priority: 'high',
          submittedAt: '2024-10-28',
          citizenName: 'Ramesh Kumar'
        },
        {
          id: 2,
          title: 'Street light not working',
          category: 'Electricity',
          status: 'in_progress',
          priority: 'medium',
          submittedAt: '2024-10-27',
          citizenName: 'Suma Bhat'
        },
        {
          id: 3,
          title: 'Water supply issue',
          category: 'Water',
          status: 'submitted',
          priority: 'high',
          submittedAt: '2024-10-26',
          citizenName: 'Krishna Rao'
        }
      ]);

      setDevelopmentWorks([
        {
          id: 1,
          name: 'Community Hall Construction',
          budget: 5000000,
          spent: 2500000,
          progress: 50,
          deadline: '2025-03-31',
          status: 'on_track'
        },
        {
          id: 2,
          name: 'Drainage System Upgrade',
          budget: 3000000,
          spent: 1800000,
          progress: 60,
          deadline: '2025-02-28',
          status: 'on_track'
        },
        {
          id: 3,
          name: 'Rural Road Improvement',
          budget: 8000000,
          spent: 3200000,
          progress: 40,
          deadline: '2025-06-30',
          status: 'delayed'
        }
      ]);

    } catch (error) {
      console.error('Error loading dashboard:', error);
    } finally {
      setLoading(false);
    }
  };

  const getStatusColor = (status) => {
    const colors = {
      submitted: 'bg-blue-100 text-blue-800',
      in_progress: 'bg-yellow-100 text-yellow-800',
      resolved: 'bg-green-100 text-green-800',
      rejected: 'bg-red-100 text-red-800'
    };
    return colors[status] || 'bg-gray-100 text-gray-800';
  };

  const getPriorityColor = (priority) => {
    const colors = {
      high: 'text-red-600',
      medium: 'text-yellow-600',
      low: 'text-green-600'
    };
    return colors[priority] || 'text-gray-600';
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
                PDO Dashboard
              </h1>
              <p className="mt-1 text-sm text-gray-600">
                {user?.gramPanchayatName || 'Gram Panchayat'} • Panchayat Development Officer
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
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
          <div className="bg-white rounded-lg shadow p-6">
            <div className="flex items-center">
              <div className="flex-shrink-0">
                <FileText className="h-8 w-8 text-indigo-600" />
              </div>
              <div className="ml-4">
                <p className="text-sm font-medium text-gray-600">Total Submissions</p>
                <p className="text-2xl font-bold text-gray-900">{stats.totalSubmissions}</p>
              </div>
            </div>
          </div>

          <div className="bg-white rounded-lg shadow p-6">
            <div className="flex items-center">
              <div className="flex-shrink-0">
                <AlertCircle className="h-8 w-8 text-yellow-600" />
              </div>
              <div className="ml-4">
                <p className="text-sm font-medium text-gray-600">Pending Action</p>
                <p className="text-2xl font-bold text-gray-900">{stats.pendingSubmissions}</p>
              </div>
            </div>
          </div>

          <div className="bg-white rounded-lg shadow p-6">
            <div className="flex items-center">
              <div className="flex-shrink-0">
                <Clock className="h-8 w-8 text-blue-600" />
              </div>
              <div className="ml-4">
                <p className="text-sm font-medium text-gray-600">In Progress</p>
                <p className="text-2xl font-bold text-gray-900">{stats.inProgress}</p>
              </div>
            </div>
          </div>

          <div className="bg-white rounded-lg shadow p-6">
            <div className="flex items-center">
              <div className="flex-shrink-0">
                <CheckCircle className="h-8 w-8 text-green-600" />
              </div>
              <div className="ml-4">
                <p className="text-sm font-medium text-gray-600">Resolved</p>
                <p className="text-2xl font-bold text-gray-900">{stats.resolved}</p>
              </div>
            </div>
          </div>

          <div className="bg-white rounded-lg shadow p-6">
            <div className="flex items-center">
              <div className="flex-shrink-0">
                <Users className="h-8 w-8 text-purple-600" />
              </div>
              <div className="ml-4">
                <p className="text-sm font-medium text-gray-600">Total Citizens</p>
                <p className="text-2xl font-bold text-gray-900">{stats.totalCitizens.toLocaleString()}</p>
              </div>
            </div>
          </div>

          <div className="bg-white rounded-lg shadow p-6">
            <div className="flex items-center">
              <div className="flex-shrink-0">
                <TrendingUp className="h-8 w-8 text-indigo-600" />
              </div>
              <div className="ml-4">
                <p className="text-sm font-medium text-gray-600">Active Schemes</p>
                <p className="text-2xl font-bold text-gray-900">{stats.schemesActive}</p>
              </div>
            </div>
          </div>
        </div>

        {/* Main Content Grid */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
          {/* Recent Submissions */}
          <div className="bg-white rounded-lg shadow">
            <div className="px-6 py-4 border-b border-gray-200">
              <h2 className="text-lg font-semibold text-gray-900">Recent Submissions</h2>
            </div>
            <div className="divide-y divide-gray-200">
              {recentSubmissions.map((submission) => (
                <div key={submission.id} className="p-6 hover:bg-gray-50 cursor-pointer">
                  <div className="flex items-start justify-between">
                    <div className="flex-1">
                      <h3 className="text-sm font-medium text-gray-900">{submission.title}</h3>
                      <p className="mt-1 text-sm text-gray-600">by {submission.citizenName}</p>
                      <div className="mt-2 flex items-center space-x-4">
                        <span className="text-xs text-gray-500">
                          {submission.category}
                        </span>
                        <span className={`text-xs font-medium ${getPriorityColor(submission.priority)}`}>
                          {submission.priority.toUpperCase()} Priority
                        </span>
                      </div>
                    </div>
                    <span className={`px-3 py-1 text-xs font-medium rounded-full ${getStatusColor(submission.status)}`}>
                      {submission.status.replace('_', ' ')}
                    </span>
                  </div>
                  <div className="mt-3 flex items-center text-xs text-gray-500">
                    <Calendar className="h-4 w-4 mr-1" />
                    {submission.submittedAt}
                  </div>
                </div>
              ))}
            </div>
            <div className="px-6 py-4 border-t border-gray-200">
              <button className="text-sm text-indigo-600 hover:text-indigo-800 font-medium">
                View All Submissions →
              </button>
            </div>
          </div>

          {/* Development Works */}
          <div className="bg-white rounded-lg shadow">
            <div className="px-6 py-4 border-b border-gray-200">
              <h2 className="text-lg font-semibold text-gray-900">Development Works</h2>
            </div>
            <div className="divide-y divide-gray-200">
              {developmentWorks.map((work) => (
                <div key={work.id} className="p-6">
                  <div className="flex items-start justify-between mb-3">
                    <div>
                      <h3 className="text-sm font-medium text-gray-900">{work.name}</h3>
                      <p className="mt-1 text-xs text-gray-600">
                        Budget: ₹{(work.budget / 100000).toFixed(1)}L • Spent: ₹{(work.spent / 100000).toFixed(1)}L
                      </p>
                    </div>
                    <span className={`px-2 py-1 text-xs font-medium rounded ${
                      work.status === 'on_track' 
                        ? 'bg-green-100 text-green-800' 
                        : 'bg-red-100 text-red-800'
                    }`}>
                      {work.status === 'on_track' ? 'On Track' : 'Delayed'}
                    </span>
                  </div>
                  
                  <div className="mb-2">
                    <div className="flex items-center justify-between text-xs text-gray-600 mb-1">
                      <span>Progress</span>
                      <span>{work.progress}%</span>
                    </div>
                    <div className="w-full bg-gray-200 rounded-full h-2">
                      <div 
                        className={`h-2 rounded-full ${
                          work.progress >= 75 ? 'bg-green-600' : 
                          work.progress >= 50 ? 'bg-blue-600' : 
                          'bg-yellow-600'
                        }`}
                        style={{ width: `${work.progress}%` }}
                      ></div>
                    </div>
                  </div>
                  
                  <div className="flex items-center text-xs text-gray-500">
                    <Calendar className="h-4 w-4 mr-1" />
                    Deadline: {work.deadline}
                  </div>
                </div>
              ))}
            </div>
            <div className="px-6 py-4 border-t border-gray-200">
              <button className="text-sm text-indigo-600 hover:text-indigo-800 font-medium">
                View All Projects →
              </button>
            </div>
          </div>
        </div>

        {/* Quick Actions */}
        <div className="mt-8 grid grid-cols-1 md:grid-cols-3 gap-6">
          <button className="bg-white rounded-lg shadow p-6 hover:shadow-md transition-shadow text-left">
            <FileCheck className="h-8 w-8 text-indigo-600 mb-3" />
            <h3 className="text-lg font-semibold text-gray-900">Generate Report</h3>
            <p className="mt-1 text-sm text-gray-600">
              Create monthly progress report for Taluk Panchayat
            </p>
          </button>

          <button className="bg-white rounded-lg shadow p-6 hover:shadow-md transition-shadow text-left">
            <PhoneCall className="h-8 w-8 text-green-600 mb-3" />
            <h3 className="text-lg font-semibold text-gray-900">Coordinate Meeting</h3>
            <p className="mt-1 text-sm text-gray-600">
              Schedule meeting with VA and department officers
            </p>
          </button>

          <button className="bg-white rounded-lg shadow p-6 hover:shadow-md transition-shadow text-left">
            <MapPin className="h-8 w-8 text-purple-600 mb-3" />
            <h3 className="text-lg font-semibold text-gray-900">Field Visit</h3>
            <p className="mt-1 text-sm text-gray-600">
              Plan field inspection of ongoing development works
            </p>
          </button>
        </div>
      </div>
    </div>
  );
};

export default Dashboard;
