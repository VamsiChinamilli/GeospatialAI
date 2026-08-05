// src/App.jsx
import React from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import WelcomePage from './pages/WelcomePage';
import MapPage from './pages/MapPage';
import UrbanDashboard from './pages/UrbanDashboard';
import ProtectedRoute from './components/ProtectedRoute'; // Import our new gatekeeper

export default function App() {
  return (
    <Router>
      <div>
        <Routes>
          <Route path="/" element={<WelcomePage />} />
          <Route path="/map" element={<MapPage />} />
          
          {/* Wrapped the dashboard with the Route Guard */}
          <Route 
            path="/dashboard" 
            element={
              <ProtectedRoute>
                <UrbanDashboard />
              </ProtectedRoute>
            } 
          />
        </Routes>
      </div>
    </Router>
  );
}