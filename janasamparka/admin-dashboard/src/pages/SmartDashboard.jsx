import { useAuth } from '../contexts/AuthContext';
import AdminDashboard from './Dashboard';
import CitizenDashboard from './citizen/Dashboard';
import OfficerDashboard from './officer/Dashboard';
import ModeratorDashboard from './moderator/Dashboard';
import AuditorDashboard from './auditor/Dashboard';
import PDODashboard from './pdo/Dashboard';
import VillageAccountantDashboard from './villageAccountant/Dashboard';
import TalukPanchayatOfficerDashboard from './talukPanchayatOfficer/Dashboard';
import { Users } from 'lucide-react';

/**
 * SmartDashboard - Routes users to role-specific dashboards
 * 
 * This component acts as a smart router that displays the appropriate
 * dashboard based on the authenticated user's role.
 */
export default function SmartDashboard() {
  const { user, loading, isAuthenticated } = useAuth();

  // Loading state
  if (loading) {
    return (
      <div className="flex h-screen items-center justify-center">
        <div className="text-center">
          <div className="inline-block h-12 w-12 animate-spin rounded-full border-4 border-sky-500 border-t-transparent"></div>
          <p className="mt-4 text-sm text-slate-600">Loading dashboard...</p>
        </div>
      </div>
    );
  }

  // Not authenticated
  if (!isAuthenticated || !user) {
    return (
      <div className="flex h-screen items-center justify-center">
        <div className="rounded-xl border border-amber-200 bg-amber-50 p-8 text-center">
          <Users className="mx-auto h-12 w-12 text-amber-600" />
          <p className="mt-4 text-lg font-semibold text-amber-900">Authentication Required</p>
          <p className="mt-2 text-sm text-amber-700">Please log in to access your dashboard</p>
        </div>
      </div>
    );
  }

  // Debug: Log user role for troubleshooting
  console.log('SmartDashboard rendering for role:', user.role);

  // Route to role-specific dashboard
  switch (user.role) {
    case 'citizen':
      return <CitizenDashboard />;
      
    case 'department_officer':
      return <OfficerDashboard />;
      
    case 'moderator':
      return <ModeratorDashboard />;
      
    case 'auditor':
      return <AuditorDashboard />;
    
    // Panchayat Raj Roles
    case 'pdo':
      return <PDODashboard />;
    
    case 'village_accountant':
      return <VillageAccountantDashboard />;
    
    case 'taluk_panchayat_officer':
    case 'tp_president':
      return <TalukPanchayatOfficerDashboard />;
    
    case 'zilla_panchayat_officer':
    case 'zp_president':
      // ZP officers and presidents can use admin dashboard with district-wide view
      return <AdminDashboard />;
    
    case 'gp_president':
      // GP Presidents see same dashboard as PDO (village level)
      return <PDODashboard />;
      
    case 'mla':
    case 'admin':
      // MLA and Admin use the comprehensive mission control dashboard
      return <AdminDashboard />;
      
    default:
      return (
        <div className="flex h-screen items-center justify-center">
          <div className="rounded-xl border border-red-200 bg-red-50 p-8 text-center max-w-md">
            <div className="mx-auto flex h-16 w-16 items-center justify-center rounded-full bg-red-100">
              <Users className="h-8 w-8 text-red-600" />
            </div>
            <p className="mt-4 text-lg font-semibold text-red-900">Unknown User Role</p>
            <p className="mt-2 text-sm text-red-700">
              Role <span className="font-mono font-semibold">{user.role}</span> is not recognized by the system.
            </p>
            <p className="mt-4 text-xs text-red-600">Please contact your system administrator for assistance.</p>
          </div>
        </div>
      );
  }
}
