import React from 'react';
import PropTypes from 'prop-types';
import { MapContainer, TileLayer, CircleMarker, Popup, Tooltip } from 'react-leaflet';
import 'leaflet/dist/leaflet.css';

/**
 * ClusterMapView - Geographic clustering visualization for batch projects
 * 
 * Features:
 * - Displays clusters as circles (size based on complaint count)
 * - Shows cost savings from batch processing
 * - Interactive popups with cluster details
 * - Heat map coloring by density
 */
const ClusterMapView = ({ 
  clusters = [],
  center = [12.9716, 77.5946], // Bangalore default
  zoom = 12,
  onClusterClick = null
}) => {
  // Calculate color based on cluster size
  const getClusterColor = (complaintCount) => {
    if (complaintCount >= 10) return '#dc2626'; // red
    if (complaintCount >= 5) return '#ea580c'; // orange
    if (complaintCount >= 3) return '#ca8a04'; // yellow
    return '#16a34a'; // green
  };

  // Calculate radius based on complaint count
  const getClusterRadius = (complaintCount) => {
    return Math.sqrt(complaintCount) * 10 + 15; // Min 15px, scales with sqrt
  };

  // Format currency
  const formatCurrency = (amount) => {
    if (!amount) return '₹0';
    return new Intl.NumberFormat('en-IN', {
      style: 'currency',
      currency: 'INR',
      maximumFractionDigits: 0
    }).format(amount);
  };

  // Calculate savings percentage
  const getSavingsPercentage = (projectedCost, individualCost) => {
    if (!individualCost || individualCost === 0) return 0;
    return ((individualCost - projectedCost) / individualCost * 100).toFixed(1);
  };

  return (
    <div className="relative w-full h-full">
      <MapContainer
        center={center}
        zoom={zoom}
        style={{ height: '100%', width: '100%' }}
        scrollWheelZoom={true}
      >
        <TileLayer
          attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
          url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
        />

        {clusters.map((cluster, idx) => {
          const color = getClusterColor(cluster.complaint_count);
          const radius = getClusterRadius(cluster.complaint_count);
          const savings = cluster.individual_cost - cluster.projected_cost;
          const savingsPercent = getSavingsPercentage(
            cluster.projected_cost, 
            cluster.individual_cost
          );

          return (
            <CircleMarker
              key={`cluster-${idx}`}
              center={[cluster.center.lat, cluster.center.lng]}
              radius={radius}
              pathOptions={{
                fillColor: color,
                color: color,
                weight: 2,
                opacity: 0.8,
                fillOpacity: 0.4
              }}
              eventHandlers={{
                click: () => {
                  if (onClusterClick) {
                    onClusterClick(cluster);
                  }
                }
              }}
            >
              {/* Tooltip on hover */}
              <Tooltip direction="top" offset={[0, -10]} opacity={0.9}>
                <div className="text-xs">
                  <strong>{cluster.complaint_count} complaints</strong>
                  <br />
                  {cluster.category || 'Mixed categories'}
                </div>
              </Tooltip>

              {/* Popup on click */}
              <Popup>
                <div className="p-2">
                  <h3 className="font-bold text-sm mb-2 text-gray-800">
                    📍 Cluster Details
                  </h3>
                  
                  <div className="space-y-1 text-xs">
                    <div>
                      <span className="font-semibold">Complaints:</span> {cluster.complaint_count}
                    </div>
                    
                    <div>
                      <span className="font-semibold">Category:</span> {cluster.category || 'Mixed'}
                    </div>
                    
                    <div>
                      <span className="font-semibold">Radius:</span> {cluster.radius}m
                    </div>

                    {cluster.projected_cost && (
                      <>
                        <div className="border-t border-gray-200 mt-2 pt-2">
                          <div className="font-semibold text-green-700 mb-1">
                            💰 Batch Project Savings
                          </div>
                          
                          <div>
                            <span className="font-semibold">Individual Cost:</span>{' '}
                            {formatCurrency(cluster.individual_cost)}
                          </div>
                          
                          <div>
                            <span className="font-semibold">Batch Cost:</span>{' '}
                            {formatCurrency(cluster.projected_cost)}
                          </div>
                          
                          <div className="mt-1 px-2 py-1 bg-green-100 text-green-800 rounded font-bold text-center">
                            Save {formatCurrency(savings)} ({savingsPercent}%)
                          </div>
                        </div>
                      </>
                    )}

                    {cluster.complaint_ids && cluster.complaint_ids.length > 0 && (
                      <div className="border-t border-gray-200 mt-2 pt-2">
                        <div className="font-semibold mb-1">Complaint IDs:</div>
                        <div className="text-gray-600">
                          {cluster.complaint_ids.slice(0, 3).join(', ')}
                          {cluster.complaint_ids.length > 3 && ` +${cluster.complaint_ids.length - 3} more`}
                        </div>
                      </div>
                    )}

                    {onClusterClick && (
                      <button
                        onClick={() => onClusterClick(cluster)}
                        className="mt-2 w-full bg-blue-600 text-white px-3 py-1 rounded text-xs font-medium hover:bg-blue-700"
                      >
                        View Details
                      </button>
                    )}
                  </div>
                </div>
              </Popup>
            </CircleMarker>
          );
        })}
      </MapContainer>

      {/* Legend */}
      <div className="absolute bottom-4 right-4 bg-white rounded-lg shadow-lg p-3 z-[1000]">
        <h4 className="text-xs font-bold mb-2 text-gray-700">Cluster Size</h4>
        <div className="space-y-1 text-xs">
          <div className="flex items-center gap-2">
            <div className="w-4 h-4 rounded-full bg-red-600 opacity-40"></div>
            <span>10+ complaints</span>
          </div>
          <div className="flex items-center gap-2">
            <div className="w-4 h-4 rounded-full bg-orange-600 opacity-40"></div>
            <span>5-9 complaints</span>
          </div>
          <div className="flex items-center gap-2">
            <div className="w-4 h-4 rounded-full bg-yellow-600 opacity-40"></div>
            <span>3-4 complaints</span>
          </div>
          <div className="flex items-center gap-2">
            <div className="w-4 h-4 rounded-full bg-green-600 opacity-40"></div>
            <span>1-2 complaints</span>
          </div>
        </div>
      </div>
    </div>
  );
};

ClusterMapView.propTypes = {
  clusters: PropTypes.arrayOf(
    PropTypes.shape({
      center: PropTypes.shape({
        lat: PropTypes.number.isRequired,
        lng: PropTypes.number.isRequired
      }).isRequired,
      radius: PropTypes.number.isRequired,
      complaint_count: PropTypes.number.isRequired,
      category: PropTypes.string,
      projected_cost: PropTypes.number,
      individual_cost: PropTypes.number,
      complaint_ids: PropTypes.arrayOf(PropTypes.number)
    })
  ),
  center: PropTypes.arrayOf(PropTypes.number),
  zoom: PropTypes.number,
  onClusterClick: PropTypes.func
};

export default ClusterMapView;
