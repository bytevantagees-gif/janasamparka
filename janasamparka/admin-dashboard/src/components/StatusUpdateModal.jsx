import { useState } from 'react';
import { X, AlertCircle, CheckCircle, Clock, XCircle } from 'lucide-react';

const STATUS_OPTIONS = [
  { value: 'submitted', label: 'Submitted', color: 'blue', icon: Clock },
  { value: 'under_review', label: 'Under Review', color: 'yellow', icon: AlertCircle },
  { value: 'in_progress', label: 'In Progress', color: 'purple', icon: Clock },
  { value: 'resolved', label: 'Resolved', color: 'green', icon: CheckCircle },
  { value: 'rejected', label: 'Rejected', color: 'red', icon: XCircle },
];

function StatusUpdateModal({ isOpen, onClose, complaint, onUpdate }) {
  const [selectedStatus, setSelectedStatus] = useState(complaint?.status || 'submitted');
  const [note, setNote] = useState('');
  const [loading, setLoading] = useState(false);

  if (!isOpen) return null;

  const currentStatusConfig = STATUS_OPTIONS.find(s => s.value === complaint?.status);
  const newStatusConfig = STATUS_OPTIONS.find(s => s.value === selectedStatus);

  const handleSubmit = async (e) => {
    e.preventDefault();
    
    if (selectedStatus === complaint?.status && !note.trim()) {
      alert('Please select a different status or add a note');
      return;
    }

    setLoading(true);
    
    try {
      // Call API to update status
      await onUpdate({
        complaint_id: complaint.id,
        new_status: selectedStatus,
        note: note.trim(),
      });
      
      onClose();
    } catch (error) {
      alert('Failed to update status: ' + error.message);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="fixed inset-0 z-50 overflow-y-auto" aria-labelledby="modal-title" role="dialog" aria-modal="true">
      {/* Backdrop */}
      <div className="flex items-end justify-center min-h-screen pt-4 px-4 pb-20 text-center sm:block sm:p-0">
        <div 
          className="fixed inset-0 bg-gray-500 bg-opacity-75 transition-opacity" 
          aria-hidden="true"
          onClick={onClose}
        ></div>

        {/* Center modal */}
        <span className="hidden sm:inline-block sm:align-middle sm:h-screen" aria-hidden="true">&#8203;</span>

        <div className="inline-block align-bottom bg-white rounded-lg px-4 pt-5 pb-4 text-left overflow-hidden shadow-xl transform transition-all sm:my-8 sm:align-middle sm:max-w-lg sm:w-full sm:p-6">
          {/* Header */}
          <div className="flex items-center justify-between mb-4">
            <h3 className="text-lg font-medium text-gray-900" id="modal-title">
              Update Complaint Status
            </h3>
            <button
              onClick={onClose}
              className="text-gray-400 hover:text-gray-500 focus:outline-none"
            >
              <X className="h-6 w-6" />
            </button>
          </div>

          {/* Current Status */}
          <div className="mb-6 p-4 bg-gray-50 rounded-lg">
            <p className="text-sm text-gray-500 mb-2">Current Status</p>
            <div className="flex items-center">
              {currentStatusConfig && (
                <>
                  <currentStatusConfig.icon className={`h-5 w-5 mr-2 text-${currentStatusConfig.color}-600`} />
                  <span className={`inline-flex items-center px-3 py-1 rounded-full text-sm font-medium bg-${currentStatusConfig.color}-100 text-${currentStatusConfig.color}-800`}>
                    {currentStatusConfig.label}
                  </span>
                </>
              )}
            </div>
          </div>

          <form onSubmit={handleSubmit}>
            {/* New Status Selection */}
            <div className="mb-4">
              <label className="block text-sm font-medium text-gray-700 mb-2">
                New Status <span className="text-red-500">*</span>
              </label>
              <div className="space-y-2">
                {STATUS_OPTIONS.map((status) => {
                  const StatusIcon = status.icon;
                  const isSelected = selectedStatus === status.value;
                  const isCurrent = complaint?.status === status.value;

                  return (
                    <label
                      key={status.value}
                      className={`flex items-center p-3 border-2 rounded-lg cursor-pointer transition-all ${
                        isSelected
                          ? `border-${status.color}-500 bg-${status.color}-50`
                          : isCurrent
                          ? 'border-gray-300 bg-gray-50 opacity-50'
                          : 'border-gray-200 hover:border-gray-300'
                      }`}
                    >
                      <input
                        type="radio"
                        name="status"
                        value={status.value}
                        checked={isSelected}
                        onChange={(e) => setSelectedStatus(e.target.value)}
                        disabled={isCurrent}
                        className="sr-only"
                      />
                      <StatusIcon className={`h-5 w-5 mr-3 text-${status.color}-600`} />
                      <span className="flex-1 text-sm font-medium text-gray-900">
                        {status.label}
                      </span>
                      {isCurrent && (
                        <span className="text-xs text-gray-500">(Current)</span>
                      )}
                      {isSelected && !isCurrent && (
                        <CheckCircle className="h-5 w-5 text-green-600" />
                      )}
                    </label>
                  );
                })}
              </div>
            </div>

            {/* Note/Comment */}
            <div className="mb-6">
              <label htmlFor="note" className="block text-sm font-medium text-gray-700 mb-2">
                Add Note/Comment
              </label>
              <textarea
                id="note"
                rows="4"
                value={note}
                onChange={(e) => setNote(e.target.value)}
                placeholder="Add any notes or comments about this status change..."
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent"
              />
              <p className="mt-1 text-xs text-gray-500">
                {selectedStatus === 'resolved' && 'Please describe how the issue was resolved'}
                {selectedStatus === 'rejected' && 'Please explain why this complaint was rejected'}
                {selectedStatus === 'in_progress' && 'Optionally add details about the work in progress'}
              </p>
            </div>

            {/* Status Change Summary */}
            {selectedStatus !== complaint?.status && (
              <div className="mb-6 p-4 bg-blue-50 border border-blue-200 rounded-lg">
                <div className="flex items-center">
                  <AlertCircle className="h-5 w-5 text-blue-600 mr-2" />
                  <p className="text-sm text-blue-800">
                    Status will change from <strong>{currentStatusConfig?.label}</strong> to <strong>{newStatusConfig?.label}</strong>
                  </p>
                </div>
              </div>
            )}

            {/* Actions */}
            <div className="flex justify-end space-x-3">
              <button
                type="button"
                onClick={onClose}
                className="px-4 py-2 border border-gray-300 rounded-lg text-gray-700 hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-primary-500"
              >
                Cancel
              </button>
              <button
                type="submit"
                disabled={loading || (selectedStatus === complaint?.status && !note.trim())}
                className="px-4 py-2 bg-primary-600 text-white rounded-lg hover:bg-primary-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-primary-500 disabled:opacity-50 disabled:cursor-not-allowed flex items-center"
              >
                {loading ? (
                  <>
                    <svg className="animate-spin -ml-1 mr-2 h-4 w-4 text-white" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                      <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                      <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                    </svg>
                    Updating...
                  </>
                ) : (
                  'Update Status'
                )}
              </button>
            </div>
          </form>
        </div>
      </div>
    </div>
  );
}

export default StatusUpdateModal;
