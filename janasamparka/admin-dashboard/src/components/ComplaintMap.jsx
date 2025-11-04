import { useEffect, useState } from 'react';
import { MapContainer, TileLayer, Marker, Popup, useMap } from 'react-leaflet';
import { useNavigate } from 'react-router-dom';
import L from 'leaflet';
import 'leaflet/dist/leaflet.css';
import { MapPin, Calendar, User, AlertCircle } from 'lucide-react';
import HeatmapLayer from './HeatmapLayer';

// Fix for default marker icons in React-Leaflet
delete L.Icon.Default.prototype._getIconUrl;
L.Icon.Default.mergeOptions({
  iconRetinaUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.9.4/images/marker-icon-2x.png',
  iconUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.9.4/images/marker-icon.png',
  shadowUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.9.4/images/marker-shadow.png',
});

// Custom marker icons based on status
const createMarkerIcon = (status, category) => {
  const colors = {
    submitted: '#3B82F6',  // blue
    assigned: '#F59E0B',    // yellow
    in_progress: '#8B5CF6', // purple
    resolved: '#10B981',    // green
    closed: '#6B7280',      // gray
    rejected: '#EF4444'     // red
  };

  const color = colors[status] || colors.submitted;

  return L.divIcon({
    className: 'custom-marker',
    html: `
      <div style="
        background-color: ${color};
        width: 32px;
        height: 32px;
        border-radius: 50% 50% 50% 0;
        transform: rotate(-45deg);
        border: 3px solid white;
        box-shadow: 0 2px 8px rgba(0,0,0,0.3);
        display: flex;
        align-items: center;
        justify-center;
      ">
        <div style="transform: rotate(45deg); color: white; font-size: 16px;">
          📍
        </div>
      </div>
    `,
    iconSize: [32, 32],
    iconAnchor: [16, 32],
    popupAnchor: [0, -32]
  });
};

// Component to fit map bounds to all markers
const FitBounds = ({ complaints }) => {
  const map = useMap();

  useEffect(() => {
    if (complaints && complaints.length > 0) {
      const bounds = complaints
        .filter(c => c.lat && c.lng)
        .map(c => [c.lat, c.lng]);
      
      if (bounds.length > 0) {
        map.fitBounds(bounds, { padding: [50, 50] });
      }
    }
  }, [complaints, map]);

  return null;
};

const ComplaintMap = ({ 
  complaints = [], 
  center = [12.7626, 75.2150], 
  zoom = 13,
  showHeatmap = false,
  showClusters = false,
  viewMode = 'markers'
}) => {
  const navigate = useNavigate();
  const [selectedComplaint, setSelectedComplaint] = useState(null);

  // Debug logging with coordinate verification
  console.log('ComplaintMap received:', {
    complaintsCount: complaints.length,
    sampleComplaint: complaints[0],
    complaints: complaints.slice(0, 3)
  });

  // Filter complaints with valid coordinates
  const validComplaints = complaints.filter(c => c.lat && c.lng);

  console.log('ComplaintMap filtered:', {
    total: complaints.length,
    valid: validComplaints.length,
    invalid: complaints.length - validComplaints.length,
    sampleValid: validComplaints[0],
    coordinateSamples: validComplaints.slice(0, 5).map(c => ({
      id: c.id,
      title: c.title.substring(0, 30),
      lat: c.lat,
      lng: c.lng,
      position: `[${c.lat}, ${c.lng}]`,
      isValid: (c.lat >= 12 && c.lat <= 14 && c.lng >= 74 && c.lng <= 76)
    })),
    invalidSamples: complaints.filter(c => !c.lat || !c.lng).slice(0, 3).map(c => ({
      id: c.id,
      title: c.title,
      lat: c.lat,
      lng: c.lng,
      latType: typeof c.lat,
      lngType: typeof c.lng
    }))
  });

  // CRITICAL: Check if coordinates seem swapped
  if (validComplaints.length > 0) {
    const firstComplaint = validComplaints[0];
    if (firstComplaint.lat > 50 || firstComplaint.lng < 50) {
      console.error('🚨 COORDINATES APPEAR SWAPPED! lat:', firstComplaint.lat, 'lng:', firstComplaint.lng);
      console.error('Expected Karnataka: lat ~12-13, lng ~74-75');
    } else {
      console.log('✅ Coordinates look correct for Karnataka region');
    }
  }

  // Prepare heatmap data
  const heatmapPoints = validComplaints.map(c => [
    c.lat,
    c.lng,
    1.0 // intensity
  ]);

  const handleMarkerClick = (complaint) => {
    setSelectedComplaint(complaint);
  };

  const handleViewDetails = (complaintId) => {
    navigate(`/complaints/${complaintId}`);
  };

  const STATUS_LABELS = {
    submitted: 'Submitted',
    assigned: 'Assigned',
    in_progress: 'In Progress',
    resolved: 'Resolved',
    closed: 'Closed',
    rejected: 'Rejected'
  };

  const CATEGORY_LABELS = {
    road: 'Road & Infrastructure',
    water: 'Water Supply',
    electricity: 'Electricity',
    health: 'Health',
    education: 'Education',
    sanitation: 'Sanitation',
    other: 'Other'
  };

  // Ensure center is valid Karnataka coordinates
  const mapCenter = (center && center[0] >= 12 && center[0] <= 14 && center[1] >= 74 && center[1] <= 76) 
    ? center 
    : [12.8697, 74.8430]; // Mangalore center as fallback
  
  console.log('🗺️ MapContainer center:', mapCenter, 'zoom:', zoom);

  return (
    <div className="relative w-full h-full">
      <MapContainer
        center={mapCenter}
        zoom={zoom}
        style={{ height: '100%', width: '100%' }}
        className="rounded-lg"
        scrollWheelZoom={true}
        zoomControl={true}
      >
        <TileLayer
          attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
          url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
          maxZoom={19}
          minZoom={8}
        />

        {/* Fit bounds to show all markers */}
        <FitBounds complaints={validComplaints} />

        {/* Heatmap Layer */}
        {showHeatmap && viewMode === 'heatmap' && (
          <HeatmapLayer points={heatmapPoints} />
        )}

        {/* Complaint Markers */}
        {!showHeatmap && validComplaints.map((complaint) => (
          <Marker
            key={complaint.id}
            position={[complaint.lat, complaint.lng]}
            icon={createMarkerIcon(complaint.status, complaint.category)}
            eventHandlers={{
              click: () => handleMarkerClick(complaint)
            }}
          >
            <Popup maxWidth={300} className="custom-popup">
              <div className="p-2">
                {/* Title */}
                <h3 className="font-semibold text-gray-900 mb-2 text-sm">
                  {complaint.title}
                </h3>

                {/* Status Badge */}
                <div className="mb-3">
                  <span className={`inline-flex items-center px-2 py-1 rounded-full text-xs font-medium ${
                    complaint.status === 'submitted' ? 'bg-blue-100 text-blue-800' :
                    complaint.status === 'assigned' ? 'bg-yellow-100 text-yellow-800' :
                    complaint.status === 'in_progress' ? 'bg-purple-100 text-purple-800' :
                    complaint.status === 'resolved' ? 'bg-green-100 text-green-800' :
                    complaint.status === 'closed' ? 'bg-gray-100 text-gray-800' :
                    'bg-red-100 text-red-800'
                  }`}>
                    {STATUS_LABELS[complaint.status] || complaint.status}
                  </span>
                </div>

                {/* Details */}
                <div className="space-y-2 text-xs text-gray-600">
                  <div className="flex items-start gap-2">
                    <MapPin className="h-3 w-3 flex-shrink-0 mt-0.5" />
                    <span>{CATEGORY_LABELS[complaint.category] || complaint.category}</span>
                  </div>

                  <div className="flex items-start gap-2">
                    <Calendar className="h-3 w-3 flex-shrink-0 mt-0.5" />
                    <span>
                      {new Date(complaint.created_at).toLocaleDateString('en-IN', {
                        day: 'numeric',
                        month: 'short',
                        year: 'numeric'
                      })}
                    </span>
                  </div>

                  {complaint.user_name && (
                    <div className="flex items-start gap-2">
                      <User className="h-3 w-3 flex-shrink-0 mt-0.5" />
                      <span>{complaint.user_name}</span>
                    </div>
                  )}

                  {complaint.location_description && (
                    <div className="flex items-start gap-2">
                      <AlertCircle className="h-3 w-3 flex-shrink-0 mt-0.5" />
                      <span className="line-clamp-2">{complaint.location_description}</span>
                    </div>
                  )}
                </div>

                {/* View Button */}
                <button
                  onClick={() => handleViewDetails(complaint.id)}
                  className="mt-3 w-full px-3 py-1.5 bg-primary-600 text-white text-xs font-medium rounded hover:bg-primary-700 transition-colors"
                >
                  View Details
                </button>
              </div>
            </Popup>
          </Marker>
        ))}
      </MapContainer>

      {/* Legend */}
      <div className="absolute bottom-4 left-4 bg-white rounded-lg shadow-lg p-3 z-[1000]">
        <h4 className="text-xs font-semibold text-gray-900 mb-2">Status Legend</h4>
        <div className="space-y-1 text-xs">
          {Object.entries(STATUS_LABELS).map(([status, label]) => (
            <div key={status} className="flex items-center gap-2">
              <div className="w-4 h-4 rounded-full" style={{
                backgroundColor: 
                  status === 'submitted' ? '#3B82F6' :
                  status === 'assigned' ? '#F59E0B' :
                  status === 'in_progress' ? '#8B5CF6' :
                  status === 'resolved' ? '#10B981' :
                  status === 'closed' ? '#6B7280' :
                  '#EF4444'
              }}></div>
              <span className="text-gray-700">{label}</span>
            </div>
          ))}
        </div>
      </div>

      {/* Stats Overlay */}
      <div className="absolute top-4 right-4 bg-white rounded-lg shadow-lg p-3 z-[1000]">
        <div className="text-center">
          <div className="text-2xl font-bold text-gray-900">{validComplaints.length}</div>
          <div className="text-xs text-gray-500">Complaints on Map</div>
        </div>
      </div>
    </div>
  );
};

export default ComplaintMap;
