import { useState, useEffect } from 'react';
import { useQuery } from '@tanstack/react-query';
import { MapPin, ChevronRight, Loader2 } from 'lucide-react';
import { constituenciesAPI, usersAPI } from '../services/api';
import { useAuth } from '../contexts/AuthContext';

export default function ConstituencySelector({ onComplete }) {
  const { user, updateUser } = useAuth();
  const [selectedConstituency, setSelectedConstituency] = useState(null);
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState('');

  // Fetch constituencies
  const { data: constituenciesData, isLoading } = useQuery({
    queryKey: ['constituencies', 'active'],
    queryFn: async () => {
      const response = await constituenciesAPI.getAll(true);
      return response.data;
    },
  });

  const constituencies = constituenciesData?.constituencies || [];

  const handleSelectConstituency = async (constituency) => {
    setSelectedConstituency(constituency);
    setError('');
    setSaving(true);

    try {
      // Update user's constituency
      const response = await usersAPI.updateUser(user.id, {
        constituency_id: constituency.id,
      });

      // Update local user data
      const updatedUser = {
        ...user,
        constituency_id: constituency.id,
        constituency_name: constituency.name,
      };
      
      updateUser(updatedUser);

      // Notify parent component
      setTimeout(() => {
        onComplete();
      }, 500);
    } catch (err) {
      setError(err.response?.data?.detail || 'Failed to save constituency');
      setSaving(false);
    }
  };

  if (isLoading) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-sky-50 to-blue-100 flex items-center justify-center p-4">
        <div className="text-center">
          <Loader2 className="h-12 w-12 animate-spin text-sky-600 mx-auto" />
          <p className="mt-4 text-slate-600">Loading constituencies...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-sky-50 to-blue-100 flex items-center justify-center p-4">
      <div className="max-w-2xl w-full">
        {/* Header */}
        <div className="text-center mb-8">
          <div className="inline-flex items-center justify-center w-16 h-16 bg-sky-600 rounded-full mb-4">
            <MapPin className="w-8 h-8 text-white" />
          </div>
          <h1 className="text-3xl font-bold text-slate-900 mb-2">
            Select Your Constituency
          </h1>
          <p className="text-slate-600">
            Choose your constituency to personalize your experience and view relevant complaints
          </p>
        </div>

        {/* Constituency Cards */}
        <div className="bg-white rounded-2xl shadow-xl p-6 max-h-[600px] overflow-y-auto">
          {error && (
            <div className="mb-4 p-3 bg-red-50 border border-red-200 rounded-lg">
              <p className="text-sm text-red-600">{error}</p>
            </div>
          )}

          <div className="space-y-3">
            {constituencies.map((constituency) => (
              <button
                key={constituency.id}
                onClick={() => handleSelectConstituency(constituency)}
                disabled={saving}
                className={`w-full text-left rounded-xl border-2 p-4 transition-all ${
                  selectedConstituency?.id === constituency.id
                    ? 'border-sky-500 bg-sky-50'
                    : 'border-slate-200 hover:border-sky-300 hover:bg-slate-50'
                } ${saving ? 'opacity-50 cursor-not-allowed' : 'cursor-pointer'}`}
              >
                <div className="flex items-center justify-between">
                  <div className="flex-1">
                    <h3 className="text-lg font-semibold text-slate-900">
                      {constituency.name}
                    </h3>
                    {constituency.description && (
                      <p className="text-sm text-slate-600 mt-1">
                        {constituency.description}
                      </p>
                    )}
                    <div className="flex items-center gap-4 mt-2 text-xs text-slate-500">
                      {constituency.total_wards > 0 && (
                        <span>{constituency.total_wards} Wards</span>
                      )}
                      {constituency.total_population > 0 && (
                        <span>Population: {constituency.total_population.toLocaleString()}</span>
                      )}
                    </div>
                  </div>
                  {saving && selectedConstituency?.id === constituency.id ? (
                    <Loader2 className="h-5 w-5 animate-spin text-sky-600" />
                  ) : (
                    <ChevronRight className="h-5 w-5 text-slate-400" />
                  )}
                </div>
              </button>
            ))}
          </div>

          {constituencies.length === 0 && (
            <div className="text-center py-12">
              <MapPin className="h-12 w-12 text-slate-300 mx-auto mb-4" />
              <p className="text-slate-600">No constituencies available</p>
              <p className="text-sm text-slate-500 mt-2">
                Please contact your administrator
              </p>
            </div>
          )}
        </div>

        {/* Footer */}
        <p className="text-center text-sm text-slate-600 mt-6">
          You can change your constituency later in Settings
        </p>
      </div>
    </div>
  );
}
