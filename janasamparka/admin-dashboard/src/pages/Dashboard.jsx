import { useMemo } from 'react';
import { Link } from 'react-router-dom';
import { useQuery } from '@tanstack/react-query';
import {
  Activity,
  AlertCircle,
  ArrowUp,
  ArrowDown,
  Building2,
  Brain,
  Calendar,
  CheckCircle,
  CheckCircle2,
  Clock,
  CloudLightning,
  Compass,
  FileText,
  Gauge,
  Globe,
  History,
  MapPin,
  MessageSquare,
  Rocket,
  ShieldCheck,
  Sparkles,
  TrendingDown,
  TrendingUp,
  Users,
  Waves,
} from 'lucide-react';
import { useAuth } from '../contexts/AuthContext';
import { useTranslation } from '../hooks/useTranslation';
import { analyticsAPI, complaintsAPI, constituenciesAPI } from '../services/api';

const CATEGORY_LABELS = {
  road: 'Road & Infrastructure',
  water: 'Water Supply',
  electricity: 'Electricity',
  health: 'Health Services',
  education: 'Education',
  sanitation: 'Sanitation',
  other: 'Other',
};

const STATUS_VARIANTS = {
  submitted: { label: 'New', color: 'text-blue-600', bgColor: 'bg-blue-50', icon: FileText },
  assigned: { label: 'Assigned', color: 'text-purple-600', bgColor: 'bg-purple-50', icon: Users },
  in_progress: { label: 'In Progress', color: 'text-yellow-600', bgColor: 'bg-yellow-50', icon: History },
  resolved: { label: 'Resolved', color: 'text-green-600', bgColor: 'bg-green-50', icon: CheckCircle2 },
  closed: { label: 'Closed', color: 'text-gray-600', bgColor: 'bg-gray-50', icon: CheckCircle2 },
  rejected: { label: 'Rejected', color: 'text-red-600', bgColor: 'bg-red-50', icon: AlertCircle },
};

function Dashboard() {
  const { user, isAuthenticated } = useAuth();
  const { t } = useTranslation();

  const {
    data: dashboardData,
    isLoading: isDashboardLoading,
    error: dashboardError,
  } = useQuery({
    queryKey: ['analytics', 'dashboard'],
    queryFn: async () => {
      const response = await analyticsAPI.getDashboard();
      return response.data;
    },
    refetchInterval: 60000,
    enabled: isAuthenticated,
  });

  const { data: constituencyData } = useQuery({
    queryKey: ['constituencies', 'active'],
    queryFn: async () => {
      const response = await constituenciesAPI.getAll(true);
      return response.data;
    },
    staleTime: 300000,
    enabled: isAuthenticated,
  });

  const {
    data: recentComplaintsData,
    isLoading: isRecentLoading,
    error: recentComplaintsError,
  } = useQuery({
    queryKey: ['complaints', 'recent', user],
    queryFn: async () => {
      // The backend automatically filters by constituency based on the authenticated user
      // Admin users see all complaints, other roles see only their constituency
      const response = await complaintsAPI.getAll({ page_size: 8 });
      const complaintsData = response.data?.complaints || [];
      
      // Additional client-side filtering for specific roles (safety layer)
      const filteredComplaints = complaintsData.filter(complaint => {
        // Admin sees everything (backend already filtered correctly)
        if (user?.role === 'admin') {
          return true;
        }
        
        // MLA & Moderator: Double-check constituency match
        if (user?.role === 'mla' || user?.role === 'moderator') {
          return complaint.constituency_id === user.constituency_id;
        }
        
        // Department Officer: Show complaints assigned to them OR relevant unassigned ones in their constituency
        if (user?.role === 'department_officer') {
          // Show complaints assigned to this officer
          if (complaint.assigned_to === user.id) return true;
          
          // Show unassigned complaints in their constituency
          if (!complaint.assigned_to && complaint.constituency_id === user.constituency_id) {
            return true;
          }
          
          return false;
        }
        
        // For any other role (citizen, etc.), show only their own complaints
        return complaint.citizen_id === user.id;
      });
      
      return {
        ...response.data,
        complaints: filteredComplaints
      };
    },
    staleTime: 30000,
    enabled: isAuthenticated && !!user,
  });

  const { data: advancedStats } = useQuery({
    queryKey: ['complaints', 'advanced-stats'],
    queryFn: async () => {
      const response = await complaintsAPI.getAdvancedStats();
      return response.data;
    },
    staleTime: 60000,
    enabled: isAuthenticated,
  });

  const coverageSummary = useMemo(() => {
    const list = constituencyData?.constituencies ?? [];
    const totalPopulation = list.reduce((sum, item) => sum + (item.total_population ?? 0), 0);
    const totalWards = list.reduce((sum, item) => sum + (item.total_wards ?? 0), 0);

    return {
      totalConstituencies: constituencyData?.total ?? list.length,
      totalPopulation,
      totalWards,
    };
  }, [constituencyData]);

  const overallStats = dashboardData?.overall_stats;
  const totalComplaints = overallStats?.total ?? 0;
  const totalResolved = (overallStats?.resolved ?? 0) + (overallStats?.closed ?? 0);
  const activeQueue = (overallStats?.submitted ?? 0) + (overallStats?.assigned ?? 0) + (overallStats?.in_progress ?? 0);
  const resolutionRate = dashboardData?.resolution_rate ?? 0;
  const slaCompliance = dashboardData?.sla_metrics?.sla_compliance_rate ?? 0;
  const averageResolutionDays = dashboardData?.avg_resolution_time_days ?? null;
  const complaintsThisWeek = dashboardData?.complaints_this_week ?? 0;
  const complaintsThisMonth = dashboardData?.complaints_this_month ?? 0;

  const statusDistribution = useMemo(() => {
    if (!overallStats) return [];
    return [
      { name: 'Submitted', value: overallStats.submitted ?? 0, color: '#38bdf8' },
      { name: 'Assigned', value: overallStats.assigned ?? 0, color: '#a855f7' },
      { name: 'In Progress', value: overallStats.in_progress ?? 0, color: '#f59e0b' },
      { name: 'Resolved', value: overallStats.resolved ?? 0, color: '#10b981' },
      { name: 'Closed', value: overallStats.closed ?? 0, color: '#14b8a6' },
      { name: 'Rejected', value: overallStats.rejected ?? 0, color: '#f97316' },
    ];
  }, [overallStats]);

  const categoryBreakdown = useMemo(() => {
    if (!dashboardData?.category_breakdown) return [];
    const palette = ['#0ea5e9', '#22c55e', '#f97316', '#8b5cf6', '#ef4444'];
    return dashboardData.category_breakdown.map((item, index) => ({
      name: CATEGORY_LABELS[item.category] ?? formatTitle(item.category),
      value: item.count,
      color: palette[index % palette.length],
    }));
  }, [dashboardData?.category_breakdown]);

  const trendPoints = dashboardData?.recent_trend?.data_points ?? [];
  const timelinePoints = useMemo(() => {
    const recent = trendPoints.slice(-6);
    return recent.map((point) => {
      const dateLabel = new Date(point.date).toLocaleDateString('en-IN', {
        day: '2-digit',
        month: 'short',
      });
      const backlog = Math.max((point.new ?? 0) - (point.resolved ?? 0), 0);
      return {
        label: dateLabel,
        submitted: point.new ?? 0,
        resolved: point.resolved ?? 0,
        backlog,
      };
    });
  }, [trendPoints]);

  const timelineMax = timelinePoints.reduce(
    (max, point) => Math.max(max, point.submitted, point.resolved, point.backlog),
    1,
  );

  const backlogByDepartment = useMemo(() => {
    if (!advancedStats?.department_backlog) return new Map();
    return new Map(advancedStats.department_backlog.map((dept) => [dept.department_id, dept]));
  }, [advancedStats?.department_backlog]);

  const topUnits = useMemo(() => {
    const performance = dashboardData?.department_performance ?? [];
    return performance.slice(0, 3).map((dept) => {
      const backlog = backlogByDepartment.get(dept.department_id);
      return {
        id: dept.department_id,
        name: dept.department_name,
        totalAssigned: dept.total_assigned ?? 0,
        completed: dept.completed ?? 0,
        inProgress: dept.in_progress ?? 0,
        completionRate: dept.completion_rate ?? 0,
        avgResolutionHours: dept.avg_resolution_time_hours ?? null,
        onTimeRate: dept.on_time_rate ?? 0,
        openComplaints: backlog?.open_complaints ?? null,
        slaBreachRate: backlog?.sla_breach_rate ?? null,
      };
    });
  }, [dashboardData?.department_performance, backlogByDepartment]);

  const aiSignals = useMemo(
    () => [
      {
        title: 'Resolution Momentum',
        metric: `${formatNumber(complaintsThisMonth)} cases/mo`,
        detail: `${formatNumber(complaintsThisWeek)} logged in the last 7 days`,
        icon: TrendingUp,
        gradient: 'from-sky-500/90 via-indigo-500/90 to-blue-500/80',
      },
      {
        title: 'SLA Integrity',
        metric: formatPercent(slaCompliance),
        detail: averageResolutionDays
          ? `Avg resolution ${averageResolutionDays.toFixed(1)} days`
          : 'Awaiting resolution benchmarks',
        icon: ShieldCheck,
        gradient: 'from-emerald-500/90 via-teal-500/90 to-green-500/80',
      },
      {
        title: 'Active Queue',
        metric: `${formatNumber(activeQueue)} open`,
        detail: `${formatNumber(overallStats?.submitted ?? 0)} awaiting triage`,
        icon: CloudLightning,
        gradient: 'from-violet-500/90 via-fuchsia-500/90 to-pink-500/80',
      },
    ],
    [activeQueue, averageResolutionDays, complaintsThisMonth, complaintsThisWeek, overallStats?.submitted, slaCompliance],
  );

  const upcomingBriefings = useMemo(() => {
    if (!topUnits.length) {
      return [
        {
          title: 'Schedule sync',
          time: 'Tomorrow • 09:30',
          description: 'Review department readiness once performance data arrives.',
        },
      ];
    }

    return topUnits.slice(0, 2).map((unit) => ({
      title: `${unit.name} briefing`,
      time: `${formatNumber(unit.openComplaints ?? unit.inProgress)} active • On-time ${formatPercent(unit.onTimeRate)}`,
      description: unit.avgResolutionHours
        ? `Avg resolution ${formatDurationHours(unit.avgResolutionHours)} • Completion ${formatPercent(unit.completionRate)}`
        : `Completion ${formatPercent(unit.completionRate)} • SLA breaches ${formatPercent(unit.slaBreachRate)}`,
    }));
  }, [topUnits]);

  const recentActivities = useMemo(() => {
    const items = recentComplaintsData?.complaints ?? [];
    return items.slice(0, 6).map((complaint) => ({
      id: complaint.id,
      title: complaint.title,
      description: complaint.location_description || complaint.description || 'Citizen update logged.',
      time: formatRelativeTime(complaint.updated_at || complaint.created_at),
      status: complaint.status,
    }));
  }, [recentComplaintsData?.complaints]);

  if (!isAuthenticated) {
    return (
      <div className="flex h-64 items-center justify-center">
        <div className="rounded-xl border border-amber-200 bg-amber-50 p-6 text-center">
          <p className="text-sm font-medium text-amber-900">Please log in to access the dashboard</p>
          <p className="mt-2 text-xs text-amber-700">You need to authenticate before viewing mission control data.</p>
        </div>
      </div>
    );
  }

  if (isDashboardLoading) {
    return (
      <div className="flex h-64 items-center justify-center">
        <div className="inline-block h-12 w-12 animate-spin rounded-full border-2 border-sky-500 border-t-transparent" />
      </div>
    );
  }

  if (dashboardError) {
    return (
      <div className="rounded-xl border border-rose-200 bg-rose-50 p-6 text-sm text-rose-700">
        Failed to load mission dashboard: {getErrorMessage(dashboardError)}
      </div>
    );
  }

  const commandDeck = [
    {
      label: 'Assign Smart Taskforce',
      description: 'Deploy rapid response team with geofence route guidance.',
      icon: Rocket,
      href: '/complaints',
    },
    {
      label: 'Launch Citizens Pulse',
      description: 'Trigger multilingual poll for ward health insights.',
  icon: History,
      href: '/polls',
    },
    {
      label: 'Activate Field Ops AR',
      description: 'Enable AR overlay for on-site officers with live checklist.',
      icon: Compass,
      href: '/map',
    },
  ];

  return (
    <div className="space-y-10">
      <section className="relative overflow-hidden rounded-3xl border border-white/20 bg-gradient-to-br from-slate-900 via-sky-900 to-slate-800 p-8 text-white shadow-2xl shadow-slate-900/30">
        <div className="absolute inset-0 bg-[radial-gradient(circle_at_top,_rgba(56,189,248,0.18),transparent_50%)]" />
        <div className="relative flex flex-col gap-8 lg:flex-row lg:items-center lg:justify-between">
          <div className="max-w-xl space-y-4">
            <div className="inline-flex items-center gap-2 rounded-full bg-white/10 px-4 py-1 text-xs uppercase tracking-[0.4em] text-sky-200">
              <Sparkles className="h-4 w-4" /> {t('missionReady')}
            </div>
            <h1 className="text-3xl font-semibold sm:text-4xl flex items-center gap-6">
              {user?.profile_photo ? (
                <img
                  src={user.profile_photo.startsWith('/') ? `${import.meta.env.VITE_API_URL || 'http://localhost:8000'}${user.profile_photo}` : user.profile_photo}
                  alt={user?.name}
                  className="h-36 w-36 rounded-full object-cover ring-2 ring-white/20"
                />
              ) : (
                <div className="h-36 w-36 rounded-full bg-white/10 ring-2 ring-white/20 flex items-center justify-center">
                  <Users className="h-16 w-16 text-white/60" />
                </div>
              )}
              {t('welcomeBack')}, {user?.name?.split(' ')[0] || t('leader')} — {t('governanceIntelligenceHumming')}.
            </h1>
            <p className="text-sm text-sky-100">
              {t('realTimeTelemetry')}
            </p>
            <div className="flex flex-wrap gap-3">
              <div className="inline-flex items-center gap-2 rounded-full border border-white/30 bg-white/10 px-3 py-1 text-xs font-medium text-white/80 backdrop-blur">
                <TrendingUp className="h-4 w-4" />
                <span>{formatNumber(complaintsThisWeek)} {t('newCasesIn7d')}</span>
              </div>
              <div className="inline-flex items-center gap-2 rounded-full border border-white/30 bg-white/10 px-3 py-1 text-xs font-medium text-white/80 backdrop-blur">
                <Gauge className="h-4 w-4" />
                <span>{t('resolutionRateLabel')} {formatPercent(resolutionRate)}</span>
              </div>
              <div className="inline-flex items-center gap-2 rounded-full border border-white/30 bg-white/10 px-3 py-1 text-xs font-medium text-white/80 backdrop-blur">
                <Globe className="h-4 w-4" />
                <span>{coverageSummary.totalConstituencies} {t('constituenciesLive')}</span>
              </div>
            </div>
            <div className="flex flex-wrap gap-3 pt-2">
              <Link
                to="/analytics"
                className="inline-flex items-center gap-2 rounded-full bg-white px-5 py-2 text-sm font-semibold text-slate-900 shadow-lg shadow-slate-900/20 transition hover:bg-slate-100"
              >
                <Brain className="h-4 w-4" />
                {t('launchAIAnalyticsDeck')}
              </Link>
              <Link
                to="/complaints"
                className="inline-flex items-center gap-2 rounded-full border border-white/40 px-5 py-2 text-sm font-semibold text-white transition hover:bg-white/10"
              >
                <MessageSquare className="h-4 w-4" />
                {t('triageComplaintQueue')}
              </Link>
            </div>
          </div>

          <div className="grid gap-4 rounded-3xl bg-white/10 p-6 shadow-lg shadow-sky-500/20 backdrop-blur-xl lg:w-80">
            <div className="flex items-center justify-between">
              <p className="text-xs uppercase tracking-[0.3em] text-sky-200">{t('holoMetrics')}</p>
              <Waves className="h-4 w-4 text-sky-200" />
            </div>
            <div>
              <p className="text-sm text-sky-100">{t('liveServiceLoad')}</p>
              <p className="text-3xl font-semibold">{formatNumber(complaintsThisMonth)}</p>
              <span className="text-xs text-emerald-200">+{formatNumber(complaintsThisWeek)} {t('vs7dPrior')}</span>
            </div>
            <div className="rounded-2xl bg-white/10 p-4">
              <p className="text-xs text-sky-100">{t('resolvedVelocity')}</p>
              <p className="text-lg font-semibold text-white">{averageResolutionDays ? `${averageResolutionDays.toFixed(1)} ${t('days')}` : '—'}</p>
              <p className="mt-1 text-xs text-emerald-200">{t('slaCompliance')} {formatPercent(slaCompliance)}</p>
            </div>
            <div className="rounded-2xl bg-white/10 p-4">
              <p className="text-xs text-sky-100">{t('constituencyCoverage')}</p>
              <p className="text-sm font-medium text-white">
                {coverageSummary.totalConstituencies} {t('regions')} • {formatNumber(coverageSummary.totalWards)} {t('wards')}
              </p>
            </div>
          </div>
        </div>
      </section>

      <section className="grid grid-cols-1 gap-5 sm:grid-cols-2 xl:grid-cols-4">
        <MetricCard
          title={t('totalComplaints')}
          value={formatNumber(totalComplaints)}
          accent="from-sky-500 to-indigo-500"
          trend={`${formatNumber(complaintsThisMonth)} ${t('thisMonth')}`}
          icon={MessageSquare}
        />
        <MetricCard
          title={t('activeQueue')}
          value={formatNumber(activeQueue)}
          accent="from-amber-500 to-orange-500"
          trend={`${formatNumber(overallStats?.in_progress ?? 0)} ${t('inExecution')}`}
          icon={CloudLightning}
        />
        <MetricCard
          title={t('resolved')}
          value={formatNumber(totalResolved)}
          accent="from-emerald-500 to-teal-500"
          trend={`${formatNumber(overallStats?.resolved ?? 0)} ${t('resolved')} • ${formatNumber(overallStats?.closed ?? 0)} ${t('closed')}`}
          icon={CheckCircle}
        />
        <MetricCard
          title={t('populationServed')}
          value={formatNumber(coverageSummary.totalPopulation)}
          accent="from-purple-500 to-fuchsia-500"
          trend={`${coverageSummary.totalConstituencies} ${t('constituenciesMonitored')}`}
          icon={Users}
        />
      </section>

      <section className="grid grid-cols-1 gap-6 xl:grid-cols-3">
        <div className="rounded-3xl border border-white/20 bg-white p-6 shadow-lg shadow-slate-300/20">
          <div className="flex items-center justify-between">
            <h3 className="text-lg font-semibold text-slate-900">{t('missionTimeline')}</h3>
            <Activity className="h-5 w-5 text-slate-400" />
          </div>
          <div className="mt-6 space-y-4">
            {timelinePoints.length === 0 ? (
              <div className="rounded-lg border border-dashed border-slate-200 p-6 text-sm text-slate-500">
                {t('noRecentMovement')}
              </div>
            ) : (
              timelinePoints.map((point) => (
                <div key={point.label}>
                  <div className="flex items-center justify-between text-sm font-medium text-slate-700">
                    <span>{point.label}</span>
                    <span className="text-slate-400">
                      {t('submitted')} {point.submitted} • {t('resolved')} {point.resolved}
                    </span>
                  </div>
                  <div className="mt-2 grid grid-cols-3 gap-2">
                    <ProgressBar value={point.submitted} max={timelineMax} color="bg-sky-500" />
                    <ProgressBar value={point.resolved} max={timelineMax} color="bg-emerald-500" />
                    <ProgressBar value={point.backlog} max={timelineMax} color="bg-violet-500" />
                  </div>
                </div>
              ))
            )}
          </div>
        </div>

        <div className="rounded-3xl border border-white/20 bg-white p-6 shadow-lg shadow-slate-300/20">
          <h3 className="text-lg font-semibold text-slate-900">{t('futuristicInsights')}</h3>
          <div className="mt-6 grid gap-4">
            {aiSignals.map((signal) => (
              <div
                key={signal.title}
                className={`rounded-2xl bg-gradient-to-r ${signal.gradient} p-4 text-white shadow-lg shadow-slate-900/20`}
              >
                <div className="flex items-center justify-between">
                  <p className="text-sm font-semibold">{signal.title}</p>
                  <signal.icon className="h-4 w-4" />
                </div>
                <p className="mt-2 text-2xl font-semibold">{signal.metric}</p>
                <p className="mt-1 text-xs text-white/80">{signal.detail}</p>
              </div>
            ))}
          </div>
        </div>

        <div className="rounded-3xl border border-white/20 bg-white p-6 shadow-lg shadow-slate-300/20">
          <h3 className="text-lg font-semibold text-slate-900">Command Deck</h3>
          <div className="mt-6 space-y-4">
            {commandDeck.map((item) => (
              <Link
                key={item.label}
                to={item.href}
                className="flex items-start gap-4 rounded-2xl border border-slate-200 p-4 transition hover:border-sky-400 hover:shadow-md"
              >
                <div className="rounded-xl bg-slate-900 p-2 text-slate-100">
                  <item.icon className="h-5 w-5" />
                </div>
                <div>
                  <p className="text-sm font-semibold text-slate-900">{item.label}</p>
                  <p className="text-xs text-slate-500">{item.description}</p>
                </div>
              </Link>
            ))}
          </div>
          <div className="mt-6 rounded-2xl bg-slate-900 p-4 text-white">
            <p className="text-xs uppercase tracking-[0.3em] text-sky-300">{t('upcomingBriefings')}</p>
            <div className="mt-3 space-y-3">
              {upcomingBriefings.map((briefing) => (
                <div key={briefing.title} className="rounded-xl bg-white/10 p-3">
                  <p className="text-sm font-semibold">{briefing.title}</p>
                  <p className="text-xs text-sky-200">{briefing.time}</p>
                  <p className="mt-1 text-xs text-white/80">{briefing.description}</p>
                </div>
              ))}
            </div>
          </div>
        </div>
      </section>

      <section className="grid grid-cols-1 gap-6 2xl:grid-cols-4">
        <div className="rounded-3xl border border-white/20 bg-white p-6 shadow-lg shadow-slate-300/20">
          <div className="flex items-center justify-between">
            <h3 className="text-lg font-semibold text-slate-900">{t('liveHeatmapCoverage')}</h3>
            <Globe className="h-5 w-5 text-slate-400" />
          </div>
          <div className="mt-6 space-y-3">
            {statusDistribution.map((item) => (
              <div key={item.name}>
                <div className="flex items-center justify-between text-xs uppercase tracking-[0.2em] text-slate-500">
                  <span>{item.name}</span>
                  <span>{formatNumber(item.value)}</span>
                </div>
                <div className="mt-1 h-2 rounded-full bg-slate-100">
                  <div
                    className="h-2 rounded-full"
                    style={{
                      width: `${totalComplaints ? Math.min((item.value / totalComplaints) * 100, 100) : 0}%`,
                      backgroundColor: item.color,
                    }}
                  />
                </div>
              </div>
            ))}
          </div>
        </div>

        <div className="rounded-3xl border border-white/20 bg-white p-6 shadow-lg shadow-slate-300/20">
          <p className="text-sm font-semibold text-slate-900">{t('operationalPerformance')}</p>
          <div className="mt-4 space-y-4">
            {topUnits.map((unit, index) => (
              <div key={unit.id} className="flex items-center gap-3">
                <div className="flex h-10 w-10 items-center justify-center rounded-full bg-slate-900 text-white">
                  #{index + 1}
                </div>
                <div className="flex-1">
                  <div className="flex items-center justify-between text-sm font-medium text-slate-700">
                    <span>{unit.name}</span>
                    <span className="text-slate-400">
                      {formatNumber(unit.completed)}/{formatNumber(unit.totalAssigned)}
                    </span>
                  </div>
                  <div className="mt-2 h-2 rounded-full bg-slate-200">
                    <div className="h-2 rounded-full bg-emerald-500" style={{ width: `${Math.min(unit.completionRate, 100)}%` }} />
                  </div>
                </div>
                <div className="text-right">
                  <p className="text-sm font-semibold text-slate-900">{formatPercent(unit.completionRate)}</p>
                  <p className="text-[11px] text-slate-400">On-time {formatPercent(unit.onTimeRate)}</p>
                </div>
              </div>
            ))}
          </div>
          <Link
            to="/departments"
            className="mt-6 inline-flex items-center gap-2 text-xs font-semibold text-sky-600 hover:text-sky-700"
          >
            Open department mission hub →
          </Link>
        </div>

        <div className="rounded-3xl border border-white/20 bg-white p-6 shadow-lg shadow-slate-300/20">
          <h3 className="text-lg font-semibold text-slate-900">Category Mix</h3>
          <div className="mt-6 space-y-4">
            {categoryBreakdown.length === 0 ? (
              <div className="rounded-lg border border-dashed border-slate-200 p-6 text-sm text-slate-500">
                No category analytics available yet.
              </div>
            ) : (
              categoryBreakdown.map((category) => (
                <div key={category.name} className="flex items-center justify-between">
                  <div className="flex items-center gap-3">
                    <span
                      className="h-3 w-3 rounded-full"
                      style={{ backgroundColor: category.color }}
                    />
                    <span className="text-sm font-medium text-slate-700">{category.name}</span>
                  </div>
                  <span className="text-sm text-slate-500">{formatNumber(category.value)}</span>
                </div>
              ))
            )}
          </div>
        </div>

        <div className="rounded-3xl border border-white/20 bg-white p-6 shadow-lg shadow-slate-300/20">
          <div className="flex items-start justify-between">
            <div>
              <h3 className="text-lg font-semibold text-slate-900">AI Concierge</h3>
              <p className="text-xs text-slate-500">Ask the assistant for projections, summaries, or routing help.</p>
            </div>
            <Brain className="h-5 w-5 text-slate-400" />
          </div>
          <div className="mt-4 space-y-4">
            <div className="rounded-2xl border border-slate-200 p-4">
              <p className="text-xs uppercase tracking-[0.3em] text-slate-400">Suggested Prompt</p>
              <p className="mt-2 text-sm font-semibold text-slate-900">
                “How many critical road complaints are trending towards SLA breach in Ward 11 this weekend?”
              </p>
            </div>
            <div className="rounded-2xl border border-slate-200 p-4">
              <p className="text-xs uppercase tracking-[0.3em] text-slate-400">Latest Insight</p>
              <p className="mt-2 text-sm text-slate-600">
                AI forecasts citizen satisfaction to climb 4.2% if sanitation backlog is cleared in the next 36 hours.
              </p>
            </div>
            <button className="w-full rounded-full bg-slate-900 py-3 text-sm font-semibold text-white shadow-lg shadow-slate-900/30 hover:bg-slate-800">
              Open conversational console
            </button>
          </div>
        </div>
      </section>

      <section className="rounded-3xl border border-white/20 bg-white p-6 shadow-lg shadow-slate-300/20">
        <div className="flex items-center justify-between">
          <h3 className="text-lg font-semibold text-slate-900">Live Operations Stream</h3>
          <History className="h-5 w-5 text-slate-400" />
        </div>
        <div className="mt-6 flow-root">
          {recentComplaintsError ? (
            <div className="rounded-lg border border-amber-200 bg-amber-50 p-4 text-sm text-amber-700">
              Unable to load live stream: {getErrorMessage(recentComplaintsError)}
            </div>
          ) : isRecentLoading ? (
            <div className="flex items-center justify-center rounded-lg border border-dashed border-slate-200 p-8 text-sm text-slate-500">
              <div className="inline-block h-8 w-8 animate-spin rounded-full border-2 border-slate-300 border-t-transparent" />
            </div>
          ) : recentActivities.length === 0 ? (
            <div className="flex items-center justify-center rounded-lg border border-dashed border-slate-200 p-8 text-sm text-slate-500">
              No live updates yet—activity will appear here once complaints flow in.
            </div>
          ) : (
            <ul className="-mb-10">
              {recentActivities.map((activity, index) => {
                const variant = STATUS_VARIANTS[activity.status] ?? STATUS_VARIANTS.submitted;
                const StatusIcon = variant.icon;

                return (
                  <li key={activity.id}>
                    <div className="relative pb-10">
                      {index !== recentActivities.length - 1 && (
                        <span className="absolute top-5 left-4 -ml-px h-full w-0.5 bg-slate-200" aria-hidden="true" />
                      )}
                      <div className="relative flex space-x-3">
                        <div>
                          <span className={`flex h-9 w-9 items-center justify-center rounded-full ring-8 ring-white ${variant.timeline}`}>
                            <StatusIcon className="h-5 w-5" />
                          </span>
                        </div>
                        <div className="flex min-w-0 flex-1 justify-between space-x-4 pt-1.5">
                          <div>
                            <p className="text-sm font-semibold text-slate-900">{activity.title}</p>
                            <p className="text-sm text-slate-500">{activity.description}</p>
                          </div>
                          <div className="whitespace-nowrap text-right text-xs text-slate-400">{activity.time}</div>
                        </div>
                      </div>
                    </div>
                  </li>
                );
              })}
            </ul>
          )}
        </div>
        <Link
          to="/complaints"
          className="mt-8 inline-flex items-center gap-2 text-xs font-semibold text-sky-600 hover:text-sky-700"
        >
          Open live complaint console →
        </Link>
      </section>
    </div>
  );
}

export default Dashboard;

function MetricCard({ title, value, accent, trend, icon: Icon }) {
  return (
    <div className={`relative overflow-hidden rounded-3xl bg-gradient-to-br ${accent} text-white shadow-xl shadow-slate-900/30`}>
      <div className="absolute right-4 top-4 h-12 w-12 rounded-3xl bg-white/20" />
      <div className="relative p-6">
        <div className="flex items-center gap-3">
          <div className="rounded-2xl bg-white/20 p-2">
            <Icon className="h-5 w-5" />
          </div>
          <p className="text-xs uppercase tracking-[0.3em] text-white/70">{title}</p>
        </div>
        <p className="mt-3 text-3xl font-semibold">{value}</p>
        <div className="mt-2 flex items-center gap-2 text-xs text-white/80">
          <ArrowUp className="h-4 w-4" />
          <span>{trend}</span>
        </div>
      </div>
    </div>
  );
}

function ProgressBar({ value, max, color }) {
  const width = max ? Math.min((value / max) * 100, 100) : 0;
  return (
    <div className="h-2 rounded-full bg-slate-200">
      <div className={`${color} h-2 rounded-full`} style={{ width: `${width}%` }} />
    </div>
  );
}

function formatTitle(value) {
  if (!value) return 'Unknown';
  return value
    .replace(/_/g, ' ')
    .replace(/\b\w/g, (char) => char.toUpperCase());
}

function formatPercent(value) {
  if (value === null || value === undefined || Number.isNaN(value)) {
    return '0%';
  }
  return `${Number(value).toFixed(1)}%`;
}

function formatNumber(value) {
  if (value === null || value === undefined) return '0';
  return Number(value).toLocaleString('en-IN');
}

function formatDurationHours(value) {
  if (value === null || value === undefined) return '—';
  if (value >= 24) {
    return `${(value / 24).toFixed(1)} days`;
  }
  return `${value.toFixed(1)} hrs`;
}

function formatRelativeTime(timestamp) {
  if (!timestamp) return 'Unknown';
  const now = new Date();
  const then = new Date(timestamp);
  const diffMs = now.getTime() - then.getTime();

  const diffMinutes = Math.floor(diffMs / 60000);
  if (diffMinutes < 1) return 'Just now';
  if (diffMinutes < 60) return `${diffMinutes} min ago`;

  const diffHours = Math.floor(diffMinutes / 60);
  if (diffHours < 24) return `${diffHours} hr${diffHours > 1 ? 's' : ''} ago`;

  const diffDays = Math.floor(diffHours / 24);
  if (diffDays < 7) return `${diffDays} day${diffDays > 1 ? 's' : ''} ago`;

  return then.toLocaleDateString('en-IN', {
    day: '2-digit',
    month: 'short',
    year: 'numeric',
  });
}

function getErrorMessage(error) {
  if (!error) return 'Unknown error';
  if (error.response?.data?.detail) return error.response.data.detail;
  if (error.message) return error.message;
  return 'Unexpected error';
}
