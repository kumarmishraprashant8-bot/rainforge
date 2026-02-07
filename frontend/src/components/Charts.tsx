/**
 * Data Visualization Charts Component
 * Reusable chart components for analytics
 */

import React, { useEffect, useRef } from 'react';

// Types
interface ChartData {
    labels: string[];
    datasets: Dataset[];
}

interface Dataset {
    label: string;
    data: number[];
    color?: string;
    backgroundColor?: string;
}

interface ChartProps {
    data: ChartData;
    height?: number;
    showLegend?: boolean;
    animate?: boolean;
}

// Color palette
const COLORS = [
    '#0ea5e9', // Sky blue
    '#22c55e', // Green
    '#f59e0b', // Amber
    '#7c3aed', // Purple
    '#ef4444', // Red
    '#14b8a6', // Teal
    '#f97316', // Orange
    '#6366f1'  // Indigo
];

/**
 * Line Chart Component
 */
export function LineChart({ data, height = 300, showLegend = true, animate = true }: ChartProps) {
    const canvasRef = useRef<HTMLCanvasElement>(null);

    useEffect(() => {
        const canvas = canvasRef.current;
        if (!canvas) return;

        const ctx = canvas.getContext('2d');
        if (!ctx) return;

        // Set canvas size
        const dpr = window.devicePixelRatio || 1;
        const rect = canvas.getBoundingClientRect();
        canvas.width = rect.width * dpr;
        canvas.height = rect.height * dpr;
        ctx.scale(dpr, dpr);

        // Chart dimensions
        const padding = { top: 20, right: 20, bottom: 40, left: 50 };
        const chartWidth = rect.width - padding.left - padding.right;
        const chartHeight = rect.height - padding.top - padding.bottom;

        // Calculate scales
        const allValues = data.datasets.flatMap(d => d.data);
        const maxValue = Math.max(...allValues) * 1.1;
        const minValue = Math.min(0, Math.min(...allValues));

        // Clear canvas
        ctx.clearRect(0, 0, rect.width, rect.height);

        // Draw grid
        ctx.strokeStyle = 'rgba(100, 116, 139, 0.2)';
        ctx.lineWidth = 1;

        for (let i = 0; i <= 5; i++) {
            const y = padding.top + (chartHeight / 5) * i;
            ctx.beginPath();
            ctx.moveTo(padding.left, y);
            ctx.lineTo(rect.width - padding.right, y);
            ctx.stroke();

            // Y-axis labels
            const value = Math.round(maxValue - (maxValue - minValue) * (i / 5));
            ctx.fillStyle = '#94a3b8';
            ctx.font = '11px system-ui';
            ctx.textAlign = 'right';
            ctx.fillText(formatNumber(value), padding.left - 8, y + 4);
        }

        // Draw X-axis labels
        const stepX = chartWidth / (data.labels.length - 1 || 1);
        ctx.textAlign = 'center';
        data.labels.forEach((label, i) => {
            if (i % Math.ceil(data.labels.length / 10) === 0 || data.labels.length <= 10) {
                ctx.fillText(label, padding.left + stepX * i, rect.height - 10);
            }
        });

        // Draw lines
        data.datasets.forEach((dataset, datasetIndex) => {
            const color = dataset.color || COLORS[datasetIndex % COLORS.length];

            ctx.strokeStyle = color;
            ctx.lineWidth = 2;
            ctx.lineJoin = 'round';
            ctx.lineCap = 'round';

            ctx.beginPath();

            dataset.data.forEach((value, i) => {
                const x = padding.left + stepX * i;
                const y = padding.top + chartHeight - ((value - minValue) / (maxValue - minValue)) * chartHeight;

                if (i === 0) {
                    ctx.moveTo(x, y);
                } else {
                    ctx.lineTo(x, y);
                }
            });

            ctx.stroke();

            // Draw area fill
            ctx.globalAlpha = 0.1;
            ctx.fillStyle = color;
            ctx.lineTo(padding.left + stepX * (dataset.data.length - 1), rect.height - padding.bottom);
            ctx.lineTo(padding.left, rect.height - padding.bottom);
            ctx.closePath();
            ctx.fill();
            ctx.globalAlpha = 1;

            // Draw points
            dataset.data.forEach((value, i) => {
                const x = padding.left + stepX * i;
                const y = padding.top + chartHeight - ((value - minValue) / (maxValue - minValue)) * chartHeight;

                ctx.beginPath();
                ctx.arc(x, y, 4, 0, Math.PI * 2);
                ctx.fillStyle = color;
                ctx.fill();
                ctx.strokeStyle = '#fff';
                ctx.lineWidth = 2;
                ctx.stroke();
            });
        });

    }, [data]);

    return (
        <div className="chart-container">
            <canvas ref={canvasRef} style={{ width: '100%', height }} />
            {showLegend && (
                <div className="chart-legend">
                    {data.datasets.map((dataset, i) => (
                        <div key={i} className="legend-item">
                            <span className="legend-color" style={{ backgroundColor: dataset.color || COLORS[i % COLORS.length] }} />
                            <span className="legend-label">{dataset.label}</span>
                        </div>
                    ))}
                </div>
            )}
            <style>{chartStyles}</style>
        </div>
    );
}

/**
 * Bar Chart Component
 */
export function BarChart({ data, height = 300, showLegend = true }: ChartProps) {
    const canvasRef = useRef<HTMLCanvasElement>(null);

    useEffect(() => {
        const canvas = canvasRef.current;
        if (!canvas) return;

        const ctx = canvas.getContext('2d');
        if (!ctx) return;

        const dpr = window.devicePixelRatio || 1;
        const rect = canvas.getBoundingClientRect();
        canvas.width = rect.width * dpr;
        canvas.height = rect.height * dpr;
        ctx.scale(dpr, dpr);

        const padding = { top: 20, right: 20, bottom: 40, left: 50 };
        const chartWidth = rect.width - padding.left - padding.right;
        const chartHeight = rect.height - padding.top - padding.bottom;

        const allValues = data.datasets.flatMap(d => d.data);
        const maxValue = Math.max(...allValues) * 1.1;

        ctx.clearRect(0, 0, rect.width, rect.height);

        // Draw grid
        ctx.strokeStyle = 'rgba(100, 116, 139, 0.2)';
        for (let i = 0; i <= 5; i++) {
            const y = padding.top + (chartHeight / 5) * i;
            ctx.beginPath();
            ctx.moveTo(padding.left, y);
            ctx.lineTo(rect.width - padding.right, y);
            ctx.stroke();

            const value = Math.round(maxValue * (1 - i / 5));
            ctx.fillStyle = '#94a3b8';
            ctx.font = '11px system-ui';
            ctx.textAlign = 'right';
            ctx.fillText(formatNumber(value), padding.left - 8, y + 4);
        }

        // Draw bars
        const barGroupWidth = chartWidth / data.labels.length;
        const barWidth = barGroupWidth / (data.datasets.length + 1);
        const barPadding = barWidth / 2;

        data.datasets.forEach((dataset, datasetIndex) => {
            const color = dataset.color || COLORS[datasetIndex % COLORS.length];

            dataset.data.forEach((value, i) => {
                const x = padding.left + barGroupWidth * i + barPadding + barWidth * datasetIndex;
                const barHeight = (value / maxValue) * chartHeight;
                const y = padding.top + chartHeight - barHeight;

                // Draw bar with rounded top
                ctx.fillStyle = color;
                roundRect(ctx, x, y, barWidth - 4, barHeight, 4);
                ctx.fill();
            });
        });

        // X-axis labels
        ctx.fillStyle = '#94a3b8';
        ctx.textAlign = 'center';
        data.labels.forEach((label, i) => {
            ctx.fillText(label, padding.left + barGroupWidth * i + barGroupWidth / 2, rect.height - 10);
        });

    }, [data]);

    return (
        <div className="chart-container">
            <canvas ref={canvasRef} style={{ width: '100%', height }} />
            {showLegend && (
                <div className="chart-legend">
                    {data.datasets.map((dataset, i) => (
                        <div key={i} className="legend-item">
                            <span className="legend-color" style={{ backgroundColor: dataset.color || COLORS[i % COLORS.length] }} />
                            <span className="legend-label">{dataset.label}</span>
                        </div>
                    ))}
                </div>
            )}
            <style>{chartStyles}</style>
        </div>
    );
}

/**
 * Donut Chart Component
 */
export function DonutChart({ data, height = 250, showLegend = true }: { data: { label: string; value: number; color?: string }[]; height?: number; showLegend?: boolean }) {
    const canvasRef = useRef<HTMLCanvasElement>(null);

    useEffect(() => {
        const canvas = canvasRef.current;
        if (!canvas) return;

        const ctx = canvas.getContext('2d');
        if (!ctx) return;

        const dpr = window.devicePixelRatio || 1;
        const rect = canvas.getBoundingClientRect();
        canvas.width = rect.width * dpr;
        canvas.height = rect.height * dpr;
        ctx.scale(dpr, dpr);

        const centerX = rect.width / 2;
        const centerY = rect.height / 2;
        const radius = Math.min(centerX, centerY) - 20;
        const innerRadius = radius * 0.6;

        const total = data.reduce((sum, item) => sum + item.value, 0);
        let currentAngle = -Math.PI / 2;

        ctx.clearRect(0, 0, rect.width, rect.height);

        data.forEach((item, i) => {
            const sliceAngle = (item.value / total) * Math.PI * 2;
            const color = item.color || COLORS[i % COLORS.length];

            ctx.beginPath();
            ctx.arc(centerX, centerY, radius, currentAngle, currentAngle + sliceAngle);
            ctx.arc(centerX, centerY, innerRadius, currentAngle + sliceAngle, currentAngle, true);
            ctx.closePath();
            ctx.fillStyle = color;
            ctx.fill();

            currentAngle += sliceAngle;
        });

        // Center text
        ctx.fillStyle = '#f8fafc';
        ctx.font = 'bold 24px system-ui';
        ctx.textAlign = 'center';
        ctx.textBaseline = 'middle';
        ctx.fillText(formatNumber(total), centerX, centerY - 10);
        ctx.font = '12px system-ui';
        ctx.fillStyle = '#94a3b8';
        ctx.fillText('Total', centerX, centerY + 15);

    }, [data]);

    return (
        <div className="chart-container">
            <canvas ref={canvasRef} style={{ width: '100%', height }} />
            {showLegend && (
                <div className="chart-legend horizontal">
                    {data.map((item, i) => (
                        <div key={i} className="legend-item">
                            <span className="legend-color" style={{ backgroundColor: item.color || COLORS[i % COLORS.length] }} />
                            <span className="legend-label">{item.label}: {formatNumber(item.value)}</span>
                        </div>
                    ))}
                </div>
            )}
            <style>{chartStyles}</style>
        </div>
    );
}

/**
 * Sparkline Component (mini inline chart)
 */
export function Sparkline({ data, color = '#0ea5e9', width = 100, height = 30 }: { data: number[]; color?: string; width?: number; height?: number }) {
    const canvasRef = useRef<HTMLCanvasElement>(null);

    useEffect(() => {
        const canvas = canvasRef.current;
        if (!canvas || data.length < 2) return;

        const ctx = canvas.getContext('2d');
        if (!ctx) return;

        const dpr = window.devicePixelRatio || 1;
        canvas.width = width * dpr;
        canvas.height = height * dpr;
        ctx.scale(dpr, dpr);

        const maxValue = Math.max(...data);
        const minValue = Math.min(...data);
        const range = maxValue - minValue || 1;

        const stepX = width / (data.length - 1);

        ctx.clearRect(0, 0, width, height);

        // Draw line
        ctx.strokeStyle = color;
        ctx.lineWidth = 2;
        ctx.lineJoin = 'round';
        ctx.beginPath();

        data.forEach((value, i) => {
            const x = stepX * i;
            const y = height - 4 - ((value - minValue) / range) * (height - 8);

            if (i === 0) ctx.moveTo(x, y);
            else ctx.lineTo(x, y);
        });

        ctx.stroke();

        // End dot
        const lastY = height - 4 - ((data[data.length - 1] - minValue) / range) * (height - 8);
        ctx.beginPath();
        ctx.arc(width, lastY, 3, 0, Math.PI * 2);
        ctx.fillStyle = color;
        ctx.fill();

    }, [data, color, width, height]);

    return <canvas ref={canvasRef} style={{ width, height }} />;
}

// Helper functions
function formatNumber(num: number): string {
    if (num >= 1000000) return `${(num / 1000000).toFixed(1)}M`;
    if (num >= 1000) return `${(num / 1000).toFixed(1)}K`;
    return num.toString();
}

function roundRect(ctx: CanvasRenderingContext2D, x: number, y: number, w: number, h: number, r: number) {
    ctx.beginPath();
    ctx.moveTo(x + r, y);
    ctx.lineTo(x + w - r, y);
    ctx.quadraticCurveTo(x + w, y, x + w, y + r);
    ctx.lineTo(x + w, y + h);
    ctx.lineTo(x, y + h);
    ctx.lineTo(x, y + r);
    ctx.quadraticCurveTo(x, y, x + r, y);
    ctx.closePath();
}

const chartStyles = `
  .chart-container {
    position: relative;
  }
  
  .chart-legend {
    display: flex;
    flex-wrap: wrap;
    gap: 16px;
    margin-top: 12px;
    justify-content: center;
  }
  
  .chart-legend.horizontal {
    flex-direction: row;
  }
  
  .legend-item {
    display: flex;
    align-items: center;
    gap: 6px;
    font-size: 12px;
    color: #94a3b8;
  }
  
  .legend-color {
    width: 12px;
    height: 12px;
    border-radius: 3px;
  }
`;

export default { LineChart, BarChart, DonutChart, Sparkline };
