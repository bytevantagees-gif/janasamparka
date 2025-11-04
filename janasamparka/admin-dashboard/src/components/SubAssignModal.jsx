import { useState, useEffect } from 'react';
import { useQuery } from '@tanstack/react-query';
import { X, UserCheck } from 'lucide-react';
import { complaintsAPI } from '../services/api';
import { useTranslation } from '../hooks/useTranslation';

function SubAssignModal({ isOpen, onClose, complaint, onSubAssign }) {
  const { t } = useTranslation();
  const [selectedAssignee, setSelectedAssignee] = useState('');
  const [note, setNote] = useState('');
  const [isSubmitting, setIsSubmitting] = useState(false);

  // Get list of department officers and moderators from the same constituency
  const { data: officersData } = useQuery({
    queryKey: ['department-officers', complaint?.constituency_id],
    queryFn: () => complaintsAPI.getUsersByRole(['department_officer', 'moderator'], complaint?.constituency_id),
    enabled: isOpen && complaint?.constituency_id,
  });

  const officers = officersData?.data || [];

  // Filter out the current assignee
  const availableOfficers = officers.filter(officer => officer.id !== complaint?.assigned_to);

  useEffect(() => {
    if (!isOpen) {
      setSelectedAssignee('');
      setNote('');
      setIsSubmitting(false);
    }
  }, [isOpen]);

  const handleSubmit = async (e) => {
    e.preventDefault();

    if (!selectedAssignee) {
      alert('Please select an assignee');
      return;
    }

    setIsSubmitting(true);
    try {
      await onSubAssign(complaint.id, {
        assigned_to: selectedAssignee,
        note: note || `Sub-assigned by ${complaint.assigned_to_name || 'officer'}`,
      });
      onClose();
    } catch (error) {
      console.error('Sub-assignment failed:', error);
      alert('Failed to sub-assign complaint. Please try again.');
    } finally {
      setIsSubmitting(false);
    }
  };

  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
      <div className="bg-white rounded-lg shadow-xl max-w-md w-full mx-4">
        <div className="flex items-center justify-between p-6 border-b border-gray-200">
          <h2 className="text-lg font-semibold text-gray-900">{t('subAssignComplaint')}</h2>
          <button
            onClick={onClose}
            className="text-gray-400 hover:text-gray-600"
          >
            <X className="h-6 w-6" />
          </button>
        </div>

        <form onSubmit={handleSubmit} className="p-6 space-y-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              {t('selectNewAssignee')}
            </label>
            <select
              value={selectedAssignee}
              onChange={(e) => setSelectedAssignee(e.target.value)}
              className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent"
              required
            >
              <option value="">{t('selectAssignee')}</option>
              {availableOfficers.map((officer) => (
                <option key={officer.id} value={officer.id}>
                  {officer.name} ({officer.role.replace('_', ' ')})
                </option>
              ))}
            </select>
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              {t('note')} ({t('optional')})
            </label>
            <textarea
              value={note}
              onChange={(e) => setNote(e.target.value)}
              placeholder={t('addNote')}
              rows={3}
              className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent"
            />
          </div>

          <div className="flex justify-end space-x-3 pt-4">
            <button
              type="button"
              onClick={onClose}
              className="px-4 py-2 text-sm font-medium text-gray-700 bg-gray-100 border border-gray-300 rounded-lg hover:bg-gray-200 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-primary-500"
              disabled={isSubmitting}
            >
              {t('cancel')}
            </button>
            <button
              type="submit"
              disabled={isSubmitting || !selectedAssignee}
              className="px-4 py-2 text-sm font-medium text-white bg-primary-600 border border-transparent rounded-lg hover:bg-primary-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-primary-500 disabled:opacity-50 disabled:cursor-not-allowed flex items-center"
            >
              {isSubmitting ? (
                <>
                  <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white mr-2"></div>
                  {t('subAssigning')}
                </>
              ) : (
                <>
                  <UserCheck className="mr-2 h-4 w-4" />
                  {t('subAssign')}
                </>
              )}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
}

export default SubAssignModal;