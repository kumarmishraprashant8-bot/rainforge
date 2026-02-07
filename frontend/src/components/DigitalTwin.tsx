/**
 * Digital Twin Visualization
 * 3D visualization of RWH installation
 */

import React, { useEffect, useRef, useState, useMemo } from 'react';

// Types
interface TankStatus {
    level_percent: number;
    capacity_liters: number;
    current_liters: number;
    temperature_c: number;
    last_updated: string;
}

interface ComponentStatus {
    id: string;
    type: 'tank' | 'filter' | 'pipe' | 'gutter' | 'pump' | 'sensor';
    status: 'operational' | 'warning' | 'error' | 'offline';
    last_maintenance: string;
    next_maintenance: string;
}

interface DigitalTwinData {
    project_id: string;
    project_name: string;
    tank: TankStatus;
    components: ComponentStatus[];
    flow_rate_lpm: number;
    daily_collection_liters: number;
    weather: {
        raining: boolean;
        rain_intensity: number;
    };
}

interface DigitalTwinProps {
    data: DigitalTwinData;
    onComponentClick?: (component: ComponentStatus) => void;
}

/**
 * Digital Twin 3D Visualization Component
 * Uses CSS 3D transforms for lightweight visualization
 */
export function DigitalTwinVisualization({ data, onComponentClick }: DigitalTwinProps) {
    const containerRef = useRef<HTMLDivElement>(null);
    const [rotation, setRotation] = useState({ x: 15, y: -30 });
    const [isDragging, setIsDragging] = useState(false);
    const [dragStart, setDragStart] = useState({ x: 0, y: 0 });
    const [selectedComponent, setSelectedComponent] = useState<string | null>(null);

    // Animation for water level
    const [animatedLevel, setAnimatedLevel] = useState(0);

    useEffect(() => {
        // Animate water level
        const targetLevel = data.tank.level_percent;
        const duration = 1000;
        const startTime = Date.now();
        const startLevel = animatedLevel;

        const animate = () => {
            const elapsed = Date.now() - startTime;
            const progress = Math.min(elapsed / duration, 1);
            const eased = 1 - Math.pow(1 - progress, 3); // easeOutCubic

            setAnimatedLevel(startLevel + (targetLevel - startLevel) * eased);

            if (progress < 1) {
                requestAnimationFrame(animate);
            }
        };

        requestAnimationFrame(animate);
    }, [data.tank.level_percent]);

    // Mouse handlers for rotation
    const handleMouseDown = (e: React.MouseEvent) => {
        setIsDragging(true);
        setDragStart({ x: e.clientX, y: e.clientY });
    };

    const handleMouseMove = (e: React.MouseEvent) => {
        if (!isDragging) return;

        const deltaX = e.clientX - dragStart.x;
        const deltaY = e.clientY - dragStart.y;

        setRotation(prev => ({
            x: Math.max(-45, Math.min(45, prev.x - deltaY * 0.3)),
            y: prev.y + deltaX * 0.3
        }));

        setDragStart({ x: e.clientX, y: e.clientY });
    };

    const handleMouseUp = () => {
        setIsDragging(false);
    };

    // Get water color based on level
    const getWaterColor = (level: number) => {
        if (level > 70) return 'linear-gradient(180deg, #0ea5e9 0%, #0369a1 100%)';
        if (level > 30) return 'linear-gradient(180deg, #38bdf8 0%, #0ea5e9 100%)';
        return 'linear-gradient(180deg, #f59e0b 0%, #d97706 100%)';
    };

    // Get status color
    const getStatusColor = (status: string) => {
        switch (status) {
            case 'operational': return '#22c55e';
            case 'warning': return '#f59e0b';
            case 'error': return '#ef4444';
            default: return '#94a3b8';
        }
    };

    return (
        <div className="digital-twin-container">
            <div className="twin-header">
                <h2>🏠 Digital Twin - {data.project_name}</h2>
                <div className="twin-actions">
                    <button onClick={() => setRotation({ x: 15, y: -30 })}>Reset View</button>
                    <button onClick={() => setRotation(r => ({ ...r, y: r.y + 90 }))}>↻ Rotate</button>
                </div>
            </div>

            <div
                ref={containerRef}
                className="twin-viewport"
                onMouseDown={handleMouseDown}
                onMouseMove={handleMouseMove}
                onMouseUp={handleMouseUp}
                onMouseLeave={handleMouseUp}
            >
                <div
                    className="twin-scene"
                    style={{
                        transform: `rotateX(${rotation.x}deg) rotateY(${rotation.y}deg)`
                    }}
                >
                    {/* Ground/Roof plane */}
                    <div className="roof-plane">
                        <div className="roof-surface">
                            {data.weather.raining && (
                                <div className="rain-effect" style={{ opacity: data.weather.rain_intensity }}>
                                    {Array.from({ length: 20 }).map((_, i) => (
                                        <div key={i} className="raindrop" style={{
                                            left: `${Math.random() * 100}%`,
                                            animationDelay: `${Math.random() * 0.5}s`
                                        }} />
                                    ))}
                                </div>
                            )}
                        </div>
                    </div>

                    {/* Gutter system */}
                    <div className="gutter-system">
                        <div className="gutter gutter-left" />
                        <div className="gutter gutter-right" />
                        <div className="downpipe" />
                    </div>

                    {/* First flush diverter */}
                    <div
                        className={`component first-flush ${selectedComponent === 'first_flush' ? 'selected' : ''}`}
                        onClick={() => {
                            setSelectedComponent('first_flush');
                            onComponentClick?.(data.components.find(c => c.id === 'first_flush')!);
                        }}
                    >
                        <div className="component-icon">🔀</div>
                        <div className="component-label">First Flush</div>
                    </div>

                    {/* Filter */}
                    <div
                        className={`component filter ${selectedComponent === 'filter' ? 'selected' : ''}`}
                        onClick={() => {
                            setSelectedComponent('filter');
                            onComponentClick?.(data.components.find(c => c.id === 'filter')!);
                        }}
                    >
                        <div className="component-icon">🧹</div>
                        <div className="component-label">Filter</div>
                        <div
                            className="status-indicator"
                            style={{ backgroundColor: getStatusColor(data.components.find(c => c.id === 'filter')?.status || 'offline') }}
                        />
                    </div>

                    {/* Main tank */}
                    <div
                        className={`tank ${selectedComponent === 'tank' ? 'selected' : ''}`}
                        onClick={() => {
                            setSelectedComponent('tank');
                            onComponentClick?.(data.components.find(c => c.id === 'tank')!);
                        }}
                    >
                        <div className="tank-body">
                            <div
                                className="water-level"
                                style={{
                                    height: `${animatedLevel}%`,
                                    background: getWaterColor(animatedLevel)
                                }}
                            >
                                <div className="water-surface" />
                            </div>

                            {/* Level markers */}
                            <div className="level-markers">
                                {[25, 50, 75].map(level => (
                                    <div key={level} className="level-marker" style={{ bottom: `${level}%` }}>
                                        <span>{level}%</span>
                                    </div>
                                ))}
                            </div>

                            {/* Tank info overlay */}
                            <div className="tank-info">
                                <div className="tank-level-display">{Math.round(animatedLevel)}%</div>
                                <div className="tank-volume">
                                    {Math.round(data.tank.current_liters).toLocaleString()} L
                                </div>
                            </div>
                        </div>

                        {/* Sensor */}
                        <div className="sensor ultrasonic">
                            <div className="sensor-waves" />
                            📡
                        </div>
                    </div>

                    {/* Pump */}
                    <div
                        className={`component pump ${selectedComponent === 'pump' ? 'selected' : ''}`}
                        onClick={() => {
                            setSelectedComponent('pump');
                            onComponentClick?.(data.components.find(c => c.id === 'pump')!);
                        }}
                    >
                        <div className="pump-motor">⚡</div>
                        <div className="component-label">Pump</div>
                    </div>

                    {/* Pipes */}
                    <svg className="pipes-svg" viewBox="0 0 400 300">
                        {/* Downpipe to filter */}
                        <path d="M 100 50 L 100 100 L 150 100" stroke="#64748b" strokeWidth="6" fill="none" />
                        {/* Filter to tank */}
                        <path d="M 200 100 L 250 100 L 250 150" stroke="#64748b" strokeWidth="6" fill="none" />
                        {/* Tank to pump */}
                        <path d="M 280 250 L 320 250 L 320 220" stroke="#64748b" strokeWidth="6" fill="none" />

                        {/* Animated water flow */}
                        {data.flow_rate_lpm > 0 && (
                            <circle className="water-flow" r="4" fill="#0ea5e9">
                                <animateMotion
                                    dur="2s"
                                    repeatCount="indefinite"
                                    path="M 100 50 L 100 100 L 150 100 L 200 100 L 250 100 L 250 150"
                                />
                            </circle>
                        )}
                    </svg>
                </div>
            </div>

            {/* Stats panel */}
            <div className="twin-stats">
                <div className="stat-card">
                    <span className="stat-icon">💧</span>
                    <span className="stat-value">{data.tank.level_percent}%</span>
                    <span className="stat-label">Tank Level</span>
                </div>
                <div className="stat-card">
                    <span className="stat-icon">🌊</span>
                    <span className="stat-value">{data.flow_rate_lpm} L/min</span>
                    <span className="stat-label">Flow Rate</span>
                </div>
                <div className="stat-card">
                    <span className="stat-icon">📊</span>
                    <span className="stat-value">{data.daily_collection_liters} L</span>
                    <span className="stat-label">Today's Collection</span>
                </div>
                <div className="stat-card">
                    <span className="stat-icon">🌡️</span>
                    <span className="stat-value">{data.tank.temperature_c}°C</span>
                    <span className="stat-label">Water Temp</span>
                </div>
            </div>

            {/* Component status list */}
            <div className="component-list">
                <h3>System Components</h3>
                {data.components.map(component => (
                    <div
                        key={component.id}
                        className={`component-item ${selectedComponent === component.id ? 'selected' : ''}`}
                        onClick={() => {
                            setSelectedComponent(component.id);
                            onComponentClick?.(component);
                        }}
                    >
                        <div
                            className="status-dot"
                            style={{ backgroundColor: getStatusColor(component.status) }}
                        />
                        <span className="component-name">{component.type}</span>
                        <span className="component-status">{component.status}</span>
                    </div>
                ))}
            </div>

            <style>{`
        .digital-twin-container {
          background: linear-gradient(135deg, #0f172a 0%, #1e293b 100%);
          border-radius: 16px;
          padding: 20px;
          color: white;
        }

        .twin-header {
          display: flex;
          justify-content: space-between;
          align-items: center;
          margin-bottom: 20px;
        }

        .twin-header h2 {
          margin: 0;
          font-size: 20px;
        }

        .twin-actions button {
          background: rgba(255,255,255,0.1);
          border: none;
          color: white;
          padding: 8px 16px;
          border-radius: 8px;
          cursor: pointer;
          margin-left: 10px;
        }

        .twin-viewport {
          position: relative;
          height: 400px;
          perspective: 1000px;
          cursor: grab;
          overflow: hidden;
          background: radial-gradient(circle at 50% 120%, #1e3a5f 0%, #0f172a 70%);
          border-radius: 12px;
        }

        .twin-viewport:active {
          cursor: grabbing;
        }

        .twin-scene {
          position: absolute;
          top: 50%;
          left: 50%;
          transform-style: preserve-3d;
          transition: transform 0.1s ease-out;
        }

        .roof-plane {
          position: absolute;
          width: 200px;
          height: 150px;
          background: linear-gradient(135deg, #475569 0%, #334155 100%);
          transform: translateX(-100px) translateY(-180px) translateZ(50px) rotateX(75deg);
          border-radius: 4px;
        }

        .rain-effect {
          position: absolute;
          inset: 0;
          overflow: hidden;
        }

        .raindrop {
          position: absolute;
          width: 2px;
          height: 15px;
          background: linear-gradient(180deg, transparent, #0ea5e9);
          animation: fall 0.5s linear infinite;
        }

        @keyframes fall {
          from { transform: translateY(-20px); }
          to { transform: translateY(150px); }
        }

        .tank {
          position: absolute;
          width: 100px;
          height: 150px;
          transform: translateX(-50px) translateY(-75px);
          cursor: pointer;
        }

        .tank-body {
          width: 100%;
          height: 100%;
          background: linear-gradient(90deg, #334155 0%, #475569 50%, #334155 100%);
          border-radius: 8px;
          overflow: hidden;
          position: relative;
          border: 2px solid #64748b;
        }

        .water-level {
          position: absolute;
          bottom: 0;
          left: 0;
          right: 0;
          transition: height 0.5s ease-out;
        }

        .water-surface {
          position: absolute;
          top: 0;
          left: 0;
          right: 0;
          height: 10px;
          background: linear-gradient(180deg, rgba(255,255,255,0.3) 0%, transparent 100%);
          animation: ripple 2s ease-in-out infinite;
        }

        @keyframes ripple {
          0%, 100% { transform: scaleY(1); }
          50% { transform: scaleY(1.2); }
        }

        .tank-info {
          position: absolute;
          top: 10px;
          left: 50%;
          transform: translateX(-50%);
          text-align: center;
          text-shadow: 0 2px 4px rgba(0,0,0,0.5);
        }

        .tank-level-display {
          font-size: 28px;
          font-weight: bold;
        }

        .tank-volume {
          font-size: 14px;
          opacity: 0.8;
        }

        .sensor {
          position: absolute;
          top: -20px;
          left: 50%;
          transform: translateX(-50%);
          font-size: 20px;
        }

        .sensor-waves {
          position: absolute;
          top: 100%;
          left: 50%;
          width: 30px;
          height: 30px;
          border: 2px solid #0ea5e9;
          border-radius: 50%;
          transform: translateX(-50%);
          animation: pulse 1s ease-out infinite;
          opacity: 0;
        }

        @keyframes pulse {
          0% { transform: translateX(-50%) scale(0.5); opacity: 0.8; }
          100% { transform: translateX(-50%) scale(2); opacity: 0; }
        }

        .component {
          position: absolute;
          padding: 10px;
          background: rgba(255,255,255,0.1);
          border-radius: 8px;
          cursor: pointer;
          transition: all 0.2s;
        }

        .component:hover, .component.selected {
          background: rgba(255,255,255,0.2);
          transform: scale(1.05);
        }

        .filter {
          transform: translateX(-120px) translateY(-30px);
        }

        .first-flush {
          transform: translateX(-150px) translateY(-100px);
        }

        .pump {
          transform: translateX(60px) translateY(50px);
        }

        .status-indicator {
          position: absolute;
          top: 5px;
          right: 5px;
          width: 8px;
          height: 8px;
          border-radius: 50%;
        }

        .twin-stats {
          display: grid;
          grid-template-columns: repeat(4, 1fr);
          gap: 15px;
          margin-top: 20px;
        }

        .stat-card {
          background: rgba(255,255,255,0.05);
          padding: 15px;
          border-radius: 12px;
          text-align: center;
        }

        .stat-icon {
          font-size: 24px;
          display: block;
          margin-bottom: 5px;
        }

        .stat-value {
          font-size: 20px;
          font-weight: bold;
          display: block;
          color: #0ea5e9;
        }

        .stat-label {
          font-size: 12px;
          opacity: 0.7;
        }

        .component-list {
          margin-top: 20px;
          background: rgba(255,255,255,0.05);
          border-radius: 12px;
          padding: 15px;
        }

        .component-list h3 {
          margin: 0 0 15px 0;
          font-size: 16px;
        }

        .component-item {
          display: flex;
          align-items: center;
          gap: 10px;
          padding: 10px;
          border-radius: 8px;
          cursor: pointer;
          transition: background 0.2s;
        }

        .component-item:hover, .component-item.selected {
          background: rgba(255,255,255,0.1);
        }

        .status-dot {
          width: 10px;
          height: 10px;
          border-radius: 50%;
        }

        .component-name {
          flex: 1;
          text-transform: capitalize;
        }

        .component-status {
          font-size: 12px;
          opacity: 0.7;
          text-transform: capitalize;
        }

        .pipes-svg {
          position: absolute;
          top: 0;
          left: -200px;
          width: 400px;
          height: 300px;
          pointer-events: none;
        }
      `}</style>
        </div>
    );
}

export default DigitalTwinVisualization;
