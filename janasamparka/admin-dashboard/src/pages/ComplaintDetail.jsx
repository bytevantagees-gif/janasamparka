import { useState } from 'react';
import { useParams, Link } from 'react-router-dom';
import { useQuery, useQueryClient } from '@tanstack/react-query';
import { 
  ArrowLeft, 
  MapPin, 
  User, 
  Calendar, 
  MessageSquare,
  CheckCircle,
  Clock,
  AlertCircle,
  XCircle,
  Image as ImageIcon,
  Phone,
  Mail,
  Edit3,
  Building2,
  UserCheck
} from 'lucide-react';
import { complaintsAPI, authAPI } from '../services/api';
import StatusUpdateModal from '../components/StatusUpdateModal';
import DepartmentAssignModal from '../components/DepartmentAssignModal';
import PhotoUploadModal from '../components/PhotoUploadModal';
import BeforeAfterComparison from '../components/BeforeAfterComparison';
import WorkCompletionApproval from '../components/WorkCompletionApproval';
import SubAssignModal from '../components/SubAssignModal';
import PriorityBadge from '../components/PriorityBadge';
import InternalNotesSection from '../components/InternalNotesSection';

const STATUS_CONFIG = {
  submitted: { color: 'blue', icon: Clock, label: 'Submitted' },
  under_review: { color: 'yellow', icon: AlertCircle, label: 'Under Review' },
  in_progress: { color: 'purple', icon: Clock, label: 'In Progress' },
  resolved: { color: 'green', icon: CheckCircle, label: 'Resolved' },
  rejected: { color: 'red', icon: XCircle, label: 'Rejected' },
};

const CATEGORY_LABELS = {
  road: 'Road & Infrastructure',
  water: 'Water Supply',
  electricity: 'Electricity',
  health: 'Health',
  education: 'Education',
  sanitation: 'Sanitation',
  other: 'Other',
};

function ComplaintDetail() {
  const { id } = useParams();
  const queryClient = useQueryClient();
  const [isStatusModalOpen, setIsStatusModalOpen] = useState(false);
  const [isAssignModalOpen, setIsAssignModalOpen] = useState(false);
  const [isPhotoModalOpen, setIsPhotoModalOpen] = useState(false);
  const [isSubAssignModalOpen, setIsSubAssignModalOpen] = useState(false);

  const { data, isLoading, error } = useQuery({
    queryKey: ['complaint', id],
    queryFn: () => complaintsAPI.getById(id),
  });

  const { data: userData } = useQuery({
    queryKey: ['current-user'],
    queryFn: () => authAPI.getCurrentUser(),
  });

  const complaint = data?.data;
  const currentUser = userData?.data;

  const handleStatusUpdate = async (updateData) => {
    // TODO: Implement actual API call
    console.log('Updating status:', updateData);
    
    // Mock success - in production, call the API
    await new Promise(resolve => setTimeout(resolve, 1000));
    
    // Invalidate query to refetch data
    queryClient.invalidateQueries(['complaint', id]);
    queryClient.invalidateQueries(['complaints']);
    
    alert('Status updated successfully!');
  };

  const handleDepartmentAssign = async (assignData) => {
    // TODO: Implement actual API call
    console.log('Assigning department:', assignData);
    
    // Mock success - in production, call the API
    await new Promise(resolve => setTimeout(resolve, 1000));
    
    // Invalidate query to refetch data
    queryClient.invalidateQueries(['complaint', id]);
    queryClient.invalidateQueries(['complaints']);
    queryClient.invalidateQueries(['departments']);
    
    alert('Department assigned successfully!');
  };

  const handlePhotoUpload = async (photos) => {
    console.log('Photos uploaded:', photos);
    // TODO: Implement actual API call
    // For now, show success message
    queryClient.invalidateQueries({ queryKey: ['complaint', id] });
    alert('Photos uploaded successfully!');
  };

  const handleWorkApprove = async (approvalData) => {
    try {
      // TODO: Replace with actual API call
      console.log('Approving work:', approvalData);
      await new Promise(resolve => setTimeout(resolve, 1000));
      queryClient.invalidateQueries({ queryKey: ['complaint', id] });
      alert('Work completion approved successfully!');
    } catch (error) {
      console.error('Error approving work:', error);
      throw error;
    }
  };

  const handleWorkReject = async (rejectionData) => {
    try {
      // TODO: Replace with actual API call
      console.log('Rejecting work:', rejectionData);
      await new Promise(resolve => setTimeout(resolve, 1000));
      queryClient.invalidateQueries({ queryKey: ['complaint', id] });
      alert('Work completion rejected. Department notified.');
    } catch (error) {
      console.error('Error rejecting work:', error);
      throw error;
    }
  };

  const handleSubAssign = async (complaintId, assignData) => {
    try {
      await complaintsAPI.subAssign(complaintId, assignData);
      queryClient.invalidateQueries({ queryKey: ['complaint', id] });
      queryClient.invalidateQueries({ queryKey: ['complaints'] });
      alert('Complaint sub-assigned successfully!');
    } catch (error) {
      console.error('Error sub-assigning complaint:', error);
      throw error;
    }
  };

  if (isLoading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="text-center">
          <div className="inline-block animate-spin rounded-full h-8 w-8 border-b-2 border-primary-600"></div>
          <p className="mt-2 text-sm text-gray-500">Loading complaint...</p>
        </div>
      </div>
    );
  }

  if (error || !complaint) {
    return (
      <div className="space-y-4">
        <Link
          to="/complaints"
          className="inline-flex items-center text-sm font-medium text-gray-500 hover:text-gray-700"
        >
          <ArrowLeft className="mr-2 h-4 w-4" />
          Back to Complaints
        </Link>
        <div className="rounded-md bg-red-50 p-4">
          <p className="text-sm text-red-800">
            Error loading complaint: {error?.message || 'Complaint not found'}
          </p>
        </div>
      </div>
    );
  }

  const StatusIcon = STATUS_CONFIG[complaint.status]?.icon || AlertCircle;
  const statusColor = STATUS_CONFIG[complaint.status]?.color || 'gray';

  return (
    <div className="space-y-6">
      {/* Back Button */}
      <Link
        to="/complaints"
        className="inline-flex items-center text-sm font-medium text-gray-500 hover:text-gray-700"
      >
        <ArrowLeft className="mr-2 h-4 w-4" />
        Back to Complaints
      </Link>

      {/* Header */}
      <div className="bg-white shadow rounded-lg p-6">
        <div className="flex items-start justify-between">
          <div className="flex-1">
            <h1 className="text-2xl font-bold text-gray-900">{complaint.title}</h1>
            <p className="mt-2 text-gray-600">{complaint.description}</p>
            
            {/* Priority Badge */}
            {complaint.priority_score !== undefined && (
              <div className="mt-4">
                <PriorityBadge
                  score={complaint.priority_score}
                  isEmergency={complaint.is_emergency}
                  queuePosition={complaint.queue_position}
                  slaDeadline={complaint.sla_deadline}
                  category={complaint.category}
                />
              </div>
            )}
          </div>
          <span className={`inline-flex items-center px-3 py-1 rounded-full text-sm font-medium bg-${statusColor}-100 text-${statusColor}-800`}>
            <StatusIcon className="mr-2 h-4 w-4" />
            {STATUS_CONFIG[complaint.status]?.label || complaint.status}
          </span>
        </div>

        {/* Meta Information */}
        <div className="mt-6 grid grid-cols-1 gap-4 sm:grid-cols-3">
          <div className="flex items-center text-sm text-gray-500">
            <User className="mr-2 h-5 w-5 text-gray-400" />
            <div>
              <p className="font-medium text-gray-700">Submitted by</p>
              <p>{complaint.user_name || 'Anonymous'}</p>
            </div>
          </div>

          <div className="flex items-center text-sm text-gray-500">
            <Calendar className="mr-2 h-5 w-5 text-gray-400" />
            <div>
              <p className="font-medium text-gray-700">Created</p>
              <p>
                {new Date(complaint.created_at).toLocaleDateString('en-IN', {
                  day: 'numeric',
                  month: 'short',
                  year: 'numeric',
                  hour: '2-digit',
                  minute: '2-digit',
                })}
              </p>
            </div>
          </div>

          <div className="flex items-center text-sm text-gray-500">
            <MessageSquare className="mr-2 h-5 w-5 text-gray-400" />
            <div>
              <p className="font-medium text-gray-700">Category</p>
              <p>{CATEGORY_LABELS[complaint.category] || complaint.category}</p>
            </div>
          </div>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Main Content */}
        <div className="lg:col-span-2 space-y-6">
          {/* Location */}
          {(complaint.location_description || complaint.lat) && (
            <div className="bg-white shadow rounded-lg p-6">
              <h2 className="text-lg font-medium text-gray-900 mb-4 flex items-center">
                <MapPin className="mr-2 h-5 w-5 text-gray-400" />
                Location
              </h2>
              {complaint.location_description && (
                <p className="text-gray-600 mb-2">{complaint.location_description}</p>
              )}
              {complaint.lat && complaint.lng && (
                <p className="text-sm text-gray-500">
                  Coordinates: {complaint.lat}, {complaint.lng}
                </p>
              )}
            </div>
          )}

          {/* Before/After Photos */}
          {complaint.media && complaint.media.length > 0 && (
            <BeforeAfterComparison
              beforePhotos={complaint.media.filter(m => m.photo_type === 'before')}
              afterPhotos={complaint.media.filter(m => m.photo_type === 'after')}
            />
          )}

          {/* Other Media (Evidence, During) */}
          {complaint.media && complaint.media.filter(m => !['before', 'after'].includes(m.photo_type)).length > 0 && (
            <div className="bg-white shadow rounded-lg p-6">
              <h2 className="text-lg font-medium text-gray-900 mb-4 flex items-center">
                <ImageIcon className="mr-2 h-5 w-5 text-gray-400" />
                Evidence Photos
              </h2>
              <div className="grid grid-cols-2 gap-4">
                {complaint.media
                  .filter(m => !['before', 'after'].includes(m.photo_type))
                  .map((media, index) => (
                    <div key={index} className="relative aspect-video bg-gray-100 rounded-lg overflow-hidden">
                      <img
                        src={media.url}
                        alt={`Evidence ${index + 1}`}
                        className="w-full h-full object-cover"
                      />
                      {media.photo_type && (
                        <span className="absolute top-2 right-2 px-2 py-1 bg-black bg-opacity-50 text-white text-xs rounded capitalize">
                          {media.photo_type}
                        </span>
                      )}
                    </div>
                  ))
                }
              </div>
            </div>
          )}

          {/* Work Completion Approval */}
          <WorkCompletionApproval
            complaint={complaint}
            onApprove={handleWorkApprove}
            onReject={handleWorkReject}
          />

          {/* Internal Notes Section - Only visible to officials */}
          <InternalNotesSection complaint={complaint} />

          {/* Status History */}
          {complaint.status_logs && complaint.status_logs.length > 0 && (
            <div className="bg-white shadow rounded-lg p-6">
              <h2 className="text-lg font-medium text-gray-900 mb-4">Status History</h2>
              <div className="flow-root">
                <ul className="-mb-8">
                  {complaint.status_logs.map((log, index) => (
                    <li key={index}>
                      <div className="relative pb-8">
                        {index !== complaint.status_logs.length - 1 && (
                          <span
                            className="absolute top-4 left-4 -ml-px h-full w-0.5 bg-gray-200"
                            aria-hidden="true"
                          />
                        )}
                        <div className="relative flex space-x-3">
                          <div>
                            <span className="h-8 w-8 rounded-full bg-gray-100 flex items-center justify-center ring-8 ring-white">
                              <Clock className="h-4 w-4 text-gray-500" />
                            </span>
                          </div>
                          <div className="flex min-w-0 flex-1 justify-between space-x-4 pt-1.5">
                            <div>
                              <p className="text-sm text-gray-500">
                                Status changed to <span className="font-medium text-gray-900">{log.new_status}</span>
                              </p>
                              {log.note && (
                                <p className="mt-1 text-sm text-gray-600">{log.note}</p>
                              )}
                            </div>
                            <div className="whitespace-nowrap text-right text-sm text-gray-500">
                              {new Date(log.timestamp).toLocaleDateString('en-IN', {
                                month: 'short',
                                day: 'numeric',
                              })}
                            </div>
                          </div>
                        </div>
                      </div>
                    </li>
                  ))}
                </ul>
              </div>
            </div>
          )}
        </div>

        {/* Sidebar */}
        <div className="space-y-6">
          {/* Assignment */}
          <div className="bg-white shadow rounded-lg p-6">
            <h2 className="text-lg font-medium text-gray-900 mb-4">Assignment</h2>
            {complaint.dept_name ? (
              <div className="space-y-3">
                <div>
                  <p className="text-sm font-medium text-gray-500">Department</p>
                  <p className="mt-1 text-sm text-gray-900">{complaint.dept_name}</p>
                </div>
                {complaint.assigned_to_name && (
                  <div>
                    <p className="text-sm font-medium text-gray-500">Assigned To</p>
                    <p className="mt-1 text-sm text-gray-900">{complaint.assigned_to_name}</p>
                  </div>
                )}
              </div>
            ) : (
              <p className="text-sm text-gray-500">Not yet assigned</p>
            )}
          </div>

          {/* Contact */}
          {(complaint.user_phone || complaint.user_email) && (
            <div className="bg-white shadow rounded-lg p-6">
              <h2 className="text-lg font-medium text-gray-900 mb-4">Contact</h2>
              <div className="space-y-3">
                {complaint.user_phone && (
                  <div className="flex items-center text-sm">
                    <Phone className="mr-2 h-4 w-4 text-gray-400" />
                    <a href={`tel:${complaint.user_phone}`} className="text-primary-600 hover:text-primary-700">
                      {complaint.user_phone}
                    </a>
                  </div>
                )}
                {complaint.user_email && (
                  <div className="flex items-center text-sm">
                    <Mail className="mr-2 h-4 w-4 text-gray-400" />
                    <a href={`mailto:${complaint.user_email}`} className="text-primary-600 hover:text-primary-700">
                      {complaint.user_email}
                    </a>
                  </div>
                )}
              </div>
            </div>
          )}

          {/* Actions */}
          <div className="bg-white shadow rounded-lg p-6">
            <h2 className="text-lg font-medium text-gray-900 mb-4">Actions</h2>
            <div className="space-y-2">
              <button 
                onClick={() => setIsStatusModalOpen(true)}
                className="w-full px-4 py-2 bg-primary-600 text-white rounded-lg hover:bg-primary-700 focus:outline-none focus:ring-2 focus:ring-primary-500 flex items-center justify-center"
              >
                <Edit3 className="mr-2 h-4 w-4" />
                Update Status
              </button>
              <button 
                onClick={() => setIsAssignModalOpen(true)}
                className="w-full px-4 py-2 bg-white text-gray-700 border border-gray-300 rounded-lg hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-primary-500 flex items-center justify-center"
              >
                <Building2 className="mr-2 h-4 w-4" />
                {complaint?.dept_name ? 'Re-assign Department' : 'Assign Department'}
              </button>
              {currentUser?.role === 'department_officer' && currentUser?.id === complaint?.assigned_to && (
                <button 
                  onClick={() => setIsSubAssignModalOpen(true)}
                  className="w-full px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-blue-500 flex items-center justify-center"
                >
                  <UserCheck className="mr-2 h-4 w-4" />
                  Sub-Assign
                </button>
              )}
              <button 
                onClick={() => setIsPhotoModalOpen(true)}
                className="w-full px-4 py-2 bg-white text-gray-700 border border-gray-300 rounded-lg hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-primary-500 flex items-center justify-center"
              >
                <ImageIcon className="mr-2 h-4 w-4" />
                Upload Photos
              </button>
            </div>
          </div>
        </div>
      </div>

      {/* Status Update Modal */}
      <StatusUpdateModal
        isOpen={isStatusModalOpen}
        onClose={() => setIsStatusModalOpen(false)}
        complaint={complaint}
        onUpdate={handleStatusUpdate}
      />

      {/* Department Assignment Modal */}
      <DepartmentAssignModal
        isOpen={isAssignModalOpen}
        onClose={() => setIsAssignModalOpen(false)}
        complaint={complaint}
        onAssign={handleDepartmentAssign}
      />

      {/* Photo Upload Modal */}
      <PhotoUploadModal
        isOpen={isPhotoModalOpen}
        onClose={() => setIsPhotoModalOpen(false)}
        complaint={complaint}
        onUpload={handlePhotoUpload}
      />

      {/* Sub-Assign Modal */}
      <SubAssignModal
        isOpen={isSubAssignModalOpen}
        onClose={() => setIsSubAssignModalOpen(false)}
        complaint={complaint}
        onSubAssign={handleSubAssign}
      />
    </div>
  );
}

export default ComplaintDetail;
