// src/pages/MapPage.jsx
import React, { useEffect } from 'react';
import IndianMapCanvas from '../components/IndianMapCanvas';
import { useNavigate } from 'react-router-dom';
import '../styles/MapPage.css';

export default function MapPage() {
  const navigate = useNavigate();

  // Listen on window so mouse tracking works even over the Leaflet map canvas
  useEffect(() => {
    const handleMouseMove = (e) => {
      document.documentElement.style.setProperty('--mouse-x', `${e.clientX}px`);
      document.documentElement.style.setProperty('--mouse-y', `${e.clientY}px`);
    };

    window.addEventListener('mousemove', handleMouseMove);
    return () => window.removeEventListener('mousemove', handleMouseMove);
  }, []);

  const handleBBoxSelected = (bbox) => {
    console.log("Locked BBox coordinates array:", bbox);
    navigate(`/dashboard?bbox=${bbox.join(',')}`);
  };

  return (
    <div className="map-page-container">
      
      {/* Top Navigation Header Utility */}
      <header className="map-page-header">
        <div style={{ display: 'flex', alignItems: 'center', gap: '16px' }}>
          <div style={{
            padding: '8px',
            backgroundColor: 'rgba(61, 74, 54, 0.08)',
            borderRadius: '50%',
            border: '1px solid rgba(61, 74, 54, 0.15)',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center'
          }}>
            <span className="material-symbols-outlined" style={{ color: '#3d4a36', fontSize: '20px' }}>
              map
            </span>
          </div>

          <div>
            <h1 style={{ 
              fontFamily: "'Newsreader', serif",
              color: '#1e1b18', 
              margin: 0, 
              fontSize: '20px', 
              fontWeight: '600',
              lineHeight: 1.2
            }}>
              Spatial Region Selector
            </h1>
            <p style={{ 
              fontFamily: "'JetBrains Mono', monospace",
              color: '#8c8275', 
              margin: '2px 0 0 0', 
              fontSize: '11px',
              letterSpacing: '0.05em',
              textTransform: 'uppercase'
            }}>
              BOUNDING BOX MATRIX // SELECT REGIONAL FRAMEWORK
            </p>
          </div>
        </div>

        <button 
          onClick={() => navigate('/')}
          style={{
            backgroundColor: 'transparent',
            color: '#3d4a36',
            border: '1px solid #3d4a36',
            padding: '8px 18px',
            borderRadius: '9999px',
            fontSize: '12px',
            fontFamily: "'JetBrains Mono', monospace",
            fontWeight: '500',
            letterSpacing: '0.08em',
            cursor: 'pointer',
            display: 'flex',
            alignItems: 'center',
            gap: '6px',
            transition: 'all 0.2s ease'
          }}
          onMouseEnter={(e) => {
            e.currentTarget.style.backgroundColor = '#3d4a36';
            e.currentTarget.style.color = '#ffffff';
          }}
          onMouseLeave={(e) => {
            e.currentTarget.style.backgroundColor = 'transparent';
            e.currentTarget.style.color = '#3d4a36';
          }}
        >
          <span className="material-symbols-outlined" style={{ fontSize: '16px' }}>
            arrow_back
          </span>
          RETURN HOME
        </button>
      </header>

      {/* Main Map Card Area */}
      <div className="map-card-wrapper">
        <div className="map-glass-card">
          <IndianMapCanvas onBBoxSelected={handleBBoxSelected} />
        </div>
      </div>

    </div>
  );
}