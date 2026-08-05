// src/pages/UrbanDashboard.jsx
import React, { useEffect } from 'react';
import { useSearchParams, useNavigate } from 'react-router-dom';
import MetricsPanel from '../components/MetricsPanel';
import ChatPanel from '../components/ChatPanel';
import { useUrbanPipeline } from '../hooks/useUrbanPipeline'; 
import { RefreshCw, ArrowLeft } from 'lucide-react';

export default function UrbanDashboard() {
  const [searchParams] = useSearchParams();
  const navigate = useNavigate();
 const bboxQuery = searchParams.get('bbox');
const sessionQuery = searchParams.get('session');

const {
  metrics,
  activeBBox,
  statusMessage,
  conversation,
  isStreaming,
  locationDetails,
  handleSendMessage
} = useUrbanPipeline({
  bboxQuery,
  sessionQuery,
});
  useEffect(() => {
    document.body.style.margin = "0";
    document.body.style.padding = "0";
    document.body.style.backgroundColor = "#f7f5ed";
    return () => {
      document.body.style.margin = "";
      document.body.style.padding = "";
    };
  }, []);

  return (
    <div style={{
      width: '100vw',
      height: '100vh',
      display: 'flex',
      flexDirection: 'column',
      backgroundColor: '#f7f5ed',
      fontFamily: 'sans-serif',
      overflow: 'hidden', 
      boxSizing: 'border-box',
      color: '#1c1917'
    }}>
      
      {/* Top Header Navigation Panel */}
      
<div
  style={{
    width: '100%',
    backgroundColor: '#f7f5ed',
    borderBottom: '1px solid #e5e7eb',
    padding: '14px 28px',
    display: 'flex',
    alignItems: 'center',
    justifyContent: 'space-between',
    boxSizing: 'border-box',
    zIndex: 10,
  }}
>
  <button
    onClick={() => navigate('/')}
    style={{
      display: 'flex',
      alignItems: 'center',
      gap: '8px',
      backgroundColor: 'transparent',
      border: 'none',
      color: '#374151',
      fontSize: '12px',
      fontFamily: 'monospace',
      letterSpacing: '0.05em',
      cursor: 'pointer',
    }}
  >
    <ArrowLeft className="w-4 h-4" />
    Home
  </button>

  <button
    onClick={() => navigate('/map')}
    style={{
      display: 'flex',
      alignItems: 'center',
      gap: '8px',
      backgroundColor: '#2d5a27',
      color: '#ffffff',
      border: '1px solid #24471f',
      padding: '8px 18px',
      borderRadius: '10px',
      fontSize: '12px',
      fontFamily: 'monospace',
      fontWeight: '600',
      letterSpacing: '0.05em',
      cursor: 'pointer',
      boxShadow: '0 2px 8px rgba(0,0,0,0.06)',
    }}
  >
    <RefreshCw className="w-3.5 h-3.5" />
    NEW SESSION
  </button>
</div>

      {/* Main Split-Screen Layout Workspace */}
      <div style={{
        flex: 1,
        width: '100%',
        display: 'flex',
        height: 'calc(100vh - 57px)', 
        minHeight: 0,
        boxSizing: 'border-box',
        overflow: 'hidden'
      }}>
        {/* Left Data Analytics Panel Column */}
        <div style={{ 
          flex: 1, 
          height: '100%', 
          overflowY: 'auto', 
          boxSizing: 'border-box'
        }}>
          <MetricsPanel 
            metrics={metrics} 
            activeBBox={activeBBox} 
            locationDetails={locationDetails} 
          />
        </div>
        
        {/* Right Interactive AI Control Console Column */}
        <div style={{ 
          width: '550px', 
          height: '100%', 
          borderLeft: '1px solid #e5e7eb', 
          backgroundColor: '#f7f5ed',
          display: 'flex',
          flexDirection: 'column',
          overflow: 'hidden'
        }}>
          {statusMessage && (
            <div style={{
  backgroundColor: '#ffffff',
  borderBottom: '1px solid #e5e7eb',
  padding: '12px 20px',
  fontSize: '12px',
  fontFamily: 'monospace',
  color: '#2d5a27',
  display: 'flex',
  alignItems: 'center',
  gap: '8px',
  width: '100%',
  boxSizing: 'border-box'
}}>
              <span style={{ width: '8px', height: '8px', borderRadius: '50%', backgroundColor: '#34d399', display: 'inline-block' }}></span>
              {statusMessage}
            </div>
          )}

          {/* Clean Scroll Wrapper Injecting the UI Panel */}
          <div style={{ flex: 1, display: 'flex', flexDirection: 'column', minHeight: 0, overflow: 'hidden' }}>
            <ChatPanel conversation={conversation} isStreaming={isStreaming} onSendMessage={handleSendMessage} />
          </div>
        </div>
      </div>

    </div>
  );
}