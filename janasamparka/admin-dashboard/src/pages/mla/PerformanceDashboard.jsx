import React, { useState } from 'react';
import { useQuery } from '@tanstack/react-query';
import {
  BarChart, Bar, LineChart, Line, XAxis, YAxis, CartesianGrid, 
  Tooltip, Legend, ResponsiveContainer
} from 'recharts';
import { 
  TrendingUp, TrendingDown, AlertCircle, Award, Filter,
  ChevronDown, Download, RefreshCw
} from 'lucide-react';
import { analyticsAPI } from '../../services/api';

export default function MLAPerformanceDashboard() {
  const [unitType, setUnitType] = useState('ward');
  const [selectedUnits, setSelectedUnits] = useState([]);
  const [dateRange, setDateRange] = useState('last_30_days');

  // Fetch comparison data
  const { data: comparison, isLoading, refetch } = useQuery({
    queryKey: ['mla-performance-comparison', unitType, selectedUnits, dateRange],
    queryFn: async () => {
      const params = new URLSearchParams({
        unit_type: unitType,
        ...getDateRangeParams(dateRange)
      });
      
      if (selectedUnits.length > 0) {
        selectedUnits.forEach(id => params.append('unit_ids', id));
      }
      
      const response = await analyticsAPI.getMLAPerformanceComparison(params);
      return response.data;
    }
  });

  const handleExportCSV = () => {
    if (!comparison || !comparison.comparison) return;
    
    // Create CSV content
    const headers = ['Name', 'Total Cases', 'Resolved', 'Resolution Rate %', 'Avg Days', 'Satisfaction', 'Status'];
    const rows = comparison.comparison.map(unit => [
      unit.name,
      unit.metrics.total_complaints,
      unit.metrics.resolved,
      unit.metrics.resolution_rate,
      unit.metrics.avg_resolution_days || 'N/A',
      unit.metrics.citizen_satisfaction || 'N/A',
      unit.insights.performance_level
    ]);
    
    const csvContent = [
      headers.join(','),
      ...rows.map(row => row.join(','))
    ].join('\n');
    
    // Download
    const blob = new Blob([csvContent], { type: 'text/csv' });
    const url = window.URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `performance-comparison-${unitType}-${new Date().toISOString().split('T')[0]}.csv`;
    a.click();
  };

  return (
    <div className="space-y-6">
      {/* Header with Filters */}
      <div className="bg-white rounded-lg shadow p-6">
        <div className="flex items-center justify-between mb-6">
          <h1 className="text-2xl font-bold text-gray-900">Performance Comparison Dashboard</h1>
          <div className="flex gap-2">
            <button
              onClick={handleExportCSV}
              disabled={!comparison}
              className="px-4 py-2 border border-gray-300 rounded-lg text-sm font-medium text-gray-700 hover:bg-gray-50 disabled:opacity-50 flex items-center gap-2"
            >
              <Download className="h-4 w-4" />
              Export CSV
            </button>
            <button
              onClick={() => refetch()}
              disabled={isLoading}
              className="px-4 py-2 bg-blue-600 text-white rounded-lg text-sm font-medium hover:bg-blue-700 disabled:opacity-50 flex items-center gap-2"
            >
              <RefreshCw className={`h-4 w-4 ${isLoading ? 'animate-spin' : ''}`} />
              Refresh
            </button>
          </div>
        </div>
        
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          {/* Unit Type Selector */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Compare By
            </label>
            <select
              value={unitType}
              onChange={(e) => {
                setUnitType(e.target.value);
                setSelectedUnits([]);
              }}
              className="w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500"
            >
              <option value="ward">Wards (Urban)</option>
              <option value="gram_panchayat">Gram Panchayats (Rural)</option>
              <option value="taluk_panchayat">Taluk Panchayats</option>
              <option value="department">Departments</option>
            </select>
          </div>

          {/* Date Range Selector */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Time Period
            </label>
            <select
              value={dateRange}
              onChange={(e) => setDateRange(e.target.value)}
              className="w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500"
            >
              <option value="last_7_days">Last 7 Days</option>
              <option value="last_30_days">Last 30 Days</option>
              <option value="last_3_months">Last 3 Months</option>
              <option value="last_6_months">Last 6 Months</option>
              <option value="last_year">Last Year</option>
            </select>
          </div>

          {/* Quick Stats */}
          <div className="bg-gray-50 rounded-lg p-4">
            <p className="text-sm text-gray-600 mb-1">Units Compared</p>
            <p className="text-2xl font-bold text-gray-900">
              {comparison?.comparison?.length || 0}
            </p>
          </div>
        </div>
      </div>

      {isLoading ? (
        <div className="flex justify-center items-center h-64">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
        </div>
      ) : comparison ? (
        <>
          {/* Key Insights Cards */}
          <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
            {/* Best Performer */}
            <div className="bg-gradient-to-br from-green-500 to-green-600 rounded-lg shadow p-6 text-white">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm opacity-90">Best Performer</p>
                  <p className="text-2xl font-bold mt-1">
                    {comparison.best_performer?.name || 'N/A'}
                  </p>
                  <p className="text-sm mt-2">
                    {comparison.best_performer?.metrics?.resolution_rate}% Resolution Rate
                  </p>
                </div>
                <Award className="h-12 w-12 opacity-80" />
              </div>
            </div>

            {/* Constituency Average */}
            <div className="bg-gradient-to-br from-blue-500 to-blue-600 rounded-lg shadow p-6 text-white">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm opacity-90">Constituency Average</p>
                  <p className="text-2xl font-bold mt-1">
                    {comparison.constituency_average?.resolution_rate}%
                  </p>
                  <p className="text-sm mt-2">
                    {comparison.constituency_average?.total_complaints} Total Cases
                  </p>
                </div>
                <TrendingUp className="h-12 w-12 opacity-80" />
              </div>
            </div>

            {/* Needs Attention */}
            <div className="bg-gradient-to-br from-red-500 to-red-600 rounded-lg shadow p-6 text-white">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm opacity-90">Needs Attention</p>
                  <p className="text-2xl font-bold mt-1">
                    {comparison.needs_attention?.length || 0}
                  </p>
                  <p className="text-sm mt-2">
                    Units Below 70% Resolution Rate
                  </p>
                </div>
                <AlertCircle className="h-12 w-12 opacity-80" />
              </div>
            </div>
          </div>

          {/* Side-by-Side Comparison Chart */}
          <div className="bg-white rounded-lg shadow p-6">
            <h2 className="text-xl font-bold mb-6">Resolution Rate Comparison</h2>
            <ResponsiveContainer width="100%" height={400}>
              <BarChart data={comparison.comparison || []}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis 
                  dataKey="name" 
                  angle={-45} 
                  textAnchor="end" 
                  height={100}
                  interval={0}
                  fontSize={12}
                />
                <YAxis />
                <Tooltip />
                <Legend />
                <Bar 
                  dataKey="metrics.resolution_rate" 
                  name="Resolution Rate (%)" 
                  fill="#3B82F6"
                  radius={[8, 8, 0, 0]}
                />
              </BarChart>
            </ResponsiveContainer>
          </div>

          {/* Citizen Satisfaction Index Chart */}
          <div className="bg-white rounded-lg shadow p-6">
            <h2 className="text-xl font-bold mb-6">Citizen Satisfaction Index</h2>
            <ResponsiveContainer width="100%" height={400}>
              <LineChart data={comparison.comparison || []}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis 
                  dataKey="name" 
                  angle={-45} 
                  textAnchor="end" 
                  height={100}
                  interval={0}
                  fontSize={12}
                />
                <YAxis domain={[0, 5]} />
                <Tooltip />
                <Legend />
                <Line 
                  type="monotone" 
                  dataKey="metrics.citizen_satisfaction" 
                  name="Satisfaction Rating" 
                  stroke="#F59E0B" 
                  strokeWidth={3}
                  dot={{ r: 6 }}
                />
              </LineChart>
            </ResponsiveContainer>
          </div>

          {/* Detailed Comparison Table */}
          <div className="bg-white rounded-lg shadow overflow-hidden">
            <h2 className="text-xl font-bold p-6 border-b">Detailed Metrics</h2>
            <div className="overflow-x-auto">
              <table className="min-w-full divide-y divide-gray-200">
                <thead className="bg-gray-50">
                  <tr>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      {unitType === 'ward' ? 'Ward' : 
                       unitType === 'gram_panchayat' ? 'Gram Panchayat' :
                       unitType === 'taluk_panchayat' ? 'Taluk Panchayat' : 'Department'}
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Total Cases
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Resolved
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Resolution Rate
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Avg Time (days)
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Satisfaction
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Overdue
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Status
                    </th>
                  </tr>
                </thead>
                <tbody className="bg-white divide-y divide-gray-200">
                  {comparison.comparison?.map((unit) => (
                    <tr key={unit.id} className="hover:bg-gray-50">
                      <td className="px-6 py-4 whitespace-nowrap font-medium text-gray-900">
                        {unit.name}
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-gray-700">
                        {unit.metrics.total_complaints}
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-gray-700">
                        {unit.metrics.resolved}
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap">
                        <div className="flex items-center">
                          <span className={`font-semibold ${
                            unit.metrics.resolution_rate >= 80 ? 'text-green-600' :
                            unit.metrics.resolution_rate >= 60 ? 'text-yellow-600' :
                            'text-red-600'
                          }`}>
                            {unit.metrics.resolution_rate}%
                          </span>
                          {unit.metrics.resolution_rate >= comparison.constituency_average.resolution_rate ? (
                            <TrendingUp className="ml-2 h-4 w-4 text-green-600" />
                          ) : (
                            <TrendingDown className="ml-2 h-4 w-4 text-red-600" />
                          )}
                        </div>
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-gray-700">
                        {unit.metrics.avg_resolution_days?.toFixed(1) || 'N/A'}
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap">
                        <div className="flex items-center">
                          <span className="text-yellow-500">★</span>
                          <span className="ml-1 font-medium">
                            {unit.metrics.citizen_satisfaction?.toFixed(1) || 'N/A'}
                          </span>
                        </div>
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap">
                        <span className={`px-2 py-1 text-xs font-semibold rounded-full ${
                          unit.metrics.overdue_cases > 5 ? 'bg-red-100 text-red-800' :
                          unit.metrics.overdue_cases > 0 ? 'bg-yellow-100 text-yellow-800' :
                          'bg-green-100 text-green-800'
                        }`}>
                          {unit.metrics.overdue_cases}
                        </span>
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap">
                        {unit.insights.red_flags.length > 0 ? (
                          <span className="px-2 py-1 text-xs font-semibold rounded-full bg-red-100 text-red-800">
                            Needs Attention
                          </span>
                        ) : unit.insights.green_stars.length > 0 ? (
                          <span className="px-2 py-1 text-xs font-semibold rounded-full bg-green-100 text-green-800">
                            Excellent
                          </span>
                        ) : (
                          <span className="px-2 py-1 text-xs font-semibold rounded-full bg-blue-100 text-blue-800">
                            Good
                          </span>
                        )}
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>

          {/* Insights & Recommendations */}
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            {/* Areas Excelling */}
            <div className="bg-white rounded-lg shadow p-6">
              <h3 className="text-lg font-bold text-green-800 mb-4 flex items-center gap-2">
                <Award className="h-5 w-5" />
                Areas Excelling
              </h3>
              <div className="space-y-3">
                {comparison.comparison
                  ?.filter(unit => unit.insights.green_stars.length > 0)
                  .map(unit => (
                    <div key={unit.id} className="border-l-4 border-green-500 pl-4 py-2">
                      <p className="font-semibold text-gray-900">{unit.name}</p>
                      {unit.insights.green_stars.map((star, idx) => (
                        <p key={idx} className="text-sm text-gray-600 mt-1">• {star}</p>
                      ))}
                    </div>
                  ))}
                {comparison.comparison?.filter(unit => unit.insights.green_stars.length > 0).length === 0 && (
                  <p className="text-sm text-gray-500 text-center py-4">
                    No units currently exceeding expectations. Focus on improving overall performance.
                  </p>
                )}
              </div>
            </div>

            {/* Areas Needing Attention */}
            <div className="bg-white rounded-lg shadow p-6">
              <h3 className="text-lg font-bold text-red-800 mb-4 flex items-center gap-2">
                <AlertCircle className="h-5 w-5" />
                Areas Needing Attention
              </h3>
              <div className="space-y-3">
                {comparison.comparison
                  ?.filter(unit => unit.insights.red_flags.length > 0)
                  .map(unit => (
                    <div key={unit.id} className="border-l-4 border-red-500 pl-4 py-2">
                      <p className="font-semibold text-gray-900">{unit.name}</p>
                      {unit.insights.red_flags.map((flag, idx) => (
                        <p key={idx} className="text-sm text-gray-600 mt-1">• {flag}</p>
                      ))}
                      {unit.insights.recommendations.length > 0 && (
                        <div className="mt-2 bg-blue-50 rounded p-2">
                          <p className="text-xs font-semibold text-blue-900 mb-1">Recommendations:</p>
                          {unit.insights.recommendations.map((rec, idx) => (
                            <p key={idx} className="text-xs text-blue-800">→ {rec}</p>
                          ))}
                        </div>
                      )}
                    </div>
                  ))}
                {comparison.comparison?.filter(unit => unit.insights.red_flags.length > 0).length === 0 && (
                  <p className="text-sm text-gray-500 text-center py-4">
                    ✓ All units performing within acceptable parameters!
                  </p>
                )}
              </div>
            </div>
          </div>
        </>
      ) : (
        <div className="bg-white rounded-lg shadow p-12 text-center">
          <p className="text-gray-500">No data available. Please select filters and try again.</p>
        </div>
      )}
    </div>
  );
}

function getDateRangeParams(range) {
  const today = new Date();
  let date_from;
  
  switch (range) {
    case 'last_7_days':
      date_from = new Date(today);
      date_from.setDate(date_from.getDate() - 7);
      break;
    case 'last_30_days':
      date_from = new Date(today);
      date_from.setDate(date_from.getDate() - 30);
      break;
    case 'last_3_months':
      date_from = new Date(today);
      date_from.setMonth(date_from.getMonth() - 3);
      break;
    case 'last_6_months':
      date_from = new Date(today);
      date_from.setMonth(date_from.getMonth() - 6);
      break;
    case 'last_year':
      date_from = new Date(today);
      date_from.setFullYear(date_from.getFullYear() - 1);
      break;
    default:
      date_from = new Date(today);
      date_from.setDate(date_from.getDate() - 30);
  }
  
  return {
    date_from: date_from.toISOString().split('T')[0],
    date_to: new Date().toISOString().split('T')[0]
  };
}
