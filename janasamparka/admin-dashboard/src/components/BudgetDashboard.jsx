import React, { useState, useEffect } from 'react';
import PropTypes from 'prop-types';
import {
  BarChart,
  Bar,
  PieChart,
  Pie,
  Cell,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer
} from 'recharts';
import axios from 'axios';

/**
 * BudgetDashboard - Budget transparency and tracking
 * 
 * Features:
 * - Allocation by category (pie chart)
 * - Utilization progress bars
 * - Recent transactions table
 * - Budget vs actual spending
 */
const BudgetDashboard = ({ 
  constituencyId = null,
  wardId = null,
  departmentId = null,
  type = 'ward' // 'ward' or 'department'
}) => {
  const [budgetData, setBudgetData] = useState(null);
  const [transactions, setTransactions] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  const COLORS = {
    'roads': '#3b82f6',
    'water': '#06b6d4',
    'electricity': '#f59e0b',
    'sanitation': '#10b981',
    'infrastructure': '#8b5cf6',
    'other': '#6b7280'
  };

  useEffect(() => {
    fetchBudgetData();
  }, [constituencyId, wardId, departmentId]);

  const fetchBudgetData = async () => {
    try {
      setLoading(true);
      let endpoint;
      
      // Get current financial year (April to March)
      const now = new Date();
      const currentYear = now.getFullYear();
      const currentMonth = now.getMonth() + 1; // 0-indexed
      const financialYear = currentMonth >= 4 
        ? `${currentYear}-${currentYear + 1}` 
        : `${currentYear - 1}-${currentYear}`;
      
      if (type === 'ward' && wardId) {
        endpoint = `/api/v1/budgets/wards/${wardId}`;
      } else if (type === 'department' && departmentId) {
        endpoint = `/api/v1/budgets/departments/${departmentId}`;
      } else if (constituencyId) {
        endpoint = `/api/v1/budgets/constituencies/${constituencyId}/overview?financial_year=${financialYear}`;
      } else {
        throw new Error('No valid ID provided');
      }

      const response = await axios.get(endpoint);
      setBudgetData(response.data);

      // Fetch recent transactions
      const transactionsEndpoint = type === 'ward' 
        ? `/api/v1/budgets/wards/${wardId}/transactions`
        : `/api/v1/budgets/departments/${departmentId}/transactions`;
      
      if (wardId || departmentId) {
        const txResponse = await axios.get(transactionsEndpoint, {
          params: { limit: 10 }
        });
        setTransactions(txResponse.data.transactions || []);
      }
      
      setError(null);
    } catch (err) {
      console.error('Error fetching budget data:', err);
      
      // Handle budget endpoints not yet implemented
      if (err.response?.status === 422 || err.response?.status === 404) {
        setError('Budget tracking feature coming soon. Please check back later.');
      } else {
        setError(err.message);
      }
    } finally {
      setLoading(false);
    }
  };

  const formatCurrency = (amount) => {
    return new Intl.NumberFormat('en-IN', {
      style: 'currency',
      currency: 'INR',
      maximumFractionDigits: 0
    }).format(amount || 0);
  };

  const formatDate = (dateString) => {
    return new Date(dateString).toLocaleDateString('en-IN', {
      year: 'numeric',
      month: 'short',
      day: 'numeric'
    });
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
      <div className="bg-blue-50 border border-blue-200 rounded-lg p-6">
        <div className="flex items-start">
          <div className="flex-shrink-0">
            <svg className="h-6 w-6 text-blue-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
            </svg>
          </div>
          <div className="ml-3">
            <h3 className="text-sm font-medium text-blue-800">Budget Tracking Coming Soon</h3>
            <p className="mt-2 text-sm text-blue-700">{error}</p>
          </div>
        </div>
      </div>
    );
  }

  if (!budgetData) {
    return (
      <div className="bg-gray-50 border border-gray-200 rounded-lg p-4">
        <p className="text-gray-600">No budget data available</p>
      </div>
    );
  }

  // Prepare data for pie chart
  const pieData = budgetData.by_category?.map(item => ({
    name: item.category,
    value: item.allocated,
    spent: item.spent,
    remaining: item.remaining
  })) || [];

  return (
    <div className="space-y-6">
      {/* Summary Cards */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
          <div className="text-sm text-blue-600 font-medium mb-1">Total Allocated</div>
          <div className="text-2xl font-bold text-blue-900">
            {formatCurrency(budgetData.total_allocated)}
          </div>
        </div>

        <div className="bg-red-50 border border-red-200 rounded-lg p-4">
          <div className="text-sm text-red-600 font-medium mb-1">Total Spent</div>
          <div className="text-2xl font-bold text-red-900">
            {formatCurrency(budgetData.total_spent)}
          </div>
        </div>

        <div className="bg-yellow-50 border border-yellow-200 rounded-lg p-4">
          <div className="text-sm text-yellow-600 font-medium mb-1">Committed</div>
          <div className="text-2xl font-bold text-yellow-900">
            {formatCurrency(budgetData.total_committed || 0)}
          </div>
        </div>

        <div className="bg-green-50 border border-green-200 rounded-lg p-4">
          <div className="text-sm text-green-600 font-medium mb-1">Remaining</div>
          <div className="text-2xl font-bold text-green-900">
            {formatCurrency(budgetData.total_remaining)}
          </div>
        </div>
      </div>

      {/* Charts Row */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Pie Chart - Allocation by Category */}
        <div className="bg-white border border-gray-200 rounded-lg p-4">
          <h3 className="text-lg font-bold mb-4 text-gray-800">Budget Allocation by Category</h3>
          <ResponsiveContainer width="100%" height={300}>
            <PieChart>
              <Pie
                data={pieData}
                cx="50%"
                cy="50%"
                labelLine={false}
                label={({ name, percent }) => `${name}: ${(percent * 100).toFixed(0)}%`}
                outerRadius={80}
                fill="#8884d8"
                dataKey="value"
              >
                {pieData.map((entry, index) => (
                  <Cell key={`cell-${index}`} fill={COLORS[entry.name.toLowerCase()] || COLORS.other} />
                ))}
              </Pie>
              <Tooltip formatter={(value) => formatCurrency(value)} />
            </PieChart>
          </ResponsiveContainer>
        </div>

        {/* Utilization Progress Bars */}
        <div className="bg-white border border-gray-200 rounded-lg p-4">
          <h3 className="text-lg font-bold mb-4 text-gray-800">Budget Utilization</h3>
          <div className="space-y-4">
            {budgetData.by_category?.map((item, idx) => {
              const utilizationPercent = (item.spent / item.allocated * 100).toFixed(1);
              const isOverBudget = item.spent > item.allocated;
              
              return (
                <div key={idx}>
                  <div className="flex justify-between text-sm mb-1">
                    <span className="font-medium text-gray-700">{item.category}</span>
                    <span className={`font-bold ${isOverBudget ? 'text-red-600' : 'text-gray-900'}`}>
                      {utilizationPercent}%
                    </span>
                  </div>
                  <div className="w-full bg-gray-200 rounded-full h-2.5">
                    <div
                      className={`h-2.5 rounded-full ${
                        isOverBudget 
                          ? 'bg-red-600' 
                          : utilizationPercent >= 80 
                            ? 'bg-yellow-500'
                            : 'bg-blue-600'
                      }`}
                      style={{ width: `${Math.min(utilizationPercent, 100)}%` }}
                    ></div>
                  </div>
                  <div className="flex justify-between text-xs text-gray-500 mt-1">
                    <span>Spent: {formatCurrency(item.spent)}</span>
                    <span>Of: {formatCurrency(item.allocated)}</span>
                  </div>
                </div>
              );
            })}
          </div>
        </div>
      </div>

      {/* Recent Transactions Table */}
      {transactions.length > 0 && (
        <div className="bg-white border border-gray-200 rounded-lg p-4">
          <h3 className="text-lg font-bold mb-4 text-gray-800">Recent Transactions</h3>
          <div className="overflow-x-auto">
            <table className="min-w-full divide-y divide-gray-200">
              <thead className="bg-gray-50">
                <tr>
                  <th className="px-4 py-2 text-left text-xs font-medium text-gray-500 uppercase">Date</th>
                  <th className="px-4 py-2 text-left text-xs font-medium text-gray-500 uppercase">Category</th>
                  <th className="px-4 py-2 text-left text-xs font-medium text-gray-500 uppercase">Description</th>
                  <th className="px-4 py-2 text-right text-xs font-medium text-gray-500 uppercase">Amount</th>
                  <th className="px-4 py-2 text-center text-xs font-medium text-gray-500 uppercase">Type</th>
                </tr>
              </thead>
              <tbody className="bg-white divide-y divide-gray-200">
                {transactions.map((tx, idx) => (
                  <tr key={idx} className="hover:bg-gray-50">
                    <td className="px-4 py-2 text-sm text-gray-900">
                      {formatDate(tx.transaction_date)}
                    </td>
                    <td className="px-4 py-2 text-sm">
                      <span className="px-2 py-1 rounded text-xs font-medium bg-blue-100 text-blue-800">
                        {tx.category}
                      </span>
                    </td>
                    <td className="px-4 py-2 text-sm text-gray-700">
                      {tx.description}
                    </td>
                    <td className="px-4 py-2 text-sm text-right font-medium text-gray-900">
                      {formatCurrency(tx.amount)}
                    </td>
                    <td className="px-4 py-2 text-center">
                      <span className={`px-2 py-1 rounded text-xs font-medium ${
                        tx.transaction_type === 'expense' 
                          ? 'bg-red-100 text-red-800'
                          : 'bg-green-100 text-green-800'
                      }`}>
                        {tx.transaction_type}
                      </span>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      )}
    </div>
  );
};

BudgetDashboard.propTypes = {
  constituencyId: PropTypes.string,
  wardId: PropTypes.string,
  departmentId: PropTypes.string,
  type: PropTypes.oneOf(['ward', 'department', 'constituency'])
};

export default BudgetDashboard;
