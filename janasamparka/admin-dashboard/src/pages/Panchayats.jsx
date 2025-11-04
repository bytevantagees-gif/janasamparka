import { useState } from 'react';
import { useQuery } from '@tanstack/react-query';
import { Link } from 'react-router-dom';
import { 
  Building2, 
  MapPin, 
  Users, 
  ChevronRight, 
  Search,
  Layers,
  Home,
  TrendingUp,
  TrendingDown,
  AlertCircle,
  CheckCircle,
  Clock,
  DollarSign,
  Phone,
  Mail,
  MapPinned,
  BarChart3,
  Filter,
  Download,
  RefreshCw
} from 'lucide-react';
import { panchayatsAPI, complaintsAPI } from '../services/api';
import { useAuth } from '../contexts/AuthContext';

function Panchayats() {
  const { user } = useAuth();
  const [searchTerm, setSearchTerm] = useState('');
  const [viewMode, setViewMode] = useState('performance'); // 'hierarchy', 'performance', 'comparison'
  const [filterStatus, setFilterStatus] = useState('all'); // 'all', 'good', 'warning', 'critical'

  // Fetch all levels
  const { data: zpData, isLoading: zpLoading } = useQuery({
    queryKey: ['zilla-panchayats'],
    queryFn: async () => {
      const response = await panchayatsAPI.getAllZP();
      return response.data;
    },
  });

  const { data: tpData, isLoading: tpLoading } = useQuery({
    queryKey: ['taluk-panchayats'],
    queryFn: async () => {
      const response = await panchayatsAPI.getAllTP();
      return response.data;
    },
  });

  const { data: gpData, isLoading: gpLoading } = useQuery({
    queryKey: ['gram-panchayats'],
    queryFn: async () => {
      const response = await panchayatsAPI.getAllGP();
      return response.data;
    },
  });

  // Fetch complaints for panchayat analysis
  const { data: complaintsData } = useQuery({
    queryKey: ['panchayat-complaints'],
    queryFn: async () => {
      const response = await complaintsAPI.getAll({ page_size: 1000 });
      return response.data;
    },
  });

  const zillaPanchayats = zpData || [];
  const talukPanchayats = tpData || [];
  const gramPanchayats = gpData || [];
  const complaints = complaintsData?.complaints || [];

  // Calculate performance metrics for each GP
  const calculateGPMetrics = (gp) => {
    const gpComplaints = complaints.filter(c => c.gram_panchayat_id === gp.id);
    const resolved = gpComplaints.filter(c => c.status === 'resolved').length;
    const pending = gpComplaints.filter(c => c.status === 'submitted' || c.status === 'assigned' || c.status === 'in_progress').length;
    const total = gpComplaints.length;
    const resolutionRate = total > 0 ? ((resolved / total) * 100).toFixed(1) : 0;

    // Calculate health score
    let healthScore = 100;
    if (pending > 10) healthScore -= 30;
    else if (pending > 5) healthScore -= 15;
    if (resolutionRate < 50) healthScore -= 30;
    else if (resolutionRate < 70) healthScore -= 15;

    return {
      total,
      resolved,
      pending,
      resolutionRate,
      healthScore,
      status: healthScore >= 70 ? 'good' : healthScore >= 50 ? 'warning' : 'critical'
    };
  };

  // Enrich GPs with metrics
  const enrichedGPs = gramPanchayats.map(gp => ({
    ...gp,
    metrics: calculateGPMetrics(gp),
    taluk: talukPanchayats.find(tp => tp.id === gp.taluk_panchayat_id),
    zilla: zillaPanchayats.find(zp => zp.id === talukPanchayats.find(tp => tp.id === gp.taluk_panchayat_id)?.zilla_panchayat_id)
  }));

  // Filter panchayats
  const filteredGPs = enrichedGPs.filter(gp => {
    const matchesSearch = !searchTerm || 
      gp.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
      gp.taluk?.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
      gp.zilla?.name.toLowerCase().includes(searchTerm.toLowerCase());
    
    const matchesStatus = filterStatus === 'all' || gp.metrics.status === filterStatus;
    
    return matchesSearch && matchesStatus;
  });

  // Calculate overall statistics
  const overallStats = {
    totalGPs: gramPanchayats.length,
    totalComplaints: complaints.length,
    avgResolutionRate: (enrichedGPs.reduce((sum, gp) => sum + parseFloat(gp.metrics.resolutionRate), 0) / enrichedGPs.length || 0).toFixed(1),
    goodPerformers: enrichedGPs.filter(gp => gp.metrics.status === 'good').length,
    needsAttention: enrichedGPs.filter(gp => gp.metrics.status === 'critical').length,
  };

  if (zpLoading || tpLoading || gpLoading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary-600 mx-auto"></div>
          <p className="mt-4 text-gray-600">Loading panchayat data...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Header with Actions */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">Panchayat Performance Dashboard</h1>
          <p className="mt-1 text-sm text-gray-500">
            Monitor development, resolve issues, and track progress across all panchayats
          </p>
        </div>
        <div className="flex items-center space-x-3">
          <button className="inline-flex items-center px-4 py-2 border border-gray-300 shadow-sm text-sm font-medium rounded-md text-gray-700 bg-white hover:bg-gray-50">
            <Download className="h-4 w-4 mr-2" />
            Export Report
          </button>
          <button 
            onClick={() => window.location.reload()}
            className="inline-flex items-center px-4 py-2 border border-gray-300 shadow-sm text-sm font-medium rounded-md text-gray-700 bg-white hover:bg-gray-50"
          >
            <RefreshCw className="h-4 w-4 mr-2" />
            Refresh
          </button>
        </div>
      </div>

      {/* Overall Statistics Dashboard */}
      <div className="grid grid-cols-1 gap-5 sm:grid-cols-2 lg:grid-cols-5">
        <div className="bg-gradient-to-br from-blue-500 to-blue-600 overflow-hidden shadow rounded-lg">
          <div className="p-5">
            <div className="flex items-center">
              <div className="flex-shrink-0">
                <Home className="h-8 w-8 text-white" />
              </div>
              <div className="ml-5 w-0 flex-1">
                <dl>
                  <dt className="text-sm font-medium text-blue-100 truncate">Total Gram Panchayats</dt>
                  <dd className="text-2xl font-bold text-white">{overallStats.totalGPs}</dd>
                </dl>
              </div>
            </div>
          </div>
        </div>

        <div className="bg-gradient-to-br from-purple-500 to-purple-600 overflow-hidden shadow rounded-lg">
          <div className="p-5">
            <div className="flex items-center">
              <div className="flex-shrink-0">
                <BarChart3 className="h-8 w-8 text-white" />
              </div>
              <div className="ml-5 w-0 flex-1">
                <dl>
                  <dt className="text-sm font-medium text-purple-100 truncate">Total Issues</dt>
                  <dd className="text-2xl font-bold text-white">{overallStats.totalComplaints}</dd>
                </dl>
              </div>
            </div>
          </div>
        </div>

        <div className="bg-gradient-to-br from-green-500 to-green-600 overflow-hidden shadow rounded-lg">
          <div className="p-5">
            <div className="flex items-center">
              <div className="flex-shrink-0">
                <TrendingUp className="h-8 w-8 text-white" />
              </div>
              <div className="ml-5 w-0 flex-1">
                <dl>
                  <dt className="text-sm font-medium text-green-100 truncate">Avg Resolution Rate</dt>
                  <dd className="text-2xl font-bold text-white">{overallStats.avgResolutionRate}%</dd>
                </dl>
              </div>
            </div>
          </div>
        </div>

        <div className="bg-gradient-to-br from-emerald-500 to-emerald-600 overflow-hidden shadow rounded-lg">
          <div className="p-5">
            <div className="flex items-center">
              <div className="flex-shrink-0">
                <CheckCircle className="h-8 w-8 text-white" />
              </div>
              <div className="ml-5 w-0 flex-1">
                <dl>
                  <dt className="text-sm font-medium text-emerald-100 truncate">Good Performers</dt>
                  <dd className="text-2xl font-bold text-white">{overallStats.goodPerformers}</dd>
                </dl>
              </div>
            </div>
          </div>
        </div>

        <div className="bg-gradient-to-br from-red-500 to-red-600 overflow-hidden shadow rounded-lg">
          <div className="p-5">
            <div className="flex items-center">
              <div className="flex-shrink-0">
                <AlertCircle className="h-8 w-8 text-white" />
              </div>
              <div className="ml-5 w-0 flex-1">
                <dl>
                  <dt className="text-sm font-medium text-red-100 truncate">Needs Attention</dt>
                  <dd className="text-2xl font-bold text-white">{overallStats.needsAttention}</dd>
                </dl>
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Search and Filters */}
      <div className="bg-white p-4 rounded-lg shadow">
        <div className="flex flex-col sm:flex-row gap-4">
          <div className="flex-1 relative">
            <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 h-5 w-5 text-gray-400" />
            <input
              type="text"
              placeholder="Search by Panchayat, Taluk, or Zilla name..."
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              className="pl-10 w-full border-gray-300 rounded-md shadow-sm focus:ring-primary-500 focus:border-primary-500"
            />
          </div>
          <select
            value={filterStatus}
            onChange={(e) => setFilterStatus(e.target.value)}
            className="border-gray-300 rounded-md shadow-sm focus:ring-primary-500 focus:border-primary-500"
          >
            <option value="all">All Panchayats</option>
            <option value="good">Good Performers</option>
            <option value="warning">Needs Improvement</option>
            <option value="critical">Critical - Needs Attention</option>
          </select>
        </div>
      </div>

      {/* Performance Cards Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        {filteredGPs.length === 0 ? (
          <div className="col-span-3 p-8 text-center text-gray-500 bg-white rounded-lg shadow">
            No panchayats found matching your criteria
          </div>
        ) : (
          filteredGPs.map((gp) => (
            <div key={gp.id} className="bg-white rounded-lg shadow hover:shadow-lg transition-shadow border-l-4" style={{
              borderLeftColor: gp.metrics.status === 'good' ? '#10b981' : gp.metrics.status === 'warning' ? '#f59e0b' : '#ef4444'
            }}>
              <div className="p-6">
                {/* Header */}
                <div className="flex items-start justify-between mb-4">
                  <div className="flex-1">
                    <h3 className="text-lg font-semibold text-gray-900">{gp.name}</h3>
                    <p className="text-sm text-gray-500 mt-1">
                      {gp.taluk?.name} Taluk, {gp.zilla?.name}
                    </p>
                  </div>
                  <div className={`px-3 py-1 rounded-full text-xs font-medium ${
                    gp.metrics.status === 'good' ? 'bg-green-100 text-green-800' :
                    gp.metrics.status === 'warning' ? 'bg-yellow-100 text-yellow-800' :
                    'bg-red-100 text-red-800'
                  }`}>
                    Score: {gp.metrics.healthScore}
                  </div>
                </div>

                {/* Metrics Grid */}
                <div className="grid grid-cols-2 gap-4 mb-4">
                  <div className="bg-blue-50 rounded-lg p-3">
                    <p className="text-xs text-blue-600 font-medium">Population</p>
                    <p className="text-lg font-bold text-blue-900">{gp.population?.toLocaleString() || 'N/A'}</p>
                    <p className="text-xs text-blue-600">{gp.households?.toLocaleString() || 'N/A'} households</p>
                  </div>
                  <div className="bg-purple-50 rounded-lg p-3">
                    <p className="text-xs text-purple-600 font-medium">Total Issues</p>
                    <p className="text-lg font-bold text-purple-900">{gp.metrics.total}</p>
                    <p className="text-xs text-purple-600">{gp.metrics.pending} pending</p>
                  </div>
                  <div className="bg-green-50 rounded-lg p-3">
                    <p className="text-xs text-green-600 font-medium">Resolved</p>
                    <p className="text-lg font-bold text-green-900">{gp.metrics.resolved}</p>
                    <p className="text-xs text-green-600">{gp.metrics.resolutionRate}% rate</p>
                  </div>
                  <div className="bg-orange-50 rounded-lg p-3">
                    <p className="text-xs text-orange-600 font-medium">Status</p>
                    <p className="text-lg font-bold text-orange-900">
                      {gp.metrics.status === 'good' ? 'Good' : gp.metrics.status === 'warning' ? 'Fair' : 'Critical'}
                    </p>
                    {gp.metrics.pending > 0 && (
                      <p className="text-xs text-orange-600">Action needed</p>
                    )}
                  </div>
                </div>

                {/* Contact Information */}
                {gp.president_name && (
                  <div className="bg-gray-50 rounded-lg p-3 mb-4">
                    <p className="text-xs text-gray-600 font-medium mb-1">President</p>
                    <p className="text-sm font-semibold text-gray-900">{gp.president_name}</p>
                    {gp.president_phone && (
                      <div className="flex items-center mt-1 text-xs text-gray-600">
                        <Phone className="h-3 w-3 mr-1" />
                        {gp.president_phone}
                      </div>
                    )}
                  </div>
                )}

                {/* Quick Actions */}
                <div className="flex items-center space-x-2">
                  <Link
                    to={`/panchayats/gram/${gp.id}`}
                    className="flex-1 inline-flex items-center justify-center px-3 py-2 border border-primary-300 shadow-sm text-sm font-medium rounded-md text-primary-700 bg-white hover:bg-primary-50"
                  >
                    View Details
                    <ChevronRight className="ml-1 h-4 w-4" />
                  </Link>
                  {gp.metrics.pending > 0 && (
                    <Link
                      to={`/complaints?gram_panchayat=${gp.id}&status=pending`}
                      className="flex-1 inline-flex items-center justify-center px-3 py-2 border border-transparent shadow-sm text-sm font-medium rounded-md text-white bg-orange-600 hover:bg-orange-700"
                    >
                      <AlertCircle className="mr-1 h-4 w-4" />
                      {gp.metrics.pending} Pending
                    </Link>
                  )}
                </div>
              </div>
            </div>
          ))
        )}
      </div>

      {/* Top Performers & Bottom Performers */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Top Performers */}
        <div className="bg-white rounded-lg shadow">
          <div className="p-6 border-b border-gray-200">
            <h3 className="text-lg font-semibold text-gray-900 flex items-center">
              <TrendingUp className="w-5 h-5 mr-2 text-green-600" />
              Top 5 Performing Panchayats
            </h3>
          </div>
          <div className="p-6">
            <div className="space-y-3">
              {enrichedGPs
                .sort((a, b) => b.metrics.healthScore - a.metrics.healthScore)
                .slice(0, 5)
                .map((gp, idx) => (
                  <div key={gp.id} className="flex items-center justify-between p-3 bg-green-50 rounded-lg">
                    <div className="flex items-center space-x-3">
                      <div className="flex-shrink-0 w-8 h-8 bg-green-600 text-white rounded-full flex items-center justify-center font-bold">
                        {idx + 1}
                      </div>
                      <div>
                        <p className="font-medium text-gray-900">{gp.name}</p>
                        <p className="text-sm text-gray-600">{gp.taluk?.name}</p>
                      </div>
                    </div>
                    <div className="text-right">
                      <p className="text-lg font-bold text-green-700">{gp.metrics.healthScore}</p>
                      <p className="text-xs text-gray-600">{gp.metrics.resolutionRate}% resolved</p>
                    </div>
                  </div>
                ))}
            </div>
          </div>
        </div>

        {/* Needs Attention */}
        <div className="bg-white rounded-lg shadow">
          <div className="p-6 border-b border-gray-200">
            <h3 className="text-lg font-semibold text-gray-900 flex items-center">
              <AlertCircle className="w-5 h-5 mr-2 text-red-600" />
              Panchayats Needing Attention
            </h3>
          </div>
          <div className="p-6">
            <div className="space-y-3">
              {enrichedGPs
                .filter(gp => gp.metrics.status === 'critical' || gp.metrics.pending > 5)
                .sort((a, b) => a.metrics.healthScore - b.metrics.healthScore)
                .slice(0, 5)
                .map((gp, idx) => (
                  <div key={gp.id} className="flex items-center justify-between p-3 bg-red-50 rounded-lg">
                    <div className="flex items-center space-x-3">
                      <div className="flex-shrink-0 w-8 h-8 bg-red-600 text-white rounded-full flex items-center justify-center font-bold">
                        !
                      </div>
                      <div>
                        <p className="font-medium text-gray-900">{gp.name}</p>
                        <p className="text-sm text-gray-600">{gp.taluk?.name}</p>
                      </div>
                    </div>
                    <div className="text-right">
                      <p className="text-lg font-bold text-red-700">{gp.metrics.pending}</p>
                      <p className="text-xs text-gray-600">pending issues</p>
                    </div>
                  </div>
                ))}
              {enrichedGPs.filter(gp => gp.metrics.status === 'critical' || gp.metrics.pending > 5).length === 0 && (
                <div className="text-center text-gray-500 py-8">
                  <CheckCircle className="w-12 h-12 mx-auto text-green-500 mb-2" />
                  <p>All panchayats performing well!</p>
                </div>
              )}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}

export default Panchayats;
