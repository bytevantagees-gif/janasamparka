import React, { useState, useEffect } from 'react';
import PropTypes from 'prop-types';
import {
  BarChart,
  Bar,
  LineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer,
  ComposedChart
} from 'recharts';
import axios from 'axios';

/**
 * SeasonalForecastChart - Predictive planning with seasonal adjustments
 * 
 * Features:
 * - Monthly forecast by category
 * - Historical trend comparison
 * - Seasonal patterns visualization
 * - Resource planning recommendations
 */
const SeasonalForecastChart = ({ 
  constituencyId,
  months = 6, // Forecast period
  showRecommendations = true
}) => {
  const [forecastData, setForecastData] = useState(null);
  const [budgetForecast, setBudgetForecast] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [viewMode, setViewMode] = useState('complaints'); // 'complaints' or 'budget'

  const CATEGORY_COLORS = {
    'roads': '#3b82f6',
    'water': '#06b6d4',
    'electricity': '#f59e0b',
    'sanitation': '#10b981',
    'infrastructure': '#8b5cf6',
    'other': '#6b7280'
  };

  useEffect(() => {
    if (constituencyId) {
      fetchForecastData();
    }
  }, [constituencyId, months]);

  const fetchForecastData = async () => {
    try {
      setLoading(true);

      // Fetch seasonal forecast
      const forecastResponse = await axios.get(
        `/api/v1/case-management/constituencies/${constituencyId}/seasonal-forecast`,
        { params: { months } }
      );
      setForecastData(forecastResponse.data);

      // Fetch budget forecast
      const budgetResponse = await axios.get(
        `/api/v1/budgets/constituencies/${constituencyId}/forecast`,
        { params: { months } }
      );
      setBudgetForecast(budgetResponse.data);

      setError(null);
    } catch (err) {
      console.error('Error fetching forecast data:', err);
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  const formatCurrency = (amount) => {
    return new Intl.NumberFormat('en-IN', {
      style: 'currency',
      currency: 'INR',
      maximumFractionDigits: 0,
      notation: 'compact'
    }).format(amount || 0);
  };

  const formatMonth = (monthStr) => {
    const date = new Date(monthStr + '-01');
    return date.toLocaleDateString('en-IN', { month: 'short', year: '2-digit' });
  };

  const prepareChartData = () => {
    if (!forecastData?.monthly_forecast) return [];

    return forecastData.monthly_forecast.map(month => {
      const data = {
        month: formatMonth(month.month),
        fullMonth: month.month,
        total: month.total_predicted_complaints
      };

      // Add category breakdowns
      month.by_category?.forEach(cat => {
        data[cat.category] = cat.predicted_count;
      });

      return data;
    });
  };

  const prepareBudgetChartData = () => {
    if (!budgetForecast?.monthly_forecast) return [];

    return budgetForecast.monthly_forecast.map(month => ({
      month: formatMonth(month.month),
      projected: month.projected_spending,
      available: month.available_budget,
      shortfall: month.shortfall > 0 ? month.shortfall : 0
    }));
  };

  const getTopCategories = () => {
    if (!forecastData?.category_trends) return [];
    return forecastData.category_trends
      .sort((a, b) => b.total_predicted - a.total_predicted)
      .slice(0, 5);
  };

  const getRecommendations = () => {
    const recommendations = [];
    
    if (forecastData?.high_demand_periods) {
      forecastData.high_demand_periods.forEach(period => {
        recommendations.push({
          type: 'high-demand',
          month: period.month,
          category: period.category,
          count: period.predicted_count,
          message: `High demand expected for ${period.category} in ${formatMonth(period.month)} (${period.predicted_count} complaints)`
        });
      });
    }

    if (budgetForecast?.budget_alerts) {
      budgetForecast.budget_alerts.forEach(alert => {
        recommendations.push({
          type: 'budget-alert',
          month: alert.month,
          category: alert.category,
          shortfall: alert.shortfall,
          message: `Budget shortfall of ${formatCurrency(alert.shortfall)} expected in ${formatMonth(alert.month)}`
        });
      });
    }

    return recommendations;
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="bg-red-50 border border-red-200 rounded-lg p-4">
        <p className="text-red-800">Error loading forecast: {error}</p>
      </div>
    );
  }

  if (!forecastData) {
    return (
      <div className="bg-gray-50 border border-gray-200 rounded-lg p-4">
        <p className="text-gray-600">No forecast data available</p>
      </div>
    );
  }

  const chartData = viewMode === 'complaints' ? prepareChartData() : prepareBudgetChartData();
  const topCategories = getTopCategories();
  const recommendations = getRecommendations();

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h3 className="text-lg font-bold text-gray-800">📊 Seasonal Forecast & Planning</h3>
          <p className="text-sm text-gray-600">Next {months} months prediction</p>
        </div>
        
        {/* View Toggle */}
        <div className="flex gap-2">
          <button
            onClick={() => setViewMode('complaints')}
            className={`px-4 py-2 rounded-lg text-sm font-medium transition ${
              viewMode === 'complaints'
                ? 'bg-blue-600 text-white'
                : 'bg-gray-200 text-gray-700 hover:bg-gray-300'
            }`}
          >
            Complaints Forecast
          </button>
          <button
            onClick={() => setViewMode('budget')}
            className={`px-4 py-2 rounded-lg text-sm font-medium transition ${
              viewMode === 'budget'
                ? 'bg-blue-600 text-white'
                : 'bg-gray-200 text-gray-700 hover:bg-gray-300'
            }`}
          >
            Budget Forecast
          </button>
        </div>
      </div>

      {/* Main Chart */}
      <div className="bg-white border border-gray-200 rounded-lg p-4">
        <ResponsiveContainer width="100%" height={400}>
          {viewMode === 'complaints' ? (
            <BarChart data={chartData}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis dataKey="month" />
              <YAxis />
              <Tooltip />
              <Legend />
              {Object.keys(CATEGORY_COLORS).map(category => (
                <Bar
                  key={category}
                  dataKey={category}
                  stackId="a"
                  fill={CATEGORY_COLORS[category]}
                  name={category.charAt(0).toUpperCase() + category.slice(1)}
                />
              ))}
            </BarChart>
          ) : (
            <ComposedChart data={chartData}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis dataKey="month" />
              <YAxis tickFormatter={formatCurrency} />
              <Tooltip formatter={(value) => formatCurrency(value)} />
              <Legend />
              <Bar dataKey="available" fill="#10b981" name="Available Budget" />
              <Bar dataKey="projected" fill="#3b82f6" name="Projected Spending" />
              <Bar dataKey="shortfall" fill="#ef4444" name="Shortfall" />
              <Line type="monotone" dataKey="projected" stroke="#8b5cf6" strokeWidth={2} name="Trend" />
            </ComposedChart>
          )}
        </ResponsiveContainer>
      </div>

      {/* Category Trends */}
      {viewMode === 'complaints' && topCategories.length > 0 && (
        <div className="grid grid-cols-1 md:grid-cols-5 gap-4">
          {topCategories.map((cat, idx) => {
            const trend = cat.trend_direction;
            const trendIcon = trend === 'increasing' ? '📈' : trend === 'decreasing' ? '📉' : '➡️';
            const trendColor = trend === 'increasing' ? 'text-red-600' : trend === 'decreasing' ? 'text-green-600' : 'text-gray-600';
            
            return (
              <div key={idx} className="bg-white border border-gray-200 rounded-lg p-4">
                <div className="text-sm text-gray-600 mb-1">{cat.category}</div>
                <div className="text-2xl font-bold text-gray-900 mb-1">
                  {cat.total_predicted}
                </div>
                <div className={`text-xs font-medium ${trendColor}`}>
                  {trendIcon} {trend}
                </div>
              </div>
            );
          })}
        </div>
      )}

      {/* Recommendations */}
      {showRecommendations && recommendations.length > 0 && (
        <div className="bg-white border border-gray-200 rounded-lg p-4">
          <h4 className="font-bold text-gray-800 mb-3">🎯 Planning Recommendations</h4>
          <div className="space-y-2">
            {recommendations.map((rec, idx) => (
              <div
                key={idx}
                className={`p-3 rounded-lg flex items-start gap-3 ${
                  rec.type === 'high-demand'
                    ? 'bg-orange-50 border border-orange-200'
                    : 'bg-red-50 border border-red-200'
                }`}
              >
                <span className="text-2xl">
                  {rec.type === 'high-demand' ? '⚡' : '⚠️'}
                </span>
                <div className="flex-1">
                  <p className={`text-sm font-medium ${
                    rec.type === 'high-demand' ? 'text-orange-900' : 'text-red-900'
                  }`}>
                    {rec.message}
                  </p>
                  <p className="text-xs text-gray-600 mt-1">
                    {rec.type === 'high-demand' 
                      ? 'Consider pre-allocating resources and staff'
                      : 'Review budget allocation or consider reallocation'}
                  </p>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Summary Stats */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
          <div className="text-sm text-blue-600 font-medium mb-1">Total Predicted</div>
          <div className="text-2xl font-bold text-blue-900">
            {forecastData.total_predicted_complaints || 0}
          </div>
          <div className="text-xs text-blue-600 mt-1">
            complaints over {months} months
          </div>
        </div>

        <div className="bg-green-50 border border-green-200 rounded-lg p-4">
          <div className="text-sm text-green-600 font-medium mb-1">Avg Per Month</div>
          <div className="text-2xl font-bold text-green-900">
            {Math.round((forecastData.total_predicted_complaints || 0) / months)}
          </div>
          <div className="text-xs text-green-600 mt-1">
            based on historical patterns
          </div>
        </div>

        <div className="bg-purple-50 border border-purple-200 rounded-lg p-4">
          <div className="text-sm text-purple-600 font-medium mb-1">Peak Month</div>
          <div className="text-2xl font-bold text-purple-900">
            {forecastData.peak_month ? formatMonth(forecastData.peak_month) : 'N/A'}
          </div>
          <div className="text-xs text-purple-600 mt-1">
            highest demand expected
          </div>
        </div>
      </div>
    </div>
  );
};

SeasonalForecastChart.propTypes = {
  constituencyId: PropTypes.number.isRequired,
  months: PropTypes.number,
  showRecommendations: PropTypes.bool
};

export default SeasonalForecastChart;
