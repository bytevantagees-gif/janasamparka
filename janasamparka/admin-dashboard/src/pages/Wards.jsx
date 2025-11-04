import { useEffect, useMemo, useState } from 'react';
import { useQuery, useQueryClient } from '@tanstack/react-query';
import {
  MapPin,
  Plus,
  Search,
  Edit2,
  Building2,
  Landmark,
  Layers,
  Trees,
  AlertCircle,
} from 'lucide-react';
import WardCreateModal from '../components/WardCreateModal';
import { useTranslation } from '../hooks/useTranslation';
import { constituenciesAPI, wardsAPI, panchayatsAPI } from '../services/api';

const ensureArray = (value, fallback = []) => {
  if (!value) return fallback;
  if (Array.isArray(value)) return value;
  if (Array.isArray(value?.data)) return value.data;
  if (Array.isArray(value?.results)) return value.results;
  if (Array.isArray(value?.items)) return value.items;
  return fallback;
};

const resolveEntityId = (entity) =>
  entity?.id ??
  entity?.uuid ??
  entity?.slug ??
  entity?.code ??
  entity?.external_id ??
  entity?.name ??
  entity?.ward_number ??
  JSON.stringify(entity);

const getDisplayName = (entity) =>
  entity?.name ||
  entity?.title ||
  entity?.label ||
  entity?.display_name ||
  entity?.code ||
  'Unnamed';

const formatNumber = (value) => {
  const number = Number(value);
  if (Number.isNaN(number)) {
    return value || '0';
  }
  return number.toLocaleString();
};

const resolveWardAffiliation = (ward) => {
  if (!ward) return '';
  const parts = [
    ward.city_corporation?.name || ward.city_corporation_name,
    ward.town_municipality?.name || ward.municipality?.name || ward.municipality_name,
    ward.taluk_panchayat?.name || ward.taluk_name || ward.taluk,
    ward.gram_panchayat?.name || ward.gram_panchayat_name,
  ].filter(Boolean);
  return parts.join(' • ');
};

const formatWardType = (type) => {
  const dictionary = {
    city_corporation: 'City Corporation Ward',
    town_municipality: 'Town Municipality Ward',
    municipality: 'Municipal Ward',
    taluk_panchayat: 'Taluk Panchayat Ward',
    gram_panchayat: 'Gram Panchayat Ward',
    urban: 'Urban Ward',
    rural: 'Rural Ward',
  };

  return dictionary[type] || 'Ward';
};

const wardMatchesNode = (ward, node) => {
  if (!node) return true;
  if (!ward) return false;

  switch (node.type) {
    case 'constituency':
      return ward.constituency_id === node.id;
    case 'city_corporation':
      return ward.city_corporation_id === node.id;
    case 'town_municipality':
      return ward.town_municipality_id === node.id || ward.municipality_id === node.id;
    case 'taluk_panchayat':
      return ward.taluk_panchayat_id === node.id || ward.taluk_id === node.id;
    case 'gram_panchayat':
      return ward.gram_panchayat_id === node.id || ward.gram_id === node.id;
    default:
      return true;
  }
};

const computeWardStats = (wards) => {
  if (!wards?.length) {
    return {
      total: 0,
      totalPopulation: 0,
      byType: {},
    };
  }

  const totalPopulation = wards.reduce(
    (sum, ward) => sum + (Number(ward.population) || 0),
    0
  );

  const byType = wards.reduce((accumulator, ward) => {
    const key = ward.ward_type || 'general';
    accumulator[key] = (accumulator[key] || 0) + 1;
    return accumulator;
  }, {});

  return {
    total: wards.length,
    totalPopulation,
    byType,
  };
};

function Wards() {
  const { t } = useTranslation();
  const queryClient = useQueryClient();

  const [selectedConstituencyId, setSelectedConstituencyId] = useState('');
  const [selectedNode, setSelectedNode] = useState(null);
  const [searchTerm, setSearchTerm] = useState('');
  const [isCreateModalOpen, setIsCreateModalOpen] = useState(false);
  const [editingWard, setEditingWard] = useState(null);

  const {
    data: constituenciesResponse,
    isLoading: isLoadingConstituencies,
    error: constituenciesError,
  } = useQuery({
    queryKey: ['constituencies', 'for-wards'],
    queryFn: async () => {
      const response = await constituenciesAPI.getAll(true);
      return response.data;
    },
    staleTime: 60000,
  });

  const constituencies = useMemo(
    () => ensureArray(constituenciesResponse?.constituencies ?? constituenciesResponse),
    [constituenciesResponse]
  );

  useEffect(() => {
    if (!selectedConstituencyId && constituencies.length) {
      setSelectedConstituencyId(constituencies[0].id);
    }
  }, [constituencies, selectedConstituencyId]);

  useEffect(() => {
    setSelectedNode(null);
  }, [selectedConstituencyId]);

  const {
    data: hierarchyResponse,
    isLoading: isLoadingHierarchy,
    error: hierarchyError,
  } = useQuery({
    queryKey: ['panchayatHierarchy', selectedConstituencyId],
    queryFn: async () => {
      const response = await panchayatsAPI.getHierarchy(selectedConstituencyId);
      return response.data;
    },
    enabled: Boolean(selectedConstituencyId),
    staleTime: 60000,
  });

  const hierarchyGroups = useMemo(
    () => [
      {
        key: 'cityCorporations',
        title: 'City Corporations',
        type: 'city_corporation',
        icon: Building2,
        items: ensureArray(hierarchyResponse?.city_corporations),
      },
      {
        key: 'townMunicipalities',
        title: 'City & Town Municipalities',
        type: 'town_municipality',
        icon: Landmark,
        items: ensureArray(
          hierarchyResponse?.town_municipalities ?? hierarchyResponse?.municipalities
        ),
      },
      {
        key: 'talukPanchayats',
        title: 'Taluk Panchayats',
        type: 'taluk_panchayat',
        icon: Layers,
        items: ensureArray(hierarchyResponse?.taluk_panchayats),
      },
      {
        key: 'gramPanchayats',
        title: 'Gram Panchayats',
        type: 'gram_panchayat',
        icon: Trees,
        items: ensureArray(hierarchyResponse?.gram_panchayats),
      },
    ],
    [hierarchyResponse]
  );

  const hierarchyOptions = useMemo(() => {
    const lookup = hierarchyGroups.reduce((accumulator, group) => {
      accumulator[group.key] = group.items;
      return accumulator;
    }, {});

    return {
      constituencies,
      cityCorporations: lookup.cityCorporations || [],
      townMunicipalities: lookup.townMunicipalities || [],
      talukPanchayats: lookup.talukPanchayats || [],
      gramPanchayats: lookup.gramPanchayats || [],
    };
  }, [hierarchyGroups, constituencies]);

  const {
    data: wardsResponse,
    isLoading: isLoadingWards,
    error: wardsError,
  } = useQuery({
    queryKey: ['wards', selectedConstituencyId],
    queryFn: async () => {
      const params = selectedConstituencyId
        ? { constituency_id: selectedConstituencyId }
        : undefined;
      const response = await wardsAPI.getAll(params);
      return response.data;
    },
    enabled: Boolean(selectedConstituencyId),
    staleTime: 30000,
  });

  const wards = useMemo(
    () => ensureArray(wardsResponse?.wards ?? wardsResponse),
    [wardsResponse]
  );

  const filteredWards = useMemo(() => {
    const query = searchTerm.trim().toLowerCase();

    return wards.filter((ward) => {
      const matchesSearch = !query
        ? true
        : ward.name?.toLowerCase().includes(query) ||
          String(ward.ward_number ?? '').includes(query);

      return matchesSearch && wardMatchesNode(ward, selectedNode);
    });
  }, [wards, searchTerm, selectedNode]);

  const stats = useMemo(() => computeWardStats(wards), [wards]);

  const statTiles = useMemo(
    () => [
      {
        label: 'Total Wards',
        value: formatNumber(stats.total),
        icon: Layers,
      },
      {
        label: 'Estimated Population',
        value: formatNumber(stats.totalPopulation),
        icon: MapPin,
      },
      {
        label: 'Urban Wards',
        value: formatNumber(
          (stats.byType.city_corporation || 0) +
            (stats.byType.town_municipality || 0) +
            (stats.byType.municipality || 0)
        ),
        icon: Building2,
      },
      {
        label: 'Rural Wards',
        value: formatNumber(
          (stats.byType.taluk_panchayat || 0) + (stats.byType.gram_panchayat || 0)
        ),
        icon: Trees,
      },
    ],
    [stats]
  );

  const openWardModal = (ward = null) => {
    setEditingWard(ward);
    setIsCreateModalOpen(true);
  };

  const handleCloseModal = () => {
    setIsCreateModalOpen(false);
    setEditingWard(null);
  };

  const handlePersistWard = async (formData) => {
    const payload = {
      ...formData,
      constituency_id: formData.constituency_id || selectedConstituencyId,
    };

    try {
      if (editingWard?.id) {
        await wardsAPI.update(editingWard.id, payload);
      } else {
        await wardsAPI.create(payload);
      }

      await Promise.all([
        queryClient.invalidateQueries({ queryKey: ['wards'] }),
        queryClient.invalidateQueries({
          queryKey: ['panchayatHierarchy', selectedConstituencyId],
        }),
      ]);

      window.alert(`Ward ${editingWard?.id ? 'updated' : 'created'} successfully!`);
    } catch (error) {
      console.error('Failed to persist ward', error);
      throw error;
    }
  };

  const toggleNode = (type, entity) => {
    const entityId = resolveEntityId(entity);
    const isActive = selectedNode?.type === type && selectedNode?.id === entityId;

    setSelectedNode(
      isActive
        ? null
        : {
            type,
            id: entityId,
            name: getDisplayName(entity),
          }
    );
  };

  if (isLoadingConstituencies) {
    return (
      <div className="flex h-64 items-center justify-center">
        <div className="text-center">
          <div className="mx-auto h-12 w-12 animate-spin rounded-full border-2 border-primary-500 border-t-transparent" />
          <p className="mt-4 text-sm text-gray-500">Loading constituencies…</p>
        </div>
      </div>
    );
  }

  if (constituenciesError) {
    return (
      <div className="rounded-xl border border-red-100 bg-red-50 p-6 text-red-700">
        Failed to load constituencies: {constituenciesError.message}
      </div>
    );
  }

  if (!constituencies.length) {
    return (
      <div className="rounded-xl border border-dashed border-primary-200 bg-white p-10 text-center shadow-sm">
        <h2 className="text-lg font-semibold text-gray-900">No constituencies available</h2>
        <p className="mt-2 text-sm text-gray-500">
          Once constituencies are configured, you will be able to explore their ward hierarchy here.
        </p>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      <div className="flex flex-col gap-4 sm:flex-row sm:items-end sm:justify-between">
        <div>
          <h1 className="text-2xl font-semibold text-gray-900">
            {t('wards.pageTitle', 'Ward Hierarchy Explorer')}
          </h1>
          <p className="mt-1 text-sm text-gray-500">
            {t(
              'wards.pageSubtitle',
              'Choose a constituency, then drill down into towns, cities, and village panchayats.'
            )}
          </p>
        </div>
        <button
          type="button"
          onClick={() => openWardModal()}
          className="inline-flex items-center justify-center rounded-full bg-primary-600 px-5 py-2 text-sm font-medium text-white shadow-lg shadow-primary-500/30 transition hover:bg-primary-700"
        >
          <Plus className="mr-2 h-4 w-4" />
          {t('wards.addWard', 'Register Ward')}
        </button>
      </div>

      <div className="grid gap-6 lg:grid-cols-[320px,1fr]">
        <aside className="space-y-6">
          <div className="rounded-2xl border border-primary-100 bg-white/80 p-6 shadow-sm shadow-primary-100/40 backdrop-blur">
            <label className="mb-2 block text-sm font-medium text-gray-600" htmlFor="constituency-select">
              {t('wards.selectConstituency', 'Constituency')}
            </label>
            <select
              id="constituency-select"
              value={selectedConstituencyId}
              onChange={(event) => setSelectedConstituencyId(event.target.value)}
              className="w-full rounded-xl border border-gray-200 bg-white px-4 py-2 text-sm focus:border-primary-500 focus:outline-none focus:ring-2 focus:ring-primary-200"
            >
              {constituencies.map((constituency) => (
                <option key={constituency.id} value={constituency.id}>
                  {constituency.name}
                </option>
              ))}
            </select>
          </div>

          {hierarchyError && (
            <div className="rounded-xl border border-red-100 bg-red-50 p-4 text-sm text-red-600">
              <div className="flex items-start">
                <AlertCircle className="mr-2 h-5 w-5" />
                <div>
                  <p className="font-medium">Failed to load hierarchy</p>
                  <p className="mt-1 text-xs text-red-500">{hierarchyError.message}</p>
                </div>
              </div>
            </div>
          )}

          <div className="rounded-2xl border border-primary-50 bg-gradient-to-br from-white via-white to-primary-50/60 p-6 shadow-sm shadow-primary-100/40 backdrop-blur">
            <div className="flex items-center justify-between">
              <h2 className="text-sm font-semibold uppercase tracking-wide text-gray-500">
                {t('wards.hierarchyFilter', 'Governance Layers')}
              </h2>
              {selectedNode && (
                <button
                  type="button"
                  onClick={() => setSelectedNode(null)}
                  className="text-xs font-medium text-primary-600 hover:text-primary-700"
                >
                  Clear
                </button>
              )}
            </div>
            <p className="mt-2 text-xs text-gray-500">
              {t(
                'wards.hierarchyDescription',
                'Select a town, city, or panchayat to constrain the ward list.'
              )}
            </p>

            {isLoadingHierarchy ? (
              <div className="flex items-center justify-center py-10">
                <div className="h-10 w-10 animate-spin rounded-full border-2 border-primary-500 border-t-transparent" />
              </div>
            ) : (
              <div className="mt-5 space-y-6">
                {hierarchyGroups.map(({ key, title, type, icon: Icon, items }) => {
                  if (!items.length) return null;

                  return (
                    <div key={key}>
                      <div className="mb-2 flex items-center justify-between">
                        <div className="flex items-center text-xs font-semibold uppercase tracking-wide text-gray-500">
                          <Icon className="mr-2 h-4 w-4 text-primary-500" />
                          {title}
                        </div>
                        <span className="text-xs text-gray-400">{items.length}</span>
                      </div>
                      <div className="flex flex-wrap gap-2">
                        {items.map((entity) => {
                          const entityId = resolveEntityId(entity);
                          const isActive =
                            selectedNode?.type === type && selectedNode?.id === entityId;

                          return (
                            <button
                              key={entityId}
                              type="button"
                              onClick={() => toggleNode(type, entity)}
                              className={`rounded-full border px-3 py-1.5 text-sm transition-all ${
                                isActive
                                  ? 'border-primary-600 bg-primary-600 text-white shadow-lg shadow-primary-500/40'
                                  : 'border-gray-200 bg-white text-gray-700 hover:border-primary-400 hover:text-primary-600'
                              }`}
                            >
                              {getDisplayName(entity)}
                            </button>
                          );
                        })}
                      </div>
                    </div>
                  );
                })}

                {!hierarchyGroups.some((group) => group.items.length) && (
                  <div className="rounded-lg border border-dashed border-primary-100 bg-white/80 p-4 text-xs text-gray-500">
                    {t(
                      'wards.noHierarchyData',
                      'No subordinate governance layers have been linked to this constituency yet.'
                    )}
                  </div>
                )}
              </div>
            )}
          </div>
        </aside>

        <section className="space-y-6">
          <div className="rounded-2xl border border-primary-100 bg-white/80 p-6 shadow-sm shadow-primary-100/30 backdrop-blur">
            <div className="grid gap-4 sm:grid-cols-2 xl:grid-cols-4">
              {statTiles.map(({ label, value, icon: Icon }) => (
                <div
                  key={label}
                  className="rounded-2xl border border-primary-50 bg-white/90 p-4 shadow-inner shadow-primary-100/20"
                >
                  <div className="flex items-center justify-between">
                    <p className="text-xs uppercase tracking-wide text-gray-400">{label}</p>
                    <Icon className="h-4 w-4 text-primary-500" />
                  </div>
                  <p className="mt-3 text-2xl font-semibold text-gray-900">{value}</p>
                </div>
              ))}
            </div>
          </div>

          <div className="rounded-2xl border border-primary-50 bg-white/90 p-6 shadow-sm shadow-primary-100/30 backdrop-blur">
            <div className="flex flex-col gap-4 sm:flex-row sm:items-center sm:justify-between">
              <div className="relative w-full sm:max-w-sm">
                <Search className="pointer-events-none absolute left-3 top-2.5 h-4 w-4 text-gray-400" />
                <input
                  type="text"
                  value={searchTerm}
                  onChange={(event) => setSearchTerm(event.target.value)}
                  placeholder={t('wards.searchPlaceholder', 'Search wards or numbers…')}
                  className="w-full rounded-full border border-gray-200 bg-white py-2 pl-9 pr-4 text-sm focus:border-primary-500 focus:outline-none focus:ring-2 focus:ring-primary-200"
                />
              </div>

              {selectedNode && (
                <div className="inline-flex items-center rounded-full bg-primary-100 px-3 py-1 text-sm text-primary-700">
                  <MapPin className="mr-2 h-4 w-4" />
                  <span>{selectedNode.name}</span>
                </div>
              )}
            </div>

            <div className="mt-6">
              {isLoadingWards ? (
                <div className="flex justify-center py-16">
                  <div className="h-12 w-12 animate-spin rounded-full border-2 border-primary-500 border-t-transparent" />
                </div>
              ) : wardsError ? (
                <div className="rounded-xl border border-red-100 bg-red-50 p-6 text-sm text-red-600">
                  <div className="flex items-start">
                    <AlertCircle className="mr-2 h-5 w-5" />
                    <div>
                      <p className="font-medium">Failed to load wards</p>
                      <p className="mt-1 text-xs text-red-500">{wardsError.message}</p>
                    </div>
                  </div>
                </div>
              ) : filteredWards.length === 0 ? (
                <div className="rounded-xl border border-dashed border-primary-100 bg-white/90 p-12 text-center text-sm text-gray-500">
                  {t(
                    'wards.emptyState',
                    'No wards match the current filters. Try a different search or reset the hierarchy filter.'
                  )}
                </div>
              ) : (
                <div className="grid gap-6 sm:grid-cols-2 xl:grid-cols-3">
                  {filteredWards.map((ward) => {
                    const affiliation = resolveWardAffiliation(ward);
                    const wardId = resolveEntityId(ward);

                    return (
                      <div
                        key={wardId}
                        className="group relative h-full rounded-2xl border border-primary-100 bg-white/80 p-6 shadow-sm transition-all hover:-translate-y-1 hover:border-primary-200 hover:shadow-xl"
                      >
                        <div className="flex items-start justify-between">
                          <div>
                            <p className="text-xs uppercase tracking-wide text-primary-500">
                              {formatWardType(ward.ward_type)}
                            </p>
                            <h3 className="mt-1 text-lg font-semibold text-gray-900">
                              {ward.name || 'Unnamed Ward'}
                            </h3>
                            {ward.ward_number && (
                              <p className="text-sm text-gray-500">Ward #{ward.ward_number}</p>
                            )}
                          </div>
                          <button
                            type="button"
                            onClick={() => openWardModal(ward)}
                            className="inline-flex h-9 w-9 items-center justify-center rounded-full border border-primary-200 text-primary-500 transition-colors hover:bg-primary-600 hover:text-white"
                          >
                            <Edit2 className="h-4 w-4" />
                          </button>
                        </div>

                        <div className="mt-4 flex items-start text-sm text-gray-600">
                          <MapPin className="mr-2 h-4 w-4 text-primary-500" />
                          <span>{affiliation || 'Jurisdiction pending'}</span>
                        </div>

                        <div className="mt-6 grid grid-cols-2 gap-4 text-sm">
                          <div>
                            <p className="text-xs uppercase tracking-wide text-gray-400">Population</p>
                            <p className="mt-1 font-medium text-gray-900">
                              {formatNumber(ward.population) || 'N/A'}
                            </p>
                          </div>
                          <div>
                            <p className="text-xs uppercase tracking-wide text-gray-400">Last Updated</p>
                            <p className="mt-1 text-gray-700">
                              {ward.updated_at
                                ? new Date(ward.updated_at).toLocaleDateString()
                                : '—'}
                            </p>
                          </div>
                        </div>
                      </div>
                    );
                  })}
                </div>
              )}
            </div>
          </div>
        </section>
      </div>

      <WardCreateModal
        isOpen={isCreateModalOpen}
        onClose={handleCloseModal}
        onCreate={handlePersistWard}
        ward={editingWard}
        defaultConstituencyId={selectedConstituencyId}
        hierarchyOptions={hierarchyOptions}
        contextNode={selectedNode}
      />
    </div>
  );
}

export default Wards;
