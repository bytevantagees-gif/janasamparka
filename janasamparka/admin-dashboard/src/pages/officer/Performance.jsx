import { useQuery } from '@tanstack/react-query';
import {
  BarChart,
  Bar,
  LineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer,
  RadarChart,
  PolarGrid,
  PolarAngleAxis,
  PolarRadiusAxis,
  Radar,
} from 'recharts';
import {
  Award,
  TrendingUp,
  TrendingDown,
  Trophy,
  Target,
  Clock,
  CheckCircle2,
  Users,
  BarChart3,
} from 'lucide-react';
import { useAuth } from '../../contexts/AuthContext';
import { useTranslation } from '../../hooks/useTranslation';
import { complaintsAPI, analyticsAPI } from '../../services/api';

export default function OfficerPerformance() {
  const { user } = useAuth();
  const { t } = useTranslation();

  // Fetch officer's complaints
  const { data: myComplaintsData, isLoading: complaintsLoading } = useQuery({
    queryKey: ['complaints', 'my-assignments'],
    queryFn: async () => {
      const response = await complaintsAPI.getAll({
        assigned_to: user?.id,
        page_size: 1000,
      });
      return response.data;
    },
    enabled: !!user?.id,
  });

  // Fetch department statistics for comparison
  const { data: deptStatsData, isLoading: deptLoading } = useQuery({
    queryKey: ['analytics', 'department-stats'],
    queryFn: async () => {
      const response = await analyticsAPI.getDepartmentStats();
      return response.data;
    },
  });

  // Fetch leaderboard
  const { data: leaderboardData } = useQuery({
    queryKey: ['analytics', 'officer-leaderboard'],
    queryFn: async () => {
      const response = await analyticsAPI.getOfficerLeaderboard();
      return response.data;
    },
  });

  const myComplaints = myComplaintsData?.complaints || [];
  const deptStats = deptStatsData?.stats || {};
  const leaderboard = leaderboardData?.leaderboard || [];

  // Calculate personal statistics
  const stats = {
    total: myComplaints.length,
    resolved: myComplaints.filter((c) => c.status === 'resolved').length,
    closed: myComplaints.filter((c) => c.status === 'closed').length,
    inProgress: myComplaints.filter((c) => c.status === 'in_progress').length,
    pending: myComplaints.filter((c) => ['submitted', 'assigned'].includes(c.status)).length,
  };

  const myCompletionRate = stats.total > 0 
    ? ((stats.resolved + stats.closed) / stats.total * 100)
    : 0;

  const deptAvgCompletionRate = deptStats.avg_completion_rate || 0;

  // Calculate average resolution time
  const resolvedComplaints = myComplaints.filter(
    (c) => c.status === 'resolved' && c.resolved_at
  );
  const myAvgResolutionDays = resolvedComplaints.length > 0
    ? resolvedComplaints.reduce((sum, c) => {
        const days = Math.floor(
          (new Date(c.resolved_at).getTime() - new Date(c.created_at).getTime()) /
            (1000 * 60 * 60 * 24)
        );
        return sum + days;
      }, 0) / resolvedComplaints.length
    : 0;

  const deptAvgResolutionDays = deptStats.avg_resolution_days || 0;

  // Find my rank
  const myRank = leaderboard.findIndex((officer) => officer.id === user?.id) + 1;

  // Performance metrics for radar chart
  const performanceMetrics = [
    {
      metric: 'Completion Rate',
      myScore: (myCompletionRate / 100) * 100,
      deptAvg: deptAvgCompletionRate,
    },
    {
      metric: 'Speed (inverted days)',
      myScore: Math.max(0, 100 - myAvgResolutionDays * 10),
      deptAvg: Math.max(0, 100 - deptAvgResolutionDays * 10),
    },
    {
      metric: 'Quality (rating)',
      myScore: 85, // TODO: Calculate from citizen ratings
      deptAvg: 80,
    },
    {
      metric: 'Volume',
      myScore: (stats.total / (deptStats.max_complaints || stats.total || 1)) * 100,
      deptAvg: 50,
    },
  ];

  // Monthly trend data (last 6 months)
  const monthlyData = [];
  for (let i = 5; i >= 0; i--) {
    const date = new Date();
    date.setMonth(date.getMonth() - i);
    const monthStr = date.toISOString().slice(0, 7); // YYYY-MM
    
    const monthComplaints = myComplaints.filter(
      (c) => c.created_at.startsWith(monthStr)
    );
    
    const monthResolved = monthComplaints.filter(
      (c) => c.status === 'resolved' || c.status === 'closed'
    ).length;
    
    monthlyData.push({
      month: date.toLocaleDateString('en-US', { month: 'short' }),
      assigned: monthComplaints.length,
      completed: monthResolved,
    });
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="rounded-2xl bg-gradient-to-br from-purple-600 to-blue-600 p-8 text-white shadow-lg">
        <div className="flex items-start justify-between">
          <div>
            <h1 className="text-3xl font-bold">My Performance Dashboard</h1>
            <p className="mt-2 text-purple-100">Track your impact and compare with peers</p>
          </div>
          <div className="text-right">
            <div className="inline-flex items-center gap-2 rounded-lg bg-white/20 px-4 py-2">
              <Trophy className="h-6 w-6" />
              <div>
                <div className="text-2xl font-bold">#{myRank || '-'}</div>
                <div className="text-xs text-purple-200">Leaderboard Rank</div>
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Key Metrics */}
      <div className="grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-4">
        <MetricCard
          icon={Trophy}
          label="Completion Rate"
          myValue={`${myCompletionRate.toFixed(1)}%`}
          deptAvg={`${deptAvgCompletionRate.toFixed(1)}%`}
          isGood={myCompletionRate >= deptAvgCompletionRate}
          color="purple"
        />
        <MetricCard
          icon={Clock}
          label="Avg Resolution Time"
          myValue={`${myAvgResolutionDays.toFixed(1)} days`}
          deptAvg={`${deptAvgResolutionDays.toFixed(1)} days`}
          isGood={myAvgResolutionDays <= deptAvgResolutionDays}
          color="blue"
        />
        <MetricCard
          icon={CheckCircle2}
          label="Total Resolved"
          myValue={stats.resolved + stats.closed}
          deptAvg={deptStats.avg_resolved || 0}
          isGood={(stats.resolved + stats.closed) >= (deptStats.avg_resolved || 0)}
          color="green"
        />
        <MetricCard
          icon={Target}
          label="Active Cases"
          myValue={stats.inProgress + stats.pending}
          deptAvg={deptStats.avg_active || 0}
          isGood={(stats.inProgress + stats.pending) <= (deptStats.avg_active || 10)}
          color="amber"
        />
      </div>

      {/* Performance Comparison */}
      <div className="grid gap-6 lg:grid-cols-2">
        {/* Radar Chart - Multi-dimensional Performance */}
        <div className="rounded-xl border border-slate-200 bg-white p-6 shadow-sm">
          <h2 className="text-xl font-bold text-slate-900">Performance Profile</h2>
          <div className="mt-6">
            <ResponsiveContainer width="100%" height={300}>
              <RadarChart data={performanceMetrics}>
                <PolarGrid />
                <PolarAngleAxis dataKey="metric" />
                <PolarRadiusAxis angle={90} domain={[0, 100]} />
                <Radar
                  name="My Performance"
                  dataKey="myScore"
                  stroke="#8B5CF6"
                  fill="#8B5CF6"
                  fillOpacity={0.6}
                />
                <Radar
                  name="Dept. Average"
                  dataKey="deptAvg"
                  stroke="#94A3B8"
                  fill="#94A3B8"
                  fillOpacity={0.3}
                />
                <Legend />
                <Tooltip />
              </RadarChart>
            </ResponsiveContainer>
          </div>
        </div>

        {/* Leaderboard Position */}
        <div className="rounded-xl border border-slate-200 bg-white p-6 shadow-sm">
          <h2 className="text-xl font-bold text-slate-900">Leaderboard</h2>
          <div className="mt-6 space-y-3">
            {leaderboard.slice(0, 10).map((officer, index) => {
              const isMe = officer.id === user?.id;
              return (
                <div
                  key={officer.id}
                  className={`flex items-center justify-between rounded-lg p-3 ${
                    isMe
                      ? 'border-2 border-purple-500 bg-purple-50'
                      : 'border border-slate-200'
                  }`}
                >
                  <div className="flex items-center gap-3">
                    <div
                      className={`flex h-8 w-8 items-center justify-center rounded-full font-bold ${
                        index === 0
                          ? 'bg-yellow-100 text-yellow-700'
                          : index === 1
                          ? 'bg-gray-100 text-gray-700'
                          : index === 2
                          ? 'bg-orange-100 text-orange-700'
                          : 'bg-slate-100 text-slate-700'
                      }`}
                    >
                      {index + 1}
                    </div>
                    <div>
                      <div className={`font-semibold ${isMe ? 'text-purple-900' : 'text-slate-900'}`}>
                        {isMe ? `${officer.name} (You)` : officer.name}
                      </div>
                      <div className="text-xs text-slate-500">
                        {officer.completed || 0} resolved
                      </div>
                    </div>
                  </div>
                  <div className="text-right">
                    <div className="font-bold text-slate-900">
                      {officer.completion_rate?.toFixed(1)}%
                    </div>
                    <div className="text-xs text-slate-500">completion</div>
                  </div>
                </div>
              );
            })}
          </div>
        </div>
      </div>

      {/* Monthly Trend */}
      <div className="rounded-xl border border-slate-200 bg-white p-6 shadow-sm">
        <h2 className="text-xl font-bold text-slate-900">6-Month Trend</h2>
        <div className="mt-6">
          <ResponsiveContainer width="100%" height={300}>
            <LineChart data={monthlyData}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis dataKey="month" />
              <YAxis />
              <Tooltip />
              <Legend />
              <Line
                type="monotone"
                dataKey="assigned"
                stroke="#3B82F6"
                strokeWidth={2}
                name="Assigned to Me"
              />
              <Line
                type="monotone"
                dataKey="completed"
                stroke="#10B981"
                strokeWidth={2}
                name="Completed"
              />
            </LineChart>
          </ResponsiveContainer>
        </div>
      </div>

      {/* Insights & Recommendations */}
      <div className="grid gap-6 lg:grid-cols-2">
        {/* Strengths */}
        <div className="rounded-xl border border-green-200 bg-green-50 p-6">
          <div className="flex items-center gap-2">
            <Award className="h-6 w-6 text-green-600" />
            <h3 className="text-lg font-bold text-green-900">Your Strengths</h3>
          </div>
          <ul className="mt-4 space-y-2 text-sm text-green-800">
            {myCompletionRate >= deptAvgCompletionRate && (
              <li className="flex items-start gap-2">
                <CheckCircle2 className="mt-0.5 h-4 w-4 flex-shrink-0" />
                <span>Above-average completion rate ({myCompletionRate.toFixed(1)}%)</span>
              </li>
            )}
            {myAvgResolutionDays <= deptAvgResolutionDays && (
              <li className="flex items-start gap-2">
                <CheckCircle2 className="mt-0.5 h-4 w-4 flex-shrink-0" />
                <span>Faster than department average resolution time</span>
              </li>
            )}
            {myRank && myRank <= 5 && (
              <li className="flex items-start gap-2">
                <CheckCircle2 className="mt-0.5 h-4 w-4 flex-shrink-0" />
                <span>Top 5 performer in the leaderboard! 🏆</span>
              </li>
            )}
            <li className="flex items-start gap-2">
              <CheckCircle2 className="mt-0.5 h-4 w-4 flex-shrink-0" />
              <span>Handled {stats.total} cases total</span>
            </li>
          </ul>
        </div>

        {/* Areas for Improvement */}
        <div className="rounded-xl border border-amber-200 bg-amber-50 p-6">
          <div className="flex items-center gap-2">
            <Target className="h-6 w-6 text-amber-600" />
            <h3 className="text-lg font-bold text-amber-900">Growth Opportunities</h3>
          </div>
          <ul className="mt-4 space-y-2 text-sm text-amber-800">
            {myCompletionRate < deptAvgCompletionRate && (
              <li className="flex items-start gap-2">
                <TrendingUp className="mt-0.5 h-4 w-4 flex-shrink-0" />
                <span>Work on increasing completion rate to match department average</span>
              </li>
            )}
            {myAvgResolutionDays > deptAvgResolutionDays && (
              <li className="flex items-start gap-2">
                <TrendingUp className="mt-0.5 h-4 w-4 flex-shrink-0" />
                <span>Focus on reducing resolution time for faster service</span>
              </li>
            )}
            {stats.pending > 5 && (
              <li className="flex items-start gap-2">
                <TrendingUp className="mt-0.5 h-4 w-4 flex-shrink-0" />
                <span>Clear pending backlog ({stats.pending} cases waiting)</span>
              </li>
            )}
            <li className="flex items-start gap-2">
              <TrendingUp className="mt-0.5 h-4 w-4 flex-shrink-0" />
              <span>Stay consistent with monthly resolution targets</span>
            </li>
          </ul>
        </div>
      </div>
    </div>
  );
}

function MetricCard({ icon: Icon, label, myValue, deptAvg, isGood, color }) {
  const colorClasses = {
    purple: 'from-purple-500 to-purple-600',
    blue: 'from-blue-500 to-blue-600',
    green: 'from-green-500 to-emerald-600',
    amber: 'from-amber-500 to-orange-600',
  };

  return (
    <div
      className={`rounded-xl bg-gradient-to-br ${colorClasses[color]} p-6 text-white shadow-lg`}
    >
      <div className="flex items-start justify-between">
        <div className="flex-1">
          <p className="text-sm font-medium text-white/80">{label}</p>
          <p className="mt-2 text-3xl font-bold">{myValue}</p>
          <div className="mt-2 flex items-center gap-2 text-sm text-white/90">
            {isGood ? (
              <TrendingUp className="h-4 w-4" />
            ) : (
              <TrendingDown className="h-4 w-4" />
            )}
            <span>Dept avg: {deptAvg}</span>
          </div>
        </div>
        <div className="rounded-lg bg-white/20 p-3">
          <Icon className="h-6 w-6" />
        </div>
      </div>
    </div>
  );
}
