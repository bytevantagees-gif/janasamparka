import { Link, useLocation, useNavigate } from 'react-router-dom';
import {
  LayoutDashboard,
  MapPin,
  MessageSquare,
  MessageCircle,
  Map,
  Globe,
  Users,
  Building2,
  BarChart3,
  TrendingUp,
  Settings,
  LogOut,
  Sparkles,
  Bell,
  Wifi,
  ShieldCheck,
  Sun,
  MoonStar,
  Satellite,
  Languages,
  Target,
  Heart,
  PlusCircle,
  Vote,
  Trophy,
  Layers,
  Sprout,
  GraduationCap,
  Briefcase,
} from 'lucide-react';
import { useEffect, useMemo, useState } from 'react';
import { useAuth } from '../contexts/AuthContext';
import { useLanguage } from '../contexts/LanguageContext';
import { useTranslation } from '../hooks/useTranslation';
import { useTokenRefresh } from '../hooks/useTokenRefresh';
import SessionTimeoutWarning from './SessionTimeoutWarning';
import emblem from '../assets/karnataka-emblem.svg';

const navigationCategories = [
  {
    title: 'dashboardOverview',
    items: [
      { key: 'dashboard', href: '/dashboard', icon: LayoutDashboard, roles: ['admin', 'mla', 'moderator', 'department_officer', 'ward_officer', 'citizen'] },
    ]
  },
  {
    title: 'constituentServices',
    items: [
      { key: 'complaints', href: '/complaints', icon: MessageSquare, roles: ['admin', 'mla', 'moderator'] },
      { key: 'citizenComplaints', href: '/citizen/complaints', icon: MessageSquare, roles: ['citizen'] },
      { key: 'submitComplaint', href: '/complaints/new', icon: PlusCircle, roles: ['citizen'] },
      { key: 'wardComplaints', href: '/ward-officer', icon: MessageSquare, roles: ['ward_officer'] },
      { key: 'myComplaints', href: '/my-complaints', icon: MessageSquare, roles: ['department_officer', 'moderator'] },
    ]
  },
  {
    title: 'engagementCommunication',
    items: [
      { key: 'videoConsultation', href: '/citizen/video-consultation', icon: Building2, roles: ['citizen'] },
      { key: 'votebank', href: '/votebank', icon: Users, roles: ['admin', 'mla', 'moderator'] },
      { key: 'liveChat', href: '/chat', icon: MessageSquare, roles: ['admin', 'mla', 'moderator', 'citizen'] },
      { key: 'forum', href: '/forum', icon: MessageCircle, roles: ['admin', 'mla', 'moderator', 'department_officer', 'citizen'] },
      { key: 'socialFeed', href: '/social', icon: MessageCircle, roles: ['admin', 'mla', 'moderator', 'department_officer', 'citizen'] },
      { key: 'citizenPolls', href: '/citizen/polls', icon: Vote, roles: ['citizen'] },
      { key: 'polls', href: '/polls', icon: BarChart3, roles: ['admin', 'mla', 'moderator'] },
    ]
  },
  {
    title: 'constituencyManagement',
    items: [
      { key: 'constituencies', href: '/constituencies', icon: MapPin, roles: ['admin', 'mla'] },
      { key: 'wards', href: '/wards', icon: Map, roles: ['admin', 'mla'] },
      { key: 'myWard', href: '/citizen/ward', icon: MapPin, roles: ['citizen'] },
      { key: 'panchayats', href: '/panchayats', icon: Layers, roles: ['admin', 'mla'] },
      { key: 'departments', href: '/departments', icon: Building2, roles: ['admin', 'mla'] },
    ]
  },
  {
    title: 'developmentSupport',
    items: [
      { key: 'agricultureHelp', href: '/citizen/agriculture-support', icon: Sprout, roles: ['citizen'] },
      { key: 'budget', href: '/budget', icon: Building2, roles: ['admin', 'mla', 'auditor'] },
    ]
  },
  {
    title: 'analyticsPerformance',
    items: [
      { key: 'mapView', href: '/map', icon: Globe, roles: ['admin', 'mla', 'moderator', 'department_officer', 'ward_officer', 'citizen'] },
      { key: 'analytics', href: '/analytics', icon: TrendingUp, roles: ['admin', 'mla', 'moderator', 'auditor'] },
      { key: 'performance', href: '/mla/performance', icon: Target, roles: ['admin', 'mla'] },
      { key: 'officerPerformance', href: '/officer/performance', icon: Trophy, roles: ['department_officer'] },
      { key: 'satisfaction', href: '/moderator/satisfaction', icon: Heart, roles: ['admin', 'mla', 'moderator'] },
    ]
  },
  {
    title: 'administration',
    items: [
      { key: 'users', href: '/users', icon: Users, roles: ['admin', 'mla'] },
      { key: 'settings', href: '/settings', icon: Settings, roles: ['admin', 'mla', 'moderator', 'department_officer', 'ward_officer', 'citizen', 'auditor'] },
    ]
  },
];

function Layout({ children }) {
  const location = useLocation();
  const navigate = useNavigate();
  const { user, logout } = useAuth();
  const { toggleLanguage, isKannada } = useLanguage();
  const { t } = useTranslation();
  const [auroraMode, setAuroraMode] = useState(true);
  
  // Enable automatic token refresh
  useTokenRefresh();

  useEffect(() => {
    if (auroraMode) {
      document.body.classList.add('aurora-sheen');
    } else {
      document.body.classList.remove('aurora-sheen');
    }

    return () => document.body.classList.remove('aurora-sheen');
  }, [auroraMode]);

  const handleLogout = () => {
    logout();
    navigate('/login');
  };

  const profilePhotoUrl = useMemo(() => {
    if (user?.profile_photo) {
      // If profile_photo starts with /, it's a relative URL, prepend API base URL
      if (user.profile_photo.startsWith('/')) {
        return `${import.meta.env.VITE_API_URL || 'http://localhost:8000'}${user.profile_photo}`;
      }
      return user.profile_photo;
    }
    const nameForAvatar = encodeURIComponent(user?.name || 'MLA');
    return `https://ui-avatars.com/api/?background=2563eb&color=fff&name=${nameForAvatar}`;
  }, [user?.profile_photo, user?.name]);

  // Filter navigation categories based on user role
  const filteredNavigationCategories = useMemo(() => {
    if (!user?.role) return [];
    return navigationCategories.map(category => ({
      ...category,
      items: category.items.filter(item => item.roles.includes(user.role))
    })).filter(category => category.items.length > 0);
  }, [user?.role]);

  const constituencyLabel = user?.constituency_name || 'Statewide Oversight';
  const roleLabel = user?.role?.replace(/_/g, ' ') || 'Leader';

  const toggleAuroraMode = () => setAuroraMode((prev) => !prev);

  return (
    <div className={`min-h-screen ${auroraMode ? 'bg-slate-950/5' : 'bg-slate-100'} transition-colors`}>
      {/* Sidebar */}
      <div className="fixed inset-y-0 left-0 w-64 bg-slate-900 text-slate-100 shadow-2xl shadow-slate-900/40">
        <div className="flex h-full flex-col">
          {/* Logo */}
          <div className="flex items-start justify-between gap-3 border-b border-white/10 px-5 py-4">
            <div className="flex items-start gap-3">
              <img src={emblem} alt="Government of Karnataka" className="h-10 w-10 shrink-0 drop-shadow-lg" />
              <div className="flex flex-col space-y-1 leading-snug text-left">
                <p className="text-xs uppercase tracking-wide text-sky-200">{t('governmentOfKarnataka')}</p>
                <h1 className="text-sm font-semibold text-white leading-snug break-words max-w-[10.5rem]">
                  {t('janasamparkaCcommand')}
                </h1>
              </div>
            </div>
            <Sparkles className="mt-1 h-5 w-5 text-sky-300 animate-pulse" />
          </div>

          {/* Navigation */}
          <nav className="flex-1 overflow-y-auto scroll-smooth px-3 py-4 space-y-1">
            {filteredNavigationCategories.flatMap((category) => category.items).map((item) => {
              const Icon = item.icon;
              const isActive = location.pathname.startsWith(item.href);
              
              return (
                <Link
                  key={item.key}
                  to={item.href}
                  className={`
                    flex items-center px-3 py-2 text-sm font-medium rounded-lg transition-all duration-200
                    ${isActive
                      ? 'bg-sky-500/20 text-white shadow-inner shadow-sky-500/20'
                      : 'text-slate-300 hover:bg-white/10 hover:text-white'
                    }
                  `}
                >
                  <Icon className="mr-3 h-5 w-5" />
                  {t(item.key)}
                </Link>
              );
            })}
          </nav>

          {/* User info */}
          <div className="border-t border-white/10 p-4">
            <div className="flex items-center mb-3 gap-3">
              <div className="h-12 w-12 overflow-hidden rounded-full border border-sky-400/40 shadow shadow-sky-500/20">
                <img
                  src={profilePhotoUrl}
                  alt={`${user?.name || 'MLA'} profile`}
                  className="h-full w-full object-cover"
                />
              </div>
              <div className="flex-1">
                <p className="text-sm font-medium text-white truncate">
                  {user?.name || 'MLA Dashboard'}
                </p>
                <p className="text-xs uppercase tracking-wide text-sky-200">
                  {roleLabel}
                </p>
                <p className="text-[11px] text-slate-300 mt-0.5">
                  {constituencyLabel}
                </p>
              </div>
            </div>
            <div className="space-y-2">
              <button
                onClick={toggleLanguage}
                className="w-full flex items-center justify-center gap-2 px-3 py-2 text-sm font-medium text-sky-300 hover:bg-sky-500/10 rounded-lg transition-colors"
              >
                <Languages className="h-4 w-4" />
                {isKannada ? 'English' : 'ಕನ್ನಡ'}
              </button>
              <button
                onClick={handleLogout}
                className="w-full flex items-center justify-center gap-2 px-3 py-2 text-sm font-medium text-red-300 hover:bg-red-500/10 rounded-lg transition-colors"
              >
                <LogOut className="h-4 w-4" />
                {t('logout')}
              </button>
            </div>
          </div>
        </div>
      </div>

      {/* Main content */}
      <div className="pl-64">
        <header className="sticky top-0 z-40 border-b border-white/20 bg-white/70 backdrop-blur-xl">
          <div className="mx-auto flex max-w-7xl items-center justify-between px-4 py-4 sm:px-6 lg:px-8">
            <div className="flex items-center gap-4">
              <div className="hidden sm:flex items-center gap-3 rounded-2xl bg-white/60 px-4 py-2 shadow-sm shadow-sky-100">
                <img src={emblem} alt="Karnataka emblem" className="h-10 w-10" />
                <div>
                  <p className="text-xs uppercase tracking-[0.3em] text-slate-500">{t('missionControl')}</p>
                  <p className="text-base font-semibold text-slate-800">{t('smartGovernanceHub')}</p>
                </div>
              </div>
              <div className="hidden lg:flex items-center gap-3 rounded-2xl bg-slate-900 text-slate-100 px-4 py-2 shadow-lg shadow-slate-900/20">
                <Satellite className="h-5 w-5 text-sky-300" />
                <p className="text-sm font-medium">{t('constellationSync')}</p>
              </div>
            </div>

            <div className="flex items-center gap-4">
              <div className="hidden md:flex items-center gap-3 rounded-2xl border border-white/60 bg-white/70 px-3 py-2 shadow-sm">
                <Wifi className="h-4 w-4 text-sky-500" />
                <span className="text-xs font-medium text-slate-600">{t('liveFeedsNominal')}</span>
              </div>
              <button
                type="button"
                className="relative rounded-full border border-white/60 bg-white/80 p-2 text-slate-600 transition hover:text-slate-900"
                aria-label={t('notifications')}
              >
                <Bell className="h-5 w-5" />
                <span className="absolute -right-0.5 -top-0.5 h-2.5 w-2.5 rounded-full bg-rose-500 ring-2 ring-white"></span>
              </button>
              <button
                type="button"
                onClick={toggleAuroraMode}
                className="flex items-center gap-2 rounded-full bg-slate-900 text-slate-100 px-4 py-2 text-sm font-semibold shadow-lg shadow-slate-900/30 transition hover:bg-slate-800"
              >
                {auroraMode ? <MoonStar className="h-4 w-4" /> : <Sun className="h-4 w-4" />}
                {t(auroraMode ? 'auroraMode' : 'luminousMode')}
              </button>
              <div className="flex items-center gap-3 rounded-full border border-white/70 bg-white/80 px-3 py-1.5 shadow">
                <ShieldCheck className="h-5 w-5 text-emerald-500" />
                <div className="leading-tight">
                  <p className="text-xs font-semibold text-slate-600">{t('secureSession')}</p>
                  <p className="text-[10px] uppercase tracking-wide text-emerald-500">{t('multiFactorLocked')}</p>
                </div>
              </div>
              <div className="relative h-12 w-12 overflow-hidden rounded-full border-2 border-sky-400/60 shadow-lg shadow-sky-500/30">
                <img src={profilePhotoUrl} alt="MLA portrait" className="h-full w-full object-cover" />
                <span className="absolute bottom-1 right-1 h-2.5 w-2.5 rounded-full border border-white bg-emerald-400"></span>
              </div>
            </div>
          </div>
        </header>

        <main className="py-10">
          <div className="mx-auto max-w-7xl px-4 sm:px-6 lg:px-8">
            {children}
          </div>
        </main>

        {/* Footer - Developer Credits */}
        <footer className="border-t border-slate-200 bg-white/50 backdrop-blur">
          <div className="mx-auto max-w-7xl px-4 py-4 sm:px-6 lg:px-8">
            <div className="flex flex-col sm:flex-row items-center justify-between gap-2 text-xs text-slate-600">
              <div className="text-center sm:text-left">
                <p className="font-medium">
                  Developed by <span className="text-primary-600">srbhandary</span> • Bytevantage Enterprise Solutions, Mangalore
                </p>
              </div>
              <div className="flex items-center gap-3">
                <a 
                  href="https://www.bytevantage.in" 
                  target="_blank" 
                  rel="noopener noreferrer" 
                  className="text-primary-600 hover:text-primary-700 hover:underline"
                >
                  www.bytevantage.in
                </a>
                <span>•</span>
                <a 
                  href="mailto:srbhandary@bytevantage.in" 
                  className="text-primary-600 hover:text-primary-700 hover:underline"
                >
                  srbhandary@bytevantage.in
                </a>
              </div>
            </div>
          </div>
        </footer>
      </div>

      {/* Session Timeout Warning */}
      <SessionTimeoutWarning />
    </div>
  );
}

export default Layout;
