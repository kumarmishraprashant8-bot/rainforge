import { useEffect, useRef, useState } from 'react';
import L from 'leaflet';
import 'leaflet/dist/leaflet.css';
import 'leaflet-draw';
import 'leaflet-draw/dist/leaflet.draw.css';

interface RoofMapProps {
    onPolygonUpdate: (area: number, geojson: any) => void;
    initialCenter?: [number, number];
}

const RoofMap = ({ onPolygonUpdate, initialCenter = [28.6139, 77.2090] }: RoofMapProps) => {
    const mapRef = useRef<L.Map | null>(null);
    const mapContainerRef = useRef<HTMLDivElement>(null);
    const [area, setArea] = useState<number | null>(null);
    const drawnItemsRef = useRef<L.FeatureGroup | null>(null);

    useEffect(() => {
        if (!mapContainerRef.current || mapRef.current) return;

        // Initialize map
        const map = L.map(mapContainerRef.current, {
            center: initialCenter,
            zoom: 18,
            zoomControl: true,
        });
        mapRef.current = map;

        // Add OpenStreetMap tiles
        L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
            attribution: '© OpenStreetMap contributors',
            maxZoom: 21,
        }).addTo(map);

        // Add satellite imagery option
        const satellite = L.tileLayer(
            'https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}',
            { attribution: '© Esri', maxZoom: 21 }
        );

        // Layer control
        const baseMaps = {
            "Street": L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
                attribution: '© OpenStreetMap',
                maxZoom: 21,
            }),
            "Satellite": satellite
        };
        L.control.layers(baseMaps).addTo(map);

        // Initialize feature group for drawn items
        const drawnItems = new L.FeatureGroup();
        map.addLayer(drawnItems);
        drawnItemsRef.current = drawnItems;

        // Initialize draw control
        const drawControl = new (L.Control as any).Draw({
            position: 'topright',
            draw: {
                polyline: false,
                rectangle: {
                    shapeOptions: {
                        color: '#06b6d4',
                        fillColor: '#06b6d4',
                        fillOpacity: 0.3,
                        weight: 3
                    }
                },
                polygon: {
                    allowIntersection: false,
                    shapeOptions: {
                        color: '#06b6d4',
                        fillColor: '#06b6d4',
                        fillOpacity: 0.3,
                        weight: 3
                    }
                },
                circle: false,
                circlemarker: false,
                marker: false
            },
            edit: {
                featureGroup: drawnItems,
                remove: true
            }
        });
        map.addControl(drawControl);

        // Handle draw events
        map.on((L as any).Draw.Event.CREATED, (e: any) => {
            const layer = e.layer;

            // Clear previous drawings
            drawnItems.clearLayers();
            drawnItems.addLayer(layer);

            // Calculate area
            const latlngs = layer.getLatLngs()[0];
            const polygon = L.polygon(latlngs);
            const geoJSON = polygon.toGeoJSON();

            // Calculate area in square meters using Leaflet's method
            const areaM2 = L.GeometryUtil ?
                (L as any).GeometryUtil.geodesicArea(latlngs) :
                calculateArea(latlngs);

            setArea(Math.round(areaM2));
            onPolygonUpdate(Math.round(areaM2), geoJSON.geometry);
        });

        map.on((L as any).Draw.Event.DELETED, () => {
            setArea(null);
        });

        // Try to get user location
        if (navigator.geolocation) {
            navigator.geolocation.getCurrentPosition(
                (pos) => {
                    map.setView([pos.coords.latitude, pos.coords.longitude], 18);
                },
                () => {
                    // Default to Delhi if location denied
                    map.setView(initialCenter, 18);
                }
            );
        }

        return () => {
            if (mapRef.current) {
                mapRef.current.remove();
                mapRef.current = null;
            }
        };
    }, []);

    // Simple area calculation fallback
    const calculateArea = (latlngs: L.LatLng[]): number => {
        const R = 6371000; // Earth radius in meters
        let area = 0;
        const len = latlngs.length;

        for (let i = 0; i < len; i++) {
            const j = (i + 1) % len;
            const lat1 = latlngs[i].lat * Math.PI / 180;
            const lat2 = latlngs[j].lat * Math.PI / 180;
            const lng1 = latlngs[i].lng * Math.PI / 180;
            const lng2 = latlngs[j].lng * Math.PI / 180;

            area += (lng2 - lng1) * (2 + Math.sin(lat1) + Math.sin(lat2));
        }

        return Math.abs(area * R * R / 2);
    };

    return (
        <div className="relative w-full h-full">
            <div ref={mapContainerRef} className="w-full h-full rounded-xl" />

            {/* Area display overlay */}
            {area && (
                <div className="absolute top-4 left-4 bg-slate-900/90 backdrop-blur text-white px-4 py-3 rounded-xl shadow-xl z-[1000]">
                    <div className="text-xs text-gray-400 mb-1">Roof Area</div>
                    <div className="text-2xl font-black text-cyan-400">{area.toLocaleString()} m²</div>
                </div>
            )}

            {/* Instructions */}
            <div className="absolute bottom-4 left-4 right-4 bg-slate-900/90 backdrop-blur text-white p-4 rounded-xl shadow-xl z-[1000]">
                <div className="flex items-center justify-between">
                    <div>
                        <div className="font-semibold mb-1">🎯 Draw Your Roof</div>
                        <div className="text-sm text-gray-300">
                            Use the ▢ or ⬠ tools on the right to outline your roof. Click to add points, double-click to finish.
                        </div>
                    </div>
                    {area && (
                        <div className="text-green-400 font-semibold flex items-center gap-2">
                            <div className="w-2 h-2 bg-green-400 rounded-full animate-pulse"></div>
                            Ready!
                        </div>
                    )}
                </div>
            </div>
        </div>
    );
};

export default RoofMap;
