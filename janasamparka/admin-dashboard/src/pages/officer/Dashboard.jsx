import { useQuery } from '@tanstack/react-query';
import { Link } from 'react-router-dom';
import {
  AlertCircle,
  Award,
  CheckCircle2,
  Clock,
  History,
  MapPin,
  MessageSquare,
  Target,
  TrendingUp,
  Trophy,
  Users,
} from 'lucide-react';
import { useAuth } from '../../contexts/AuthContext';
import { useTranslation } from '../../hooks/useTranslation';
import { complaintsAPI } from '../../services/api';

export default function OfficerDashboard() {
  const { user } = useAuth();
  const { t } = useTranslation();

  // Fetch officer's assigned complaints
  const { data: complaintsData, isLoading } = useQuery({
    queryKey: ['complaints', 'my-assignments'],
    queryFn: async () => {
      const response = await complaintsAPI.getAll({
        assigned_to: user?.id,
        page_size: 100,
      });
      return response.data;
    },
    enabled: !!user?.id,
  });

  const myComplaints = complaintsData?.complaints || [];

  // Calculate personal statistics
  const stats = {
    total: myComplaints.length,
    pending: myComplaints.filter(c => ['assigned', 'in_progress'].includes(c.status)).length,
    resolved: myComplaints.filter(c => c.status === 'resolved').length,
    closed: myComplaints.filter(c => c.status === 'closed').length,
  };

  const completionRate = stats.total > 0 
    ? ((stats.resolved + stats.closed) / stats.total * 100).toFixed(1)
    : 0;

  // Get urgent complaints (older than 3 days in pending status)
  const urgentComplaints = myComplaints.filter(c => {
    if (!['assigned', 'in_progress'].includes(c.status)) return false;
    const daysSince = Math.floor((Date.now() - new Date(c.created_at).getTime()) / (1000 * 60 * 60 * 24));
    return daysSince > 3;
  });

  return (
    <div className="space-y-6">
      {/* Welcome Header with Profile */}
      <div className="rounded-2xl bg-gradient-to-br from-purple-600 to-blue-600 p-8 text-white shadow-lg">
        <div className="flex items-start justify-between">
          <div className="flex items-center gap-4">
            {user?.profile_photo ? (
              <img
                src={user.profile_photo.startsWith('/') 
                  ? `${import.meta.env.VITE_API_URL || 'http://localhost:8000'}${user.profile_photo}` 
                  : user.profile_photo}
                alt={user?.name}
                className="h-20 w-20 rounded-full border-4 border-white/20 object-cover shadow-lg"
              />
            ) : (
              <div className="flex h-20 w-20 items-center justify-center rounded-full border-4 border-white/20 bg-white/10">
                <Users className="h-10 w-10" />
              </div>
            )}
            <div>
              <h1 className="text-3xl font-bold">
                {user?.name || 'Officer'} 🎯
              </h1>
              <p className="mt-1 text-purple-100">Department Officer Dashboard</p>
              <p className="mt-1 text-sm text-purple-200">
                {user?.constituency_name || 'All Constituencies'}
              </p>
            </div>
          </div>
          <div className="text-right">
            <div className="inline-flex items-center gap-2 rounded-lg bg-white/20 px-4 py-2">
              <Trophy className="h-5 w-5" />
              <span className="text-sm font-semibold">Rank: Top Performer</span>
            </div>
          </div>
        </div>
      </div>

      {/* Performance Statistics */}
      <div className="grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-4">
        <StatCard
          title="Assigned to Me"
          value={stats.total}
          icon={MessageSquare}
          color="from-blue-500 to-blue-600"
          trend={`${stats.pending} pending`}
        />
        <StatCard
          title="In Progress"
          value={stats.pending}
          icon={Clock}
          color="from-amber-500 to-orange-600"
          trend={urgentComplaints.length > 0 ? `${urgentComplaints.length} urgent` : 'On track'}
        />
        <StatCard
          title="Resolved"
          value={stats.resolved}
          icon={CheckCircle2}
          color="from-green-500 to-emerald-600"
          trend="Great job!"
        />
        <StatCard
          title="Completion Rate"
          value={`${completionRate}%`}
          icon={Target}
          color="from-purple-500 to-fuchsia-600"
          trend={completionRate >= 80 ? 'Excellent' : 'Keep going'}
        />
      </div>

      {/* Urgent Actions Required */}
      {urgentComplaints.length > 0 && (
        <div className="rounded-2xl border-2 border-red-200 bg-red-50 p-6">
          <div className="flex items-center gap-3">
            <AlertCircle className="h-6 w-6 text-red-600" />
            <div>
              <h3 className="font-bold text-red-900">Urgent Attention Required</h3>
              <p className="text-sm text-red-700">
                {urgentComplaints.length} complaint{urgentComplaints.length !== 1 ? 's' : ''} need immediate attention (pending for 3+ days)
              </p>
            </div>
          </div>
        </div>
      )}

      {/* My Work Queue */}
      <div className="rounded-2xl border border-slate-200 bg-white p-6 shadow-sm">
        <div className="flex items-center justify-between">
          <div>
            <h2 className="text-xl font-bold text-slate-900">My Work Queue</h2>
            <p className="text-sm text-slate-600">Complaints assigned to you</p>
          </div>
          <Link
            to="/my-complaints"
            className="text-sm font-semibold text-purple-600 hover:text-purple-700"
          >
            View All →
          </Link>
        </div>

        {isLoading ? (
          <div className="mt-6 flex items-center justify-center py-12">
            <div className="h-8 w-8 animate-spin rounded-full border-4 border-purple-500 border-t-transparent"></div>
          </div>
        ) : myComplaints.length === 0 ? (
          <div className="mt-6 rounded-xl border-2 border-dashed border-slate-200 p-12 text-center">
            <CheckCircle2 className="mx-auto h-12 w-12 text-slate-300" />
            <p className="mt-4 text-sm font-medium text-slate-600">No complaints assigned yet</p>
            <p className="mt-1 text-xs text-slate-500">
              Check back later for new assignments
            </p>
          </div>
        ) : (
          <div className="mt-6 space-y-3">
            {myComplaints
              .filter(c => ['assigned', 'in_progress'].includes(c.status))
              .slice(0, 8)
              .map((complaint) => (
                <WorkQueueCard key={complaint.id} complaint={complaint} />
              ))}
          </div>
        )}
      </div>

      {/* Performance Insights */}
      <div className="grid grid-cols-1 gap-6 lg:grid-cols-2">
        {/* Recent Achievements */}
        <div className="rounded-2xl border border-slate-200 bg-white p-6 shadow-sm">
          <div className="flex items-center gap-3">
            <div className="rounded-lg bg-amber-500 p-3 text-white">
              <Award className="h-6 w-6" />
            </div>
            <div>
              <h3 className="font-bold text-slate-900">Recent Achievements</h3>
              <p className="text-sm text-slate-600">Your performance milestones</p>
            </div>
          </div>
          <div className="mt-6 space-y-4">
            <AchievementItem
              title="Fast Resolver"
              description="Resolved 5 complaints in under 24 hours"
              icon="🚀"
            />
            <AchievementItem
              title="Quality Service"
              description="Maintained 4.5+ star rating"
              icon="⭐"
            />
            <AchievementItem
              title="Team Player"
              description="Helped with 10 collaborative resolutions"
              icon="🤝"
            />
          </div>
        </div>

        {/* Quick Actions */}
        <div className="rounded-2xl border border-slate-200 bg-white p-6 shadow-sm">
          <h3 className="font-bold text-slate-900">Quick Actions</h3>
          <div className="mt-6 grid grid-cols-2 gap-3">
            <ActionButton
              title="View Map"
              icon={MapPin}
              href="/map"
              color="bg-blue-500"
            />
            <ActionButton
              title="My Tasks"
              icon={MessageSquare}
              href="/my-complaints"
              color="bg-purple-500"
            />
            <ActionButton
              title="Analytics"
              icon={TrendingUp}
              href="/analytics"
              color="bg-emerald-500"
            />
            <ActionButton
              title="Settings"
              icon={Users}
              href="/settings"
              color="bg-slate-500"
            />
          </div>
        </div>
      </div>
    </div>
  );
}

function StatCard({ title, value, icon: Icon, color, trend }) {
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

function WorkQueueCard({ complaint }) {
  const daysSince = Math.floor(
    (Date.now() - new Date(complaint.created_at).getTime()) / (1000 * 60 * 60 * 24)
  );
  const isUrgent = daysSince > 3;

  return (
    <Link
      to={`/complaints/${complaint.id}`}
      className={`block rounded-xl border p-4 transition hover:shadow-md ${
        isUrgent
          ? 'border-red-300 bg-red-50 hover:border-red-400'
          : 'border-slate-200 bg-white hover:border-purple-300'
      }`}
    >
      <div className="flex items-start justify-between">
        <div className="flex-1">
          <div className="flex items-center gap-2">
            {isUrgent && (
              <span className="inline-flex items-center gap-1 rounded-full bg-red-100 px-2 py-0.5 text-xs font-semibold text-red-700">
                <AlertCircle className="h-3 w-3" />
                URGENT
              </span>
            )}
            <span className="text-xs text-slate-500">{daysSince} days ago</span>
          </div>
          <h4 className="mt-2 font-semibold text-slate-900">{complaint.title}</h4>
          <p className="mt-1 text-sm text-slate-600 line-clamp-1">{complaint.description}</p>
          {complaint.location_description && (
            <div className="mt-2 flex items-center gap-1 text-xs text-slate-500">
              <MapPin className="h-3.5 w-3.5" />
              {complaint.location_description}
            </div>
          )}
        </div>
        <History className={`h-5 w-5 ${isUrgent ? 'text-red-500' : 'text-slate-400'}`} />
      </div>
    </Link>
  );
}

function AchievementItem({ title, description, icon }) {
  return (
    <div className="flex items-start gap-3 rounded-lg border border-slate-200 p-3">
      <span className="text-2xl">{icon}</span>
      <div>
        <p className="font-semibold text-slate-900">{title}</p>
        <p className="text-xs text-slate-600">{description}</p>
      </div>
    </div>
  );
}

function ActionButton({ title, icon: Icon, href, color }) {
  return (
    <Link
      to={href}
      className={`flex flex-col items-center gap-2 rounded-xl ${color} p-4 text-white transition hover:opacity-90`}
    >
      <Icon className="h-6 w-6" />
      <span className="text-sm font-semibold">{title}</span>
    </Link>
  );
}
