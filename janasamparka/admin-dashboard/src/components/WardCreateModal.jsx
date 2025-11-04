import { useEffect, useMemo, useState } from 'react';
import { X, AlertCircle, MapPin } from 'lucide-react';

const fieldForContextType = {
  city_corporation: 'city_corporation_id',
  town_municipality: 'town_municipality_id',
  municipality: 'town_municipality_id',
  taluk_panchayat: 'taluk_panchayat_id',
  gram_panchayat: 'gram_panchayat_id',
};

function WardCreateModal({
  isOpen,
  onClose,
  onCreate,
  ward = null,
  defaultConstituencyId = '',
  hierarchyOptions = {},
  contextNode = null,
}) {
  const isEdit = Boolean(ward);

  const emptyForm = useMemo(
    () => ({
      name: '',
      ward_number: '',
      taluk: '',
      constituency_id: defaultConstituencyId || '',
      city_corporation_id: '',
      town_municipality_id: '',
      taluk_panchayat_id: '',
      gram_panchayat_id: '',
      population: '',
      male_population: '',
      female_population: '',
      area_sq_km: '',
    }),
    [defaultConstituencyId]
  );

  const [formData, setFormData] = useState(emptyForm);
  const [loading, setLoading] = useState(false);
  const [errors, setErrors] = useState({});

  useEffect(() => {
    if (!isOpen) return;

    const mappedField = contextNode?.type ? fieldForContextType[contextNode.type] : null;

    setFormData({
      ...emptyForm,
      name: ward?.name || '',
      ward_number: ward?.ward_number || '',
      taluk: ward?.taluk || '',
      constituency_id: ward?.constituency_id || emptyForm.constituency_id,
      city_corporation_id:
        ward?.city_corporation_id ||
        (mappedField === 'city_corporation_id' ? contextNode?.id : ''),
      town_municipality_id:
        ward?.town_municipality_id ||
        ward?.municipality_id ||
        (mappedField === 'town_municipality_id' ? contextNode?.id : ''),
      taluk_panchayat_id:
        ward?.taluk_panchayat_id ||
        ward?.taluk_id ||
        (mappedField === 'taluk_panchayat_id' ? contextNode?.id : ''),
      gram_panchayat_id:
        ward?.gram_panchayat_id ||
        ward?.gram_id ||
        (mappedField === 'gram_panchayat_id' ? contextNode?.id : ''),
      population: ward?.population || '',
      male_population: ward?.male_population || '',
      female_population: ward?.female_population || '',
      area_sq_km: ward?.area_sq_km || '',
    });
    setErrors({});
  }, [isOpen, ward, emptyForm, contextNode?.id, contextNode?.type]);

  useEffect(() => {
    if (!isOpen && !isEdit) {
      setFormData(emptyForm);
      setErrors({});
    }
  }, [isOpen, isEdit, emptyForm]);

  const {
    constituencies = [],
    cityCorporations = [],
    townMunicipalities = [],
    talukPanchayats = [],
    gramPanchayats = [],
  } = useMemo(
    () => ({
      constituencies: hierarchyOptions.constituencies || [],
      cityCorporations: hierarchyOptions.cityCorporations || [],
      townMunicipalities: hierarchyOptions.townMunicipalities || [],
      talukPanchayats: hierarchyOptions.talukPanchayats || [],
      gramPanchayats: hierarchyOptions.gramPanchayats || [],
    }),
    [hierarchyOptions]
  );

  const hasHierarchyOptions =
    cityCorporations.length +
      townMunicipalities.length +
      talukPanchayats.length +
      gramPanchayats.length >
    0;

  const validateForm = () => {
    const newErrors = {};

    if (!formData.name.trim()) {
      newErrors.name = 'Ward name is required';
    }

    if (!formData.ward_number.trim()) {
      newErrors.ward_number = 'Ward number is required';
    }

    if (!formData.constituency_id) {
      newErrors.constituency_id = 'Constituency is required';
    }

    if (
      hasHierarchyOptions &&
      !formData.city_corporation_id &&
      !formData.town_municipality_id &&
      !formData.taluk_panchayat_id &&
      !formData.gram_panchayat_id
    ) {
      newErrors.jurisdiction = 'Select at least one governance layer for this ward';
    }

    if (formData.population && Number.isNaN(Number(formData.population))) {
      newErrors.population = 'Must be a number';
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
      setFormData({ ...emptyForm });
      setErrors({});
      onClose();
    } catch (error) {
      alert(`Failed to ${isEdit ? 'update' : 'create'} ward: ${error.message}`);
    } finally {
      setLoading(false);
    }
  };

  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 z-50 overflow-y-auto" aria-labelledby="modal-title" role="dialog" aria-modal="true">
      <div className="flex items-end justify-center min-h-screen pt-4 px-4 pb-20 text-center sm:block sm:p-0">
        <div
          className="fixed inset-0 bg-gray-500 bg-opacity-75 transition-opacity"
          aria-hidden="true"
          onClick={onClose}
        ></div>

        <span className="hidden sm:inline-block sm:align-middle sm:h-screen" aria-hidden="true">
          &#8203;
        </span>

        <div className="inline-block align-bottom bg-white rounded-lg px-4 pt-5 pb-4 text-left overflow-hidden shadow-xl transform transition-all sm:my-8 sm:align-middle sm:max-w-2xl sm:w-full sm:p-6">
          <div className="flex items-center justify-between mb-6">
            <h3 className="text-xl font-medium text-gray-900" id="modal-title">
              {isEdit ? 'Edit Ward' : 'Add New Ward'}
            </h3>
            <button onClick={onClose} className="text-gray-400 hover:text-gray-500 focus:outline-none">
              <X className="h-6 w-6" />
            </button>
          </div>

          <form onSubmit={handleSubmit} className="space-y-5">
            <div className="grid grid-cols-2 gap-4">
              <div>
                <label htmlFor="name" className="block text-sm font-medium text-gray-700 mb-2">
                  Ward Name <span className="text-red-500">*</span>
                </label>
                <input
                  type="text"
                  id="name"
                  value={formData.name}
                  onChange={(e) => setFormData({ ...formData, name: e.target.value })}
                  placeholder="e.g., MG Road Ward"
                  className={`w-full px-4 py-2 border rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent ${
                    errors.name ? 'border-red-500' : 'border-gray-300'
                  }`}
                />
                {errors.name && <p className="mt-1 text-sm text-red-500">{errors.name}</p>}
              </div>

              <div>
                <label htmlFor="ward_number" className="block text-sm font-medium text-gray-700 mb-2">
                  Ward Number <span className="text-red-500">*</span>
                </label>
                <input
                  type="text"
                  id="ward_number"
                  value={formData.ward_number}
                  onChange={(e) => setFormData({ ...formData, ward_number: e.target.value })}
                  placeholder="e.g., 1"
                  className={`w-full px-4 py-2 border rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent ${
                    errors.ward_number ? 'border-red-500' : 'border-gray-300'
                  }`}
                />
                {errors.ward_number && <p className="mt-1 text-sm text-red-500">{errors.ward_number}</p>}
              </div>
            </div>

            <div className="grid grid-cols-2 gap-4">
              <div>
                <label htmlFor="taluk" className="block text-sm font-medium text-gray-700 mb-2">
                  Taluk
                </label>
                <input
                  type="text"
                  id="taluk"
                  value={formData.taluk}
                  onChange={(e) => setFormData({ ...formData, taluk: e.target.value })}
                  placeholder="e.g., Puttur"
                  className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent"
                />
              </div>

              <div>
                <label htmlFor="constituency_id" className="block text-sm font-medium text-gray-700 mb-2">
                  Constituency <span className="text-red-500">*</span>
                </label>
                <select
                  id="constituency_id"
                  value={formData.constituency_id}
                  onChange={(e) =>
                    setFormData((prev) => ({
                      ...prev,
                      constituency_id: e.target.value,
                      city_corporation_id: '',
                      town_municipality_id: '',
                      taluk_panchayat_id: '',
                      gram_panchayat_id: '',
                    }))
                  }
                  className={`w-full px-4 py-2 border rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent ${
                    errors.constituency_id ? 'border-red-500' : 'border-gray-300'
                  }`}
                >
                  <option value="">-- Select --</option>
                  {constituencies.map((constituency) => (
                    <option key={constituency.id} value={constituency.id}>
                      {constituency.name}
                    </option>
                  ))}
                </select>
                {errors.constituency_id && <p className="mt-1 text-sm text-red-500">{errors.constituency_id}</p>}
              </div>
            </div>

            {hasHierarchyOptions && (
              <div className="space-y-4">
                <div className="flex items-center justify-between">
                  <h4 className="text-sm font-medium text-gray-900">Link Governance Layer</h4>
                  <span className="text-xs text-gray-500 flex items-center">
                    <MapPin className="mr-1 h-4 w-4 text-primary-500" />
                    Choose at least one
                  </span>
                </div>

                <div className="grid grid-cols-1 gap-4 md:grid-cols-2">
                  {cityCorporations.length > 0 && (
                    <div>
                      <label htmlFor="city_corporation_id" className="block text-sm font-medium text-gray-700 mb-2">
                        City Corporation
                      </label>
                      <select
                        id="city_corporation_id"
                        value={formData.city_corporation_id}
                        onChange={(e) =>
                          setFormData((prev) => ({
                            ...prev,
                            city_corporation_id: e.target.value,
                            town_municipality_id: '',
                            taluk_panchayat_id: '',
                            gram_panchayat_id: '',
                          }))
                        }
                        className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent"
                      >
                        <option value="">-- Select --</option>
                        {cityCorporations.map((entity) => (
                          <option key={entity.id} value={entity.id}>
                            {entity.name}
                          </option>
                        ))}
                      </select>
                    </div>
                  )}

                  {townMunicipalities.length > 0 && (
                    <div>
                      <label htmlFor="town_municipality_id" className="block text-sm font-medium text-gray-700 mb-2">
                        Town / City Municipality
                      </label>
                      <select
                        id="town_municipality_id"
                        value={formData.town_municipality_id}
                        onChange={(e) =>
                          setFormData((prev) => ({
                            ...prev,
                            town_municipality_id: e.target.value,
                            city_corporation_id: '',
                          }))
                        }
                        className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent"
                      >
                        <option value="">-- Select --</option>
                        {townMunicipalities.map((entity) => (
                          <option key={entity.id} value={entity.id}>
                            {entity.name}
                          </option>
                        ))}
                      </select>
                    </div>
                  )}

                  {talukPanchayats.length > 0 && (
                    <div>
                      <label htmlFor="taluk_panchayat_id" className="block text-sm font-medium text-gray-700 mb-2">
                        Taluk Panchayat
                      </label>
                      <select
                        id="taluk_panchayat_id"
                        value={formData.taluk_panchayat_id}
                        onChange={(e) =>
                          setFormData((prev) => ({
                            ...prev,
                            taluk_panchayat_id: e.target.value,
                            gram_panchayat_id: '',
                          }))
                        }
                        className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent"
                      >
                        <option value="">-- Select --</option>
                        {talukPanchayats.map((entity) => (
                          <option key={entity.id} value={entity.id}>
                            {entity.name}
                          </option>
                        ))}
                      </select>
                    </div>
                  )}

                  {gramPanchayats.length > 0 && (
                    <div>
                      <label htmlFor="gram_panchayat_id" className="block text-sm font-medium text-gray-700 mb-2">
                        Gram Panchayat
                      </label>
                      <select
                        id="gram_panchayat_id"
                        value={formData.gram_panchayat_id}
                        onChange={(e) =>
                          setFormData((prev) => ({
                            ...prev,
                            gram_panchayat_id: e.target.value,
                          }))
                        }
                        className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent"
                      >
                        <option value="">-- Select --</option>
                        {gramPanchayats.map((entity) => (
                          <option key={entity.id} value={entity.id}>
                            {entity.name}
                          </option>
                        ))}
                      </select>
                    </div>
                  )}
                </div>

                {errors.jurisdiction && <p className="text-sm text-red-500">{errors.jurisdiction}</p>}
              </div>
            )}

            <div>
              <h4 className="text-sm font-medium text-gray-900 mb-3">Demographics (Optional)</h4>
              <div className="grid grid-cols-3 gap-4">
                <div>
                  <label htmlFor="population" className="block text-sm font-medium text-gray-700 mb-2">
                    Total Population
                  </label>
                  <input
                    type="number"
                    id="population"
                    value={formData.population}
                    onChange={(e) => setFormData({ ...formData, population: e.target.value })}
                    placeholder="e.g., 15000"
                    className={`w-full px-4 py-2 border rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent ${
                      errors.population ? 'border-red-500' : 'border-gray-300'
                    }`}
                  />
                  {errors.population && <p className="mt-1 text-sm text-red-500">{errors.population}</p>}
                </div>

                <div>
                  <label htmlFor="male_population" className="block text-sm font-medium text-gray-700 mb-2">
                    Male
                  </label>
                  <input
                    type="number"
                    id="male_population"
                    value={formData.male_population}
                    onChange={(e) => setFormData({ ...formData, male_population: e.target.value })}
                    placeholder="7500"
                    className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent"
                  />
                </div>

                <div>
                  <label htmlFor="female_population" className="block text-sm font-medium text-gray-700 mb-2">
                    Female
                  </label>
                  <input
                    type="number"
                    id="female_population"
                    value={formData.female_population}
                    onChange={(e) => setFormData({ ...formData, female_population: e.target.value })}
                    placeholder="7500"
                    className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent"
                  />
                </div>
              </div>
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
                placeholder="e.g., 12.5"
                className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent"
              />
            </div>

            <div className="p-4 bg-blue-50 border border-blue-200 rounded-lg">
              <div className="flex items-start">
                <AlertCircle className="h-5 w-5 text-blue-600 mr-2 mt-0.5" />
                <p className="text-sm text-blue-800">
                  Ward boundaries and geographic data can be uploaded later via GIS tools.
                </p>
              </div>
            </div>

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
                    <svg
                      className="animate-spin -ml-1 mr-2 h-4 w-4 text-white"
                      xmlns="http://www.w3.org/2000/svg"
                      fill="none"
                      viewBox="0 0 24 24"
                    >
                      <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                      <path
                        className="opacity-75"
                        fill="currentColor"
                        d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"
                      ></path>
                    </svg>
                    {isEdit ? 'Updating...' : 'Creating...'}
                  </>
                ) : (
                  <>{isEdit ? 'Update Ward' : 'Create Ward'}</>
                )}
              </button>
            </div>
          </form>
        </div>
      </div>
    </div>
  );
}

export default WardCreateModal;
