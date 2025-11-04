import { useState } from 'react';
import { X, AlertCircle } from 'lucide-react';

function ConstituencyCreateModal({ isOpen, onClose, onCreate, constituency = null }) {
  const isEdit = !!constituency;
  
  const [formData, setFormData] = useState({
    name: constituency?.name || '',
    mla_name: constituency?.mla_name || '',
    mla_phone: constituency?.mla_phone || '',
    district: constituency?.district || '',
    state: constituency?.state || 'Karnataka',
    total_wards: constituency?.total_wards || '',
    total_population: constituency?.total_population || '',
    area_sq_km: constituency?.area_sq_km || '',
  });

  const [loading, setLoading] = useState(false);
  const [errors, setErrors] = useState({});

  if (!isOpen) return null;

  const validateForm = () => {
    const newErrors = {};

    if (!formData.name.trim()) {
      newErrors.name = 'Constituency name is required';
    }

    if (!formData.district.trim()) {
      newErrors.district = 'District is required';
    }

    if (formData.mla_phone && !/^\+?\d{10,}$/.test(formData.mla_phone.replace(/\s/g, ''))) {
      newErrors.mla_phone = 'Invalid phone number format';
    }

    if (formData.total_wards && isNaN(parseInt(formData.total_wards))) {
      newErrors.total_wards = 'Must be a number';
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
        mla_name: '',
        mla_phone: '',
        district: '',
        state: 'Karnataka',
        total_wards: '',
        total_population: '',
        area_sq_km: '',
      });
      setErrors({});
      
      onClose();
    } catch (error) {
      alert(`Failed to ${isEdit ? 'update' : 'create'} constituency: ` + error.message);
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

        <div className="inline-block align-bottom bg-white rounded-lg px-4 pt-5 pb-4 text-left overflow-hidden shadow-xl transform transition-all sm:my-8 sm:align-middle sm:max-w-2xl sm:w-full sm:p-6">
          {/* Header */}
          <div className="flex items-center justify-between mb-6">
            <h3 className="text-xl font-medium text-gray-900" id="modal-title">
              {isEdit ? 'Edit Constituency' : 'Add New Constituency'}
            </h3>
            <button
              onClick={onClose}
              className="text-gray-400 hover:text-gray-500 focus:outline-none"
            >
              <X className="h-6 w-6" />
            </button>
          </div>

          <form onSubmit={handleSubmit} className="space-y-5">
            {/* Basic Info */}
            <div className="grid grid-cols-2 gap-4">
              <div>
                <label htmlFor="name" className="block text-sm font-medium text-gray-700 mb-2">
                  Constituency Name <span className="text-red-500">*</span>
                </label>
                <input
                  type="text"
                  id="name"
                  value={formData.name}
                  onChange={(e) => setFormData({ ...formData, name: e.target.value })}
                  placeholder="e.g., Puttur"
                  className={`w-full px-4 py-2 border rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent ${
                    errors.name ? 'border-red-500' : 'border-gray-300'
                  }`}
                />
                {errors.name && (
                  <p className="mt-1 text-sm text-red-500">{errors.name}</p>
                )}
              </div>

              <div>
                <label htmlFor="district" className="block text-sm font-medium text-gray-700 mb-2">
                  District <span className="text-red-500">*</span>
                </label>
                <input
                  type="text"
                  id="district"
                  value={formData.district}
                  onChange={(e) => setFormData({ ...formData, district: e.target.value })}
                  placeholder="e.g., Dakshina Kannada"
                  className={`w-full px-4 py-2 border rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent ${
                    errors.district ? 'border-red-500' : 'border-gray-300'
                  }`}
                />
                {errors.district && (
                  <p className="mt-1 text-sm text-red-500">{errors.district}</p>
                )}
              </div>
            </div>

            {/* State */}
            <div>
              <label htmlFor="state" className="block text-sm font-medium text-gray-700 mb-2">
                State
              </label>
              <input
                type="text"
                id="state"
                value={formData.state}
                onChange={(e) => setFormData({ ...formData, state: e.target.value })}
                placeholder="Karnataka"
                className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent"
              />
            </div>

            {/* MLA Info */}
            <div>
              <h4 className="text-sm font-medium text-gray-900 mb-3">MLA Information (Optional)</h4>
              <div className="grid grid-cols-2 gap-4">
                <div>
                  <label htmlFor="mla_name" className="block text-sm font-medium text-gray-700 mb-2">
                    MLA Name
                  </label>
                  <input
                    type="text"
                    id="mla_name"
                    value={formData.mla_name}
                    onChange={(e) => setFormData({ ...formData, mla_name: e.target.value })}
                    placeholder="e.g., Ashok Kumar Rai"
                    className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent"
                  />
                </div>

                <div>
                  <label htmlFor="mla_phone" className="block text-sm font-medium text-gray-700 mb-2">
                    MLA Phone
                  </label>
                  <input
                    type="tel"
                    id="mla_phone"
                    value={formData.mla_phone}
                    onChange={(e) => setFormData({ ...formData, mla_phone: e.target.value })}
                    placeholder="+91 98765 43210"
                    className={`w-full px-4 py-2 border rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent ${
                      errors.mla_phone ? 'border-red-500' : 'border-gray-300'
                    }`}
                  />
                  {errors.mla_phone && (
                    <p className="mt-1 text-sm text-red-500">{errors.mla_phone}</p>
                  )}
                </div>
              </div>
            </div>

            {/* Demographics */}
            <div>
              <h4 className="text-sm font-medium text-gray-900 mb-3">Demographics (Optional)</h4>
              <div className="grid grid-cols-3 gap-4">
                <div>
                  <label htmlFor="total_wards" className="block text-sm font-medium text-gray-700 mb-2">
                    Total Wards
                  </label>
                  <input
                    type="number"
                    id="total_wards"
                    value={formData.total_wards}
                    onChange={(e) => setFormData({ ...formData, total_wards: e.target.value })}
                    placeholder="e.g., 35"
                    className={`w-full px-4 py-2 border rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent ${
                      errors.total_wards ? 'border-red-500' : 'border-gray-300'
                    }`}
                  />
                  {errors.total_wards && (
                    <p className="mt-1 text-sm text-red-500">{errors.total_wards}</p>
                  )}
                </div>

                <div>
                  <label htmlFor="total_population" className="block text-sm font-medium text-gray-700 mb-2">
                    Population
                  </label>
                  <input
                    type="number"
                    id="total_population"
                    value={formData.total_population}
                    onChange={(e) => setFormData({ ...formData, total_population: e.target.value })}
                    placeholder="e.g., 487500"
                    className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent"
                  />
                </div>

                <div>
                  <label htmlFor="area_sq_km" className="block text-sm font-medium text-gray-700 mb-2">
                    Area (sq. km)
                  </label>
                  <input
                    type="number"
                    step="0.01"
                    id="area_sq_km"
                    value={formData.area_sq_km}
                    onChange={(e) => setFormData({ ...formData, area_sq_km: e.target.value })}
                    placeholder="e.g., 450.5"
                    className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent"
                  />
                </div>
              </div>
            </div>

            {/* Info Message */}
            <div className="p-4 bg-blue-50 border border-blue-200 rounded-lg">
              <div className="flex items-start">
                <AlertCircle className="h-5 w-5 text-blue-600 mr-2 mt-0.5" />
                <p className="text-sm text-blue-800">
                  Constituency boundaries and GIS data can be configured later via admin tools.
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
                  <>{isEdit ? 'Update Constituency' : 'Create Constituency'}</>
                )}
              </button>
            </div>
          </form>
        </div>
      </div>
    </div>
  );
}

export default ConstituencyCreateModal;
