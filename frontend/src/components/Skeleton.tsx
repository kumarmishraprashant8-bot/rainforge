/**
 * Skeleton Loading Components
 * Beautiful animated skeleton loaders for premium UX
 */

import React from 'react';

interface SkeletonProps {
    className?: string;
    width?: string;
    height?: string;
}

// Base skeleton component with shimmer animation
export const Skeleton: React.FC<SkeletonProps> = ({ className = '', width, height }) => {
    return (
        <div
            className={`skeleton-shimmer rounded bg-gradient-to-r from-slate-700 via-slate-600 to-slate-700 ${className}`}
            style={{ width, height }}
        />
    );
};

// Card skeleton for dashboard cards
export const SkeletonCard: React.FC<{ className?: string }> = ({ className = '' }) => {
    return (
        <div className={`glass rounded-2xl p-6 space-y-4 ${className}`}>
            <div className="flex items-center gap-4">
                <Skeleton className="w-12 h-12 rounded-xl" />
                <div className="flex-1 space-y-2">
                    <Skeleton className="h-4 w-3/4" />
                    <Skeleton className="h-3 w-1/2" />
                </div>
            </div>
            <Skeleton className="h-20 w-full" />
            <div className="flex gap-2">
                <Skeleton className="h-8 w-24 rounded-lg" />
                <Skeleton className="h-8 w-24 rounded-lg" />
            </div>
        </div>
    );
};

// Table row skeleton
export const SkeletonTableRow: React.FC<{ columns?: number }> = ({ columns = 5 }) => {
    return (
        <tr className="border-b border-white/5">
            {Array.from({ length: columns }).map((_, i) => (
                <td key={i} className="py-4 px-4">
                    <Skeleton className="h-4 w-full" />
                </td>
            ))}
        </tr>
    );
};

// Stats card skeleton
export const SkeletonStatsCard: React.FC = () => {
    return (
        <div className="glass rounded-xl p-4 space-y-3">
            <Skeleton className="w-10 h-10 rounded-lg" />
            <Skeleton className="h-8 w-20" />
            <Skeleton className="h-3 w-16" />
        </div>
    );
};

// Chart skeleton
export const SkeletonChart: React.FC<{ height?: string }> = ({ height = '300px' }) => {
    return (
        <div className="glass rounded-2xl p-6">
            <div className="flex justify-between items-center mb-4">
                <Skeleton className="h-6 w-40" />
                <Skeleton className="h-8 w-24 rounded-lg" />
            </div>
            <div className="relative" style={{ height }}>
                <div className="absolute inset-0 flex items-end justify-around gap-2 px-4">
                    {Array.from({ length: 12 }).map((_, i) => (
                        <Skeleton
                            key={i}
                            className="flex-1 rounded-t"
                            height={`${30 + Math.random() * 60}%`}
                        />
                    ))}
                </div>
            </div>
        </div>
    );
};

// List skeleton
export const SkeletonList: React.FC<{ items?: number }> = ({ items = 5 }) => {
    return (
        <div className="space-y-3">
            {Array.from({ length: items }).map((_, i) => (
                <div key={i} className="flex items-center gap-3 p-3 glass rounded-xl">
                    <Skeleton className="w-10 h-10 rounded-full" />
                    <div className="flex-1 space-y-2">
                        <Skeleton className="h-4 w-3/4" />
                        <Skeleton className="h-3 w-1/2" />
                    </div>
                    <Skeleton className="w-16 h-6 rounded" />
                </div>
            ))}
        </div>
    );
};

// Form skeleton
export const SkeletonForm: React.FC = () => {
    return (
        <div className="space-y-6">
            {Array.from({ length: 4 }).map((_, i) => (
                <div key={i} className="space-y-2">
                    <Skeleton className="h-4 w-24" />
                    <Skeleton className="h-12 w-full rounded-lg" />
                </div>
            ))}
            <Skeleton className="h-12 w-full rounded-xl" />
        </div>
    );
};

// Profile skeleton
export const SkeletonProfile: React.FC = () => {
    return (
        <div className="flex items-center gap-4">
            <Skeleton className="w-16 h-16 rounded-full" />
            <div className="space-y-2">
                <Skeleton className="h-5 w-32" />
                <Skeleton className="h-4 w-24" />
            </div>
        </div>
    );
};

export default {
    Skeleton,
    SkeletonCard,
    SkeletonTableRow,
    SkeletonStatsCard,
    SkeletonChart,
    SkeletonList,
    SkeletonForm,
    SkeletonProfile
};
