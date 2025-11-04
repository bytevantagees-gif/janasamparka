import { useState, useEffect, useMemo } from 'react';
import { useQuery } from '@tanstack/react-query';
import { Filter, X, Download, RefreshCw, Layers, MapPin } from 'lucide-react';
import ComplaintMap from '../components/ComplaintMap';
import { complaintsAPI, authAPI } from '../services/api';
import { useTranslation } from '../hooks/useTranslation';

const Map = () => {
  const { t } = useTranslation();
  const [filters, setFilters] = useState({
    status: '',
    category: '',
    ward_id: '',
    date_from: '',
    date_to: ''
  });
  const [showFilters, setShowFilters] = useState(false);
  const [viewMode, setViewMode] = useState('markers'); // 'markers', 'heatmap', 'clusters'
  const [showHeatmap, setShowHeatmap] = useState(false);
  const [showClusters, setShowClusters] = useState(false);

  // Fetch current user to determine role
  const { data: userResponse, isLoading: isUserLoading, error: userError } = useQuery({
    queryKey: ['currentUser'],
    queryFn: authAPI.getCurrentUser,
    staleTime: 5 * 60 * 1000, // 5 minutes
    onError: (error) => {
      console.error('❌ Error fetching current user:', error);
    },
    onSuccess: (data) => {
      console.log('✅ User fetched:', data);
    }
  });

  console.log('👤 User query state:', { 
    userResponse, 
    isUserLoading, 
    userError,
    hasResponse: !!userResponse,
    responseData: userResponse?.data,
    responseKeys: userResponse ? Object.keys(userResponse) : []
  });

  // Extract user data from the response
  // The backend returns the user object directly in response.data
  const currentUser = userResponse?.data || null;
  
  console.log('👤 Current user extracted:', { 
    currentUser, 
    hasUser: !!currentUser,
    userKeys: currentUser ? Object.keys(currentUser) : [],
    userId: currentUser?.id,
    userRole: currentUser?.role
  });
  
  // Log user data for debugging
  useEffect(() => {
    if (currentUser) {
      console.log('✅ Current User Context:', {
        id: currentUser.id,
        role: currentUser.role,
        constituency_id: currentUser.constituency_id,
        name: currentUser.name,
        phone: currentUser.phone
      });
    } else {
      console.warn('⚠️ No current user available');
    }
  }, [currentUser]);

  // Fetch complaints with proper user context
  const { data: complaintsResponse, isLoading, refetch, error: queryError } = useQuery({
    queryKey: ['complaints', filters, currentUser?.id],
    queryFn: async () => {
      console.log('🚀 Query function starting...', { currentUser });
      
      // Wait for currentUser to be available
      if (!currentUser) {
        console.log('⏸️ Waiting for user data...');
        return [];
      }

      console.log('Current User Context:', {
        id: currentUser.id,
        role: currentUser.role,
        constituency_id: currentUser.constituency_id,
        name: currentUser.name
      });

      // Prepare filters for the API
      const apiFilters = { ...filters };
      
      // For citizens, only show their own complaints
      if (currentUser.role === 'citizen') {
        apiFilters.user_id = currentUser.id;
      }
      
      try {
        console.log('Making API request with filters:', apiFilters);
        console.log('User context:', {
          role: currentUser.role,
          constituency_id: currentUser.constituency_id,
          constituency_name: currentUser.constituency_name
        });
        
        // Fetch complaints with the updated filters
        const response = await complaintsAPI.getAll(apiFilters);
        
        console.log('Raw API Response:', {
          status: response.status,
          statusText: response.statusText,
          headers: response.headers,
          data: response.data,
          config: response.config
        });
        
        // Check if response.data is an object with a complaints property
        const complaintsData = response?.data?.complaints || response?.data || [];
        
        if (!Array.isArray(complaintsData)) {
          console.error('Unexpected response format - expected an array of complaints:', complaintsData);
          return [];
        }
        
        console.log('API Response Data:', {
          url: '/api/complaints',
          filters: apiFilters,
          userRole: currentUser.role,
          userConstituency: currentUser.constituency_id,
          complaintCount: complaintsData.length,
          firstComplaint: complaintsData[0] || null,
          complaintIds: complaintsData.map(c => c.id)
        });

        // For debugging: Log a few complaints to verify filtering
        if (complaintsData.length > 0) {
          console.log('Sample complaints:', complaintsData.slice(0, 3).map(c => ({
            id: c.id,
            title: c.title,
            lat: c.lat,
            lng: c.lng,
            location: c.location,
            constituency_id: c.constituency_id,
            status: c.status
          })));
        } else {
          console.warn('⚠️ NO COMPLAINTS RETURNED FROM API', {
            apiFilters,
            userRole: currentUser.role,
            userConstituency: currentUser.constituency_id,
            userConstituencyName: currentUser.constituency_name
          });
        }

        return complaintsData;
      } catch (error) {
        console.error('❌ Error fetching complaints:', {
          message: error.message,
          response: error.response?.data,
          config: error.config
        });
        throw error; // Re-throw to let React Query handle it
      }
    },
    enabled: !!currentUser,
    staleTime: 30000, // 30 seconds
    onError: (error) => {
      console.error('❌ Query Error:', error);
    },
    onSuccess: (data) => {
      console.log('✅ Query Success:', { dataLength: data?.length, sampleItem: data?.[0] });
    },
    onSettled: (data, error) => {
      console.log('⚙️ Query settled:', { hasData: !!data, dataLength: data?.length, error });
    }
  });

  console.log('📊 Query state after fetch:', { 
    complaintsResponse, 
    isLoading, 
    queryError,
    hasData: !!complaintsResponse,
    dataType: typeof complaintsResponse,
    isArray: Array.isArray(complaintsResponse)
  });

  // Process complaints to ensure they have the correct structure
  const complaints = useMemo(() => {
    console.log('🔍 useMemo processing complaintsResponse:', {
      isArray: Array.isArray(complaintsResponse),
      type: typeof complaintsResponse,
      length: complaintsResponse?.length,
      value: complaintsResponse
    });

    if (!Array.isArray(complaintsResponse)) return [];
    
    // Log the raw response for debugging
    console.log('Raw complaints response:', complaintsResponse);
    
    // Process complaints to ensure they have the correct structure
    const processed = complaintsResponse.map(complaint => {
      // Debug log for each complaint's location data
      console.log('Processing complaint:', {
        id: complaint.id,
        title: complaint.title,
        rawLat: complaint.lat || complaint.latitude || (complaint.location?.lat || complaint.location?.latitude),
        rawLng: complaint.lng || complaint.long || complaint.lon || complaint.longitude || (complaint.location?.lng || complaint.location?.long || complaint.location?.longitude),
        location: complaint.location
      });
      
      // Parse coordinates, handling both string and number types
      const parseCoord = (coord) => {
        if (coord === null || coord === undefined) return null;
        const num = typeof coord === 'string' ? parseFloat(coord) : coord;
        return isNaN(num) ? null : num;
      };
      
      const lat = parseCoord(complaint.lat || complaint.latitude || complaint.location?.lat || complaint.location?.latitude);
      const lng = parseCoord(complaint.lng || complaint.long || complaint.lon || complaint.longitude || complaint.location?.lng || complaint.location?.long || complaint.location?.longitude);
      
      return {
        ...complaint,
        lat,
        lng,
        hasValidCoords: lat !== null && lng !== null
      };
    });
    
    // Filter out complaints without valid coordinates
    const validComplaints = processed.filter(c => c.hasValidCoords);
    
    console.log('Processed complaints:', {
      total: complaintsResponse.length,
      withValidCoords: validComplaints.length,
      sample: validComplaints[0] || null,
      allConstituencies: [...new Set(validComplaints.map(c => c.constituency_id))],
      complaintsWithoutCoords: processed.filter(c => !c.hasValidCoords).map(c => ({
        id: c.id,
        title: c.title,
        lat: c.lat,
        lng: c.lng
      }))
    });

    // More visible warning if no valid coordinates
    if (complaintsResponse.length > 0 && validComplaints.length === 0) {
      console.error('❌ CRITICAL: All complaints are missing valid coordinates!', {
        totalComplaints: complaintsResponse.length,
        sampleComplaints: processed.slice(0, 5).map(c => ({
          id: c.id,
          title: c.title,
          lat: c.lat,
          lng: c.lng,
          rawLat: c.lat,
          rawLng: c.lng
        }))
      });
    }
    
    return validComplaints;
  }, [complaintsResponse]);
  
  // Set default center to Puttur if we have complaints, otherwise use default center
  const defaultCenter = useMemo(() => {
    if (complaints.length > 0) {
      // Calculate center of all complaints
      const lats = complaints.map(c => c.lat).filter(Boolean);
      const lngs = complaints.map(c => c.lng).filter(Boolean);
      
      if (lats.length > 0 && lngs.length > 0) {
        const avgLat = lats.reduce((a, b) => a + b, 0) / lats.length;
        const avgLng = lngs.reduce((a, b) => a + b, 0) / lngs.length;
        console.log('🎯 Calculated map center:', { avgLat, avgLng, latsCount: lats.length });
        return [avgLat, avgLng];
      }
    }
    // Default to Mangalore coordinates if no valid complaints
    console.log('🎯 Using default center: Mangalore');
    return [12.8697, 74.8430]; // Mangalore, Karnataka
  }, [complaints]);

  const handleFilterChange = (key, value) => {
    setFilters(prev => ({ ...prev, [key]: value }));
  };

  const clearFilters = () => {
    setFilters({
      status: '',
      category: '',
      ward_id: '',
      date_from: '',
      date_to: ''
    });
  };

  const hasActiveFilters = Object.values(filters).some(v => v !== '');

  const exportData = () => {
    // TODO: Implement export functionality
    alert('Export functionality coming soon!');
  };

  const STATUS_OPTIONS = [
    { value: '', label: 'All Statuses' },
    { value: 'submitted', label: 'Submitted' },
    { value: 'assigned', label: 'Assigned' },
    { value: 'in_progress', label: 'In Progress' },
    { value: 'resolved', label: 'Resolved' },
    { value: 'closed', label: 'Closed' },
    { value: 'rejected', label: 'Rejected' }
  ];

  const CATEGORY_OPTIONS = [
    { value: '', label: 'All Categories' },
    { value: 'road', label: 'Road & Infrastructure' },
    { value: 'water', label: 'Water Supply' },
    { value: 'electricity', label: 'Electricity' },
    { value: 'health', label: 'Health' },
    { value: 'education', label: 'Education' },
    { value: 'sanitation', label: 'Sanitation' },
    { value: 'other', label: 'Other' }
  ];

  return (
    <div className="h-screen flex flex-col">
      {/* Header */}
      <div className="bg-white shadow-sm border-b border-gray-200 px-6 py-4">
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-2xl font-bold text-gray-900">{t('complaintMap')}</h1>
            <p className="text-sm text-gray-500 mt-1">
              {complaints?.length || 0} complaints plotted
              {hasActiveFilters && ' (filtered)'}
              {currentUser?.role === 'mla' && ' · MLA Constituency View'}
              {currentUser?.role === 'moderator' && ' · Moderator Constituency View'}
              {currentUser?.role === 'department_officer' && ' · Department View'}
              {currentUser?.constituency_name && ` · ${currentUser.constituency_name}`}
            </p>
          </div>

          <div className="flex items-center gap-3">
            {/* Refresh Button */}
            <button
              onClick={() => refetch()}
              className="inline-flex items-center px-4 py-2 border border-gray-300 rounded-lg text-sm font-medium text-gray-700 bg-white hover:bg-gray-50"
              disabled={isLoading}
            >
              <RefreshCw className={`mr-2 h-4 w-4 ${isLoading ? 'animate-spin' : ''}`} />
              Refresh
            </button>

            {/* Export Button */}
            <button
              onClick={exportData}
              className="inline-flex items-center px-4 py-2 border border-gray-300 rounded-lg text-sm font-medium text-gray-700 bg-white hover:bg-gray-50"
            >
              <Download className="mr-2 h-4 w-4" />
              Export
            </button>

            {/* View Mode Toggle */}
            <div className="flex items-center gap-1 border border-gray-300 rounded-lg p-1 bg-white">
              <button
                onClick={() => {
                  setViewMode('markers');
                  setShowHeatmap(false);
                  setShowClusters(false);
                }}
                className={`px-3 py-1.5 rounded text-sm font-medium transition-colors ${
                  viewMode === 'markers'
                    ? 'bg-primary-600 text-white'
                    : 'text-gray-700 hover:bg-gray-100'
                }`}
                title="Marker View"
              >
                <MapPin className="h-4 w-4" />
              </button>
              <button
                onClick={() => {
                  setViewMode('heatmap');
                  setShowHeatmap(true);
                  setShowClusters(false);
                }}
                className={`px-3 py-1.5 rounded text-sm font-medium transition-colors ${
                  viewMode === 'heatmap'
                    ? 'bg-primary-600 text-white'
                    : 'text-gray-700 hover:bg-gray-100'
                }`}
                title="Heatmap View"
              >
                <Layers className="h-4 w-4" />
              </button>
              <button
                onClick={() => {
                  setViewMode('clusters');
                  setShowHeatmap(false);
                  setShowClusters(true);
                }}
                className={`px-3 py-1.5 rounded text-sm font-medium transition-colors ${
                  viewMode === 'clusters'
                    ? 'bg-primary-600 text-white'
                    : 'text-gray-700 hover:bg-gray-100'
                }`}
                title="Cluster View"
              >
                ●●●
              </button>
            </div>

            {/* Filter Toggle */}
            <button
              onClick={() => setShowFilters(!showFilters)}
              className={`inline-flex items-center px-4 py-2 rounded-lg text-sm font-medium ${
                showFilters || hasActiveFilters
                  ? 'bg-primary-600 text-white'
                  : 'border border-gray-300 text-gray-700 bg-white hover:bg-gray-50'
              }`}
            >
              <Filter className="mr-2 h-4 w-4" />
              Filters
              {hasActiveFilters && (
                <span className="ml-2 px-1.5 py-0.5 bg-white text-primary-600 rounded-full text-xs font-bold">
                  {Object.values(filters).filter(v => v !== '').length}
                </span>
              )}
            </button>
          </div>
        </div>
      </div>

      {/* Filters Panel */}
      {showFilters && (
        <div className="bg-gray-50 border-b border-gray-200 px-6 py-4">
          <div className="flex items-center justify-between mb-4">
            <h3 className="text-sm font-semibold text-gray-900">Filter Complaints</h3>
            {hasActiveFilters && (
              <button
                onClick={clearFilters}
                className="text-sm text-primary-600 hover:text-primary-700 font-medium flex items-center gap-1"
              >
                <X className="h-4 w-4" />
                Clear All
              </button>
            )}
          </div>

          <div className="grid grid-cols-1 md:grid-cols-5 gap-4">
            {/* Status Filter */}
            <div>
              <label className="block text-xs font-medium text-gray-700 mb-1">
                Status
              </label>
              <select
                value={filters.status}
                onChange={(e) => handleFilterChange('status', e.target.value)}
                className="w-full px-3 py-2 border border-gray-300 rounded-lg text-sm focus:ring-2 focus:ring-primary-500 focus:border-transparent"
              >
                {STATUS_OPTIONS.map(opt => (
                  <option key={opt.value} value={opt.value}>{opt.label}</option>
                ))}
              </select>
            </div>

            {/* Category Filter */}
            <div>
              <label className="block text-xs font-medium text-gray-700 mb-1">
                Category
              </label>
              <select
                value={filters.category}
                onChange={(e) => handleFilterChange('category', e.target.value)}
                className="w-full px-3 py-2 border border-gray-300 rounded-lg text-sm focus:ring-2 focus:ring-primary-500 focus:border-transparent"
              >
                {CATEGORY_OPTIONS.map(opt => (
                  <option key={opt.value} value={opt.value}>{opt.label}</option>
                ))}
              </select>
            </div>

            {/* Date From */}
            <div>
              <label className="block text-xs font-medium text-gray-700 mb-1">
                From Date
              </label>
              <input
                type="date"
                value={filters.date_from}
                onChange={(e) => handleFilterChange('date_from', e.target.value)}
                className="w-full px-3 py-2 border border-gray-300 rounded-lg text-sm focus:ring-2 focus:ring-primary-500 focus:border-transparent"
              />
            </div>

            {/* Date To */}
            <div>
              <label className="block text-xs font-medium text-gray-700 mb-1">
                To Date
              </label>
              <input
                type="date"
                value={filters.date_to}
                onChange={(e) => handleFilterChange('date_to', e.target.value)}
                className="w-full px-3 py-2 border border-gray-300 rounded-lg text-sm focus:ring-2 focus:ring-primary-500 focus:border-transparent"
              />
            </div>

            {/* Apply Button */}
            <div className="flex items-end">
              <button
                onClick={() => refetch()}
                className="w-full px-4 py-2 bg-primary-600 text-white rounded-lg text-sm font-medium hover:bg-primary-700"
              >
                Apply Filters
              </button>
            </div>
          </div>
        </div>
      )}

      {/* Map Container */}
      <div className="flex-1 relative min-h-0">
        {isLoading ? (
          <div className="absolute inset-0 flex items-center justify-center bg-gray-50">
            <div className="text-center">
              <div className="inline-block animate-spin rounded-full h-12 w-12 border-b-2 border-primary-600"></div>
              <p className="mt-4 text-sm text-gray-500">Loading map...</p>
            </div>
          </div>
        ) : complaints && complaints.length > 0 ? (
          <div className="absolute inset-0">
            {console.log('🗺️ Rendering ComplaintMap with:', {
              complaintCount: complaints.length,
              sampleComplaint: complaints[0],
              firstFiveCoords: complaints.slice(0, 5).map(c => ({ id: c.id, lat: c.lat, lng: c.lng })),
              centerBeingPassed: defaultCenter
            })}
            <ComplaintMap 
              complaints={complaints} 
              center={defaultCenter}
              showHeatmap={showHeatmap}
              showClusters={showClusters}
              viewMode={viewMode}
            />
          </div>
        ) : (
          <div className="absolute inset-0 flex items-center justify-center bg-gray-50">
            <div className="text-center">
              <div className="text-6xl mb-4">🗺️</div>
              <h3 className="text-lg font-medium text-gray-900 mb-2">No Complaints to Display</h3>
              <p className="text-sm text-gray-500">
                {hasActiveFilters
                  ? 'Try adjusting your filters'
                  : 'Complaints will appear here once they are created'}
              </p>
            </div>
          </div>
        )}
      </div>
    </div>
  );
};

export default Map;
