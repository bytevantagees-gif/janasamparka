import { useState } from 'react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { Phone, Calendar, Check, X, AlertTriangle, TrendingDown, TrendingUp, Clock, User } from 'lucide-react';
import { analyticsAPI, interventionsAPI } from '../../services/api';

export default function SatisfactionDashboard() {
  const queryClient = useQueryClient();
  const [unitType, setUnitType] = useState('ward');
  const [dateRange, setDateRange] = useState('last_30_days');
  const [selectedCitizen, setSelectedCitizen] = useState(null);
  const [interventionModal, setInterventionModal] = useState(false);
  
  // Form state for intervention
  const [interventionForm, setInterventionForm] = useState({
    intervention_type: 'call',
    notes: '',
    scheduled_at: ''
  });

  // Helper function to convert date range to params
  const getDateRangeParams = (range) => {
    const today = new Date();
    let date_from = null;
    
    switch(range) {
      case 'last_7_days':
        date_from = new Date(today.setDate(today.getDate() - 7));
        break;
      case 'last_30_days':
        date_from = new Date(today.setDate(today.getDate() - 30));
        break;
      case 'last_3_months':
        date_from = new Date(today.setMonth(today.getMonth() - 3));
        break;
      case 'last_6_months':
        date_from = new Date(today.setMonth(today.getMonth() - 6));
        break;
      default:
        date_from = new Date(today.setDate(today.getDate() - 30));
    }
    
    return {
      date_from: date_from.toISOString().split('T')[0],
      date_to: new Date().toISOString().split('T')[0]
    };
  };

  // Fetch satisfaction data
  const { data: satisfactionData, isLoading } = useQuery({
    queryKey: ['satisfaction-aggregated', unitType, dateRange],
    queryFn: () => {
      const dateParams = getDateRangeParams(dateRange);
      return analyticsAPI.getSatisfactionAggregated({
        unit_type: unitType,
        unhappy_threshold: 2,
        ...dateParams
      });
    }
  });

  // Create intervention mutation
  const createInterventionMutation = useMutation({
    mutationFn: (interventionData) => interventionsAPI.createIntervention(interventionData),
    onSuccess: () => {
      queryClient.invalidateQueries(['satisfaction-aggregated']);
      setInterventionModal(false);
      setSelectedCitizen(null);
      setInterventionForm({
        intervention_type: 'call',
        notes: '',
        scheduled_at: ''
      });
    }
  });

  // Handle create intervention
  const handleCreateIntervention = () => {
    if (!selectedCitizen) return;
    
    createInterventionMutation.mutate({
      complaint_id: selectedCitizen.complaint_id,
      citizen_id: selectedCitizen.citizen_id,
      ...interventionForm
    });
  };

  // Open intervention modal
  const openInterventionModal = (citizen) => {
    setSelectedCitizen(citizen);
    setInterventionModal(true);
  };

  if (isLoading) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto"></div>
          <p className="mt-4 text-gray-600">Loading satisfaction data...</p>
        </div>
      </div>
    );
  }

  const { satisfaction_summary = [], unhappy_citizens = [], summary_stats = {}, total_unhappy_citizens = 0 } = satisfactionData || {};

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex justify-between items-center">
        <div>
          <h1 className="text-3xl font-bold text-gray-900">Citizen Satisfaction Dashboard</h1>
          <p className="text-gray-600 mt-1">Monitor satisfaction and intervene with unhappy citizens</p>
        </div>
      </div>

      {/* Filters */}
      <div className="bg-white rounded-lg shadow p-6">
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">Unit Type</label>
            <select
              value={unitType}
              onChange={(e) => setUnitType(e.target.value)}
              className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
            >
              <option value="ward">Wards</option>
              <option value="gram_panchayat">Gram Panchayats</option>
              <option value="taluk_panchayat">Taluk Panchayats</option>
            </select>
          </div>
          
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">Date Range</label>
            <select
              value={dateRange}
              onChange={(e) => setDateRange(e.target.value)}
              className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
            >
              <option value="last_7_days">Last 7 Days</option>
              <option value="last_30_days">Last 30 Days</option>
              <option value="last_3_months">Last 3 Months</option>
              <option value="last_6_months">Last 6 Months</option>
            </select>
          </div>

          <div className="bg-gradient-to-br from-red-500 to-red-600 rounded-lg p-4 text-white">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-red-100 text-sm">Needs Attention</p>
                <p className="text-3xl font-bold mt-1">{total_unhappy_citizens}</p>
                <p className="text-red-100 text-xs mt-1">Unhappy Citizens</p>
              </div>
              <AlertTriangle className="w-12 h-12 text-red-200" />
            </div>
          </div>
        </div>
      </div>

      {/* Summary Stats */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
        <div className="bg-white rounded-lg shadow p-6">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-gray-600 text-sm">Total Units</p>
              <p className="text-2xl font-bold text-gray-900 mt-1">{summary_stats.total_units || 0}</p>
            </div>
            <User className="w-10 h-10 text-blue-500" />
          </div>
        </div>

        <div className="bg-white rounded-lg shadow p-6">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-gray-600 text-sm">Avg Satisfaction</p>
              <p className="text-2xl font-bold text-gray-900 mt-1">{summary_stats.avg_satisfaction_index || 0}%</p>
            </div>
            <TrendingUp className="w-10 h-10 text-green-500" />
          </div>
        </div>

        <div className="bg-white rounded-lg shadow p-6">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-gray-600 text-sm">Units Below 50%</p>
              <p className="text-2xl font-bold text-gray-900 mt-1">{summary_stats.units_below_50 || 0}</p>
            </div>
            <TrendingDown className="w-10 h-10 text-red-500" />
          </div>
        </div>

        <div className="bg-white rounded-lg shadow p-6">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-gray-600 text-sm">Total Ratings</p>
              <p className="text-2xl font-bold text-gray-900 mt-1">{summary_stats.total_ratings_received || 0}</p>
            </div>
            <Check className="w-10 h-10 text-purple-500" />
          </div>
        </div>
      </div>

      {/* Satisfaction by Unit */}
      <div className="bg-white rounded-lg shadow">
        <div className="p-6 border-b border-gray-200">
          <h2 className="text-xl font-bold text-gray-900">Satisfaction Index by {unitType === 'ward' ? 'Ward' : unitType === 'gram_panchayat' ? 'Gram Panchayat' : 'Taluk Panchayat'}</h2>
          <p className="text-gray-600 text-sm mt-1">Lowest satisfaction units shown first</p>
        </div>
        
        <div className="overflow-x-auto">
          <table className="min-w-full divide-y divide-gray-200">
            <thead className="bg-gray-50">
              <tr>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Unit Name</th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Satisfaction Index</th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Total Ratings</th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Unhappy Count</th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Unhappy %</th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Status</th>
              </tr>
            </thead>
            <tbody className="bg-white divide-y divide-gray-200">
              {satisfaction_summary.map((unit) => (
                <tr key={unit.unit_id} className="hover:bg-gray-50">
                  <td className="px-6 py-4 whitespace-nowrap">
                    <div className="text-sm font-medium text-gray-900">{unit.unit_name}</div>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap">
                    <div className="flex items-center">
                      <div className="w-32 bg-gray-200 rounded-full h-2 mr-2">
                        <div
                          className={`h-2 rounded-full ${
                            unit.satisfaction_index >= 70 ? 'bg-green-500' :
                            unit.satisfaction_index >= 50 ? 'bg-yellow-500' :
                            'bg-red-500'
                          }`}
                          style={{ width: `${unit.satisfaction_index}%` }}
                        />
                      </div>
                      <span className="text-sm font-medium text-gray-900">{unit.satisfaction_index}%</span>
                    </div>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">{unit.total_ratings}</td>
                  <td className="px-6 py-4 whitespace-nowrap">
                    <span className={`px-2 py-1 text-xs font-semibold rounded-full ${
                      unit.unhappy_count > 5 ? 'bg-red-100 text-red-800' :
                      unit.unhappy_count > 2 ? 'bg-yellow-100 text-yellow-800' :
                      'bg-green-100 text-green-800'
                    }`}>
                      {unit.unhappy_count}
                    </span>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">{unit.unhappy_percentage}%</td>
                  <td className="px-6 py-4 whitespace-nowrap">
                    <span className={`px-2 py-1 text-xs font-semibold rounded-full ${
                      unit.satisfaction_index >= 70 ? 'bg-green-100 text-green-800' :
                      unit.satisfaction_index >= 50 ? 'bg-yellow-100 text-yellow-800' :
                      'bg-red-100 text-red-800'
                    }`}>
                      {unit.satisfaction_index >= 70 ? 'Good' : unit.satisfaction_index >= 50 ? 'Fair' : 'Critical'}
                    </span>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>

      {/* Unhappy Citizens List */}
      <div className="bg-white rounded-lg shadow">
        <div className="p-6 border-b border-gray-200">
          <h2 className="text-xl font-bold text-gray-900">Unhappy Citizens Needing Intervention</h2>
          <p className="text-gray-600 text-sm mt-1">Citizens who rated their experience 2 stars or below</p>
        </div>
        
        <div className="overflow-x-auto">
          <table className="min-w-full divide-y divide-gray-200">
            <thead className="bg-gray-50">
              <tr>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Citizen</th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Phone</th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Complaint</th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Rating</th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Feedback</th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Unit</th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Actions</th>
              </tr>
            </thead>
            <tbody className="bg-white divide-y divide-gray-200">
              {unhappy_citizens.map((citizen) => (
                <tr key={`${citizen.citizen_id}-${citizen.complaint_id}`} className="hover:bg-gray-50">
                  <td className="px-6 py-4 whitespace-nowrap">
                    <div className="text-sm font-medium text-gray-900">{citizen.citizen_name}</div>
                    <div className="text-xs text-gray-500">{new Date(citizen.rating_submitted_at).toLocaleDateString()}</div>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap">
                    <a href={`tel:${citizen.citizen_phone}`} className="flex items-center text-blue-600 hover:text-blue-800">
                      <Phone className="w-4 h-4 mr-1" />
                      <span className="text-sm">{citizen.citizen_phone}</span>
                    </a>
                  </td>
                  <td className="px-6 py-4">
                    <div className="text-sm text-gray-900 max-w-xs truncate">{citizen.complaint_title}</div>
                    <div className="text-xs text-gray-500">{citizen.complaint_status}</div>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap">
                    <div className="flex items-center">
                      {'★'.repeat(citizen.rating)}
                      {'☆'.repeat(5 - citizen.rating)}
                      <span className={`ml-2 px-2 py-1 text-xs font-semibold rounded-full ${
                        citizen.rating === 1 ? 'bg-red-100 text-red-800' : 'bg-yellow-100 text-yellow-800'
                      }`}>
                        {citizen.rating}/5
                      </span>
                    </div>
                  </td>
                  <td className="px-6 py-4">
                    <div className="text-sm text-gray-900 max-w-xs truncate">{citizen.rating_feedback || 'No feedback'}</div>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">{citizen.unit_name || 'N/A'}</td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm font-medium">
                    <button
                      onClick={() => openInterventionModal(citizen)}
                      className="inline-flex items-center px-3 py-1 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors"
                    >
                      <Calendar className="w-4 h-4 mr-1" />
                      Schedule Intervention
                    </button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>

      {/* Intervention Modal */}
      {interventionModal && selectedCitizen && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center p-4 z-50">
          <div className="bg-white rounded-lg max-w-2xl w-full p-6">
            <div className="flex justify-between items-center mb-4">
              <h3 className="text-xl font-bold text-gray-900">Schedule Intervention</h3>
              <button
                onClick={() => {
                  setInterventionModal(false);
                  setSelectedCitizen(null);
                }}
                className="text-gray-400 hover:text-gray-600"
              >
                <X className="w-6 h-6" />
              </button>
            </div>

            <div className="space-y-4">
              <div className="bg-gray-50 rounded-lg p-4">
                <h4 className="font-medium text-gray-900">Citizen Details</h4>
                <div className="mt-2 space-y-1 text-sm">
                  <p><span className="font-medium">Name:</span> {selectedCitizen.citizen_name}</p>
                  <p><span className="font-medium">Phone:</span> {selectedCitizen.citizen_phone}</p>
                  <p><span className="font-medium">Complaint:</span> {selectedCitizen.complaint_title}</p>
                  <p><span className="font-medium">Rating:</span> {selectedCitizen.rating}/5</p>
                  {selectedCitizen.rating_feedback && (
                    <p><span className="font-medium">Feedback:</span> {selectedCitizen.rating_feedback}</p>
                  )}
                </div>
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">Intervention Type</label>
                <select
                  value={interventionForm.intervention_type}
                  onChange={(e) => setInterventionForm({ ...interventionForm, intervention_type: e.target.value })}
                  className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                >
                  <option value="call">Phone Call</option>
                  <option value="visit">In-Person Visit</option>
                  <option value="follow-up">Follow-up</option>
                </select>
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">Schedule Date & Time</label>
                <input
                  type="datetime-local"
                  value={interventionForm.scheduled_at}
                  onChange={(e) => setInterventionForm({ ...interventionForm, scheduled_at: e.target.value })}
                  className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">Notes</label>
                <textarea
                  value={interventionForm.notes}
                  onChange={(e) => setInterventionForm({ ...interventionForm, notes: e.target.value })}
                  rows={4}
                  placeholder="Add notes about the intervention plan..."
                  className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                />
              </div>

              <div className="flex justify-end space-x-3">
                <button
                  onClick={() => {
                    setInterventionModal(false);
                    setSelectedCitizen(null);
                  }}
                  className="px-4 py-2 border border-gray-300 rounded-lg text-gray-700 hover:bg-gray-50 transition-colors"
                >
                  Cancel
                </button>
                <button
                  onClick={handleCreateIntervention}
                  disabled={createInterventionMutation.isLoading}
                  className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors disabled:opacity-50"
                >
                  {createInterventionMutation.isLoading ? 'Creating...' : 'Create Intervention'}
                </button>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
