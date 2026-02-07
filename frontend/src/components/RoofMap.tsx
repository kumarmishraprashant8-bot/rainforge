import { useEffect, useRef, useState } from 'react';
import L from 'leaflet';
import 'leaflet/dist/leaflet.css';
import 'leaflet-draw';
import 'leaflet-draw/dist/leaflet.draw.css';

interface RoofMapProps {
    onPolygonUpdate: (area: number, geojson: any) => void;
    initialCenter?: [number, number];
    /** Map type: 'street' | 'satellite' - auto switches tile layer */
    mapType?: 'street' | 'satellite';
}

const RoofMap = ({ onPolygonUpdate, initialCenter = [28.6139, 77.2090], mapType = 'street' }: RoofMapProps) => {
    const mapRef = useRef<L.Map | null>(null);
    const mapContainerRef = useRef<HTMLDivElement>(null);
    const [area, setArea] = useState<number | null>(null);
    const [mapLoaded, setMapLoaded] = useState(false);
    const drawnItemsRef = useRef<L.FeatureGroup | null>(null);
    const streetLayerRef = useRef<L.TileLayer | null>(null);
    const satelliteLayerRef = useRef<L.TileLayer | null>(null);

    useEffect(() => {
        if (!mapContainerRef.current || mapRef.current) return;

        // Initialize map immediately with default center
        const map = L.map(mapContainerRef.current, {
            center: initialCenter,
            zoom: 17, // Slightly lower zoom for faster initial load
            zoomControl: true,
        });
        mapRef.current = map;

        // Street tiles
        const streetTileLayer = L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
            attribution: '© OpenStreetMap contributors',
            maxZoom: 19,
            keepBuffer: 2,
        });
        streetLayerRef.current = streetTileLayer;

        // Satellite tiles (Esri World Imagery)
        const satelliteTileLayer = L.tileLayer(
            'https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}',
            { attribution: '© Esri World Imagery', maxZoom: 19 }
        );
        satelliteLayerRef.current = satelliteTileLayer;

        // Add initial layer based on mapType prop
        if (mapType === 'satellite') {
            satelliteTileLayer.addTo(map);
            satelliteTileLayer.on('load', () => setMapLoaded(true));
        } else {
            streetTileLayer.addTo(map);
            streetTileLayer.on('load', () => setMapLoaded(true));
        }

        // Layer control
        const baseMaps = {
            "Street": streetTileLayer,
            "Satellite": satelliteTileLayer
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
            const areaM2 = (L as any).GeometryUtil ?
                (L as any).GeometryUtil.geodesicArea(latlngs) :
                calculateArea(latlngs);

            setArea(Math.round(areaM2));
            onPolygonUpdate(Math.round(areaM2), geoJSON.geometry);
        });

        map.on((L as any).Draw.Event.DELETED, () => {
            setArea(null);
        });

        // Non-blocking geolocation - map shows immediately, then pans when location is ready
        if (navigator.geolocation) {
            navigator.geolocation.getCurrentPosition(
                (pos) => {
                    // Smoothly fly to user location
                    map.flyTo([pos.coords.latitude, pos.coords.longitude], 18, {
                        duration: 1.5,
                        easeLinearity: 0.25
                    });
                },
                () => {
                    // Location denied - already showing default center, no action needed
                },
                { timeout: 5000, maximumAge: 60000 } // 5s timeout, cache for 1 min
            );
        }

        return () => {
            if (mapRef.current) {
                mapRef.current.remove();
                mapRef.current = null;
            }
        };
    }, []);

    // Effect to switch layers when mapType changes
    useEffect(() => {
        const map = mapRef.current;
        const streetLayer = streetLayerRef.current;
        const satelliteLayer = satelliteLayerRef.current;

        if (!map || !streetLayer || !satelliteLayer) return;

        if (mapType === 'satellite') {
            if (!map.hasLayer(satelliteLayer)) {
                map.removeLayer(streetLayer);
                map.addLayer(satelliteLayer);
            }
        } else {
            if (!map.hasLayer(streetLayer)) {
                map.removeLayer(satelliteLayer);
                map.addLayer(streetLayer);
            }
        }
    }, [mapType]);

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
            {/* Loading skeleton - shows while map tiles are loading */}
            {!mapLoaded && (
                <div className="absolute inset-0 z-[999] bg-gradient-to-br from-slate-800 via-slate-700 to-slate-800 rounded-xl flex flex-col items-center justify-center">
                    <div className="relative">
                        <div className="w-16 h-16 border-4 border-cyan-500/30 border-t-cyan-400 rounded-full animate-spin"></div>
                        <div className="absolute inset-0 flex items-center justify-center">
                            <svg className="w-6 h-6 text-cyan-400" fill="currentColor" viewBox="0 0 20 20">
                                <path fillRule="evenodd" d="M5.05 4.05a7 7 0 119.9 9.9L10 18.9l-4.95-4.95a7 7 0 010-9.9zM10 11a2 2 0 100-4 2 2 0 000 4z" clipRule="evenodd" />
                            </svg>
                        </div>
                    </div>
                    <p className="mt-4 text-gray-300 font-medium animate-pulse">Loading map...</p>
                    <p className="mt-1 text-gray-500 text-sm">Fetching satellite imagery</p>
                </div>
            )}
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
