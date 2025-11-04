import { useState } from 'react';
import { useQuery } from '@tanstack/react-query';
import { Link } from 'react-router-dom';
import {
  AlertCircle,
  CheckCircle2,
  Clock,
  FileText,
  Filter,
  History,
  MapPin,
  MessageSquare,
  Plus,
  Search,
  Users,
  X,
} from 'lucide-react';
import { useAuth } from '../../contexts/AuthContext';
import { useTranslation } from '../../hooks/useTranslation';
import { complaintsAPI } from '../../services/api';

const STATUS_CONFIG = {
  submitted: { 
    label: 'Submitted', 
    color: 'text-blue-700', 
    bgColor: 'bg-blue-100',
    borderColor: 'border-blue-200',
    icon: FileText 
  },
  assigned: { 
    label: 'Assigned', 
    color: 'text-purple-700', 
    bgColor: 'bg-purple-100',
    borderColor: 'border-purple-200',
    icon: Users 
  },
  in_progress: { 
    label: 'In Progress', 
    color: 'text-yellow-700', 
    bgColor: 'bg-yellow-100',
    borderColor: 'border-yellow-200',
    icon: History 
  },
  resolved: { 
    label: 'Resolved', 
    color: 'text-green-700', 
    bgColor: 'bg-green-100',
    borderColor: 'border-green-200',
    icon: CheckCircle2 
  },
  closed: { 
    label: 'Closed', 
    color: 'text-gray-700', 
    bgColor: 'bg-gray-100',
    borderColor: 'border-gray-200',
    icon: CheckCircle2 
  },
  rejected: { 
    label: 'Rejected', 
    color: 'text-red-700', 
    bgColor: 'bg-red-100',
    borderColor: 'border-red-200',
    icon: AlertCircle 
  },
};

export default function MyComplaints() {
  const { user } = useAuth();
  const { t } = useTranslation();
  const [searchQuery, setSearchQuery] = useState('');
  const [statusFilter, setStatusFilter] = useState('all');

  // Fetch citizen's complaints
  const { data: complaintsData, isLoading } = useQuery({
    queryKey: ['complaints', 'my-complaints'],
    queryFn: async () => {
      const response = await complaintsAPI.getAll({ 
        submitted_by: user?.id,
        page_size: 100,
        sort: '-created_at'
      });
      return response.data;
    },
    enabled: !!user?.id,
  });

  const allComplaints = complaintsData?.complaints || [];

  // Filter complaints
  const filteredComplaints = allComplaints.filter((complaint) => {
    // Status filter
    if (statusFilter !== 'all') {
      if (statusFilter === 'active') {
        if (!['submitted', 'assigned', 'in_progress'].includes(complaint.status)) {
          return false;
        }
      } else if (statusFilter === 'completed') {
        if (!['resolved', 'closed'].includes(complaint.status)) {
          return false;
        }
      } else if (complaint.status !== statusFilter) {
        return false;
      }
    }

    // Search filter
    if (searchQuery) {
      const query = searchQuery.toLowerCase();
      return (
        complaint.title?.toLowerCase().includes(query) ||
        complaint.description?.toLowerCase().includes(query) ||
        complaint.location_description?.toLowerCase().includes(query) ||
        complaint.category?.toLowerCase().includes(query)
      );
    }

    return true;
  });

  // Statistics
  const stats = {
    total: allComplaints.length,
    active: allComplaints.filter(c => ['submitted', 'assigned', 'in_progress'].includes(c.status)).length,
    resolved: allComplaints.filter(c => c.status === 'resolved').length,
    closed: allComplaints.filter(c => c.status === 'closed').length,
    rejected: allComplaints.filter(c => c.status === 'rejected').length,
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold text-slate-900">My Submissions</h1>
          <p className="mt-1 text-sm text-slate-600">
            Track all your complaints, feedback, and queries
          </p>
        </div>
        <Link
          to="/complaints/new"
          className="inline-flex items-center gap-2 rounded-lg bg-sky-600 px-4 py-2 font-semibold text-white shadow-sm transition hover:bg-sky-700"
        >
          <Plus className="h-5 w-5" />
          New Submission
        </Link>
      </div>

      {/* Statistics Cards */}
      <div className="grid grid-cols-2 gap-4 md:grid-cols-5">
        <StatCard
          label="Total"
          value={stats.total}
          color="blue"
          active={statusFilter === 'all'}
          onClick={() => setStatusFilter('all')}
        />
        <StatCard
          label="Active"
          value={stats.active}
          color="amber"
          active={statusFilter === 'active'}
          onClick={() => setStatusFilter('active')}
        />
        <StatCard
          label="Resolved"
          value={stats.resolved}
          color="green"
          active={statusFilter === 'resolved'}
          onClick={() => setStatusFilter('resolved')}
        />
        <StatCard
          label="Closed"
          value={stats.closed}
          color="gray"
          active={statusFilter === 'closed'}
          onClick={() => setStatusFilter('closed')}
        />
        <StatCard
          label="Rejected"
          value={stats.rejected}
          color="red"
          active={statusFilter === 'rejected'}
          onClick={() => setStatusFilter('rejected')}
        />
      </div>

      {/* Search and Filters */}
      <div className="flex flex-col gap-4 rounded-lg border border-slate-200 bg-white p-4 shadow-sm md:flex-row md:items-center md:justify-between">
        <div className="relative flex-1">
          <Search className="absolute left-3 top-1/2 h-5 w-5 -translate-y-1/2 text-slate-400" />
          <input
            type="text"
            placeholder="Search by title, description, location..."
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            className="w-full rounded-lg border border-slate-300 py-2 pl-10 pr-10 focus:border-sky-500 focus:outline-none focus:ring-2 focus:ring-sky-500/20"
          />
          {searchQuery && (
            <button
              onClick={() => setSearchQuery('')}
              className="absolute right-3 top-1/2 -translate-y-1/2 text-slate-400 hover:text-slate-600"
            >
              <X className="h-5 w-5" />
            </button>
          )}
        </div>

        <div className="flex items-center gap-2">
          <Filter className="h-5 w-5 text-slate-400" />
          <select
            value={statusFilter}
            onChange={(e) => setStatusFilter(e.target.value)}
            className="rounded-lg border border-slate-300 px-4 py-2 focus:border-sky-500 focus:outline-none focus:ring-2 focus:ring-sky-500/20"
          >
            <option value="all">All Status</option>
            <option value="active">Active</option>
            <option value="submitted">Submitted</option>
            <option value="assigned">Assigned</option>
            <option value="in_progress">In Progress</option>
            <option value="resolved">Resolved</option>
            <option value="closed">Closed</option>
            <option value="rejected">Rejected</option>
            <option value="completed">Completed (Resolved/Closed)</option>
          </select>
        </div>
      </div>

      {/* Results Summary */}
      <div className="flex items-center justify-between text-sm text-slate-600">
        <div>
          Showing <span className="font-semibold text-slate-900">{filteredComplaints.length}</span> of{' '}
          <span className="font-semibold text-slate-900">{allComplaints.length}</span> submissions
        </div>
        {(searchQuery || statusFilter !== 'all') && (
          <button
            onClick={() => {
              setSearchQuery('');
              setStatusFilter('all');
            }}
            className="text-sky-600 hover:text-sky-700"
          >
            Clear filters
          </button>
        )}
      </div>

      {/* Complaints List */}
      {isLoading ? (
        <div className="flex items-center justify-center py-12">
          <div className="h-8 w-8 animate-spin rounded-full border-4 border-sky-500 border-t-transparent"></div>
        </div>
      ) : filteredComplaints.length === 0 ? (
        <div className="rounded-xl border-2 border-dashed border-slate-200 bg-white p-12 text-center">
          <MessageSquare className="mx-auto h-16 w-16 text-slate-300" />
          <p className="mt-4 text-lg font-semibold text-slate-700">
            {searchQuery || statusFilter !== 'all' ? 'No submissions found' : 'No submissions yet'}
          </p>
          <p className="mt-2 text-sm text-slate-500">
            {searchQuery || statusFilter !== 'all'
              ? 'Try adjusting your filters or search query'
              : 'Submit your first complaint, feedback, or query to get started'}
          </p>
          {!searchQuery && statusFilter === 'all' && (
            <Link
              to="/complaints/new"
              className="mt-6 inline-flex items-center gap-2 rounded-lg bg-sky-600 px-4 py-2 font-semibold text-white hover:bg-sky-700"
            >
              <Plus className="h-4 w-4" />
              Create Submission
            </Link>
          )}
        </div>
      ) : (
        <div className="space-y-4">
          {filteredComplaints.map((complaint) => (
            <ComplaintCard key={complaint.id} complaint={complaint} />
          ))}
        </div>
      )}
    </div>
  );
}

function StatCard({ label, value, color, active, onClick }) {
  const colorClasses = {
    blue: 'border-blue-200 bg-blue-50 text-blue-700 hover:bg-blue-100',
    amber: 'border-amber-200 bg-amber-50 text-amber-700 hover:bg-amber-100',
    green: 'border-green-200 bg-green-50 text-green-700 hover:bg-green-100',
    gray: 'border-gray-200 bg-gray-50 text-gray-700 hover:bg-gray-100',
    red: 'border-red-200 bg-red-50 text-red-700 hover:bg-red-100',
  };

  const activeClasses = {
    blue: 'border-blue-500 bg-blue-600 text-white',
    amber: 'border-amber-500 bg-amber-600 text-white',
    green: 'border-green-500 bg-green-600 text-white',
    gray: 'border-gray-500 bg-gray-600 text-white',
    red: 'border-red-500 bg-red-600 text-white',
  };

  return (
    <button
      onClick={onClick}
      className={`rounded-lg border-2 p-4 text-center transition ${
        active ? activeClasses[color] : colorClasses[color]
      }`}
    >
      <div className={`text-3xl font-bold ${active ? 'text-white' : ''}`}>{value}</div>
      <div className={`mt-1 text-sm font-medium ${active ? 'text-white/90' : ''}`}>{label}</div>
    </button>
  );
}

function ComplaintCard({ complaint }) {
  const config = STATUS_CONFIG[complaint.status] || STATUS_CONFIG.submitted;
  const StatusIcon = config.icon;

  const daysSince = Math.floor(
    (Date.now() - new Date(complaint.created_at).getTime()) / (1000 * 60 * 60 * 24)
  );

  return (
    <Link
      to={`/complaints/${complaint.id}`}
      className="block rounded-xl border border-slate-200 bg-white p-6 transition hover:border-sky-300 hover:shadow-md"
    >
      <div className="flex items-start justify-between">
        <div className="flex-1">
          {/* Header */}
          <div className="flex flex-wrap items-center gap-3">
            <span
              className={`inline-flex items-center gap-1.5 rounded-lg border ${config.borderColor} ${config.bgColor} px-3 py-1 text-sm font-semibold ${config.color}`}
            >
              <StatusIcon className="h-4 w-4" />
              {config.label}
            </span>
            {complaint.priority && (
              <span className="text-xs font-medium text-slate-500">
                Priority: {complaint.priority}
              </span>
            )}
            <span className="text-xs text-slate-500">
              {daysSince === 0 ? 'Today' : daysSince === 1 ? 'Yesterday' : `${daysSince} days ago`}
            </span>
          </div>

          {/* Content */}
          <h3 className="mt-3 text-lg font-semibold text-slate-900">{complaint.title}</h3>
          <p className="mt-1 text-sm text-slate-600 line-clamp-2">{complaint.description}</p>

          {/* Metadata */}
          <div className="mt-3 flex flex-wrap items-center gap-4 text-xs text-slate-500">
            {complaint.location_description && (
              <div className="flex items-center gap-1">
                <MapPin className="h-3.5 w-3.5" />
                {complaint.location_description}
              </div>
            )}
            {complaint.category && (
              <div className="flex items-center gap-1">
                <FileText className="h-3.5 w-3.5" />
                {complaint.category}
              </div>
            )}
            {complaint.assigned_officer_name && (
              <div className="flex items-center gap-1">
                <Users className="h-3.5 w-3.5" />
                Assigned to: {complaint.assigned_officer_name}
              </div>
            )}
          </div>

          {/* Rating if completed */}
          {complaint.citizen_rating && (
            <div className="mt-3 flex items-center gap-1">
              <span className="text-sm font-medium text-slate-700">Your rating:</span>
              <div className="flex">
                {[1, 2, 3, 4, 5].map((star) => (
                  <span
                    key={star}
                    className={`text-lg ${
                      star <= complaint.citizen_rating ? 'text-yellow-500' : 'text-gray-300'
                    }`}
                  >
                    ★
                  </span>
                ))}
              </div>
            </div>
          )}
        </div>
      </div>
    </Link>
  );
}
