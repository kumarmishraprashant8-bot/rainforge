/**
 * AR Roof Measurement Module
 * Camera-based roof area estimation using AR
 */

import React, { useEffect, useRef, useState, useCallback } from 'react';

// WebXR types (minimal, for TypeScript compatibility)
declare global {
    interface Navigator {
        xr?: {
            isSessionSupported(mode: string): Promise<boolean>;
            requestSession(mode: string, options?: any): Promise<any>;
        };
    }
}

// Types
interface Point3D {
    x: number;
    y: number;
    z: number;
}

interface RoofMeasurement {
    area_sqm: number;
    perimeter_m: number;
    vertices: Point3D[];
    confidence: number;
    roof_type: 'flat' | 'sloped' | 'complex';
}

interface ARSession {
    active: boolean;
    supported: boolean;
    error?: string;
}

/**
 * Check WebXR AR support
 */
export async function checkARSupport(): Promise<boolean> {
    if (!navigator.xr) {
        return false;
    }

    try {
        return await navigator.xr.isSessionSupported('immersive-ar');
    } catch {
        return false;
    }
}

/**
 * AR Roof Measurement Component
 */
export function ARRoofMeasurement({
    onMeasurementComplete,
    onError,
}: {
    onMeasurementComplete: (measurement: RoofMeasurement) => void;
    onError: (error: string) => void;
}) {
    const containerRef = useRef<HTMLDivElement>(null);
    const canvasRef = useRef<HTMLCanvasElement>(null);
    const [session, setSession] = useState<ARSession>({ active: false, supported: false });
    const [vertices, setVertices] = useState<Point3D[]>([]);
    const [measuring, setMeasuring] = useState(false);
    const [currentMeasurement, setCurrentMeasurement] = useState<RoofMeasurement | null>(null);

    // Check AR support on mount
    useEffect(() => {
        checkARSupport().then(supported => {
            setSession(prev => ({ ...prev, supported }));
        });
    }, []);

    // Start AR session
    const startAR = useCallback(async () => {
        if (!navigator.xr) {
            onError('WebXR not supported');
            return;
        }

        try {
            const xrSession = await navigator.xr.requestSession('immersive-ar', {
                requiredFeatures: ['hit-test', 'dom-overlay'],
                domOverlay: { root: containerRef.current! },
            });

            setSession({ active: true, supported: true });
            setMeasuring(true);

            // Session ended handler
            xrSession.addEventListener('end', () => {
                setSession(prev => ({ ...prev, active: false }));
                setMeasuring(false);
            });

            // Start render loop (simplified)
            // In production, would use Three.js/Babylon.js for full AR rendering

        } catch (error: any) {
            onError(error.message || 'Failed to start AR');
            setSession(prev => ({ ...prev, error: error.message }));
        }
    }, [onError]);

    // Add vertex point
    const addVertex = useCallback((point: Point3D) => {
        setVertices(prev => [...prev, point]);
    }, []);

    // Calculate area from vertices
    const calculateArea = useCallback((points: Point3D[]): number => {
        if (points.length < 3) return 0;

        // Shoelace formula for 2D polygon area
        let area = 0;
        const n = points.length;

        for (let i = 0; i < n; i++) {
            const j = (i + 1) % n;
            area += points[i].x * points[j].z;
            area -= points[j].x * points[i].z;
        }

        return Math.abs(area) / 2;
    }, []);

    // Calculate perimeter
    const calculatePerimeter = useCallback((points: Point3D[]): number => {
        if (points.length < 2) return 0;

        let perimeter = 0;
        const n = points.length;

        for (let i = 0; i < n; i++) {
            const j = (i + 1) % n;
            const dx = points[j].x - points[i].x;
            const dy = points[j].y - points[i].y;
            const dz = points[j].z - points[i].z;
            perimeter += Math.sqrt(dx * dx + dy * dy + dz * dz);
        }

        return perimeter;
    }, []);

    // Complete measurement
    const completeMeasurement = useCallback(() => {
        if (vertices.length < 3) {
            onError('At least 3 points required');
            return;
        }

        const area = calculateArea(vertices);
        const perimeter = calculatePerimeter(vertices);

        // Determine roof type from vertex heights
        const heights = vertices.map(v => v.y);
        const heightVariance = Math.max(...heights) - Math.min(...heights);
        const roofType = heightVariance < 0.5 ? 'flat' : heightVariance < 2 ? 'sloped' : 'complex';

        const measurement: RoofMeasurement = {
            area_sqm: Math.round(area * 100) / 100,
            perimeter_m: Math.round(perimeter * 100) / 100,
            vertices: vertices,
            confidence: 0.85,
            roof_type: roofType,
        };

        setCurrentMeasurement(measurement);
        onMeasurementComplete(measurement);
    }, [vertices, calculateArea, calculatePerimeter, onMeasurementComplete, onError]);

    // Reset measurement
    const reset = useCallback(() => {
        setVertices([]);
        setCurrentMeasurement(null);
    }, []);

    // End AR session
    const endAR = useCallback(() => {
        setSession(prev => ({ ...prev, active: false }));
        setMeasuring(false);
    }, []);

    // Fallback for non-AR devices
    if (!session.supported) {
        return (
            <div className="ar-fallback">
                <div className="ar-fallback__icon">📐</div>
                <h3>AR Not Available</h3>
                <p>Your device doesn't support AR measurement.</p>
                <p>Please use manual measurement or try on a compatible device.</p>

                <div className="manual-input">
                    <h4>Manual Entry</h4>
                    <div className="form-group">
                        <label>Roof Length (meters)</label>
                        <input type="number" id="roof-length" placeholder="e.g., 10" />
                    </div>
                    <div className="form-group">
                        <label>Roof Width (meters)</label>
                        <input type="number" id="roof-width" placeholder="e.g., 8" />
                    </div>
                    <button
                        className="btn btn-primary"
                        onClick={() => {
                            const length = parseFloat((document.getElementById('roof-length') as HTMLInputElement).value);
                            const width = parseFloat((document.getElementById('roof-width') as HTMLInputElement).value);

                            if (length && width) {
                                onMeasurementComplete({
                                    area_sqm: length * width,
                                    perimeter_m: 2 * (length + width),
                                    vertices: [],
                                    confidence: 1.0,
                                    roof_type: 'flat'
                                });
                            }
                        }}
                    >
                        Calculate Area
                    </button>
                </div>
            </div>
        );
    }

    return (
        <div ref={containerRef} className="ar-measurement">
            <canvas ref={canvasRef} className="ar-canvas" />

            {/* AR UI Overlay */}
            <div className="ar-overlay">
                {/* Status */}
                <div className="ar-status">
                    {measuring ? (
                        <span className="status-active">📍 Tap to add corner points</span>
                    ) : (
                        <span className="status-ready">Ready to measure</span>
                    )}
                </div>

                {/* Vertex count */}
                <div className="ar-vertex-count">
                    Points: {vertices.length}
                </div>

                {/* Current measurement */}
                {currentMeasurement && (
                    <div className="ar-measurement-result">
                        <div className="result-area">
                            <span className="label">Area</span>
                            <span className="value">{currentMeasurement.area_sqm} m²</span>
                        </div>
                        <div className="result-perimeter">
                            <span className="label">Perimeter</span>
                            <span className="value">{currentMeasurement.perimeter_m} m</span>
                        </div>
                        <div className="result-type">
                            <span className="label">Roof Type</span>
                            <span className="value">{currentMeasurement.roof_type}</span>
                        </div>
                    </div>
                )}

                {/* Controls */}
                <div className="ar-controls">
                    {!session.active ? (
                        <button className="btn btn-ar-start" onClick={startAR}>
                            📱 Start AR Measurement
                        </button>
                    ) : (
                        <>
                            <button
                                className="btn btn-ar-complete"
                                onClick={completeMeasurement}
                                disabled={vertices.length < 3}
                            >
                                ✅ Complete
                            </button>
                            <button className="btn btn-ar-reset" onClick={reset}>
                                🔄 Reset
                            </button>
                            <button className="btn btn-ar-end" onClick={endAR}>
                                ❌ Exit AR
                            </button>
                        </>
                    )}
                </div>
            </div>

            <style>{`
        .ar-measurement {
          position: relative;
          width: 100%;
          height: 100vh;
          background: #000;
        }
        
        .ar-canvas {
          width: 100%;
          height: 100%;
        }
        
        .ar-overlay {
          position: absolute;
          top: 0;
          left: 0;
          right: 0;
          bottom: 0;
          pointer-events: none;
          display: flex;
          flex-direction: column;
          justify-content: space-between;
          padding: 20px;
        }
        
        .ar-status {
          background: rgba(0,0,0,0.7);
          color: white;
          padding: 12px 20px;
          border-radius: 25px;
          text-align: center;
          align-self: center;
        }
        
        .ar-vertex-count {
          position: absolute;
          top: 80px;
          right: 20px;
          background: rgba(0,0,0,0.7);
          color: #0ea5e9;
          padding: 8px 16px;
          border-radius: 20px;
          font-weight: bold;
        }
        
        .ar-measurement-result {
          background: rgba(255,255,255,0.95);
          border-radius: 16px;
          padding: 20px;
          display: grid;
          grid-template-columns: repeat(3, 1fr);
          gap: 15px;
          pointer-events: auto;
        }
        
        .ar-measurement-result .label {
          display: block;
          font-size: 12px;
          color: #64748b;
          text-transform: uppercase;
        }
        
        .ar-measurement-result .value {
          display: block;
          font-size: 24px;
          font-weight: bold;
          color: #0ea5e9;
        }
        
        .ar-controls {
          display: flex;
          gap: 10px;
          justify-content: center;
          pointer-events: auto;
        }
        
        .ar-controls .btn {
          padding: 15px 25px;
          border-radius: 30px;
          font-size: 16px;
          font-weight: 600;
          border: none;
          cursor: pointer;
          transition: transform 0.2s;
        }
        
        .btn-ar-start {
          background: linear-gradient(135deg, #0ea5e9, #7c3aed);
          color: white;
          font-size: 18px;
        }
        
        .btn-ar-complete {
          background: #10b981;
          color: white;
        }
        
        .btn-ar-reset {
          background: #f59e0b;
          color: white;
        }
        
        .btn-ar-end {
          background: #ef4444;
          color: white;
        }
        
        .btn:hover {
          transform: scale(1.05);
        }
        
        .btn:disabled {
          opacity: 0.5;
          cursor: not-allowed;
        }
        
        .ar-fallback {
          padding: 40px;
          text-align: center;
          background: #f8fafc;
          border-radius: 16px;
        }
        
        .ar-fallback__icon {
          font-size: 60px;
          margin-bottom: 20px;
        }
        
        .manual-input {
          margin-top: 30px;
          padding-top: 30px;
          border-top: 1px solid #e2e8f0;
        }
        
        .form-group {
          margin-bottom: 15px;
        }
        
        .form-group label {
          display: block;
          margin-bottom: 5px;
          font-weight: 500;
        }
        
        .form-group input {
          width: 100%;
          padding: 12px;
          border: 1px solid #cbd5e1;
          border-radius: 8px;
          font-size: 16px;
        }
        
        .btn-primary {
          background: #0ea5e9;
          color: white;
          padding: 12px 30px;
          border: none;
          border-radius: 8px;
          font-size: 16px;
          cursor: pointer;
          margin-top: 10px;
        }
      `}</style>
        </div>
    );
}

export default ARRoofMeasurement;
