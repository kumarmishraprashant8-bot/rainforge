import React, { useEffect, useRef, useState } from 'react';
import mapboxgl from 'mapbox-gl';
import MapboxDraw from '@mapbox/mapbox-gl-draw';
import '@mapbox/mapbox-gl-draw/dist/mapbox-gl-draw.css';
import 'mapbox-gl/dist/mapbox-gl.css';

// Use a placeholder if env var is missing to avoid crashing, 
// but Mapbox will fail to load tiles without a valid token.
// Ideally user provides one in .env
mapboxgl.accessToken = import.meta.env.VITE_MAPBOX_TOKEN || 'pk.placeholder';

interface MapEditorProps {
    onPolygonUpdate: (area: number, geojson: any) => void;
    initialCenter?: [number, number]; // lng, lat
}

const MapEditor: React.FC<MapEditorProps> = ({ onPolygonUpdate, initialCenter = [-74.5, 40] }) => {
    const mapContainer = useRef<HTMLDivElement>(null);
    const map = useRef<mapboxgl.Map | null>(null);
    const draw = useRef<MapboxDraw | null>(null);
    const [mapLoaded, setMapLoaded] = useState(false);

    useEffect(() => {
        if (map.current) return;
        if (!mapContainer.current) return;

        map.current = new mapboxgl.Map({
            container: mapContainer.current,
            style: 'mapbox://styles/mapbox/satellite-streets-v12', // Satellite for roof visibility
            center: initialCenter,
            zoom: 18,
        });

        draw.current = new MapboxDraw({
            displayControlsDefault: false,
            controls: {
                polygon: true,
                trash: true
            },
            defaultMode: 'draw_polygon'
        });

        map.current.addControl(draw.current);

        map.current.on('load', () => {
            setMapLoaded(true);
        });

        const updateArea = (e: any) => {
            const data = draw.current?.getAll();
            if (data && data.features.length > 0) {
                // Simple area calc or use turf/area (omitted for brevity, assume simple approximation or backend calc)
                // For MVP, we pass the GeoJSON to backend to calculate accurate area via PostGIS
                // But for UI feedback, we might want turf.js. 
                // For now, just pass geojson.
                onPolygonUpdate(0, data.features[0].geometry);
            }
        };

        map.current.on('draw.create', updateArea);
        map.current.on('draw.delete', updateArea);
        map.current.on('draw.update', updateArea);

    }, [initialCenter, onPolygonUpdate]);

    return (
        <div className="relative w-full h-full rounded-lg overflow-hidden shadow-lg border border-gray-200">
            {!mapLoaded && (
                <div className="absolute inset-0 flex items-center justify-center bg-gray-100 z-10 opacity-75">
                    <span className="text-gray-500 animate-pulse">Loading Map...</span>
                </div>
            )}
            <div ref={mapContainer} className="w-full h-full" />

            {/* Overlay Instructions */}
            <div className="absolute top-4 left-4 bg-white/90 p-3 rounded shadow-md text-sm max-w-xs z-10">
                <p className="font-semibold text-gray-800">Draw Your Roof</p>
                <p className="text-gray-600 mt-1">Click points to outline the roof area. Double click to finish.</p>
            </div>
        </div>
    );
};

export default MapEditor;
