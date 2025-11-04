import { useQuery } from '@tanstack/react-query';
import { Link } from 'react-router-dom';
import {
  AlertCircle,
  CheckCircle2,
  Clock,
  Eye,
  FileText,
  Filter,
  MessageSquare,
  Shield,
  ThumbsUp,
  Users,
  XCircle,
} from 'lucide-react';
import { useAuth } from '../../contexts/AuthContext';
import { useTranslation } from '../../hooks/useTranslation';
import { complaintsAPI } from '../../services/api';

export default function ModeratorDashboard() {
  const { user } = useAuth();
  const { t } = useTranslation();

  // Fetch all complaints for moderation
  const { data: complaintsData, isLoading } = useQuery({
    queryKey: ['complaints', 'moderation-queue'],
    queryFn: async () => {
      const response = await complaintsAPI.getAll({ page_size: 200 });
      return response.data;
    },
  });

  const complaints = complaintsData?.complaints || [];

  // Categorize complaints for triage
  const triageQueue = {
    newSubmissions: complaints.filter(c => c.status === 'submitted'),
    pendingApproval: complaints.filter(c => c.status === 'assigned' && !c.approved_by_moderator),
    needsReview: complaints.filter(c => {
      const daysSince = Math.floor((Date.now() - new Date(c.created_at).getTime()) / (1000 * 60 * 60 * 24));
      return ['in_progress'].includes(c.status) && daysSince > 5;
    }),
    flaggedIssues: complaints.filter(c => c.priority === 'high' || c.priority === 'critical'),
  };

  // Statistics
  const stats = {
    totalQueue: triageQueue.newSubmissions.length + triageQueue.needsReview.length,
    newSubmissions: triageQueue.newSubmissions.length,
    pendingReview: triageQueue.needsReview.length,
    flagged: triageQueue.flaggedIssues.length,
  };

  return (
    <div className="space-y-6">
      {/* Welcome Header */}
      <div className="rounded-2xl bg-gradient-to-br from-violet-600 to-purple-600 p-8 text-white shadow-lg">
        <div className="flex items-start justify-between">
          <div>
            <h1 className="text-3xl font-bold">
              Moderator Control Center 🛡️
            </h1>
            <p className="mt-2 text-violet-100">
              Quality Assurance & Triage Management
            </p>
            <p className="mt-1 text-sm text-violet-200">
              {user?.name || 'Moderator'} • {user?.constituency_name || 'All Constituencies'}
            </p>
          </div>
          <div className="text-right">
            <div className="inline-flex items-center gap-2 rounded-lg bg-white/20 px-4 py-2">
              <Shield className="h-5 w-5" />
              <span className="text-sm font-semibold">Moderation Active</span>
            </div>
          </div>
        </div>
      </div>

      {/* Key Metrics */}
      <div className="grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-4">
        <MetricCard
          title="Total Queue"
          value={stats.totalQueue}
          icon={MessageSquare}
          color="from-blue-500 to-blue-600"
          trend="Items awaiting action"
        />
        <MetricCard
          title="New Submissions"
          value={stats.newSubmissions}
          icon={FileText}
          color="from-purple-500 to-fuchsia-600"
          trend="Needs first review"
        />
        <MetricCard
          title="Pending Review"
          value={stats.pendingReview}
          icon={Clock}
          color="from-amber-500 to-orange-600"
          trend="Long-running cases"
        />
        <MetricCard
          title="Flagged Items"
          value={stats.flagged}
          icon={AlertCircle}
          color="from-red-500 to-rose-600"
          trend="High priority"
        />
      </div>

      {/* Action Required Alert */}
      {stats.newSubmissions > 0 && (
        <div className="rounded-2xl border-2 border-purple-200 bg-purple-50 p-6">
          <div className="flex items-start gap-4">
            <Shield className="h-6 w-6 flex-shrink-0 text-purple-600" />
            <div className="flex-1">
              <h3 className="font-bold text-purple-900">
                {stats.newSubmissions} New Submission{stats.newSubmissions !== 1 ? 's' : ''} Awaiting Triage
              </h3>
              <p className="mt-1 text-sm text-purple-700">
                Review and assign these complaints to appropriate departments for resolution.
              </p>
              <button className="mt-3 rounded-lg bg-purple-600 px-4 py-2 text-sm font-semibold text-white hover:bg-purple-700">
                Start Triage Process
              </button>
            </div>
          </div>
        </div>
      )}

      {/* Triage Center */}
      <div className="grid grid-cols-1 gap-6 lg:grid-cols-2">
        {/* New Submissions Queue */}
        <TriageSection
          title="New Submissions"
          count={triageQueue.newSubmissions.length}
          icon={FileText}
          color="bg-purple-500"
          complaints={triageQueue.newSubmissions}
          isLoading={isLoading}
          emptyMessage="No new submissions"
        />

        {/* Needs Review Queue */}
        <TriageSection
          title="Needs Review"
          count={triageQueue.needsReview.length}
          icon={Eye}
          color="bg-amber-500"
          complaints={triageQueue.needsReview}
          isLoading={isLoading}
          emptyMessage="All cases are current"
        />
      </div>

      {/* Flagged Issues */}
      <div className="rounded-2xl border border-slate-200 bg-white p-6 shadow-sm">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-3">
            <div className="rounded-lg bg-red-500 p-3 text-white">
              <AlertCircle className="h-6 w-6" />
            </div>
            <div>
              <h2 className="text-xl font-bold text-slate-900">Flagged High-Priority Issues</h2>
              <p className="text-sm text-slate-600">Complaints requiring immediate attention</p>
            </div>
          </div>
          <button className="flex items-center gap-2 rounded-lg bg-violet-600 px-4 py-2 text-sm font-semibold text-white hover:bg-violet-700">
            <Filter className="h-4 w-4" />
            Filter
          </button>
        </div>

        {isLoading ? (
          <div className="mt-6 flex items-center justify-center py-12">
            <div className="h-8 w-8 animate-spin rounded-full border-4 border-violet-500 border-t-transparent"></div>
          </div>
        ) : triageQueue.flaggedIssues.length === 0 ? (
          <div className="mt-6 rounded-xl border-2 border-dashed border-slate-200 p-12 text-center">
            <CheckCircle2 className="mx-auto h-12 w-12 text-slate-300" />
            <p className="mt-4 text-sm font-medium text-slate-600">No flagged issues</p>
            <p className="mt-1 text-xs text-slate-500">
              All complaints are at normal priority levels
            </p>
          </div>
        ) : (
          <div className="mt-6 space-y-3">
            {triageQueue.flaggedIssues.slice(0, 8).map((complaint) => (
              <FlaggedComplaintCard key={complaint.id} complaint={complaint} />
            ))}
          </div>
        )}
      </div>

      {/* Quick Actions */}
      <div className="grid grid-cols-1 gap-4 md:grid-cols-4">
        <ActionCard
          title="Triage Queue"
          icon={Filter}
          href="/complaints"
          color="bg-purple-500"
        />
        <ActionCard
          title="Approve/Reject"
          icon={ThumbsUp}
          href="/my-complaints"
          color="bg-blue-500"
        />
        <ActionCard
          title="Analytics"
          icon={MessageSquare}
          href="/analytics"
          color="bg-emerald-500"
        />
        <ActionCard
          title="User Management"
          icon={Users}
          href="/users"
          color="bg-slate-500"
        />
      </div>
    </div>
  );
}

function MetricCard({ title, value, icon: Icon, color, trend }) {
  return (
    <div className={`rounded-xl bg-gradient-to-br ${color} p-6 text-white shadow-lg`}>
      <div className="flex items-center justify-between">
        <div>
          <p className="text-sm font-medium text-white/80">{title}</p>
          <p className="mt-2 text-3xl font-bold">{value}</p>
          <p className="mt-1 text-xs text-white/70">{trend}</p>
        </div>
        <div className="rounded-lg bg-white/20 p-3">
          <Icon className="h-6 w-6" />
        </div>
      </div>
    </div>
  );
}

function TriageSection({ title, count, icon: Icon, color, complaints, isLoading, emptyMessage }) {
  return (
    <div className="rounded-2xl border border-slate-200 bg-white p-6 shadow-sm">
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-3">
          <div className={`rounded-lg ${color} p-3 text-white`}>
            <Icon className="h-6 w-6" />
          </div>
          <div>
            <h3 className="font-bold text-slate-900">{title}</h3>
            <p className="text-sm text-slate-600">{count} items</p>
          </div>
        </div>
      </div>

      {isLoading ? (
        <div className="mt-6 flex items-center justify-center py-8">
          <div className="h-6 w-6 animate-spin rounded-full border-4 border-violet-500 border-t-transparent"></div>
        </div>
      ) : complaints.length === 0 ? (
        <div className="mt-6 rounded-xl border border-dashed border-slate-200 p-6 text-center">
          <CheckCircle2 className="mx-auto h-8 w-8 text-slate-300" />
          <p className="mt-2 text-xs text-slate-500">{emptyMessage}</p>
        </div>
      ) : (
        <div className="mt-6 space-y-2">
          {complaints.slice(0, 5).map((complaint) => (
            <TriageCard key={complaint.id} complaint={complaint} />
          ))}
        </div>
      )}
    </div>
  );
}

function TriageCard({ complaint }) {
  const daysSince = Math.floor(
    (Date.now() - new Date(complaint.created_at).getTime()) / (1000 * 60 * 60 * 24)
  );

  return (
    <Link
      to={`/complaints/${complaint.id}`}
      className="block rounded-lg border border-slate-200 bg-slate-50 p-3 text-sm transition hover:border-violet-300 hover:bg-white hover:shadow-sm"
    >
      <div className="flex items-start justify-between">
        <div className="flex-1">
          <p className="font-semibold text-slate-900 line-clamp-1">{complaint.title}</p>
          <p className="mt-1 text-xs text-slate-600">
            {daysSince} day{daysSince !== 1 ? 's' : ''} ago • {complaint.category}
          </p>
        </div>
        <span className="text-xs font-medium text-violet-600">Review →</span>
      </div>
    </Link>
  );
}

function FlaggedComplaintCard({ complaint }) {
  const priorityColors = {
    critical: 'border-red-300 bg-red-50',
    high: 'border-orange-300 bg-orange-50',
    medium: 'border-amber-300 bg-amber-50',
    low: 'border-blue-300 bg-blue-50',
  };

  const priorityBadges = {
    critical: 'bg-red-100 text-red-700',
    high: 'bg-orange-100 text-orange-700',
    medium: 'bg-amber-100 text-amber-700',
    low: 'bg-blue-100 text-blue-700',
  };

  const bgColor = priorityColors[complaint.priority] || priorityColors.low;
  const badgeColor = priorityBadges[complaint.priority] || priorityBadges.low;

  return (
    <Link
      to={`/complaints/${complaint.id}`}
      className={`block rounded-xl border-2 p-4 transition hover:shadow-md ${bgColor}`}
    >
      <div className="flex items-start justify-between">
        <div className="flex-1">
          <div className="flex items-center gap-2">
            <span className={`rounded-full px-2 py-0.5 text-xs font-semibold uppercase ${badgeColor}`}>
              {complaint.priority}
            </span>
            <span className="text-xs text-slate-600">
              {complaint.status.replace('_', ' ').toUpperCase()}
            </span>
          </div>
          <h4 className="mt-2 font-semibold text-slate-900">{complaint.title}</h4>
          <p className="mt-1 text-sm text-slate-600 line-clamp-1">{complaint.description}</p>
        </div>
        <AlertCircle className="h-5 w-5 text-red-600" />
      </div>
    </Link>
  );
}

function ActionCard({ title, icon: Icon, href, color }) {
  return (
    <Link
      to={href}
      className="group rounded-xl border border-slate-200 bg-white p-6 transition hover:border-violet-300 hover:shadow-lg"
    >
      <div className={`inline-flex rounded-lg ${color} p-3 text-white`}>
        <Icon className="h-6 w-6" />
      </div>
      <h3 className="mt-4 font-semibold text-slate-900 group-hover:text-violet-600">
        {title}
      </h3>
    </Link>
  );
}
