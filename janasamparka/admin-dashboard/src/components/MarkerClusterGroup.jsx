import { useEffect, useRef } from 'react';
import { useMap } from 'react-leaflet';
import L from 'leaflet';
import 'leaflet.markercluster';
import 'leaflet.markercluster/dist/MarkerCluster.css';
import 'leaflet.markercluster/dist/MarkerCluster.Default.css';

const MarkerClusterGroup = ({ children, options = {} }) => {
  const map = useMap();
  const clusterGroupRef = useRef(null);

  useEffect(() => {
    // Default options
    const defaultOptions = {
      chunkedLoading: true,
      spiderfyOnMaxZoom: true,
      showCoverageOnHover: false,
      zoomToBoundsOnClick: true,
      maxClusterRadius: 80,
      disableClusteringAtZoom: 18,
      iconCreateFunction: (cluster) => {
        const count = cluster.getChildCount();
        let size = 'small';
        let className = 'marker-cluster-';

        if (count < 10) {
          size = 'small';
        } else if (count < 50) {
          size = 'medium';
        } else {
          size = 'large';
        }

        className += size;

        return L.divIcon({
          html: `<div><span>${count}</span></div>`,
          className: className,
          iconSize: L.point(40, 40)
        });
      },
      ...options
    };

    // Create cluster group
    clusterGroupRef.current = L.markerClusterGroup(defaultOptions);

    // Add to map
    map.addLayer(clusterGroupRef.current);

    // Cleanup
    return () => {
      if (clusterGroupRef.current) {
        map.removeLayer(clusterGroupRef.current);
      }
    };
  }, [map, options]);

  // Add markers to cluster group
  useEffect(() => {
    if (!clusterGroupRef.current) return;

    // Clear existing markers
    clusterGroupRef.current.clearLayers();

    // Add new markers
    // Note: In a real implementation, you would pass markers as children
    // This is a simplified version
  }, [children]);

  return null; // This component doesn't render anything itself
};

export default MarkerClusterGroup;
