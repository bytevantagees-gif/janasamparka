import { useState } from 'react';
import { CheckCircle, XCircle, AlertCircle, MessageSquare, Clock } from 'lucide-react';

const WorkCompletionApproval = ({ complaint, onApprove, onReject }) => {
  const [showApprovalForm, setShowApprovalForm] = useState(false);
  const [showRejectionForm, setShowRejectionForm] = useState(false);
  const [comments, setComments] = useState('');
  const [isSubmitting, setIsSubmitting] = useState(false);

  const handleApprove = async () => {
    if (!comments.trim()) {
      alert('Please provide approval comments');
      return;
    }

    setIsSubmitting(true);
    try {
      await onApprove({
        complaint_id: complaint.id,
        comments: comments,
        approved_at: new Date().toISOString()
      });
      
      setShowApprovalForm(false);
      setComments('');
    } catch (error) {
      console.error('Error approving work:', error);
      alert('Failed to approve work completion');
    } finally {
      setIsSubmitting(false);
    }
  };

  const handleReject = async () => {
    if (!comments.trim()) {
      alert('Please provide rejection reason');
      return;
    }

    setIsSubmitting(true);
    try {
      await onReject({
        complaint_id: complaint.id,
        reason: comments,
        rejected_at: new Date().toISOString()
      });
      
      setShowRejectionForm(false);
      setComments('');
    } catch (error) {
      console.error('Error rejecting work:', error);
      alert('Failed to reject work completion');
    } finally {
      setIsSubmitting(false);
    }
  };

  // Check if work is pending approval
  const hasAfterPhotos = complaint.media?.some(m => m.photo_type === 'after');
  const isPendingApproval = complaint.status === 'RESOLVED' && hasAfterPhotos && !complaint.work_approved;
  const isApproved = complaint.work_approved === true;
  const isRejected = complaint.work_approved === false;

  return (
    <div className="bg-white rounded-lg border border-gray-200 overflow-hidden">
      <div className="p-4 border-b border-gray-200">
        <h3 className="text-lg font-semibold text-gray-900">Work Completion Status</h3>
      </div>

      <div className="p-6">
        {/* Current Status */}
        {isApproved && (
          <div className="flex items-start gap-4 p-4 bg-green-50 border border-green-200 rounded-lg mb-4">
            <CheckCircle className="h-6 w-6 text-green-600 flex-shrink-0 mt-0.5" />
            <div className="flex-1">
              <h4 className="text-sm font-semibold text-green-900">Work Approved</h4>
              <p className="text-sm text-green-700 mt-1">
                Work completion has been approved by MLA
              </p>
              {complaint.approval_comments && (
                <div className="mt-3 p-3 bg-white rounded border border-green-200">
                  <p className="text-sm text-gray-700">{complaint.approval_comments}</p>
                  <p className="text-xs text-gray-500 mt-2">
                    Approved on {new Date(complaint.approved_at).toLocaleDateString()}
                  </p>
                </div>
              )}
            </div>
          </div>
        )}

        {isRejected && (
          <div className="flex items-start gap-4 p-4 bg-red-50 border border-red-200 rounded-lg mb-4">
            <XCircle className="h-6 w-6 text-red-600 flex-shrink-0 mt-0.5" />
            <div className="flex-1">
              <h4 className="text-sm font-semibold text-red-900">Work Rejected</h4>
              <p className="text-sm text-red-700 mt-1">
                Work completion needs revision
              </p>
              {complaint.rejection_reason && (
                <div className="mt-3 p-3 bg-white rounded border border-red-200">
                  <p className="text-sm text-gray-700">{complaint.rejection_reason}</p>
                  <p className="text-xs text-gray-500 mt-2">
                    Rejected on {new Date(complaint.rejected_at).toLocaleDateString()}
                  </p>
                </div>
              )}
            </div>
          </div>
        )}

        {isPendingApproval && !showApprovalForm && !showRejectionForm && (
          <div className="flex items-start gap-4 p-4 bg-yellow-50 border border-yellow-200 rounded-lg mb-4">
            <Clock className="h-6 w-6 text-yellow-600 flex-shrink-0 mt-0.5" />
            <div className="flex-1">
              <h4 className="text-sm font-semibold text-yellow-900">Pending Approval</h4>
              <p className="text-sm text-yellow-700 mt-1">
                Work completion is awaiting MLA approval
              </p>
            </div>
          </div>
        )}

        {!hasAfterPhotos && (
          <div className="flex items-start gap-4 p-4 bg-gray-50 border border-gray-200 rounded-lg mb-4">
            <AlertCircle className="h-6 w-6 text-gray-400 flex-shrink-0 mt-0.5" />
            <div className="flex-1">
              <h4 className="text-sm font-semibold text-gray-900">Work In Progress</h4>
              <p className="text-sm text-gray-600 mt-1">
                No completion photos uploaded yet
              </p>
            </div>
          </div>
        )}

        {/* Approval Actions */}
        {isPendingApproval && !isApproved && !isRejected && (
          <div className="space-y-4">
            {!showApprovalForm && !showRejectionForm && (
              <div className="flex gap-3">
                <button
                  onClick={() => {
                    setShowApprovalForm(true);
                    setShowRejectionForm(false);
                    setComments('');
                  }}
                  className="flex-1 inline-flex items-center justify-center px-4 py-3 border border-transparent rounded-lg shadow-sm text-sm font-medium text-white bg-green-600 hover:bg-green-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-green-500"
                >
                  <CheckCircle className="mr-2 h-5 w-5" />
                  Approve Work
                </button>

                <button
                  onClick={() => {
                    setShowRejectionForm(true);
                    setShowApprovalForm(false);
                    setComments('');
                  }}
                  className="flex-1 inline-flex items-center justify-center px-4 py-3 border border-gray-300 rounded-lg shadow-sm text-sm font-medium text-gray-700 bg-white hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-red-500"
                >
                  <XCircle className="mr-2 h-5 w-5" />
                  Request Revision
                </button>
              </div>
            )}

            {/* Approval Form */}
            {showApprovalForm && (
              <div className="p-4 bg-green-50 border border-green-200 rounded-lg">
                <h4 className="text-sm font-semibold text-green-900 mb-3">Approve Work Completion</h4>
                
                <div className="space-y-3">
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">
                      Approval Comments *
                    </label>
                    <textarea
                      value={comments}
                      onChange={(e) => setComments(e.target.value)}
                      rows={3}
                      placeholder="e.g., Work completed satisfactorily. Quality is good."
                      className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-green-500 focus:border-transparent"
                    />
                  </div>

                  <div className="flex gap-2">
                    <button
                      onClick={handleApprove}
                      disabled={isSubmitting || !comments.trim()}
                      className="flex-1 px-4 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700 disabled:opacity-50 disabled:cursor-not-allowed"
                    >
                      {isSubmitting ? 'Approving...' : 'Confirm Approval'}
                    </button>
                    <button
                      onClick={() => {
                        setShowApprovalForm(false);
                        setComments('');
                      }}
                      disabled={isSubmitting}
                      className="px-4 py-2 border border-gray-300 text-gray-700 rounded-lg hover:bg-gray-50"
                    >
                      Cancel
                    </button>
                  </div>
                </div>
              </div>
            )}

            {/* Rejection Form */}
            {showRejectionForm && (
              <div className="p-4 bg-red-50 border border-red-200 rounded-lg">
                <h4 className="text-sm font-semibold text-red-900 mb-3">Request Work Revision</h4>
                
                <div className="space-y-3">
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">
                      Reason for Rejection *
                    </label>
                    <textarea
                      value={comments}
                      onChange={(e) => setComments(e.target.value)}
                      rows={3}
                      placeholder="e.g., Work quality not satisfactory. Please redo the repair work."
                      className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-red-500 focus:border-transparent"
                    />
                  </div>

                  <div className="flex gap-2">
                    <button
                      onClick={handleReject}
                      disabled={isSubmitting || !comments.trim()}
                      className="flex-1 px-4 py-2 bg-red-600 text-white rounded-lg hover:bg-red-700 disabled:opacity-50 disabled:cursor-not-allowed"
                    >
                      {isSubmitting ? 'Rejecting...' : 'Request Revision'}
                    </button>
                    <button
                      onClick={() => {
                        setShowRejectionForm(false);
                        setComments('');
                      }}
                      disabled={isSubmitting}
                      className="px-4 py-2 border border-gray-300 text-gray-700 rounded-lg hover:bg-gray-50"
                    >
                      Cancel
                    </button>
                  </div>
                </div>
              </div>
            )}
          </div>
        )}

        {/* Re-approval for rejected work */}
        {isRejected && hasAfterPhotos && (
          <div className="mt-4">
            <button
              onClick={() => setShowApprovalForm(true)}
              className="w-full inline-flex items-center justify-center px-4 py-3 border border-transparent rounded-lg shadow-sm text-sm font-medium text-white bg-green-600 hover:bg-green-700"
            >
              <CheckCircle className="mr-2 h-5 w-5" />
              Review Again & Approve
            </button>
          </div>
        )}
      </div>
    </div>
  );
};

export default WorkCompletionApproval;
