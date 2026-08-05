import { StrictMode } from 'react'
import { createRoot } from 'react-dom/client'
import ReactDOM from 'react-dom/client'
// Add this at the absolute top of your main entry file (e.g., src/main.jsx or src/App.jsx)
import 'leaflet/dist/leaflet.css';
import './index.css'
import './styles/global.css';
import App from './App.jsx'

createRoot(document.getElementById('root')).render(
  <StrictMode>
    <App />
  </StrictMode>,
)
