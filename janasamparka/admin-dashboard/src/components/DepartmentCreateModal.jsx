import { useState, useEffect } from 'react';
import { useQuery } from '@tanstack/react-query';
import { X, AlertCircle } from 'lucide-react';
import api from '../services/api';

function DepartmentCreateModal({ isOpen, onClose, onCreate, department = null }) {
  const isEdit = !!department;
  
  const [formData, setFormData] = useState({
    name: department?.name || '',
    code: department?.code || '',
    constituency_id: department?.constituency_id || '',
    taluk_panchayat_id: department?.taluk_panchayat_id || '',
    contact_phone: department?.contact_phone || '',
    contact_email: department?.contact_email || '',
    head_name: department?.head_name || '',
    office_address: department?.office_address || '',
    is_active: department?.is_active ?? true,
  });

  const [loading, setLoading] = useState(false);
  const [errors, setErrors] = useState({});

  // Fetch constituencies
  const { data: constituenciesData } = useQuery({
    queryKey: ['constituencies'],
    queryFn: async () => {
      const response = await api.get('/api/constituencies/');
      return response.data;
    },
    enabled: isOpen,
  });

  const constituencies = Array.isArray(constituenciesData?.constituencies)
    ? constituenciesData.constituencies
    : Array.isArray(constituenciesData?.items)
    ? constituenciesData.items
    : Array.isArray(constituenciesData)
    ? constituenciesData
    : [];

  // Fetch taluk panchayats for selected constituency
  const { data: taluksData } = useQuery({
    queryKey: ['taluk-panchayats', formData.constituency_id],
    queryFn: async () => {
      const response = await api.get(
        `/api/panchayats/taluk?constituency_id=${formData.constituency_id}`
      );
      return response.data;
    },
    enabled: isOpen && !!formData.constituency_id,
  });

  const talukPanchayats = Array.isArray(taluksData?.taluk_panchayats)
    ? taluksData.taluk_panchayats
    : Array.isArray(taluksData?.items)
    ? taluksData.items
    : Array.isArray(taluksData)
    ? taluksData
    : [];

  // Reset form when modal closes or department changes
  useEffect(() => {
    if (isOpen && department) {
      // Editing mode - populate form with department data
      setFormData({
        name: department.name || '',
        code: department.code || '',
        constituency_id: department.constituency_id || '',
        taluk_panchayat_id: department.taluk_panchayat_id || '',
        contact_phone: department.contact_phone || '',
        contact_email: department.contact_email || '',
        head_name: department.head_name || '',
        office_address: department.office_address || '',
        is_active: department.is_active ?? true,
      });
    } else if (!isOpen) {
      // Modal closed - reset form
      setFormData({
        name: '',
        code: '',
        constituency_id: '',
        taluk_panchayat_id: '',
        contact_phone: '',
        contact_email: '',
        head_name: '',
        office_address: '',
        is_active: true,
      });
      setErrors({});
    }
  }, [isOpen, department]);

  if (!isOpen) return null;

  const validateForm = () => {
    const newErrors = {};

    if (!formData.name.trim()) {
      newErrors.name = 'Department name is required';
    }

    if (!formData.code.trim()) {
      newErrors.code = 'Department code is required';
    }

    if (!formData.constituency_id) {
      newErrors.constituency_id = 'Constituency is required';
    }

    if (!formData.contact_phone.trim()) {
      newErrors.contact_phone = 'Contact phone is required';
    } else if (!/^\+?\d{10,}$/.test(formData.contact_phone.replace(/\s/g, ''))) {
      newErrors.contact_phone = 'Invalid phone number format';
    }

    if (formData.contact_email && !/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(formData.contact_email)) {
      newErrors.contact_email = 'Invalid email format';
    }

    setErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    
    if (!validateForm()) {
      return;
    }

    setLoading(true);
    
    try {
      await onCreate(formData);
      
      // Reset form
      setFormData({
        name: '',
        code: '',
        constituency_id: '',
        taluk_panchayat_id: '',
        contact_phone: '',
        contact_email: '',
        head_name: '',
        office_address: '',
        is_active: true,
      });
      setErrors({});
      
      onClose();
    } catch (error) {
      alert(`Failed to ${isEdit ? 'update' : 'create'} department: ` + error.message);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="fixed inset-0 z-50 overflow-y-auto" aria-labelledby="modal-title" role="dialog" aria-modal="true">
      {/* Backdrop */}
      <div className="flex items-end justify-center min-h-screen pt-4 px-4 pb-20 text-center sm:block sm:p-0">
        <div 
          className="fixed inset-0 bg-gray-500 bg-opacity-75 transition-opacity" 
          aria-hidden="true"
          onClick={onClose}
        ></div>

        {/* Center modal */}
        <span className="hidden sm:inline-block sm:align-middle sm:h-screen" aria-hidden="true">&#8203;</span>

        <div className="inline-block align-bottom bg-white rounded-lg px-4 pt-5 pb-4 text-left overflow-hidden shadow-xl transform transition-all sm:my-8 sm:align-middle sm:max-w-lg sm:w-full sm:p-6">
          {/* Header */}
          <div className="flex items-center justify-between mb-6">
            <h3 className="text-xl font-medium text-gray-900" id="modal-title">
              {isEdit ? 'Edit Department' : 'Add New Department'}
            </h3>
            <button
              onClick={onClose}
              className="text-gray-400 hover:text-gray-500 focus:outline-none"
            >
              <X className="h-6 w-6" />
            </button>
          </div>

          <form onSubmit={handleSubmit} className="space-y-5">
            {/* Department Name */}
            <div>
              <label htmlFor="name" className="block text-sm font-medium text-gray-700 mb-2">
                Department Name <span className="text-red-500">*</span>
              </label>
              <input
                type="text"
                id="name"
                value={formData.name}
                onChange={(e) => setFormData({ ...formData, name: e.target.value })}
                placeholder="e.g., Public Works Department"
                className={`w-full px-4 py-2 border rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent ${
                  errors.name ? 'border-red-500' : 'border-gray-300'
                }`}
              />
              {errors.name && (
                <p className="mt-1 text-sm text-red-500">{errors.name}</p>
              )}
            </div>

            {/* Department Code */}
            <div>
              <label htmlFor="code" className="block text-sm font-medium text-gray-700 mb-2">
                Department Code <span className="text-red-500">*</span>
              </label>
              <input
                type="text"
                id="code"
                value={formData.code}
                onChange={(e) => setFormData({ ...formData, code: e.target.value.toUpperCase() })}
                placeholder="e.g., PWD"
                className={`w-full px-4 py-2 border rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent ${
                  errors.code ? 'border-red-500' : 'border-gray-300'
                }`}
              />
              {errors.code && (
                <p className="mt-1 text-sm text-red-500">{errors.code}</p>
              )}
            </div>

            {/* Constituency */}
            <div>
              <label htmlFor="constituency_id" className="block text-sm font-medium text-gray-700 mb-2">
                Constituency <span className="text-red-500">*</span>
              </label>
              <select
                id="constituency_id"
                value={formData.constituency_id}
                onChange={(e) =>
                  setFormData({
                    ...formData,
                    constituency_id: e.target.value,
                    taluk_panchayat_id: '', // Reset taluk when constituency changes
                  })
                }
                className={`w-full px-4 py-2 border rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent ${
                  errors.constituency_id ? 'border-red-500' : 'border-gray-300'
                }`}
              >
                <option value="">-- Select Constituency --</option>
                {constituencies.map((constituency) => (
                  <option key={constituency.id} value={constituency.id}>
                    {constituency.name}
                  </option>
                ))}
              </select>
              {errors.constituency_id && (
                <p className="mt-1 text-sm text-red-500">{errors.constituency_id}</p>
              )}
            </div>

            {/* Taluk Panchayat (Optional) */}
            {formData.constituency_id && talukPanchayats.length > 0 && (
              <div>
                <label htmlFor="taluk_panchayat_id" className="block text-sm font-medium text-gray-700 mb-2">
                  Taluk Panchayat (Optional)
                </label>
                <select
                  id="taluk_panchayat_id"
                  value={formData.taluk_panchayat_id}
                  onChange={(e) =>
                    setFormData({ ...formData, taluk_panchayat_id: e.target.value })
                  }
                  className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent"
                >
                  <option value="">-- All Taluks (Constituency Level) --</option>
                  {talukPanchayats.map((taluk) => (
                    <option key={taluk.id} value={taluk.id}>
                      {taluk.name}
                    </option>
                  ))}
                </select>
                <p className="mt-1 text-xs text-gray-500">
                  Leave empty if department serves the entire constituency
                </p>
              </div>
            )}

            {/* Department Head */}
            <div>
              <label htmlFor="head_name" className="block text-sm font-medium text-gray-700 mb-2">
                Department Head
              </label>
              <input
                type="text"
                id="head_name"
                value={formData.head_name}
                onChange={(e) => setFormData({ ...formData, head_name: e.target.value })}
                placeholder="e.g., Engineer Ramesh Kumar"
                className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent"
              />
            </div>

            {/* Contact Phone */}
            <div>
              <label htmlFor="contact_phone" className="block text-sm font-medium text-gray-700 mb-2">
                Contact Phone <span className="text-red-500">*</span>
              </label>
              <input
                type="tel"
                id="contact_phone"
                value={formData.contact_phone}
                onChange={(e) => setFormData({ ...formData, contact_phone: e.target.value })}
                placeholder="+91 82422 20001"
                className={`w-full px-4 py-2 border rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent ${
                  errors.contact_phone ? 'border-red-500' : 'border-gray-300'
                }`}
              />
              {errors.contact_phone && (
                <p className="mt-1 text-sm text-red-500">{errors.contact_phone}</p>
              )}
            </div>

            {/* Contact Email */}
            <div>
              <label htmlFor="contact_email" className="block text-sm font-medium text-gray-700 mb-2">
                Contact Email
              </label>
              <input
                type="email"
                id="contact_email"
                value={formData.contact_email}
                onChange={(e) => setFormData({ ...formData, contact_email: e.target.value })}
                placeholder="dept@example.com"
                className={`w-full px-4 py-2 border rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent ${
                  errors.contact_email ? 'border-red-500' : 'border-gray-300'
                }`}
              />
              {errors.contact_email && (
                <p className="mt-1 text-sm text-red-500">{errors.contact_email}</p>
              )}
            </div>

            {/* Office Address */}
            <div>
              <label htmlFor="office_address" className="block text-sm font-medium text-gray-700 mb-2">
                Office Address
              </label>
              <textarea
                id="office_address"
                value={formData.office_address}
                onChange={(e) => setFormData({ ...formData, office_address: e.target.value })}
                placeholder="Department office location"
                rows="2"
                className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent"
              />
            </div>

            {/* Status */}
            <div>
              <label className="flex items-center">
                <input
                  type="checkbox"
                  checked={formData.is_active}
                  onChange={(e) => setFormData({ ...formData, is_active: e.target.checked })}
                  className="h-4 w-4 text-primary-600 focus:ring-primary-500 border-gray-300 rounded"
                />
                <span className="ml-2 text-sm text-gray-700">Active Department</span>
              </label>
            </div>

            {/* Info Message */}
            <div className="p-4 bg-blue-50 border border-blue-200 rounded-lg">
              <div className="flex items-start">
                <AlertCircle className="h-5 w-5 text-blue-600 mr-2 mt-0.5" />
                <p className="text-sm text-blue-800">
                  Department will be available for complaint assignment once created.
                </p>
              </div>
            </div>

            {/* Actions */}
            <div className="flex justify-end space-x-3 pt-4 border-t">
              <button
                type="button"
                onClick={onClose}
                className="px-4 py-2 border border-gray-300 rounded-lg text-gray-700 hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-primary-500"
              >
                Cancel
              </button>
              <button
                type="submit"
                disabled={loading}
                className="px-4 py-2 bg-primary-600 text-white rounded-lg hover:bg-primary-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-primary-500 disabled:opacity-50 disabled:cursor-not-allowed flex items-center"
              >
                {loading ? (
                  <>
                    <svg className="animate-spin -ml-1 mr-2 h-4 w-4 text-white" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                      <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                      <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                    </svg>
                    {isEdit ? 'Updating...' : 'Creating...'}
                  </>
                ) : (
                  <>{isEdit ? 'Update Department' : 'Create Department'}</>
                )}
              </button>
            </div>
          </form>
        </div>
      </div>
    </div>
  );
}

export default DepartmentCreateModal;
