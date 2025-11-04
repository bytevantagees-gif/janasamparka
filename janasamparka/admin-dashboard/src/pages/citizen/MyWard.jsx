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
  PieChart,
  Pie,
  Cell,
} from 'recharts';
import {
  MapPin,
  Users,
  TrendingUp,
  CheckCircle2,
  Clock,
  AlertCircle,
  Building2,
  Phone,
  Mail,
  User,
} from 'lucide-react';
import { useAuth } from '../../contexts/AuthContext';
import { useTranslation } from '../../hooks/useTranslation';
import { wardsAPI, complaintsAPI } from '../../services/api';

const COLORS = {
  resolved: '#10B981',
  in_progress: '#F59E0B',
  submitted: '#3B82F6',
  assigned: '#8B5CF6',
  rejected: '#EF4444',
};

export default function MyWard() {
  const { user } = useAuth();
  const { t } = useTranslation();

  // Fetch ward information
  const { data: wardData, isLoading: wardLoading } = useQuery({
    queryKey: ['wards', 'my-ward'],
    queryFn: async () => {
      // Get user's ward based on their location or profile
      const response = await wardsAPI.getAll({ constituency_id: user?.constituency_id });
      return response.data;
    },
    enabled: !!user?.constituency_id,
  });

  // Fetch ward statistics
  const { data: statsData, isLoading: statsLoading } = useQuery({
    queryKey: ['complaints', 'ward-stats'],
    queryFn: async () => {
      const response = await complaintsAPI.getAll({
        ward_id: wardData?.wards?.[0]?.id,
        page_size: 1000,
      });
      return response.data;
    },
    enabled: !!wardData?.wards?.[0]?.id,
  });

  const ward = wardData?.wards?.[0];
  const complaints = statsData?.complaints || [];

  // Calculate statistics
  const stats = {
    total: complaints.length,
    resolved: complaints.filter((c) => c.status === 'resolved').length,
    inProgress: complaints.filter((c) => c.status === 'in_progress').length,
    pending: complaints.filter((c) =>
      ['submitted', 'assigned'].includes(c.status)
    ).length,
  };

  const resolutionRate = stats.total > 0 ? (stats.resolved / stats.total) * 100 : 0;

  // Status distribution for chart
  const statusDistribution = [
    { name: 'Resolved', value: stats.resolved, color: COLORS.resolved },
    { name: 'In Progress', value: stats.inProgress, color: COLORS.in_progress },
    { name: 'Pending', value: stats.pending, color: COLORS.submitted },
  ].filter((item) => item.value > 0);

  // Category distribution
  const categoryStats = complaints.reduce((acc, complaint) => {
    const category = complaint.category || 'Other';
    acc[category] = (acc[category] || 0) + 1;
    return {};
  }, {});

  const categoryData = Object.entries(categoryStats)
    .map(([name, value]) => ({ name, value }))
    .sort((a, b) => b.value - a.value)
    .slice(0, 10);

  // Trend data (last 30 days)
  const trendData = [];
  for (let i = 29; i >= 0; i--) {
    const date = new Date();
    date.setDate(date.getDate() - i);
    const dateStr = date.toISOString().split('T')[0];
    
    const dayComplaints = complaints.filter(
      (c) => c.created_at.split('T')[0] === dateStr
    );
    
    trendData.push({
      date: date.toLocaleDateString('en-US', { month: 'short', day: 'numeric' }),
      submitted: dayComplaints.length,
      resolved: dayComplaints.filter((c) => c.status === 'resolved').length,
    });
  }

  if (wardLoading) {
    return (
      <div className="flex h-96 items-center justify-center">
        <div className="h-8 w-8 animate-spin rounded-full border-4 border-sky-500 border-t-transparent"></div>
      </div>
    );
  }

  if (!ward) {
    return (
      <div className="rounded-xl border border-amber-200 bg-amber-50 p-8 text-center">
        <MapPin className="mx-auto h-12 w-12 text-amber-600" />
        <p className="mt-4 font-semibold text-amber-900">Ward information not available</p>
        <p className="mt-2 text-sm text-amber-700">
          Please update your profile with your ward information
        </p>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="rounded-2xl bg-gradient-to-br from-purple-600 to-blue-600 p-8 text-white shadow-lg">
        <div className="flex items-start justify-between">
          <div>
            <div className="flex items-center gap-2">
              <MapPin className="h-6 w-6" />
              <h1 className="text-3xl font-bold">{ward.name}</h1>
            </div>
            <p className="mt-2 text-purple-100">
              {ward.taluk}, {ward.district || user?.constituency_name}
            </p>
          </div>
        </div>
      </div>

      {/* Key Statistics */}
      <div className="grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-4">
        <StatCard
          icon={Users}
          label="Population"
          value={ward.population?.toLocaleString() || 'N/A'}
          color="blue"
        />
        <StatCard
          icon={CheckCircle2}
          label="Resolved"
          value={stats.resolved}
          color="green"
        />
        <StatCard
          icon={Clock}
          label="In Progress"
          value={stats.inProgress}
          color="amber"
        />
        <StatCard
          icon={TrendingUp}
          label="Resolution Rate"
          value={`${resolutionRate.toFixed(1)}%`}
          color="purple"
        />
      </div>

      {/* Ward Officials */}
      {ward.corporator_name && (
        <div className="rounded-xl border border-slate-200 bg-white p-6 shadow-sm">
          <h2 className="text-xl font-bold text-slate-900">Ward Officials</h2>
          <div className="mt-4 grid gap-6 md:grid-cols-2">
            <OfficialCard
              name={ward.corporator_name}
              role="Ward Corporator"
              phone={ward.corporator_phone}
              email={ward.corporator_email}
            />
            {ward.mla_name && (
              <OfficialCard
                name={ward.mla_name}
                role="MLA"
                phone={ward.mla_phone}
                email={ward.mla_email}
              />
            )}
          </div>
        </div>
      )}

      {/* Status Distribution Chart */}
      <div className="grid gap-6 lg:grid-cols-2">
        <div className="rounded-xl border border-slate-200 bg-white p-6 shadow-sm">
          <h2 className="text-xl font-bold text-slate-900">Status Distribution</h2>
          <div className="mt-6 flex justify-center">
            <ResponsiveContainer width="100%" height={300}>
              <PieChart>
                <Pie
                  data={statusDistribution}
                  cx="50%"
                  cy="50%"
                  labelLine={false}
                  label={({ name, percent }) =>
                    `${name}: ${(percent * 100).toFixed(0)}%`
                  }
                  outerRadius={100}
                  fill="#8884d8"
                  dataKey="value"
                >
                  {statusDistribution.map((entry, index) => (
                    <Cell key={`cell-${index}`} fill={entry.color} />
                  ))}
                </Pie>
                <Tooltip />
              </PieChart>
            </ResponsiveContainer>
          </div>
        </div>

        {/* Top Categories */}
        <div className="rounded-xl border border-slate-200 bg-white p-6 shadow-sm">
          <h2 className="text-xl font-bold text-slate-900">Top Issues</h2>
          <div className="mt-6">
            {categoryData.length === 0 ? (
              <p className="text-center text-sm text-slate-500">No data available</p>
            ) : (
              <ResponsiveContainer width="100%" height={300}>
                <BarChart data={categoryData}>
                  <CartesianGrid strokeDasharray="3 3" />
                  <XAxis
                    dataKey="name"
                    angle={-45}
                    textAnchor="end"
                    height={100}
                    fontSize={12}
                  />
                  <YAxis />
                  <Tooltip />
                  <Bar dataKey="value" fill="#3B82F6" />
                </BarChart>
              </ResponsiveContainer>
            )}
          </div>
        </div>
      </div>

      {/* 30-Day Trend */}
      <div className="rounded-xl border border-slate-200 bg-white p-6 shadow-sm">
        <h2 className="text-xl font-bold text-slate-900">30-Day Trend</h2>
        <div className="mt-6">
          <ResponsiveContainer width="100%" height={300}>
            <LineChart data={trendData}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis dataKey="date" fontSize={12} />
              <YAxis />
              <Tooltip />
              <Legend />
              <Line
                type="monotone"
                dataKey="submitted"
                stroke="#3B82F6"
                strokeWidth={2}
                name="Submitted"
              />
              <Line
                type="monotone"
                dataKey="resolved"
                stroke="#10B981"
                strokeWidth={2}
                name="Resolved"
              />
            </LineChart>
          </ResponsiveContainer>
        </div>
      </div>

      {/* Ward Information */}
      <div className="rounded-xl border border-slate-200 bg-white p-6 shadow-sm">
        <h2 className="text-xl font-bold text-slate-900">Ward Information</h2>
        <dl className="mt-6 grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
          {ward.area_sqkm && (
            <InfoItem label="Area" value={`${ward.area_sqkm} sq km`} />
          )}
          {ward.households && (
            <InfoItem label="Households" value={ward.households.toLocaleString()} />
          )}
          {ward.wards_count && (
            <InfoItem label="Total Wards" value={ward.wards_count} />
          )}
        </dl>
      </div>
    </div>
  );
}

function StatCard({ icon: Icon, label, value, color }) {
  const colorClasses = {
    blue: 'from-blue-500 to-blue-600',
    green: 'from-green-500 to-emerald-600',
    amber: 'from-amber-500 to-orange-600',
    purple: 'from-purple-500 to-purple-600',
  };

  return (
    <div
      className={`rounded-xl bg-gradient-to-br ${colorClasses[color]} p-6 text-white shadow-lg`}
    >
      <div className="flex items-center justify-between">
        <div>
          <p className="text-sm font-medium text-white/80">{label}</p>
          <p className="mt-2 text-3xl font-bold">{value}</p>
        </div>
        <div className="rounded-lg bg-white/20 p-3">
          <Icon className="h-6 w-6" />
        </div>
      </div>
    </div>
  );
}

function OfficialCard({ name, role, phone, email }) {
  return (
    <div className="rounded-lg border border-slate-200 bg-slate-50 p-4">
      <div className="flex items-start gap-3">
        <div className="flex h-12 w-12 items-center justify-center rounded-full bg-sky-100">
          <User className="h-6 w-6 text-sky-600" />
        </div>
        <div className="flex-1">
          <h3 className="font-semibold text-slate-900">{name}</h3>
          <p className="text-sm text-slate-600">{role}</p>
          {phone && (
            <div className="mt-2 flex items-center gap-2 text-sm text-slate-600">
              <Phone className="h-4 w-4" />
              {phone}
            </div>
          )}
          {email && (
            <div className="mt-1 flex items-center gap-2 text-sm text-slate-600">
              <Mail className="h-4 w-4" />
              {email}
            </div>
          )}
        </div>
      </div>
    </div>
  );
}

function InfoItem({ label, value }) {
  return (
    <div>
      <dt className="text-sm font-medium text-slate-600">{label}</dt>
      <dd className="mt-1 text-lg font-semibold text-slate-900">{value}</dd>
    </div>
  );
}
