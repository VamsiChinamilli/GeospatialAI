GeospatialAI
Urban Climate Intelligence Platform

AI-powered urban climate analysis using:
• Satellite imagery
• U-Net land-cover segmentation
• LST expert system
• Geospatial analysis
• Interactive GIS visualization
• AI climate assistant

Architecture
WeatherF → Django/Daphne → Geospatial pipeline
                         ↓
                  U-Net + LST Expert
                         ↓
                 Climate Analysis
                         ↓
                    AI Assistant

Tech Stack
Backend: Django, DRF, Django Channels
Frontend: React, Vite
AI/ML: PyTorch, U-Net
Geospatial: Rasterio, GeoPandas, Planetary Computer / Earth Engine
Database: PostgreSQL/PostGIS
Model hosting: Hugging Face
