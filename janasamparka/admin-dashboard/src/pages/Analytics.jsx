import { useState } from 'react';
import { useQuery } from '@tanstack/react-query';
import {
  TrendingUp,
  Award,
  Target,
  Download,
  Filter,
  Calendar,
  BarChart3,
  PieChart,
  Star,
  AlertTriangle
} from 'lucide-react';
import {
  LineChart,
  Line,
  BarChart,
  Bar,
  PieChart as RePieChart,
  Pie,
  Cell,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer
} from 'recharts';
import { analyticsAPI } from '../services/api';
import { useTranslation } from '../hooks/useTranslation';
import ClusterMapView from '../components/ClusterMapView';
import SeasonalForecastChart from '../components/SeasonalForecastChart';

const API_URL = 'http://localhost:8000/api';

const Analytics = () => {
  const { t } = useTranslation();
  const [dateRange, setDateRange] = useState('30');
  const [selectedConstituency, setSelectedConstituency] = useState('all');
  const [selectedDepartment, setSelectedDepartment] = useState('all');

  // Fetch analytics data
  const { data: dashboard, isLoading } = useQuery({
    queryKey: ['analytics-dashboard'],
    queryFn: async () => {
      const response = await analyticsAPI.getDashboard();
      return response.data;
    }
  });

  const { data: satisfaction } = useQuery({
    queryKey: ['citizen-satisfaction'],
    queryFn: async () => {
      const response = await analyticsAPI.getSatisfaction();
      return response.data;
    }
  });

  const { data: trends } = useQuery({
    queryKey: ['analytics-trends', dateRange],
    queryFn: async () => {
      const response = await analyticsAPI.getTrends({ days: dateRange });
      return response.data;
    }
  });

  const { data: alerts } = useQuery({
    queryKey: ['performance-alerts'],
    queryFn: async () => {
      const response = await analyticsAPI.getAlerts();
      return response.data;
    }
  });

  const handleExportCSV = async () => {
    const token = localStorage.getItem('access_token');
    const response = await fetch(`${API_URL}/analytics/export/csv`, {
      headers: { 'Authorization': `Bearer ${token}` }
    });
    const blob = await response.blob();
    const url = window.URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `complaints_${Date.now()}.csv`;
    a.click();
  };

  const handleExportJSON = async () => {
    const token = localStorage.getItem('access_token');
    const response = await fetch(`${API_URL}/analytics/export/json`, {
      headers: { 'Authorization': `Bearer ${token}` }
    });
    const data = await response.json();
    const blob = new Blob([JSON.stringify(data, null, 2)], { type: 'application/json' });
    const url = window.URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `complaints_${Date.now()}.json`;
    a.click();
  };

  if (isLoading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
      </div>
    );
  }

  // Prepare chart data
  const statusData = dashboard?.overall_stats ? [
    { name: 'Submitted', value: dashboard.overall_stats.submitted, color: '#3B82F6' },
    { name: 'Assigned', value: dashboard.overall_stats.assigned, color: '#8B5CF6' },
    { name: 'In Progress', value: dashboard.overall_stats.in_progress, color: '#F59E0B' },
    { name: 'Resolved', value: dashboard.overall_stats.resolved, color: '#10B981' },
    { name: 'Closed', value: dashboard.overall_stats.closed, color: '#059669' },
  ] : [];

  const categoryData = dashboard?.category_breakdown?.map(cat => ({
    name: cat.category,
    count: cat.count,
    resolved: cat.resolved,
    rate: cat.resolution_rate
  })) || [];

  const trendData = trends?.data_points?.map(point => ({
    date: new Date(point.date).toLocaleDateString('en-US', { month: 'short', day: 'numeric' }),
    new: point.new,
    resolved: point.resolved,
    total: point.count
  })) || [];

  const ratingData = satisfaction ? [
    { name: '5 Stars', value: satisfaction.rating_distribution?.['5'] || 0 },
    { name: '4 Stars', value: satisfaction.rating_distribution?.['4'] || 0 },
    { name: '3 Stars', value: satisfaction.rating_distribution?.['3'] || 0 },
    { name: '2 Stars', value: satisfaction.rating_distribution?.['2'] || 0 },
    { name: '1 Star', value: satisfaction.rating_distribution?.['1'] || 0 },
  ].filter(item => item.value > 0) : [];

  const COLORS = ['#10B981', '#3B82F6', '#F59E0B', '#EF4444', '#8B5CF6'];

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex justify-between items-center">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">{t('analyticsReports')}</h1>
          <p className="mt-1 text-sm text-gray-500">
            {t('comprehensiveInsights')}
          </p>
        </div>
        <div className="flex gap-2">
          <button
            onClick={handleExportCSV}
            className="flex items-center gap-2 px-4 py-2 bg-white border border-gray-300 rounded-lg hover:bg-gray-50"
          >
            <Download className="h-4 w-4" />
            {t('exportCSV')}
          </button>
          <button
            onClick={handleExportJSON}
            className="flex items-center gap-2 px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700"
          >
            <Download className="h-4 w-4" />
            {t('exportJSON')}
          </button>
        </div>
      </div>

      {/* Filters */}
      <div className="bg-white p-4 rounded-lg shadow flex gap-4 items-end">
        <div className="flex-1">
          <label className="block text-sm font-medium text-gray-700 mb-1">
            {t('dateRange')}
          </label>
          <select
            value={dateRange}
            onChange={(e) => setDateRange(e.target.value)}
            className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
          >
            <option value="7">{t('last7Days')}</option>
            <option value="30">{t('last30Days')}</option>
            <option value="90">{t('last90Days')}</option>
            <option value="180">{t('last6Months')}</option>
            <option value="365">{t('lastYear')}</option>
          </select>
        </div>
      </div>

      {/* Key Metrics */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        <div className="bg-white p-6 rounded-lg shadow">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-gray-600">{t('totalComplaints')}</p>
              <p className="text-3xl font-bold text-gray-900">
                {dashboard?.overall_stats?.total || 0}
              </p>
            </div>
            <BarChart3 className="h-12 w-12 text-blue-500" />
          </div>
        </div>

        <div className="bg-white p-6 rounded-lg shadow">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-gray-600">{t('resolutionRate')}</p>
              <p className="text-3xl font-bold text-green-600">
                {dashboard?.resolution_rate?.toFixed(1) || 0}%
              </p>
            </div>
            <Target className="h-12 w-12 text-green-500" />
          </div>
        </div>

        <div className="bg-white p-6 rounded-lg shadow">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-gray-600">{t('avgRating')}</p>
              <p className="text-3xl font-bold text-yellow-600">
                {satisfaction?.average_rating?.toFixed(1) || 0}
                <span className="text-lg text-gray-400">/5</span>
              </p>
            </div>
            <Star className="h-12 w-12 text-yellow-500" />
          </div>
        </div>

        <div className="bg-white p-6 rounded-lg shadow">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-gray-600">{t('slaCompliance')}</p>
              <p className="text-3xl font-bold text-purple-600">
                {dashboard?.sla_metrics?.sla_compliance_rate?.toFixed(0) || 0}%
              </p>
            </div>
            <Award className="h-12 w-12 text-purple-500" />
          </div>
        </div>
      </div>

      {/* Performance Alerts */}
      {alerts?.alerts && alerts.alerts.length > 0 && (
        <div className="bg-yellow-50 border border-yellow-200 rounded-lg p-4">
          <div className="flex items-start gap-3">
            <AlertTriangle className="h-5 w-5 text-yellow-600 flex-shrink-0 mt-0.5" />
            <div className="flex-1">
              <h3 className="text-sm font-medium text-yellow-800">{t('performanceAlerts')}</h3>
              <div className="mt-2 space-y-2">
                {alerts.alerts.map((alert, index) => (
                  <div key={index} className="text-sm text-yellow-700">
                    <span className={`font-medium ${
                      alert.severity === 'high' ? 'text-red-700' :
                      alert.severity === 'medium' ? 'text-yellow-700' :
                      'text-blue-700'
                    }`}>
                      [{alert.severity.toUpperCase()}]
                    </span> {alert.message}
                    {alert.affected_count && ` (${alert.affected_count} complaints)`}
                  </div>
                ))}
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Charts Grid */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Trend Chart */}
        <div className="bg-white p-6 rounded-lg shadow">
          <h3 className="text-lg font-semibold text-gray-900 mb-4">{t('complaintsTrend')}</h3>
          <ResponsiveContainer width="100%" height={300}>
            <LineChart data={trendData}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis dataKey="date" />
              <YAxis />
              <Tooltip />
              <Legend />
              <Line type="monotone" dataKey="new" stroke="#3B82F6" name="New" strokeWidth={2} />
              <Line type="monotone" dataKey="resolved" stroke="#10B981" name="Resolved" strokeWidth={2} />
            </LineChart>
          </ResponsiveContainer>
          <div className="mt-4 text-center">
            <span className={`text-sm font-medium ${
              trends?.trend_direction === 'increasing' ? 'text-red-600' :
              trends?.trend_direction === 'decreasing' ? 'text-green-600' :
              'text-gray-600'
            }`}>
              Trend: {trends?.trend_direction || 'stable'}
              {trends?.trend_direction === 'increasing' && ' ▲'}
              {trends?.trend_direction === 'decreasing' && ' ▼'}
            </span>
          </div>
        </div>

        {/* Status Distribution */}
        <div className="bg-white p-6 rounded-lg shadow">
          <h3 className="text-lg font-semibold text-gray-900 mb-4">{t('statusDistribution')}</h3>
          <ResponsiveContainer width="100%" height={300}>
            <RePieChart>
              <Pie
                data={statusData}
                cx="50%"
                cy="50%"
                labelLine={false}
                label={({ name, percent }) => `${name}: ${(percent * 100).toFixed(0)}%`}
                outerRadius={80}
                fill="#8884d8"
                dataKey="value"
              >
                {statusData.map((entry, index) => (
                  <Cell key={`cell-${index}`} fill={entry.color} />
                ))}
              </Pie>
              <Tooltip />
            </RePieChart>
          </ResponsiveContainer>
        </div>

        {/* Category Performance */}
        <div className="bg-white p-6 rounded-lg shadow">
          <h3 className="text-lg font-semibold text-gray-900 mb-4">{t('categoryPerformance')}</h3>
          <ResponsiveContainer width="100%" height={300}>
            <BarChart data={categoryData}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis dataKey="name" />
              <YAxis />
              <Tooltip />
              <Legend />
              <Bar dataKey="count" fill="#3B82F6" name="Total" />
              <Bar dataKey="resolved" fill="#10B981" name="Resolved" />
            </BarChart>
          </ResponsiveContainer>
        </div>

        {/* Citizen Satisfaction */}
        <div className="bg-white p-6 rounded-lg shadow">
          <h3 className="text-lg font-semibold text-gray-900 mb-4">{t('citizenSatisfaction')}</h3>
          {satisfaction && satisfaction.total_ratings > 0 ? (
            <>
              <ResponsiveContainer width="100%" height={250}>
                <BarChart data={ratingData} layout="vertical">
                  <CartesianGrid strokeDasharray="3 3" />
                  <XAxis type="number" />
                  <YAxis dataKey="name" type="category" />
                  <Tooltip />
                  <Bar dataKey="value" fill="#F59E0B" />
                </BarChart>
              </ResponsiveContainer>
              <div className="mt-4 grid grid-cols-2 gap-4 text-center">
                <div>
                  <p className="text-2xl font-bold text-gray-900">{satisfaction.total_ratings}</p>
                  <p className="text-sm text-gray-600">{t('totalRatings')}</p>
                </div>
                <div>
                  <p className="text-2xl font-bold text-green-600">
                    {satisfaction.satisfaction_rate.toFixed(0)}%
                  </p>
                  <p className="text-sm text-gray-600">{t('satisfactionRate')}</p>
                </div>
              </div>
            </>
          ) : (
            <div className="flex items-center justify-center h-64 text-gray-400">
              <p>{t('noRatingsYet')}</p>
            </div>
          )}
        </div>
      </div>

      {/* Department Performance Table */}
      {dashboard?.department_performance && dashboard.department_performance.length > 0 && (
        <div className="bg-white rounded-lg shadow overflow-hidden">
          <div className="px-6 py-4 border-b border-gray-200">
            <h3 className="text-lg font-semibold text-gray-900">{t('departmentPerformance')}</h3>
          </div>
          <div className="overflow-x-auto">
            <table className="min-w-full divide-y divide-gray-200">
              <thead className="bg-gray-50">
                <tr>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    {t('department')}
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    {t('totalAssigned')}
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    {t('completed')}
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    {t('completionRate')}
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    {t('avgResolutionTime')}
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    SLA Compliance
                  </th>
                </tr>
              </thead>
              <tbody className="bg-white divide-y divide-gray-200">
                {dashboard.department_performance.map((dept) => (
                  <tr key={dept.department_id}>
                    <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900">
                      {dept.department_name}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                      {dept.total_assigned}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                      {dept.completed}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap">
                      <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${
                        dept.completion_rate >= 80 ? 'bg-green-100 text-green-800' :
                        dept.completion_rate >= 60 ? 'bg-yellow-100 text-yellow-800' :
                        'bg-red-100 text-red-800'
                      }`}>
                        {dept.completion_rate.toFixed(1)}%
                      </span>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                      {dept.avg_resolution_time_hours ? 
                        `${(dept.avg_resolution_time_hours / 24).toFixed(1)} {t('days')}` : 
                        'N/A'
                      }
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap">
                      <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${
                        dept.on_time_rate >= 85 ? 'bg-green-100 text-green-800' :
                        dept.on_time_rate >= 70 ? 'bg-yellow-100 text-yellow-800' :
                        'bg-red-100 text-red-800'
                      }`}>
                        {dept.on_time_rate ? dept.on_time_rate.toFixed(0) : 0}%
                      </span>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      )}

      {/* Geographic Clustering Section */}
      {dashboard && dashboard.constituency_id && (
        <div className="bg-white shadow rounded-lg p-6">
          <h3 className="text-lg font-medium text-gray-900 mb-4">Geographic Complaint Clustering</h3>
          <div className="h-[500px]">
            <ClusterMapView
              clusters={dashboard.complaint_clusters || []}
              center={dashboard.map_center || [12.9716, 77.5946]}
              zoom={12}
              onClusterClick={(cluster) => {
                console.log('Cluster selected:', cluster);
                // TODO: Navigate to cluster details or show modal
              }}
            />
          </div>
        </div>
      )}

      {/* Seasonal Forecast Section */}
      {dashboard && dashboard.constituency_id && (
        <div className="bg-white shadow rounded-lg p-6">
          <SeasonalForecastChart
            constituencyId={dashboard.constituency_id}
            months={6}
            showRecommendations={true}
          />
        </div>
      )}
    </div>
  );
};

export default Analytics;
