import { useState } from 'react';
import { Lock, Eye, EyeOff, Save, AlertCircle } from 'lucide-react';
import { useMutation, useQueryClient } from '@tanstack/react-query';
import { complaintsAPI } from '../services/api';
import { useAuth } from '../contexts/AuthContext';

export default function InternalNotesSection({ complaint }) {
  const { user } = useAuth();
  const queryClient = useQueryClient();
  const [notes, setNotes] = useState(complaint?.internal_notes || '');
  const [isInternal, setIsInternal] = useState(complaint?.notes_are_internal !== false); // Default to internal
  const [isSaving, setIsSaving] = useState(false);

  // Check if user has permission to see internal notes
  const canViewInternalNotes = () => {
    const officialRoles = ['moderator', 'department_officer', 'admin', 'mla'];
    return officialRoles.includes(user?.role);
  };

  // Don't render if user doesn't have permission
  if (!canViewInternalNotes()) {
    return null;
  }

  // Save notes mutation
  const saveNotesMutation = useMutation({
    mutationFn: async () => {
      setIsSaving(true);
      return complaintsAPI.updateComplaintNotes(complaint.id, {
        internal_notes: notes,
        notes_are_internal: isInternal
      });
    },
    onSuccess: () => {
      queryClient.invalidateQueries(['complaint', complaint.id]);
      setIsSaving(false);
    },
    onError: () => {
      setIsSaving(false);
    }
  });

  const handleSave = () => {
    saveNotesMutation.mutate();
  };

  return (
    <div className="bg-yellow-50 border-2 border-yellow-400 rounded-lg p-6 shadow-sm">
      {/* Header */}
      <div className="flex items-center justify-between mb-4">
        <div className="flex items-center space-x-2">
          <Lock className="w-5 h-5 text-yellow-600" />
          <h3 className="text-lg font-bold text-gray-900">Internal Notes</h3>
          <span className="px-2 py-1 bg-yellow-200 text-yellow-800 text-xs font-semibold rounded">
            Officials Only
          </span>
        </div>
        
        {/* Visibility Toggle */}
        <div className="flex items-center space-x-2">
          <button
            onClick={() => setIsInternal(!isInternal)}
            className={`flex items-center space-x-1 px-3 py-1 rounded-lg transition-colors ${
              isInternal
                ? 'bg-yellow-600 text-white'
                : 'bg-gray-200 text-gray-700 hover:bg-gray-300'
            }`}
          >
            {isInternal ? (
              <>
                <EyeOff className="w-4 h-4" />
                <span className="text-sm">Private</span>
              </>
            ) : (
              <>
                <Eye className="w-4 h-4" />
                <span className="text-sm">Public</span>
              </>
            )}
          </button>
        </div>
      </div>

      {/* Info Alert */}
      <div className="bg-yellow-100 border border-yellow-300 rounded-lg p-3 mb-4">
        <div className="flex items-start space-x-2">
          <AlertCircle className="w-4 h-4 text-yellow-600 mt-0.5 flex-shrink-0" />
          <div className="text-sm text-yellow-800">
            {isInternal ? (
              <p>
                <strong>Private notes:</strong> Only visible to moderators, department officers, admins, and MLAs.
                Citizens cannot see these notes.
              </p>
            ) : (
              <p>
                <strong>Public notes:</strong> These notes will be visible to the citizen who filed this complaint.
                Use this mode to communicate updates or ask for more information.
              </p>
            )}
          </div>
        </div>
      </div>

      {/* Notes Textarea */}
      <div className="mb-4">
        <textarea
          value={notes}
          onChange={(e) => setNotes(e.target.value)}
          placeholder={
            isInternal
              ? 'Add internal notes about this complaint... (e.g., investigation status, officer assignments, internal discussions)'
              : 'Add notes that the citizen can see... (e.g., updates, requests for more information)'
          }
          rows={6}
          className="w-full px-4 py-3 border border-yellow-300 rounded-lg focus:ring-2 focus:ring-yellow-500 focus:border-transparent resize-none bg-white"
        />
        <div className="flex items-center justify-between mt-2">
          <p className="text-xs text-gray-500">
            {notes.length} characters
          </p>
          <p className="text-xs text-gray-500">
            Last updated: {complaint?.notes_updated_at 
              ? new Date(complaint.notes_updated_at).toLocaleString() 
              : 'Never'}
          </p>
        </div>
      </div>

      {/* Save Button */}
      <div className="flex justify-end space-x-3">
        <button
          onClick={() => {
            setNotes(complaint?.internal_notes || '');
            setIsInternal(complaint?.notes_are_internal !== false);
          }}
          className="px-4 py-2 border border-gray-300 rounded-lg text-gray-700 hover:bg-gray-50 transition-colors"
        >
          Reset
        </button>
        <button
          onClick={handleSave}
          disabled={isSaving || saveNotesMutation.isLoading}
          className="flex items-center space-x-2 px-4 py-2 bg-yellow-600 text-white rounded-lg hover:bg-yellow-700 transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
        >
          <Save className="w-4 h-4" />
          <span>{isSaving || saveNotesMutation.isLoading ? 'Saving...' : 'Save Notes'}</span>
        </button>
      </div>

      {/* Success/Error Messages */}
      {saveNotesMutation.isSuccess && (
        <div className="mt-4 bg-green-50 border border-green-200 rounded-lg p-3">
          <p className="text-sm text-green-800">
            ✓ Notes saved successfully!
          </p>
        </div>
      )}
      {saveNotesMutation.isError && (
        <div className="mt-4 bg-red-50 border border-red-200 rounded-lg p-3">
          <p className="text-sm text-red-800">
            ✗ Failed to save notes. Please try again.
          </p>
        </div>
      )}
    </div>
  );
}
