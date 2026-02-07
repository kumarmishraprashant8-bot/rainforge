import { useState, useEffect, useRef } from 'react';
import './ARTankPlacement.css';

interface TankModel {
    id: string;
    name: string;
    capacity: number;
    dimensions: { width: number; height: number; depth: number };
    color: string;
}

const TANK_MODELS: TankModel[] = [
    { id: 'small', name: 'Small (1000L)', capacity: 1000, dimensions: { width: 1.2, height: 1.5, depth: 1.2 }, color: '#3b82f6' },
    { id: 'medium', name: 'Medium (2000L)', capacity: 2000, dimensions: { width: 1.5, height: 2.0, depth: 1.5 }, color: '#0ea5e9' },
    { id: 'large', name: 'Large (5000L)', capacity: 5000, dimensions: { width: 2.0, height: 2.5, depth: 2.0 }, color: '#0284c7' },
    { id: 'xlarge', name: 'Extra Large (10000L)', capacity: 10000, dimensions: { width: 2.5, height: 3.0, depth: 2.5 }, color: '#0369a1' },
];

type ARMode = 'loading' | 'unsupported' | 'ready' | 'active' | 'fallback';

export default function ARTankPlacement() {
    const [mode, setMode] = useState<ARMode>('loading');
    const [selectedTank, setSelectedTank] = useState<TankModel>(TANK_MODELS[1]);
    const [tankScale, setTankScale] = useState(1);
    const [tankRotation, setTankRotation] = useState(0);
    const [isPlaced, setIsPlaced] = useState(false);
    const [showMeasurements, setShowMeasurements] = useState(true);
    const videoRef = useRef<HTMLVideoElement>(null);
    const canvasRef = useRef<HTMLCanvasElement>(null);

    useEffect(() => {
        checkARSupport();
    }, []);

    const checkARSupport = async () => {
        // Check for WebXR support
        if ('xr' in navigator) {
            try {
                const supported = await (navigator as any).xr.isSessionSupported('immersive-ar');
                if (supported) {
                    setMode('ready');
                    return;
                }
            } catch (e) {
                console.log('WebXR not available:', e);
            }
        }

        // Fallback to camera-based overlay
        if (typeof navigator.mediaDevices?.getUserMedia === 'function') {
            setMode('fallback');
        } else {
            setMode('unsupported');
        }
    };

    const startCamera = async () => {
        try {
            const stream = await navigator.mediaDevices.getUserMedia({
                video: { facingMode: 'environment', width: { ideal: 1920 }, height: { ideal: 1080 } }
            });

            if (videoRef.current) {
                videoRef.current.srcObject = stream;
                await videoRef.current.play();
                setMode('active');
            }
        } catch (error) {
            console.error('Camera access failed:', error);
            setMode('unsupported');
        }
    };

    const stopCamera = () => {
        if (videoRef.current && videoRef.current.srcObject) {
            const stream = videoRef.current.srcObject as MediaStream;
            stream.getTracks().forEach(track => track.stop());
            videoRef.current.srcObject = null;
        }
        setMode('fallback');
        setIsPlaced(false);
    };

    const placeTank = () => {
        setIsPlaced(true);
    };

    const captureScreenshot = () => {
        if (!canvasRef.current || !videoRef.current) return;

        const canvas = canvasRef.current;
        const ctx = canvas.getContext('2d');
        if (!ctx) return;

        canvas.width = videoRef.current.videoWidth;
        canvas.height = videoRef.current.videoHeight;

        // Draw video frame
        ctx.drawImage(videoRef.current, 0, 0);

        // Draw tank overlay if placed
        if (isPlaced) {
            const centerX = canvas.width / 2;
            const centerY = canvas.height / 2;
            const tankWidth = selectedTank.dimensions.width * 100 * tankScale;
            const tankHeight = selectedTank.dimensions.height * 100 * tankScale;

            ctx.save();
            ctx.translate(centerX, centerY);
            ctx.rotate((tankRotation * Math.PI) / 180);

            // Draw tank body
            ctx.fillStyle = selectedTank.color + '80';
            ctx.strokeStyle = selectedTank.color;
            ctx.lineWidth = 3;
            ctx.fillRect(-tankWidth / 2, -tankHeight / 2, tankWidth, tankHeight);
            ctx.strokeRect(-tankWidth / 2, -tankHeight / 2, tankWidth, tankHeight);

            // Draw label
            ctx.fillStyle = '#ffffff';
            ctx.font = 'bold 16px Inter';
            ctx.textAlign = 'center';
            ctx.fillText(selectedTank.name, 0, 0);

            ctx.restore();
        }

        // Download
        const link = document.createElement('a');
        link.download = `rainforge-ar-${Date.now()}.png`;
        link.href = canvas.toDataURL('image/png');
        link.click();
    };

    const renderTankPreview = () => {
        const { width, height, depth } = selectedTank.dimensions;
        const scaledWidth = width * tankScale;
        const scaledHeight = height * tankScale;

        return (
            <div className="ar-tank-preview" style={{ transform: `rotate(${tankRotation}deg)` }}>
                <div
                    className="ar-tank-3d"
                    style={{
                        '--tank-color': selectedTank.color,
                        '--tank-width': `${scaledWidth * 60}px`,
                        '--tank-height': `${scaledHeight * 60}px`,
                    } as React.CSSProperties}
                >
                    <div className="tank-face tank-front"></div>
                    <div className="tank-face tank-back"></div>
                    <div className="tank-face tank-left"></div>
                    <div className="tank-face tank-right"></div>
                    <div className="tank-face tank-top"></div>
                    <div className="tank-face tank-bottom"></div>
                </div>

                {showMeasurements && (
                    <div className="ar-measurements">
                        <span className="measure-width">{(scaledWidth).toFixed(1)}m</span>
                        <span className="measure-height">{(scaledHeight).toFixed(1)}m</span>
                        <span className="measure-depth">{(depth * tankScale).toFixed(1)}m</span>
                    </div>
                )}
            </div>
        );
    };

    if (mode === 'loading') {
        return (
            <div className="ar-container ar-loading">
                <div className="ar-spinner"></div>
                <p>Checking AR capabilities...</p>
            </div>
        );
    }

    if (mode === 'unsupported') {
        return (
            <div className="ar-container ar-unsupported">
                <div className="ar-icon">📷</div>
                <h3>AR Not Available</h3>
                <p>Your device doesn't support AR features. Please use a modern mobile device with camera access.</p>
            </div>
        );
    }

    return (
        <div className="ar-container">
            <div className="ar-header">
                <h2>🥽 AR Tank Placement</h2>
                <p>Visualize tank placement on your site</p>
            </div>

            {mode === 'fallback' || mode === 'ready' ? (
                <div className="ar-start-screen">
                    <div className="ar-preview-3d">{renderTankPreview()}</div>

                    <div className="ar-tank-selector">
                        <h4>Select Tank Size</h4>
                        <div className="tank-options">
                            {TANK_MODELS.map((tank) => (
                                <button
                                    key={tank.id}
                                    className={`tank-option ${selectedTank.id === tank.id ? 'selected' : ''}`}
                                    onClick={() => setSelectedTank(tank)}
                                >
                                    <span className="tank-name">{tank.name}</span>
                                    <span className="tank-dims">{tank.dimensions.width}×{tank.dimensions.height}×{tank.dimensions.depth}m</span>
                                </button>
                            ))}
                        </div>
                    </div>

                    <button className="ar-start-btn" onClick={startCamera}>
                        <span>📸</span> Start AR Camera
                    </button>
                </div>
            ) : (
                <div className="ar-active-screen">
                    <div className="ar-viewport">
                        <video ref={videoRef} className="ar-video" playsInline muted />
                        <canvas ref={canvasRef} className="ar-canvas" style={{ display: 'none' }} />

                        {isPlaced && (
                            <div className="ar-overlay">
                                {renderTankPreview()}
                            </div>
                        )}

                        {!isPlaced && (
                            <div className="ar-crosshair">
                                <span>+</span>
                                <p>Tap to place tank</p>
                            </div>
                        )}
                    </div>

                    <div className="ar-controls">
                        <div className="ar-control-group">
                            <label>Scale</label>
                            <input
                                type="range"
                                min="0.5"
                                max="2"
                                step="0.1"
                                value={tankScale}
                                onChange={(e) => setTankScale(parseFloat(e.target.value))}
                            />
                            <span>{(tankScale * 100).toFixed(0)}%</span>
                        </div>

                        <div className="ar-control-group">
                            <label>Rotation</label>
                            <input
                                type="range"
                                min="0"
                                max="360"
                                step="15"
                                value={tankRotation}
                                onChange={(e) => setTankRotation(parseInt(e.target.value))}
                            />
                            <span>{tankRotation}°</span>
                        </div>

                        <label className="ar-toggle">
                            <input
                                type="checkbox"
                                checked={showMeasurements}
                                onChange={(e) => setShowMeasurements(e.target.checked)}
                            />
                            Show Measurements
                        </label>
                    </div>

                    <div className="ar-actions">
                        {!isPlaced ? (
                            <button className="ar-btn ar-btn-primary" onClick={placeTank}>
                                Place Tank Here
                            </button>
                        ) : (
                            <>
                                <button className="ar-btn ar-btn-secondary" onClick={() => setIsPlaced(false)}>
                                    Reposition
                                </button>
                                <button className="ar-btn ar-btn-primary" onClick={captureScreenshot}>
                                    📷 Capture
                                </button>
                            </>
                        )}
                        <button className="ar-btn ar-btn-danger" onClick={stopCamera}>
                            Exit AR
                        </button>
                    </div>
                </div>
            )}
        </div>
    );
}
