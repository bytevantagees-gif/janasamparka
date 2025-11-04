import React, { useState, useEffect } from 'react';
import { 
  FileText, Users, IndianRupee, CheckCircle, Clock, 
  AlertCircle, Award, Calendar, Search, Filter, Download
} from 'lucide-react';
import { useAuth } from '../../contexts/AuthContext';

/**
 * Village Accountant Dashboard
 * 
 * Responsibilities:
 * - Issue certificates (income, caste, domicile, nativity, birth, death)
 * - Maintain land records and revenue data
 * - Collect property tax, water tax, trade license fees
 * - Update revenue records
 * - Facilitate government welfare schemes
 */

const Dashboard = () => {
  const { user } = useAuth();
  const [stats, setStats] = useState({
    pendingCertificates: 0,
    issuedToday: 0,
    totalThisMonth: 0,
    taxCollected: 0,
    pendingTaxCollection: 0,
    schemeApplications: 0
  });
  const [certificateRequests, setCertificateRequests] = useState([]);
  const [taxRecords, setTaxRecords] = useState([]);
  const [loading, setLoading] = useState(true);
  const [activeTab, setActiveTab] = useState('certificates'); // certificates, tax, schemes

  useEffect(() => {
    loadDashboardData();
  }, []);

  const loadDashboardData = async () => {
    try {
      setLoading(true);

      // TODO: Fetch real data from API
      setStats({
        pendingCertificates: 18,
        issuedToday: 7,
        totalThisMonth: 89,
        taxCollected: 245000,
        pendingTaxCollection: 82000,
        schemeApplications: 24
      });

      setCertificateRequests([
        {
          id: 1,
          type: 'Income Certificate',
          applicantName: 'Ramesh Kumar',
          village: 'Bolwar',
          submittedDate: '2024-10-28',
          status: 'pending',
          priority: 'high',
          phone: '+91 9876543210'
        },
        {
          id: 2,
          type: 'Caste Certificate',
          applicantName: 'Suma Bhat',
          village: 'Bolwar',
          submittedDate: '2024-10-27',
          status: 'under_review',
          priority: 'medium',
          phone: '+91 9876543211'
        },
        {
          id: 3,
          type: 'Domicile Certificate',
          applicantName: 'Krishna Rao',
          village: 'Kabaka',
          submittedDate: '2024-10-27',
          status: 'pending',
          priority: 'medium',
          phone: '+91 9876543212'
        },
        {
          id: 4,
          type: 'Birth Certificate',
          applicantName: 'Meena Shetty',
          village: 'Bolwar',
          submittedDate: '2024-10-26',
          status: 'ready_for_collection',
          priority: 'low',
          phone: '+91 9876543213'
        }
      ]);

      setTaxRecords([
        {
          id: 1,
          propertyId: 'BW-2024-001',
          ownerName: 'Manoj Shetty',
          village: 'Bolwar',
          taxType: 'Property Tax',
          amount: 5000,
          dueDate: '2024-11-30',
          status: 'paid',
          paidDate: '2024-10-25'
        },
        {
          id: 2,
          propertyId: 'BW-2024-002',
          ownerName: 'Vasanth Kumar',
          village: 'Bolwar',
          taxType: 'Water Tax',
          amount: 1200,
          dueDate: '2024-11-30',
          status: 'pending',
          paidDate: null
        },
        {
          id: 3,
          propertyId: 'KB-2024-015',
          ownerName: 'Ganesh Pai',
          village: 'Kabaka',
          taxType: 'Trade License',
          amount: 3000,
          dueDate: '2024-11-30',
          status: 'overdue',
          paidDate: null
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
      pending: 'bg-yellow-100 text-yellow-800',
      under_review: 'bg-blue-100 text-blue-800',
      ready_for_collection: 'bg-green-100 text-green-800',
      issued: 'bg-gray-100 text-gray-800',
      rejected: 'bg-red-100 text-red-800'
    };
    return colors[status] || 'bg-gray-100 text-gray-800';
  };

  const getTaxStatusColor = (status) => {
    const colors = {
      paid: 'bg-green-100 text-green-800',
      pending: 'bg-yellow-100 text-yellow-800',
      overdue: 'bg-red-100 text-red-800'
    };
    return colors[status] || 'bg-gray-100 text-gray-800';
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
                Village Accountant Dashboard
              </h1>
              <p className="mt-1 text-sm text-gray-600">
                {user?.gramPanchayatName || 'Gram Panchayat'} • Certificate & Revenue Officer
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
                <AlertCircle className="h-8 w-8 text-yellow-600" />
              </div>
              <div className="ml-4">
                <p className="text-sm font-medium text-gray-600">Pending Certificates</p>
                <p className="text-2xl font-bold text-gray-900">{stats.pendingCertificates}</p>
              </div>
            </div>
          </div>

          <div className="bg-white rounded-lg shadow p-6">
            <div className="flex items-center">
              <div className="flex-shrink-0">
                <CheckCircle className="h-8 w-8 text-green-600" />
              </div>
              <div className="ml-4">
                <p className="text-sm font-medium text-gray-600">Issued Today</p>
                <p className="text-2xl font-bold text-gray-900">{stats.issuedToday}</p>
              </div>
            </div>
          </div>

          <div className="bg-white rounded-lg shadow p-6">
            <div className="flex items-center">
              <div className="flex-shrink-0">
                <Award className="h-8 w-8 text-indigo-600" />
              </div>
              <div className="ml-4">
                <p className="text-sm font-medium text-gray-600">This Month</p>
                <p className="text-2xl font-bold text-gray-900">{stats.totalThisMonth}</p>
              </div>
            </div>
          </div>

          <div className="bg-white rounded-lg shadow p-6">
            <div className="flex items-center">
              <div className="flex-shrink-0">
                <IndianRupee className="h-8 w-8 text-green-600" />
              </div>
              <div className="ml-4">
                <p className="text-sm font-medium text-gray-600">Tax Collected</p>
                <p className="text-2xl font-bold text-gray-900">
                  ₹{(stats.taxCollected / 1000).toFixed(0)}K
                </p>
              </div>
            </div>
          </div>

          <div className="bg-white rounded-lg shadow p-6">
            <div className="flex items-center">
              <div className="flex-shrink-0">
                <Clock className="h-8 w-8 text-yellow-600" />
              </div>
              <div className="ml-4">
                <p className="text-sm font-medium text-gray-600">Pending Collection</p>
                <p className="text-2xl font-bold text-gray-900">
                  ₹{(stats.pendingTaxCollection / 1000).toFixed(0)}K
                </p>
              </div>
            </div>
          </div>

          <div className="bg-white rounded-lg shadow p-6">
            <div className="flex items-center">
              <div className="flex-shrink-0">
                <Users className="h-8 w-8 text-purple-600" />
              </div>
              <div className="ml-4">
                <p className="text-sm font-medium text-gray-600">Scheme Applications</p>
                <p className="text-2xl font-bold text-gray-900">{stats.schemeApplications}</p>
              </div>
            </div>
          </div>
        </div>

        {/* Tabs */}
        <div className="bg-white rounded-lg shadow mb-6">
          <div className="border-b border-gray-200">
            <nav className="flex -mb-px">
              <button
                onClick={() => setActiveTab('certificates')}
                className={`px-6 py-4 text-sm font-medium ${
                  activeTab === 'certificates'
                    ? 'border-b-2 border-indigo-500 text-indigo-600'
                    : 'text-gray-500 hover:text-gray-700'
                }`}
              >
                <FileText className="inline-block h-5 w-5 mr-2" />
                Certificates
              </button>
              <button
                onClick={() => setActiveTab('tax')}
                className={`px-6 py-4 text-sm font-medium ${
                  activeTab === 'tax'
                    ? 'border-b-2 border-indigo-500 text-indigo-600'
                    : 'text-gray-500 hover:text-gray-700'
                }`}
              >
                <IndianRupee className="inline-block h-5 w-5 mr-2" />
                Tax Collection
              </button>
              <button
                onClick={() => setActiveTab('schemes')}
                className={`px-6 py-4 text-sm font-medium ${
                  activeTab === 'schemes'
                    ? 'border-b-2 border-indigo-500 text-indigo-600'
                    : 'text-gray-500 hover:text-gray-700'
                }`}
              >
                <Award className="inline-block h-5 w-5 mr-2" />
                Schemes
              </button>
            </nav>
          </div>

          {/* Tab Content */}
          <div className="p-6">
            {activeTab === 'certificates' && (
              <div>
                <div className="flex items-center justify-between mb-6">
                  <div className="flex-1 max-w-lg">
                    <div className="relative">
                      <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400 h-5 w-5" />
                      <input
                        type="text"
                        placeholder="Search by name, type, or village..."
                        className="pl-10 pr-4 py-2 w-full border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500"
                      />
                    </div>
                  </div>
                  <div className="flex space-x-2">
                    <button className="px-4 py-2 text-sm font-medium text-gray-700 bg-white border border-gray-300 rounded-lg hover:bg-gray-50">
                      <Filter className="inline-block h-4 w-4 mr-2" />
                      Filter
                    </button>
                    <button className="px-4 py-2 text-sm font-medium text-white bg-indigo-600 rounded-lg hover:bg-indigo-700">
                      New Certificate
                    </button>
                  </div>
                </div>

                <div className="overflow-x-auto">
                  <table className="min-w-full divide-y divide-gray-200">
                    <thead className="bg-gray-50">
                      <tr>
                        <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                          Applicant
                        </th>
                        <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                          Certificate Type
                        </th>
                        <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                          Village
                        </th>
                        <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                          Submitted
                        </th>
                        <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                          Status
                        </th>
                        <th className="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase tracking-wider">
                          Actions
                        </th>
                      </tr>
                    </thead>
                    <tbody className="bg-white divide-y divide-gray-200">
                      {certificateRequests.map((request) => (
                        <tr key={request.id} className="hover:bg-gray-50">
                          <td className="px-6 py-4 whitespace-nowrap">
                            <div>
                              <div className="text-sm font-medium text-gray-900">{request.applicantName}</div>
                              <div className="text-xs text-gray-500">{request.phone}</div>
                            </div>
                          </td>
                          <td className="px-6 py-4 whitespace-nowrap">
                            <div className="text-sm text-gray-900">{request.type}</div>
                          </td>
                          <td className="px-6 py-4 whitespace-nowrap">
                            <div className="text-sm text-gray-900">{request.village}</div>
                          </td>
                          <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                            {request.submittedDate}
                          </td>
                          <td className="px-6 py-4 whitespace-nowrap">
                            <span className={`px-3 py-1 inline-flex text-xs leading-5 font-semibold rounded-full ${getStatusColor(request.status)}`}>
                              {request.status.replace('_', ' ')}
                            </span>
                          </td>
                          <td className="px-6 py-4 whitespace-nowrap text-right text-sm font-medium">
                            <button className="text-indigo-600 hover:text-indigo-900 mr-3">
                              Process
                            </button>
                            <button className="text-gray-600 hover:text-gray-900">
                              Details
                            </button>
                          </td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              </div>
            )}

            {activeTab === 'tax' && (
              <div>
                <div className="flex items-center justify-between mb-6">
                  <div className="flex-1 max-w-lg">
                    <div className="relative">
                      <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400 h-5 w-5" />
                      <input
                        type="text"
                        placeholder="Search by property ID or owner name..."
                        className="pl-10 pr-4 py-2 w-full border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500"
                      />
                    </div>
                  </div>
                  <div className="flex space-x-2">
                    <button className="px-4 py-2 text-sm font-medium text-gray-700 bg-white border border-gray-300 rounded-lg hover:bg-gray-50">
                      <Download className="inline-block h-4 w-4 mr-2" />
                      Export
                    </button>
                    <button className="px-4 py-2 text-sm font-medium text-white bg-green-600 rounded-lg hover:bg-green-700">
                      Record Payment
                    </button>
                  </div>
                </div>

                <div className="overflow-x-auto">
                  <table className="min-w-full divide-y divide-gray-200">
                    <thead className="bg-gray-50">
                      <tr>
                        <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                          Property ID
                        </th>
                        <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                          Owner
                        </th>
                        <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                          Tax Type
                        </th>
                        <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                          Amount
                        </th>
                        <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                          Due Date
                        </th>
                        <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                          Status
                        </th>
                        <th className="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase tracking-wider">
                          Actions
                        </th>
                      </tr>
                    </thead>
                    <tbody className="bg-white divide-y divide-gray-200">
                      {taxRecords.map((record) => (
                        <tr key={record.id} className="hover:bg-gray-50">
                          <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900">
                            {record.propertyId}
                          </td>
                          <td className="px-6 py-4 whitespace-nowrap">
                            <div>
                              <div className="text-sm text-gray-900">{record.ownerName}</div>
                              <div className="text-xs text-gray-500">{record.village}</div>
                            </div>
                          </td>
                          <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                            {record.taxType}
                          </td>
                          <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900">
                            ₹{record.amount.toLocaleString()}
                          </td>
                          <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                            {record.dueDate}
                          </td>
                          <td className="px-6 py-4 whitespace-nowrap">
                            <span className={`px-3 py-1 inline-flex text-xs leading-5 font-semibold rounded-full ${getTaxStatusColor(record.status)}`}>
                              {record.status}
                            </span>
                          </td>
                          <td className="px-6 py-4 whitespace-nowrap text-right text-sm font-medium">
                            {record.status === 'pending' || record.status === 'overdue' ? (
                              <button className="text-green-600 hover:text-green-900">
                                Collect
                              </button>
                            ) : (
                              <button className="text-gray-600 hover:text-gray-900">
                                Receipt
                              </button>
                            )}
                          </td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              </div>
            )}

            {activeTab === 'schemes' && (
              <div className="text-center py-12">
                <Users className="mx-auto h-12 w-12 text-gray-400" />
                <h3 className="mt-2 text-sm font-medium text-gray-900">Scheme Applications</h3>
                <p className="mt-1 text-sm text-gray-500">
                  Manage welfare scheme applications and beneficiary verification
                </p>
                <div className="mt-6">
                  <button className="inline-flex items-center px-4 py-2 border border-transparent shadow-sm text-sm font-medium rounded-md text-white bg-indigo-600 hover:bg-indigo-700">
                    View Applications
                  </button>
                </div>
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
};

export default Dashboard;
