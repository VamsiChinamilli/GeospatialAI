// src/pages/WelcomePage.jsx
import React, { useEffect, useRef } from 'react';
import { useNavigate } from 'react-router-dom';
import '../styles/WelcomePage.css';

export default function WelcomePage() {
  const navigate = useNavigate();
  const hudGridRef = useRef(null);

  // Mouse spotlight positioning across document and per card
  useEffect(() => {
    const handleMouseMove = (e) => {
      const x = (e.clientX / window.innerWidth) * 100;
      const y = (e.clientY / window.innerHeight) * 100;
      document.documentElement.style.setProperty('--mouse-x', `${x}%`);
      document.documentElement.style.setProperty('--mouse-y', `${y}%`);
    };

    const handleScroll = () => {
      if (hudGridRef.current) {
        const scrolled = window.pageYOffset;
        hudGridRef.current.style.transform = `translateY(${scrolled * 0.05}px)`;
      }
    };

    window.addEventListener('mousemove', handleMouseMove);
    window.addEventListener('scroll', handleScroll);

    return () => {
      window.removeEventListener('mousemove', handleMouseMove);
      window.removeEventListener('scroll', handleScroll);
    };
  }, []);

  const handleCardMouseMove = (e, cardRef) => {
    const rect = cardRef.getBoundingClientRect();
    const x = e.clientX - rect.left;
    const y = e.clientY - rect.top;
    cardRef.style.setProperty('--card-mouse-x', `${x}px`);
    cardRef.style.setProperty('--card-mouse-y', `${y}px`);
  };

  return (
    <div className="welcome-page-root">
      {/* Atmospheric Background */}
      <div className="hud-background">
        <div className="hud-grid" ref={hudGridRef}></div>
        <div className="global-spotlight"></div>
      </div>

      {/* Header */}
      <header className="welcome-header">
        <div className="header-brand">
          <div className="icon-box-primary">
            <span className="material-symbols-outlined" style={{ fontVariationSettings: "'FILL' 1" }}>
              sensors
            </span>
          </div>
          <div className="brand-details">
            <span className="brand-title">GEO-RESILIENCE MATRIX • V2.0</span>
            <div className="brand-status">
              {/*<span className="status-dot"></span>*/}
              <span className="status-text"></span>
            </div>
          </div>
        </div>

        <div className="header-actions">
          <div className="sys-metrics">
            <span>SYS: OPTIMAL</span>
            <span>ENC: AES-256</span>
          </div>
          <button className="material-symbols-outlined" style={{ background: 'none', border: 'none', cursor: 'pointer', color: 'var(--outline)' }}>
            settings
          </button>
        </div>
      </header>

      {/* Main Container */}
      <main className="welcome-main">
        {/* Hero Section */}
        <section className="hero-section">
          <div className="stability-pill">
            <div className="pulse-dot-wrapper"></div>
            <span className="stability-text">ENVIRONMENTAL STABILITY: NOMINAL</span>
          </div>

          <h1 className="hero-heading">
            URBAN HEAT ISLAND<br />
            <span className="hero-italic">COPILOT ENGINE</span>
          </h1>

          
        </section>

        {/* Interactive Feature Grid */}
        <div className="cards-grid">
          {/* Card 1 */}
          <div 
            className="spotlight-card"
            onMouseMove={(e) => handleCardMouseMove(e, e.currentTarget)}
            onClick={() => navigate('/map')}
          >
            <div className="card-icon-wrapper blue">
              <span className="material-symbols-outlined">map</span>
            </div>
            <h3 className="card-heading">Select Target Zone</h3>
            <p className="card-body">
              Isolate high-resolution urban grids for thermal profiling. Deploy multi-spectral imaging to identify heat accumulation clusters within metropolitan zones.
            </p>
            <div className="card-action-link">
              <span>GEO-TAGGING ACTIVE</span>
              <span className="material-symbols-outlined">chevron_right</span>
            </div>
          </div>

          {/* Card 2 */}
          <div 
            className="spotlight-card"
            onMouseMove={(e) => handleCardMouseMove(e, e.currentTarget)}
            onClick={() => navigate('/map')}
          >
            <div className="card-icon-wrapper green">
              <span className="material-symbols-outlined">memory</span>
            </div>
            <h3 className="card-heading">Run U-Net Matrix</h3>
            <p className="card-body">
              Execute proprietary neural network architectures to segment impervious surfaces. Calculate NDVI indices in real-time with sub-meter precision.
            </p>
            <div className="card-action-link">
              <span>NEURAL SYNC: 98%</span>
              <span className="material-symbols-outlined">chevron_right</span>
            </div>
          </div>

          {/* Card 3 */}
          <div 
            className="spotlight-card"
            onMouseMove={(e) => handleCardMouseMove(e, e.currentTarget)}
            onClick={() => navigate('/map')}
          >
            <div className="card-icon-wrapper gold">
              <span className="material-symbols-outlined">forum</span>
            </div>
            <h3 className="card-heading">Agentic Synthesis</h3>
            <p className="card-body">
              Interface with AI-driven climate advisors to derive mitigation strategies. Receive automated policy recommendations based on synthesized metrics.
            </p>
            <div className="card-action-link">
              <span>ADVISORY LINK READY</span>
              <span className="material-symbols-outlined">chevron_right</span>
            </div>
          </div>
        </div>

        {/* Map Visualization CTA Banner
        https://elements-resized.envatousercontent.com/envato-dam-assets-production/dc5543cd-20c5-4602-86b3-3a5739d45743/101e59ae-51b5-488f-8c2b-471e3af6e949.jpg?w=1600&cf_fit=scale-down&mark-alpha=18&mark=https%3A%2F%2Felements-assets.envato.com%2Fstatic%2Fwatermark4.png&q=85&format=auto&s=ced6e92b491136329cf08d2df9449e656756be0339926955546cbf764b3844c8
        */}
        <div 
          className="map-banner-cta" 
          onClick={() => navigate('/map')}
          style={{ cursor: 'pointer' }}
        >
          <div 
            className="banner-bg-image"
            style={{ 
              backgroundImage: `url('https://i.pinimg.com/1200x/4d/cc/03/4dcc033785ee5be8295320dae2cbdb8e.jpg')`
            }}
        

          ></div>
          
          <div className="banner-overlay-gradient"></div>

          <div className="banner-content">
            <div className="banner-flex-row">
              <div>
                <span className="banner-subtitle">ACTIVE SENSOR NETWORK // HYD_SEC_04</span>
                <h4 className="banner-title">Metropolitan Heat Mapping</h4>
                <p className="banner-desc">Detailed thermal analysis of heat absorption and retention across central corridors. Select a node to initiate deep analysis.</p>
              </div>
              <div>
                <div className="launch-button">
                  <span>LAUNCH ANALYSIS</span>
                  <span className="material-symbols-outlined">rocket_launch</span>
                </div>
              </div>
            </div>
          </div>
        </div>
      </main>
    </div>
  );
}