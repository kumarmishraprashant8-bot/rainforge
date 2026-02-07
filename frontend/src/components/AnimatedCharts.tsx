/**
 * Animated Charts Component
 * Wrapper for Recharts with animation support
 */

import React, { useState, useEffect, useRef } from 'react';
import {
    AreaChart, Area, BarChart, Bar, LineChart, Line,
    XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer,
    PieChart, Pie, Cell
} from 'recharts';

interface AnimatedChartProps {
    data: any[];
    type: 'area' | 'bar' | 'line' | 'pie';
    dataKey: string;
    xAxisKey?: string;
    height?: number;
    colors?: string[];
    showGrid?: boolean;
    animate?: boolean;
}

// Custom animated tooltip
const CustomTooltip = ({ active, payload, label }: any) => {
    if (active && payload && payload.length) {
        return (
            <div className="glass rounded-lg p-3 border border-white/20 animate-fade-in">
                <p className="text-gray-400 text-xs mb-1">{label}</p>
                {payload.map((entry: any, index: number) => (
                    <p key={index} className="text-white font-bold" style={{ color: entry.color }}>
                        {entry.name}: {typeof entry.value === 'number' ? entry.value.toLocaleString() : entry.value}
                    </p>
                ))}
            </div>
        );
    }
    return null;
};

// Hook for intersection observer (animate when visible)
const useIntersectionObserver = (threshold = 0.1) => {
    const ref = useRef<HTMLDivElement>(null);
    const [isVisible, setIsVisible] = useState(false);

    useEffect(() => {
        const observer = new IntersectionObserver(
            ([entry]) => {
                if (entry.isIntersecting) {
                    setIsVisible(true);
                    observer.disconnect();
                }
            },
            { threshold }
        );

        if (ref.current) {
            observer.observe(ref.current);
        }

        return () => observer.disconnect();
    }, [threshold]);

    return { ref, isVisible };
};

export const AnimatedAreaChart: React.FC<AnimatedChartProps> = ({
    data,
    dataKey,
    xAxisKey = 'name',
    height = 300,
    colors = ['#06b6d4', '#3b82f6'],
    showGrid = true,
    animate = true
}) => {
    const { ref, isVisible } = useIntersectionObserver();

    return (
        <div ref={ref} className="w-full" style={{ height }}>
            <ResponsiveContainer>
                <AreaChart data={data}>
                    {showGrid && <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.1)" />}
                    <XAxis dataKey={xAxisKey} stroke="#64748b" tick={{ fill: '#64748b', fontSize: 12 }} />
                    <YAxis stroke="#64748b" tick={{ fill: '#64748b', fontSize: 12 }} />
                    <Tooltip content={<CustomTooltip />} />
                    <defs>
                        <linearGradient id="colorGradient" x1="0" y1="0" x2="0" y2="1">
                            <stop offset="5%" stopColor={colors[0]} stopOpacity={0.3} />
                            <stop offset="95%" stopColor={colors[0]} stopOpacity={0} />
                        </linearGradient>
                    </defs>
                    <Area
                        type="monotone"
                        dataKey={dataKey}
                        stroke={colors[0]}
                        fill="url(#colorGradient)"
                        strokeWidth={2}
                        isAnimationActive={animate && isVisible}
                        animationDuration={1500}
                        animationEasing="ease-out"
                    />
                </AreaChart>
            </ResponsiveContainer>
        </div>
    );
};

export const AnimatedBarChart: React.FC<AnimatedChartProps> = ({
    data,
    dataKey,
    xAxisKey = 'name',
    height = 300,
    colors = ['#06b6d4', '#3b82f6', '#8b5cf6', '#ec4899', '#f59e0b'],
    showGrid = true,
    animate = true
}) => {
    const { ref, isVisible } = useIntersectionObserver();

    return (
        <div ref={ref} className="w-full" style={{ height }}>
            <ResponsiveContainer>
                <BarChart data={data}>
                    {showGrid && <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.1)" />}
                    <XAxis dataKey={xAxisKey} stroke="#64748b" tick={{ fill: '#64748b', fontSize: 12 }} />
                    <YAxis stroke="#64748b" tick={{ fill: '#64748b', fontSize: 12 }} />
                    <Tooltip content={<CustomTooltip />} />
                    <Bar
                        dataKey={dataKey}
                        radius={[4, 4, 0, 0]}
                        isAnimationActive={animate && isVisible}
                        animationDuration={1500}
                        animationEasing="ease-out"
                    >
                        {data.map((entry, index) => (
                            <Cell key={`cell-${index}`} fill={colors[index % colors.length]} />
                        ))}
                    </Bar>
                </BarChart>
            </ResponsiveContainer>
        </div>
    );
};

export const AnimatedLineChart: React.FC<AnimatedChartProps & { multipleLines?: string[] }> = ({
    data,
    dataKey,
    xAxisKey = 'name',
    height = 300,
    colors = ['#06b6d4', '#3b82f6', '#8b5cf6'],
    showGrid = true,
    animate = true,
    multipleLines
}) => {
    const { ref, isVisible } = useIntersectionObserver();
    const lines = multipleLines || [dataKey];

    return (
        <div ref={ref} className="w-full" style={{ height }}>
            <ResponsiveContainer>
                <LineChart data={data}>
                    {showGrid && <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.1)" />}
                    <XAxis dataKey={xAxisKey} stroke="#64748b" tick={{ fill: '#64748b', fontSize: 12 }} />
                    <YAxis stroke="#64748b" tick={{ fill: '#64748b', fontSize: 12 }} />
                    <Tooltip content={<CustomTooltip />} />
                    {lines.map((line, index) => (
                        <Line
                            key={line}
                            type="monotone"
                            dataKey={line}
                            stroke={colors[index % colors.length]}
                            strokeWidth={2}
                            dot={{ fill: colors[index % colors.length], strokeWidth: 2, r: 4 }}
                            activeDot={{ r: 6, strokeWidth: 0 }}
                            isAnimationActive={animate && isVisible}
                            animationDuration={1500}
                            animationEasing="ease-out"
                        />
                    ))}
                </LineChart>
            </ResponsiveContainer>
        </div>
    );
};

export const AnimatedPieChart: React.FC<AnimatedChartProps> = ({
    data,
    dataKey,
    height = 300,
    colors = ['#06b6d4', '#3b82f6', '#8b5cf6', '#ec4899', '#f59e0b', '#10b981'],
    animate = true
}) => {
    const { ref, isVisible } = useIntersectionObserver();

    return (
        <div ref={ref} className="w-full" style={{ height }}>
            <ResponsiveContainer>
                <PieChart>
                    <Pie
                        data={data}
                        dataKey={dataKey}
                        nameKey="name"
                        cx="50%"
                        cy="50%"
                        outerRadius={height / 3}
                        innerRadius={height / 5}
                        paddingAngle={2}
                        isAnimationActive={animate && isVisible}
                        animationDuration={1500}
                        animationEasing="ease-out"
                    >
                        {data.map((entry, index) => (
                            <Cell key={`cell-${index}`} fill={colors[index % colors.length]} />
                        ))}
                    </Pie>
                    <Tooltip content={<CustomTooltip />} />
                </PieChart>
            </ResponsiveContainer>
        </div>
    );
};

// Export all chart types
export default {
    AnimatedAreaChart,
    AnimatedBarChart,
    AnimatedLineChart,
    AnimatedPieChart
};
