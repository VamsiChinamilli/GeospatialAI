// src/components/IndianMapCanvas.jsx
import React, { useState, useEffect } from 'react';
import { MapContainer, TileLayer, useMap, Marker, Polyline, Polygon, useMapEvents } from 'react-leaflet';
import L from 'leaflet';
import 'leaflet/dist/leaflet.css';

// Custom Tactical Radar Node Icon
const tacticalNodeIcon = L.divIcon({
  className: 'tactical-map-node',
  html: `
    <div style="
      position: relative;
      width: 20px;
      height: 20px;
      display: flex;
      align-items: center;
      justify-content: center;
      transform: translate(-50%, -50%);
    ">
      <!-- Outer Pulsing Ring -->
      <span style="
        position: absolute;
        width: 26px;
        height: 26px;
        border-radius: 50%;
        border: 2px solid #3d4a36;
        animation: radarPing 1.8s cubic-bezier(0, 0, 0.2, 1) infinite;
        opacity: 0.8;
      "></span>
      <!-- Outer Solid Ring -->
      <span style="
        position: absolute;
        width: 14px;
        height: 14px;
        border-radius: 50%;
        background-color: rgba(254, 252, 249, 0.9);
        border: 2px solid #3d4a36;
        box-shadow: 0 2px 8px rgba(0,0,0,0.2);
      "></span>
      <!-- Inner Core -->
      <span style="
        width: 6px;
        height: 6px;
        border-radius: 50%;
        background-color: #3d4a36;
      "></span>
    </div>
  `,
  iconSize: [20, 20],
  iconAnchor: [10, 10]
});

function MapTileController({ center }) {
  const map = useMap();
  useEffect(() => {
    if (!map) return;
    const timer = setTimeout(() => map.invalidateSize(), 250);
    if (center) {
      map.setView(center, 13);
    }
    return () => clearTimeout(timer);
  }, [map, center]);
  return null;
}

function MapClickObserver({ onMapClick }) {
  useMapEvents({
    click(e) {
      const { lat, lng } = e.latlng;
      onMapClick([lat, lng]);
    },
  });
  return null;
}

export default function IndianMapCanvas({ onBBoxSelected }) {
  const [searchQuery, setSearchQuery] = useState('');
  const [mapCenter, setMapCenter] = useState([20.5937, 78.9629]);
  const [loading, setLoading] = useState(false);
  const [pickedPoints, setPickedPoints] = useState([]);

  const handleSearchSubmit = async (e) => {
    e.preventDefault();
    if (!searchQuery.trim()) return;
    setLoading(true);

    try {
      const res = await fetch(
        `https://nominatim.openstreetmap.org/search?format=json&q=${encodeURIComponent(searchQuery)}+India`
      );
      const data = await res.json();

      if (data && data.length > 0) {
        const topResult = data[0];
        setMapCenter([parseFloat(topResult.lat), parseFloat(topResult.lon)]);
      } else {
        alert("Location footprint not found inside India bounds.");
      }
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  const handleAnalyzeArea = () => {
    if (pickedPoints.length < 3) {
      alert("Please map out at least 3 points.");
      return;
    }
    const lats = pickedPoints.map(p => p[0]);
    const lngs = pickedPoints.map(p => p[1]);

    const bboxArray = [
      Math.round(Math.min(...lngs) * 10000) / 10000,
      Math.round(Math.min(...lats) * 10000) / 10000,
      Math.round(Math.max(...lngs) * 10000) / 10000,
      Math.round(Math.max(...lats) * 10000) / 10000
    ];
    onBBoxSelected(bboxArray);
  };

  return (
    <div style={{ position: 'relative', width: '100%', height: '100%', backgroundColor: '#f7f3ec' }}>
      
      {/* Keyframes animation tag */}
      <style>{`
        @keyframes radarPing {
          0% {
            transform: scale(0.8);
            opacity: 0.9;
          }
          100% {
            transform: scale(2.2);
            opacity: 0;
          }
        }
      `}</style>

      {/* Glassmorphic Search Bar */}
      <div style={{ 
        position: 'absolute', 
        top: '20px', 
        left: '50%', 
        transform: 'translateX(-50%)', 
        zIndex: 9999, 
        width: '90%', 
        maxWidth: '520px' 
      }}>
        <form 
          onSubmit={handleSearchSubmit} 
          style={{ 
            display: 'flex', 
            gap: '10px', 
            backgroundColor: 'rgba(254, 252, 249, 0.88)', 
            backdropFilter: 'blur(16px)',
            WebkitBackdropFilter: 'blur(16px)',
            border: '1px solid rgba(224, 214, 201, 0.9)', 
            padding: '8px 12px', 
            borderRadius: '16px',
            boxShadow: '0 12px 30px rgba(30, 27, 24, 0.12)'
          }}
        >
          <input
            type="text"
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            placeholder="Search city or zone (e.g., Tanuku, Hyderabad)..."
            style={{ 
              flex: 1, 
              backgroundColor: 'transparent', 
              border: 'none', 
              outline: 'none', 
              color: '#1e1b18', 
              fontSize: '13px',
              fontFamily: "'Work Sans', sans-serif"
            }}
          />
          <button
            type="submit"
            disabled={loading}
            style={{ 
              backgroundColor: '#3d4a36', 
              color: '#ffffff', 
              fontWeight: '600', 
              fontFamily: "'JetBrains Mono', monospace",
              letterSpacing: '0.05em',
              border: 'none', 
              padding: '8px 20px', 
              borderRadius: '10px', 
              fontSize: '11px', 
              cursor: 'pointer',
              textTransform: 'uppercase'
            }}
          >
            {loading ? 'Locating...' : 'Locate'}
          </button>
        </form>
      </div>

      {/* Map workspace */}
      <div style={{ width: '100%', height: '100%', position: 'relative', zIndex: 10 }}>
        <MapContainer 
          center={mapCenter} 
          zoom={5} 
          style={{ width: '100%', height: '100%' }}
          zoomControl={true}
        >
          <TileLayer
            attribution='&copy; Google Maps'
            url="https://mt1.google.com/vt/lyrs=y&x={x}&y={y}&z={z}"
          />
          
          <MapTileController center={mapCenter} />
          <MapClickObserver onMapClick={(pt) => setPickedPoints([...pickedPoints, pt])} />

          {pickedPoints.map((point, index) => (
            <Marker key={index} position={point} icon={tacticalNodeIcon} />
          ))}

          {/* Polyline connecting points */}
          {pickedPoints.length === 2 && (
            <Polyline 
              positions={pickedPoints} 
              pathOptions={{ 
                color: '#ffffff', 
                weight: 2.5, 
                dashArray: '6, 6' 
              }} 
            />
          )}

          {/* Glassmorphic Polygon Selection Overlay */}
          {pickedPoints.length >= 3 && (
            <Polygon 
              positions={pickedPoints} 
              pathOptions={{ 
                color: '#ffffff',           /* Crisp white vector border */
                weight: 2, 
                dashArray: '4, 4',          /* Dashed tactical bounding border */
                fillColor: '#ffffff',       /* White fill with low opacity creates frosted glass effect over imagery */
                fillOpacity: 0.25 
              }} 
            />
          )}
        </MapContainer>
      </div>

      {/* Boundary Dock */}
      <div style={{ 
        position: 'absolute', 
        bottom: '24px', 
        right: '24px', 
        zIndex: 9999, 
        display: 'flex', 
        flexDirection: 'column', 
        gap: '10px', 
        backgroundColor: 'rgba(254, 252, 249, 0.92)', 
        backdropFilter: 'blur(16px)',
        WebkitBackdropFilter: 'blur(16px)',
        border: '1px solid rgba(224, 214, 201, 0.9)', 
        padding: '16px', 
        borderRadius: '16px', 
        minWidth: '250px',
        boxShadow: '0 12px 30px rgba(30, 27, 24, 0.12)'
      }}>
        <div style={{ 
          display: 'flex', 
          justify: 'space-between', 
          alignItems: 'center', 
          fontSize: '11px', 
          color: '#8c8275', 
          borderBottom: '1px solid rgba(140, 130, 117, 0.2)', 
          paddingBottom: '8px', 
          fontFamily: "'JetBrains Mono', monospace",
          letterSpacing: '0.05em'
        }}>
          <span>BOUNDARY PLANNER</span>
          <span style={{ color: '#3d4a36', fontWeight: 'bold' }}>{pickedPoints.length} NODES</span>
        </div>

        <div style={{ display: 'flex', gap: '8px', marginTop: '4px' }}>
          <button
            type="button"
            onClick={() => setPickedPoints([])}
            disabled={pickedPoints.length === 0}
            style={{ 
              flex: 1, 
              backgroundColor: 'rgba(140, 130, 117, 0.12)', 
              color: '#1e1b18', 
              border: '1px solid rgba(140, 130, 117, 0.25)', 
              padding: '8px', 
              borderRadius: '8px', 
              fontSize: '12px', 
              fontFamily: "'Work Sans', sans-serif",
              cursor: pickedPoints.length === 0 ? 'not-allowed' : 'pointer', 
              opacity: pickedPoints.length === 0 ? 0.4 : 1 
            }}
          >
            Reset
          </button>

          <button
            type="button"
            onClick={handleAnalyzeArea}
            disabled={pickedPoints.length < 3}
            style={{ 
              flex: 1.5, 
              backgroundColor: '#3d4a36', 
              color: '#ffffff', 
              border: 'none', 
              padding: '8px', 
              borderRadius: '8px', 
              fontSize: '12px', 
              fontWeight: '600', 
              fontFamily: "'Work Sans', sans-serif",
              cursor: pickedPoints.length < 3 ? 'not-allowed' : 'pointer', 
              opacity: pickedPoints.length < 3 ? 0.4 : 1 
            }}
          >
            Analyze Area
          </button>
        </div>
      </div>

    </div>
  );
}