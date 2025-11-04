import { useState } from 'react';
import { useAuth } from '../contexts/AuthContext';
import { useTranslation } from '../hooks/useTranslation';
import { Link } from 'react-router-dom';
import { useQueryClient } from '@tanstack/react-query';
import { 
  Building2,
  Plus,
  Search,
  Edit2,
  Phone,
  Mail,
  Users,
  TrendingUp,
  Clock,
  CheckCircle
} from 'lucide-react';
import DepartmentCreateModal from '../components/DepartmentCreateModal';

function Departments() {
  const { t } = useTranslation();
  const { user } = useAuth();
  const [searchTerm, setSearchTerm] = useState('');
  const [isCreateModalOpen, setIsCreateModalOpen] = useState(false);
  const queryClient = useQueryClient();

  // Mock data - replace with API call
  const departments = [
    {
      id: '1',
      name: 'Public Works Department (PWD)',
      code: 'PWD',
      contact_phone: '+918242220001',
      contact_email: 'pwd@puttur.gov.in',
      head_name: 'Engineer Ramesh Kumar',
      total_complaints: 45,
      pending: 12,
      resolved: 33,
      avg_resolution_days: 4.2,
      is_active: true,
    },
    {
      id: '2',
      name: 'Water Supply Department',
      code: 'WSD',
      contact_phone: '+918242220002',
      contact_email: 'water@puttur.gov.in',
      head_name: 'Officer Sanjay Rao',
      total_complaints: 32,
      pending: 8,
      resolved: 24,
      avg_resolution_days: 3.5,
      is_active: true,
    },
    {
      id: '3',
      name: 'Electricity Department (MESCOM)',
      code: 'MESCOM',
      contact_phone: '+918242220003',
      contact_email: 'mescom@puttur.gov.in',
      head_name: 'Engineer Prakash Shetty',
      total_complaints: 28,
      pending: 5,
      resolved: 23,
      avg_resolution_days: 2.8,
      is_active: true,
    },
    {
      id: '4',
      name: 'Sanitation & Health',
      code: 'HEALTH',
      contact_phone: '+918242220004',
      contact_email: 'health@puttur.gov.in',
      head_name: 'Dr. Anita Bhat',
      total_complaints: 19,
      pending: 3,
      resolved: 16,
      avg_resolution_days: 3.2,
      is_active: true,
    },
    {
      id: '5',
      name: 'Education Department',
      code: 'EDU',
      contact_phone: '+918242220005',
      contact_email: 'education@puttur.gov.in',
      head_name: 'Principal Mohan Das',
      total_complaints: 15,
      pending: 4,
      resolved: 11,
      avg_resolution_days: 5.1,
      is_active: true,
    },
  ];

  const filteredDepartments = departments.filter(dept =>
    dept.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
    dept.code.toLowerCase().includes(searchTerm.toLowerCase()) ||
    dept.head_name.toLowerCase().includes(searchTerm.toLowerCase())
  );

  const totalStats = {
    departments: departments.length,
    totalComplaints: departments.reduce((sum, d) => sum + d.total_complaints, 0),
    pending: departments.reduce((sum, d) => sum + d.pending, 0),
    resolved: departments.reduce((sum, d) => sum + d.resolved, 0),
  };

  const handleCreateDepartment = async (deptData) => {
    // TODO: Implement actual API call
    console.log('Creating department:', deptData);
    
    // Mock success
    await new Promise(resolve => setTimeout(resolve, 1000));
    
    // Invalidate queries
    queryClient.invalidateQueries(['departments']);
    
    alert('Department created successfully!');
  };

  return (
    <div className="space-y-6">
      <div className="flex flex-col gap-4 sm:flex-row sm:items-end sm:justify-between">
        <div>
          <h1 className="text-2xl font-semibold text-gray-900">
            {t('departmentManagement', 'Department Management')}
          </h1>
          <p className="mt-1 text-sm text-gray-500">
            {t('departments.pageSubtitle', 'Monitor performance and manage department operations')}
          </p>
        </div>
        <button
          type="button"
          onClick={() => setIsCreateModalOpen(true)}
          className="inline-flex items-center justify-center rounded-full bg-primary-600 px-5 py-2 text-sm font-medium text-white shadow-lg shadow-primary-500/30 transition hover:bg-primary-700"
        >
          <Plus className="mr-2 h-4 w-4" />
          {t('departments.addDepartment', 'Add Department')}
        </button>
      </div>

      {/* Statistics */}
      <div className="rounded-2xl border border-primary-100 bg-white/80 p-6 shadow-sm shadow-primary-100/30 backdrop-blur">
        <div className="grid gap-4 sm:grid-cols-2 xl:grid-cols-4">
          <div className="rounded-2xl border border-primary-50 bg-white/90 p-4 shadow-inner shadow-primary-100/20">
            <div className="flex items-center justify-between">
              <p className="text-xs uppercase tracking-wide text-gray-400">Total Departments</p>
              <Building2 className="h-4 w-4 text-primary-500" />
            </div>
            <p className="mt-3 text-2xl font-semibold text-gray-900">{totalStats.departments}</p>
          </div>

          <div className="rounded-2xl border border-primary-50 bg-white/90 p-4 shadow-inner shadow-primary-100/20">
            <div className="flex items-center justify-between">
              <p className="text-xs uppercase tracking-wide text-gray-400">Total Complaints</p>
              <TrendingUp className="h-4 w-4 text-primary-500" />
            </div>
            <p className="mt-3 text-2xl font-semibold text-gray-900">{totalStats.totalComplaints}</p>
          </div>

          <div className="rounded-2xl border border-primary-50 bg-white/90 p-4 shadow-inner shadow-primary-100/20">
            <div className="flex items-center justify-between">
              <p className="text-xs uppercase tracking-wide text-gray-400">Pending</p>
              <Clock className="h-4 w-4 text-primary-500" />
            </div>
            <p className="mt-3 text-2xl font-semibold text-gray-900">{totalStats.pending}</p>
          </div>

          <div className="rounded-2xl border border-primary-50 bg-white/90 p-4 shadow-inner shadow-primary-100/20">
            <div className="flex items-center justify-between">
              <p className="text-xs uppercase tracking-wide text-gray-400">Resolved</p>
              <CheckCircle className="h-4 w-4 text-primary-500" />
            </div>
            <p className="mt-3 text-2xl font-semibold text-gray-900">{totalStats.resolved}</p>
          </div>
        </div>
      </div>

      {/* Search */}
      <div className="rounded-2xl border border-primary-50 bg-white/90 p-6 shadow-sm shadow-primary-100/30 backdrop-blur">
        <div className="relative">
          <Search className="pointer-events-none absolute left-3 top-2.5 h-4 w-4 text-gray-400" />
          <input
            type="text"
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
            placeholder="Search departments by name, code, or head..."
            className="w-full rounded-full border border-gray-200 bg-white py-2 pl-9 pr-4 text-sm focus:border-primary-500 focus:outline-none focus:ring-2 focus:ring-primary-200"
          />
        </div>
      </div>

      {/* Departments Grid */}
      <div className="grid grid-cols-1 gap-6 lg:grid-cols-2">
        {filteredDepartments.map((dept) => {
          const resolutionRate = dept.total_complaints > 0 
            ? Math.round((dept.resolved / dept.total_complaints) * 100) 
            : 0;

          return (
            <div 
              key={dept.id} 
              className="rounded-2xl border border-primary-100 bg-white/80 p-6 shadow-sm shadow-primary-100/40 backdrop-blur transition hover:shadow-lg"
            >
              {/* Header */}
              <div className="mb-4 flex items-start justify-between">
                <div className="flex items-center">
                  <div className="flex h-12 w-12 flex-shrink-0 items-center justify-center rounded-lg bg-primary-100">
                    <Building2 className="h-6 w-6 text-primary-600" />
                  </div>
                  <div className="ml-4">
                    <h3 className="text-lg font-medium text-gray-900">{dept.name}</h3>
                    <p className="text-sm text-gray-500">Code: {dept.code}</p>
                  </div>
                </div>
                <button className="rounded-lg p-2 text-gray-400 transition hover:bg-gray-100 hover:text-gray-600">
                  <Edit2 className="h-5 w-5" />
                </button>
              </div>

              {/* Department Head */}
              <div className="mb-4 border-b border-gray-200 pb-4">
                <div className="mb-2 flex items-center text-sm text-gray-600">
                  <Users className="mr-2 h-4 w-4 text-gray-400" />
                  <span className="font-medium">Head:</span>
                  <span className="ml-2">{dept.head_name}</span>
                </div>
                <div className="mb-1 flex items-center text-sm text-gray-600">
                  <Phone className="mr-2 h-4 w-4 text-gray-400" />
                  <a href={`tel:${dept.contact_phone}`} className="text-primary-600 hover:text-primary-700">
                    {dept.contact_phone}
                  </a>
                </div>
                <div className="flex items-center text-sm text-gray-600">
                  <Mail className="mr-2 h-4 w-4 text-gray-400" />
                  <a href={`mailto:${dept.contact_email}`} className="text-primary-600 hover:text-primary-700">
                    {dept.contact_email}
                  </a>
                </div>
              </div>

              {/* Statistics */}
              <div className="mb-4 grid grid-cols-2 gap-4">
                <div>
                  <p className="text-xs text-gray-500">Total Complaints</p>
                  <p className="text-lg font-semibold text-gray-900">{dept.total_complaints}</p>
                </div>
                <div>
                  <p className="text-xs text-gray-500">Pending</p>
                  <p className="text-lg font-semibold text-yellow-600">{dept.pending}</p>
                </div>
                <div>
                  <p className="text-xs text-gray-500">Resolved</p>
                  <p className="text-lg font-semibold text-green-600">{dept.resolved}</p>
                </div>
                <div>
                  <p className="text-xs text-gray-500">Avg. Resolution</p>
                  <p className="text-lg font-semibold text-gray-900">{dept.avg_resolution_days}d</p>
                </div>
              </div>

              {/* Resolution Rate */}
              <div className="mb-4">
                <div className="mb-1 flex items-center justify-between">
                  <span className="text-sm font-medium text-gray-700">Resolution Rate</span>
                  <span className="text-sm font-semibold text-gray-900">{resolutionRate}%</span>
                </div>
                <div className="h-2 w-full rounded-full bg-gray-200">
                  <div
                    className={`h-2 rounded-full ${
                      resolutionRate >= 80 ? 'bg-green-500' :
                      resolutionRate >= 60 ? 'bg-yellow-500' :
                      'bg-red-500'
                    }`}
                    style={{ width: `${resolutionRate}%` }}
                  ></div>
                </div>
              </div>

              {/* Actions */}
              <div className="flex gap-2">
                <Link
                  to={`/departments/${dept.id}`}
                  className="flex-1 rounded-lg bg-primary-50 px-4 py-2 text-center text-sm font-medium text-primary-700 hover:bg-primary-100"
                >
                  View Details
                </Link>
                <Link
                  to={`/complaints?department=${dept.id}`}
                  className="flex-1 rounded-lg bg-gray-50 px-4 py-2 text-center text-sm font-medium text-gray-700 hover:bg-gray-100"
                >
                  View Complaints
                </Link>
              </div>
            </div>
          );
        })}
      </div>

      {/* Performance Leaderboard */}
      <div className="rounded-2xl border border-primary-100 bg-white/80 p-6 shadow-sm shadow-primary-100/40 backdrop-blur">
        <h2 className="mb-4 text-lg font-medium text-gray-900">Performance Leaderboard</h2>
        <div className="space-y-3">
          {[...departments]
            .sort((a, b) => {
              const rateA = a.total_complaints > 0 ? (a.resolved / a.total_complaints) : 0;
              const rateB = b.total_complaints > 0 ? (b.resolved / b.total_complaints) : 0;
              return rateB - rateA;
            })
            .slice(0, 5)
            .map((dept, index) => {
              const resolutionRate = dept.total_complaints > 0 
                ? Math.round((dept.resolved / dept.total_complaints) * 100) 
                : 0;

              return (
                <div key={dept.id} className="flex items-center rounded-lg bg-gray-50 p-3">
                  <div className="flex h-8 w-8 flex-shrink-0 items-center justify-center rounded-full bg-primary-100">
                    <span className="font-semibold text-primary-700">{index + 1}</span>
                  </div>
                  <div className="ml-4 flex-1">
                    <p className="text-sm font-medium text-gray-900">{dept.name}</p>
                    <p className="text-xs text-gray-500">
                      {dept.resolved}/{dept.total_complaints} resolved • Avg {dept.avg_resolution_days} days
                    </p>
                  </div>
                  <div className="ml-4">
                    <span className={`text-lg font-bold ${
                      resolutionRate >= 80 ? 'text-green-600' :
                      resolutionRate >= 60 ? 'text-yellow-600' :
                      'text-red-600'
                    }`}>
                      {resolutionRate}%
                    </span>
                  </div>
                </div>
              );
            })}
        </div>
      </div>

      {/* Department Create Modal */}
      <DepartmentCreateModal
        isOpen={isCreateModalOpen}
        onClose={() => setIsCreateModalOpen(false)}
        onCreate={handleCreateDepartment}
      />
    </div>
  );
}

export default Departments;
