import { useQuery } from '@tanstack/react-query';
import { Link } from 'react-router-dom';
import {
  AlertTriangle,
  BarChart3,
  CheckCircle2,
  Clock,
  DollarSign,
  FileText,
  Search,
  ShieldAlert,
  TrendingDown,
  TrendingUp,
} from 'lucide-react';
import { useAuth } from '../../contexts/AuthContext';
import { useTranslation } from '../../hooks/useTranslation';
import { analyticsAPI, complaintsAPI } from '../../services/api';

export default function AuditorDashboard() {
  const { user } = useAuth();
  const { t } = useTranslation();

  // Fetch dashboard analytics
  const { data: dashboardData } = useQuery({
    queryKey: ['analytics', 'dashboard'],
    queryFn: async () => {
      const response = await analyticsAPI.getDashboard();
      return response.data;
    },
  });

  // Fetch all complaints for compliance analysis
  const { data: complaintsData, isLoading } = useQuery({
    queryKey: ['complaints', 'all-for-audit'],
    queryFn: async () => {
      const response = await complaintsAPI.getAll({ page_size: 500 });
      return response.data;
    },
  });

  const complaints = complaintsData?.complaints || [];
  
  // Calculate SLA compliance
  const slaCompliance = dashboardData?.sla_metrics?.sla_compliance_rate || 0;
  const avgResolutionDays = dashboardData?.avg_resolution_time_days || 0;
  
  // Identify red flag complaints (taking too long)
  const redFlags = complaints.filter(c => {
    if (c.status === 'closed' || c.status === 'resolved') return false;
    const daysSince = Math.floor(
      (Date.now() - new Date(c.created_at).getTime()) / (1000 * 60 * 60 * 24)
    );
    return daysSince > 7; // More than 7 days old
  });

  // Budget variance analysis (mock data - would come from backend)
  const budgetStats = {
    allocated: 50000000,
    spent: 38500000,
    variance: 11500000,
    utilizationRate: 77,
  };

  // Compliance metrics
  const complianceStats = {
    totalReviewed: complaints.length,
    compliant: Math.floor(complaints.length * (slaCompliance / 100)),
    nonCompliant: complaints.length - Math.floor(complaints.length * (slaCompliance / 100)),
    underInvestigation: redFlags.length,
  };

  return (
    <div className="space-y-6">
      {/* Welcome Header */}
      <div className="rounded-2xl bg-gradient-to-br from-emerald-600 to-teal-600 p-8 text-white shadow-lg">
        <div className="flex items-start justify-between">
          <div>
            <h1 className="text-3xl font-bold">
              Auditor Dashboard 🔍
            </h1>
            <p className="mt-2 text-emerald-100">
              Compliance Monitoring & SLA Integrity Assessment
            </p>
            <p className="mt-1 text-sm text-emerald-200">
              {user?.name || 'Auditor'} • {user?.constituency_name || 'All Constituencies'}
            </p>
          </div>
          <div className="text-right">
            <div className="inline-flex items-center gap-2 rounded-lg bg-white/20 px-4 py-2">
              <ShieldAlert className="h-5 w-5" />
              <span className="text-sm font-semibold">Audit Mode Active</span>
            </div>
          </div>
        </div>
      </div>

      {/* Key Metrics */}
      <div className="grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-4">
        <MetricCard
          title="SLA Compliance"
          value={`${slaCompliance.toFixed(1)}%`}
          icon={CheckCircle2}
          color={slaCompliance >= 80 ? 'from-green-500 to-emerald-600' : 'from-amber-500 to-orange-600'}
          trend={slaCompliance >= 80 ? 'Within target' : 'Below target'}
        />
        <MetricCard
          title="Red Flags"
          value={redFlags.length}
          icon={AlertTriangle}
          color="from-red-500 to-rose-600"
          trend="Require investigation"
        />
        <MetricCard
          title="Avg Resolution"
          value={`${avgResolutionDays.toFixed(1)}d`}
          icon={Clock}
          color="from-blue-500 to-blue-600"
          trend="Days to resolve"
        />
        <MetricCard
          title="Budget Utilization"
          value={`${budgetStats.utilizationRate}%`}
          icon={DollarSign}
          color="from-purple-500 to-fuchsia-600"
          trend={`₹${(budgetStats.variance / 1000000).toFixed(1)}M remaining`}
        />
      </div>

      {/* Red Flags Alert */}
      {redFlags.length > 0 && (
        <div className="rounded-2xl border-2 border-red-200 bg-red-50 p-6">
          <div className="flex items-start gap-4">
            <AlertTriangle className="h-6 w-6 flex-shrink-0 text-red-600" />
            <div className="flex-1">
              <h3 className="font-bold text-red-900">
                {redFlags.length} Complaint{redFlags.length !== 1 ? 's' : ''} Flagged for Review
              </h3>
              <p className="mt-1 text-sm text-red-700">
                These complaints have exceeded standard resolution timeframes and require immediate audit attention.
              </p>
              <button className="mt-3 rounded-lg bg-red-600 px-4 py-2 text-sm font-semibold text-white hover:bg-red-700">
                Review Red Flags
              </button>
            </div>
          </div>
        </div>
      )}

      {/* Compliance Overview */}
      <div className="grid grid-cols-1 gap-6 lg:grid-cols-2">
        {/* SLA Compliance Breakdown */}
        <div className="rounded-2xl border border-slate-200 bg-white p-6 shadow-sm">
          <div className="flex items-center gap-3">
            <div className="rounded-lg bg-emerald-500 p-3 text-white">
              <BarChart3 className="h-6 w-6" />
            </div>
            <div>
              <h3 className="font-bold text-slate-900">SLA Compliance Analysis</h3>
              <p className="text-sm text-slate-600">Service Level Agreement adherence</p>
            </div>
          </div>

          <div className="mt-6 space-y-4">
            <ComplianceBar
              label="Compliant"
              value={complianceStats.compliant}
              total={complianceStats.totalReviewed}
              color="bg-green-500"
            />
            <ComplianceBar
              label="Non-Compliant"
              value={complianceStats.nonCompliant}
              total={complianceStats.totalReviewed}
              color="bg-red-500"
            />
            <ComplianceBar
              label="Under Investigation"
              value={complianceStats.underInvestigation}
              total={complianceStats.totalReviewed}
              color="bg-amber-500"
            />
          </div>
        </div>

        {/* Budget Analysis */}
        <div className="rounded-2xl border border-slate-200 bg-white p-6 shadow-sm">
          <div className="flex items-center gap-3">
            <div className="rounded-lg bg-blue-500 p-3 text-white">
              <DollarSign className="h-6 w-6" />
            </div>
            <div>
              <h3 className="font-bold text-slate-900">Budget Analysis</h3>
              <p className="text-sm text-slate-600">Financial allocation overview</p>
            </div>
          </div>

          <div className="mt-6 space-y-4">
            <BudgetItem
              label="Total Allocated"
              amount={budgetStats.allocated}
              icon={TrendingUp}
              color="text-blue-600"
            />
            <BudgetItem
              label="Total Spent"
              amount={budgetStats.spent}
              icon={TrendingDown}
              color="text-emerald-600"
            />
            <BudgetItem
              label="Variance"
              amount={budgetStats.variance}
              icon={FileText}
              color="text-purple-600"
            />
          </div>

          <Link
            to="/budget"
            className="mt-6 block w-full rounded-lg bg-blue-500 py-3 text-center text-sm font-semibold text-white hover:bg-blue-600"
          >
            View Full Budget Report
          </Link>
        </div>
      </div>

      {/* Recent Red Flag Complaints */}
      <div className="rounded-2xl border border-slate-200 bg-white p-6 shadow-sm">
        <div className="flex items-center justify-between">
          <div>
            <h2 className="text-xl font-bold text-slate-900">Red Flag Complaints</h2>
            <p className="text-sm text-slate-600">Complaints requiring audit review</p>
          </div>
          <button className="flex items-center gap-2 rounded-lg bg-emerald-600 px-4 py-2 text-sm font-semibold text-white hover:bg-emerald-700">
            <Search className="h-4 w-4" />
            Advanced Search
          </button>
        </div>

        {isLoading ? (
          <div className="mt-6 flex items-center justify-center py-12">
            <div className="h-8 w-8 animate-spin rounded-full border-4 border-emerald-500 border-t-transparent"></div>
          </div>
        ) : redFlags.length === 0 ? (
          <div className="mt-6 rounded-xl border-2 border-dashed border-slate-200 p-12 text-center">
            <CheckCircle2 className="mx-auto h-12 w-12 text-slate-300" />
            <p className="mt-4 text-sm font-medium text-slate-600">No red flags detected</p>
            <p className="mt-1 text-xs text-slate-500">
              All complaints are within acceptable SLA timeframes
            </p>
          </div>
        ) : (
          <div className="mt-6 space-y-3">
            {redFlags.slice(0, 10).map((complaint) => (
              <RedFlagCard key={complaint.id} complaint={complaint} />
            ))}
          </div>
        )}
      </div>

      {/* Quick Actions */}
      <div className="grid grid-cols-1 gap-4 md:grid-cols-4">
        <ActionCard title="Compliance Reports" icon={FileText} href="/analytics" color="bg-emerald-500" />
        <ActionCard title="Budget Analysis" icon={DollarSign} href="/budget" color="bg-blue-500" />
        <ActionCard title="Investigate Cases" icon={Search} href="/complaints" color="bg-purple-500" />
        <ActionCard title="SLA Dashboard" icon={BarChart3} href="/analytics" color="bg-teal-500" />
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

function ComplianceBar({ label, value, total, color }) {
  const percentage = total > 0 ? (value / total * 100).toFixed(1) : 0;
  
  return (
    <div>
      <div className="flex items-center justify-between text-sm">
        <span className="font-medium text-slate-700">{label}</span>
        <span className="text-slate-600">{value} ({percentage}%)</span>
      </div>
      <div className="mt-2 h-3 overflow-hidden rounded-full bg-slate-200">
        <div
          className={`h-full ${color} transition-all duration-500`}
          style={{ width: `${percentage}%` }}
        />
      </div>
    </div>
  );
}

function BudgetItem({ label, amount, icon: Icon, color }) {
  return (
    <div className="flex items-center justify-between rounded-lg border border-slate-200 p-3">
      <div className="flex items-center gap-3">
        <Icon className={`h-5 w-5 ${color}`} />
        <span className="font-medium text-slate-700">{label}</span>
      </div>
      <span className="font-semibold text-slate-900">
        ₹{(amount / 10000000).toFixed(2)}Cr
      </span>
    </div>
  );
}

function RedFlagCard({ complaint }) {
  const daysSince = Math.floor(
    (Date.now() - new Date(complaint.created_at).getTime()) / (1000 * 60 * 60 * 24)
  );

  return (
    <Link
      to={`/complaints/${complaint.id}`}
      className="block rounded-xl border-2 border-red-200 bg-red-50 p-4 transition hover:border-red-300 hover:shadow-md"
    >
      <div className="flex items-start justify-between">
        <div className="flex-1">
          <div className="flex items-center gap-2">
            <span className="inline-flex items-center gap-1 rounded-full bg-red-100 px-2 py-0.5 text-xs font-semibold text-red-700">
              <AlertTriangle className="h-3 w-3" />
              {daysSince} DAYS OLD
            </span>
            <span className="text-xs text-slate-600">
              Status: {complaint.status.replace('_', ' ').toUpperCase()}
            </span>
          </div>
          <h4 className="mt-2 font-semibold text-slate-900">{complaint.title}</h4>
          <p className="mt-1 text-sm text-slate-600 line-clamp-1">{complaint.description}</p>
        </div>
        <ShieldAlert className="h-5 w-5 text-red-600" />
      </div>
    </Link>
  );
}

function ActionCard({ title, icon: Icon, href, color }) {
  return (
    <Link
      to={href}
      className="group rounded-xl border border-slate-200 bg-white p-6 transition hover:border-emerald-300 hover:shadow-lg"
    >
      <div className={`inline-flex rounded-lg ${color} p-3 text-white`}>
        <Icon className="h-6 w-6" />
      </div>
      <h3 className="mt-4 font-semibold text-slate-900 group-hover:text-emerald-600">
        {title}
      </h3>
    </Link>
  );
}
