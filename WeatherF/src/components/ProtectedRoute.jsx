import React from 'react';
import { Navigate, useLocation, useSearchParams } from 'react-router-dom';

export default function ProtectedRoute({ children }) {
const location = useLocation();
const [searchParams] = useSearchParams();

const bbox = searchParams.get('bbox');
const session = searchParams.get('session');

// Allow access if either a new bbox analysis
// or an existing saved session is present.
const isAllowed =
Boolean(bbox) ||
Boolean(session);

if (!isAllowed) {
return <Navigate to="/" replace />;
}

return children;
}












/* // src/components/ProtectedRoute.jsx
import React from 'react';
import { Navigate, useLocation } from 'react-router-dom';

export default function ProtectedRoute({ children }) {
  const location = useLocation();
  const searchParams = new URLSearchParams(location.search);
  const bbox = searchParams.get('bbox');

  // Check if a valid spatial footprint parameter exists in the URL
  if (!bbox) {
    console.warn("🛡️ Security Guard: Direct access to /dashboard denied. No spatial bounding box parameters located. Ejecting to home platform.");
    
    // Redirect to the Welcome page, while keeping history tracking clean
    return <Navigate to="/" replace />;
  }

  // If the parameter exists, let the dashboard mount seamlessly
  return children;
} */