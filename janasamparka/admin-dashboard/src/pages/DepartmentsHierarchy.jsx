import { useState } from 'react';
import { useQuery, useQueryClient, useMutation } from '@tanstack/react-query';
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
  CheckCircle,
  Trash2,
} from 'lucide-react';
import { useTranslation } from '../hooks/useTranslation';
import { Link } from 'react-router-dom';
import api from '../services/api';
import DepartmentCreateModal from '../components/DepartmentCreateModal';

function DepartmentsHierarchy() {
  const { t } = useTranslation();
  const queryClient = useQueryClient();
  const [searchTerm, setSearchTerm] = useState('');
  const [isCreateModalOpen, setIsCreateModalOpen] = useState(false);
  const [editingDepartment, setEditingDepartment] = useState(null);
  const [deletingDepartment, setDeletingDepartment] = useState(null);

  // Fetch departments
  const { data: departmentsData, isLoading } = useQuery({
    queryKey: ['departments'],
    queryFn: async () => {
      const response = await api.get('/api/departments/?is_active=true&limit=1000');
      return response.data;
    },
    retry: false,
  });

  // Extract departments array from response
  const departments = Array.isArray(departmentsData?.items)
    ? departmentsData.items
    : Array.isArray(departmentsData?.departments)
    ? departmentsData.departments
    : Array.isArray(departmentsData)
    ? departmentsData
    : [];

  const filteredDepartments = departments.filter(
    (dept) =>
      dept.name?.toLowerCase().includes(searchTerm.toLowerCase()) ||
      dept.code?.toLowerCase().includes(searchTerm.toLowerCase()) ||
      dept.head_name?.toLowerCase().includes(searchTerm.toLowerCase())
  );

  const totalStats = {
    departments: departments.length,
    totalComplaints: departments.reduce((sum, d) => sum + (d.total_complaints || 0), 0),
    pending: departments.reduce((sum, d) => sum + (d.pending || 0), 0),
    resolved: departments.reduce((sum, d) => sum + (d.resolved || 0), 0),
  };

  const handleCreateDepartment = async (deptData) => {
    try {
      if (editingDepartment) {
        await api.put(`/api/departments/${editingDepartment.id}/`, deptData);
        alert('Department updated successfully!');
      } else {
        await api.post('/api/departments/', deptData);
        alert('Department created successfully!');
      }
      queryClient.invalidateQueries(['departments']);
      setEditingDepartment(null);
    } catch (error) {
      console.error('Failed to save department:', error);
      throw error;
    }
  };

  // Delete department mutation
  const deleteMutation = useMutation({
    mutationFn: async (departmentId) => {
      await api.delete(`/api/departments/${departmentId}/`);
    },
    onSuccess: () => {
      queryClient.invalidateQueries(['departments']);
      alert('Department deleted successfully!');
      setDeletingDepartment(null);
    },
    onError: (error) => {
      console.error('Failed to delete department:', error);
      alert('Failed to delete department: ' + (error.response?.data?.detail || error.message));
      setDeletingDepartment(null);
    },
  });

  const handleEditDepartment = (dept) => {
    setEditingDepartment(dept);
    setIsCreateModalOpen(true);
  };

  const handleDeleteDepartment = (dept) => {
    setDeletingDepartment(dept);
  };

  const confirmDelete = () => {
    if (deletingDepartment) {
      deleteMutation.mutate(deletingDepartment.id);
    }
  };

  const handleCloseModal = () => {
    setIsCreateModalOpen(false);
    setEditingDepartment(null);
  };

  if (isLoading) {
    return (
      <div className="flex h-64 items-center justify-center">
        <div className="text-center">
          <div className="mx-auto h-12 w-12 animate-spin rounded-full border-2 border-primary-500 border-t-transparent" />
          <p className="mt-4 text-sm text-gray-500">Loading departments…</p>
        </div>
      </div>
    );
  }

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
                <button 
                  onClick={() => handleEditDepartment(dept)}
                  className="rounded-lg p-2 text-gray-400 transition hover:bg-gray-100 hover:text-gray-600"
                  title="Edit department"
                >
                  <Edit2 className="h-5 w-5" />
                </button>
              </div>

              {/* Department Head */}
              <div className="mb-4 border-b border-gray-200 pb-4">
                <div className="mb-2 flex items-center text-sm text-gray-600">
                  <Users className="mr-2 h-4 w-4 text-gray-400" />
                  <span className="font-medium">Head:</span>
                  <span className="ml-2">{dept.head_name || 'Not assigned'}</span>
                </div>
                {dept.constituency_name && (
                  <div className="mb-1 flex items-center text-sm text-gray-600">
                    <Building2 className="mr-2 h-4 w-4 text-gray-400" />
                    <span className="font-medium">Constituency:</span>
                    <span className="ml-2">{dept.constituency_name}</span>
                  </div>
                )}
                {dept.taluk_panchayat_name && (
                  <div className="mb-1 flex items-center text-sm text-gray-600">
                    <Building2 className="mr-2 h-4 w-4 text-gray-400" />
                    <span className="font-medium">Taluk:</span>
                    <span className="ml-2">{dept.taluk_panchayat_name}</span>
                  </div>
                )}
                {dept.contact_phone && (
                  <div className="mb-1 flex items-center text-sm text-gray-600">
                    <Phone className="mr-2 h-4 w-4 text-gray-400" />
                    <a href={`tel:${dept.contact_phone}`} className="text-primary-600 hover:text-primary-700">
                      {dept.contact_phone}
                    </a>
                  </div>
                )}
                {dept.contact_email && (
                  <div className="flex items-center text-sm text-gray-600">
                    <Mail className="mr-2 h-4 w-4 text-gray-400" />
                    <a href={`mailto:${dept.contact_email}`} className="text-primary-600 hover:text-primary-700">
                      {dept.contact_email}
                    </a>
                  </div>
                )}
              </div>

              {/* Statistics */}
              <div className="mb-4 grid grid-cols-2 gap-4">
                <div>
                  <p className="text-xs text-gray-500">Total Complaints</p>
                  <p className="text-lg font-semibold text-gray-900">{dept.total_complaints || 0}</p>
                </div>
                <div>
                  <p className="text-xs text-gray-500">Pending</p>
                  <p className="text-lg font-semibold text-yellow-600">{dept.pending || 0}</p>
                </div>
                <div>
                  <p className="text-xs text-gray-500">Resolved</p>
                  <p className="text-lg font-semibold text-green-600">{dept.resolved || 0}</p>
                </div>
                <div>
                  <p className="text-xs text-gray-500">Avg. Resolution</p>
                  <p className="text-lg font-semibold text-gray-900">{dept.avg_resolution_days || 0}d</p>
                </div>
              </div>

              {/* Resolution Rate */}
              {dept.total_complaints > 0 && (
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
              )}

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
                <button
                  onClick={() => handleDeleteDepartment(dept)}
                  className="rounded-lg bg-red-50 px-3 py-2 text-center text-sm font-medium text-red-700 hover:bg-red-100"
                  title="Delete department"
                >
                  <Trash2 className="h-4 w-4" />
                </button>
              </div>
            </div>
          );
        })}
      </div>

      {filteredDepartments.length === 0 && (
        <div className="rounded-2xl border border-dashed border-gray-300 bg-white p-12 text-center">
          <Building2 className="mx-auto h-12 w-12 text-gray-400" />
          <h3 className="mt-4 text-lg font-medium text-gray-900">No departments found</h3>
          <p className="mt-2 text-sm text-gray-500">
            {searchTerm ? 'Try adjusting your search terms' : 'Get started by creating a new department'}
          </p>
        </div>
      )}

      {/* Performance Leaderboard */}
      {filteredDepartments.length > 0 && (
        <div className="rounded-2xl border border-primary-100 bg-white/80 p-6 shadow-sm shadow-primary-100/40 backdrop-blur">
          <h2 className="mb-4 text-lg font-medium text-gray-900">Performance Leaderboard</h2>
          <div className="space-y-3">
            {[...filteredDepartments]
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
                        {dept.resolved}/{dept.total_complaints} resolved • Avg {dept.avg_resolution_days || 0} days
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
      )}

      {/* Department Create/Edit Modal */}
      <DepartmentCreateModal
        isOpen={isCreateModalOpen}
        onClose={handleCloseModal}
        onCreate={handleCreateDepartment}
        department={editingDepartment}
      />

      {/* Delete Confirmation Dialog */}
      {deletingDepartment && (
        <div className="fixed inset-0 z-50 overflow-y-auto" role="dialog" aria-modal="true">
          <div className="flex items-end justify-center min-h-screen pt-4 px-4 pb-20 text-center sm:block sm:p-0">
            <div
              className="fixed inset-0 bg-gray-500 bg-opacity-75 transition-opacity"
              onClick={() => setDeletingDepartment(null)}
            ></div>

            <span className="hidden sm:inline-block sm:align-middle sm:h-screen">&#8203;</span>

            <div className="inline-block align-bottom bg-white rounded-lg px-4 pt-5 pb-4 text-left overflow-hidden shadow-xl transform transition-all sm:my-8 sm:align-middle sm:max-w-lg sm:w-full sm:p-6">
              <div className="sm:flex sm:items-start">
                <div className="mx-auto flex-shrink-0 flex items-center justify-center h-12 w-12 rounded-full bg-red-100 sm:mx-0 sm:h-10 sm:w-10">
                  <Trash2 className="h-6 w-6 text-red-600" />
                </div>
                <div className="mt-3 text-center sm:mt-0 sm:ml-4 sm:text-left">
                  <h3 className="text-lg leading-6 font-medium text-gray-900">
                    Delete Department
                  </h3>
                  <div className="mt-2">
                    <p className="text-sm text-gray-500">
                      Are you sure you want to delete{' '}
                      <span className="font-semibold">{deletingDepartment.name}</span>? This action
                      cannot be undone.
                    </p>
                  </div>
                </div>
              </div>
              <div className="mt-5 sm:mt-4 sm:flex sm:flex-row-reverse">
                <button
                  type="button"
                  onClick={confirmDelete}
                  disabled={deleteMutation.isPending}
                  className="w-full inline-flex justify-center rounded-lg border border-transparent shadow-sm px-4 py-2 bg-red-600 text-base font-medium text-white hover:bg-red-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-red-500 sm:ml-3 sm:w-auto sm:text-sm disabled:opacity-50 disabled:cursor-not-allowed"
                >
                  {deleteMutation.isPending ? 'Deleting...' : 'Delete'}
                </button>
                <button
                  type="button"
                  onClick={() => setDeletingDepartment(null)}
                  disabled={deleteMutation.isPending}
                  className="mt-3 w-full inline-flex justify-center rounded-lg border border-gray-300 shadow-sm px-4 py-2 bg-white text-base font-medium text-gray-700 hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-primary-500 sm:mt-0 sm:w-auto sm:text-sm"
                >
                  Cancel
                </button>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}

export default DepartmentsHierarchy;
