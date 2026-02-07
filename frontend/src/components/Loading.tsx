/**
 * Loading States and Skeleton Components
 * Seamless loading experiences
 */

import React from 'react';

interface SkeletonProps {
    width?: string | number;
    height?: string | number;
    borderRadius?: string | number;
    className?: string;
}

/**
 * Basic skeleton loader
 */
export function Skeleton({
    width = '100%',
    height = 20,
    borderRadius = 4,
    className = ''
}: SkeletonProps) {
    return (
        <div
            className={`skeleton ${className}`}
            style={{
                width: typeof width === 'number' ? `${width}px` : width,
                height: typeof height === 'number' ? `${height}px` : height,
                borderRadius: typeof borderRadius === 'number' ? `${borderRadius}px` : borderRadius
            }}
        />
    );
}

/**
 * Card skeleton with header and content
 */
export function CardSkeleton({ lines = 3 }: { lines?: number }) {
    return (
        <div className="card-skeleton">
            <div className="card-header">
                <Skeleton width={40} height={40} borderRadius="50%" />
                <div className="header-text">
                    <Skeleton width="60%" height={16} />
                    <Skeleton width="40%" height={12} />
                </div>
            </div>
            <div className="card-body">
                {Array.from({ length: lines }).map((_, i) => (
                    <Skeleton
                        key={i}
                        width={i === lines - 1 ? '70%' : '100%'}
                        height={14}
                    />
                ))}
            </div>
        </div>
    );
}

/**
 * Table skeleton
 */
export function TableSkeleton({ rows = 5, columns = 4 }: { rows?: number; columns?: number }) {
    return (
        <div className="table-skeleton">
            <div className="table-header">
                {Array.from({ length: columns }).map((_, i) => (
                    <Skeleton key={i} width="100%" height={16} />
                ))}
            </div>
            {Array.from({ length: rows }).map((_, rowIndex) => (
                <div key={rowIndex} className="table-row">
                    {Array.from({ length: columns }).map((_, colIndex) => (
                        <Skeleton
                            key={colIndex}
                            width={colIndex === 0 ? '80%' : '60%'}
                            height={14}
                        />
                    ))}
                </div>
            ))}
        </div>
    );
}

/**
 * Stats card skeleton
 */
export function StatsSkeleton({ count = 4 }: { count?: number }) {
    return (
        <div className="stats-skeleton">
            {Array.from({ length: count }).map((_, i) => (
                <div key={i} className="stat-item">
                    <Skeleton width={48} height={48} borderRadius={12} />
                    <div className="stat-text">
                        <Skeleton width="50%" height={24} />
                        <Skeleton width="70%" height={14} />
                    </div>
                </div>
            ))}
        </div>
    );
}

/**
 * Chart skeleton
 */
export function ChartSkeleton({ height = 300 }: { height?: number }) {
    return (
        <div className="chart-skeleton" style={{ height }}>
            <div className="chart-bars">
                {Array.from({ length: 7 }).map((_, i) => (
                    <div
                        key={i}
                        className="bar"
                        style={{ height: `${30 + Math.random() * 50}%` }}
                    />
                ))}
            </div>
            <div className="chart-axis" />
        </div>
    );
}

/**
 * List item skeleton
 */
export function ListSkeleton({ count = 5 }: { count?: number }) {
    return (
        <div className="list-skeleton">
            {Array.from({ length: count }).map((_, i) => (
                <div key={i} className="list-item">
                    <Skeleton width={44} height={44} borderRadius={8} />
                    <div className="list-content">
                        <Skeleton width="70%" height={16} />
                        <Skeleton width="50%" height={12} />
                    </div>
                    <Skeleton width={60} height={28} borderRadius={6} />
                </div>
            ))}
        </div>
    );
}

/**
 * Full page loading spinner
 */
export function PageLoader({ message = 'Loading...' }: { message?: string }) {
    return (
        <div className="page-loader">
            <div className="spinner" />
            <p>{message}</p>
        </div>
    );
}

/**
 * Inline loading spinner
 */
export function Spinner({ size = 24, color }: { size?: number; color?: string }) {
    return (
        <div
            className="spinner-inline"
            style={{
                width: size,
                height: size,
                borderColor: color ? `${color}33` : undefined,
                borderTopColor: color
            }}
        />
    );
}

/**
 * Button loading state
 */
export function LoadingButton({
    loading,
    children,
    ...props
}: {
    loading: boolean;
    children: React.ReactNode;
} & React.ButtonHTMLAttributes<HTMLButtonElement>) {
    return (
        <button className="loading-button" disabled={loading} {...props}>
            {loading && <Spinner size={16} />}
            <span style={{ opacity: loading ? 0.7 : 1 }}>{children}</span>
        </button>
    );
}

/**
 * Shimmer effect overlay
 */
export function ShimmerOverlay({ children }: { children: React.ReactNode }) {
    return (
        <div className="shimmer-container">
            {children}
            <div className="shimmer-overlay" />
        </div>
    );
}

// Styles
export const loadingStyles = `
  .skeleton {
    background: linear-gradient(
      90deg,
      var(--bg-tertiary, #334155) 0%,
      var(--bg-secondary, #1e293b) 50%,
      var(--bg-tertiary, #334155) 100%
    );
    background-size: 200% 100%;
    animation: shimmer 1.5s infinite;
  }

  @keyframes shimmer {
    0% { background-position: 200% 0; }
    100% { background-position: -200% 0; }
  }

  .card-skeleton {
    background: var(--card-bg, #1e293b);
    border-radius: 12px;
    padding: 20px;
  }

  .card-skeleton .card-header {
    display: flex;
    gap: 12px;
    margin-bottom: 16px;
  }

  .card-skeleton .header-text {
    flex: 1;
    display: flex;
    flex-direction: column;
    gap: 6px;
    justify-content: center;
  }

  .card-skeleton .card-body {
    display: flex;
    flex-direction: column;
    gap: 10px;
  }

  .table-skeleton {
    display: flex;
    flex-direction: column;
    gap: 8px;
  }

  .table-skeleton .table-header,
  .table-skeleton .table-row {
    display: grid;
    grid-template-columns: repeat(4, 1fr);
    gap: 16px;
    padding: 12px;
  }

  .table-skeleton .table-header {
    background: var(--bg-tertiary, #334155);
    border-radius: 8px;
  }

  .stats-skeleton {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
    gap: 16px;
  }

  .stats-skeleton .stat-item {
    display: flex;
    gap: 16px;
    padding: 20px;
    background: var(--card-bg, #1e293b);
    border-radius: 12px;
  }

  .stats-skeleton .stat-text {
    flex: 1;
    display: flex;
    flex-direction: column;
    gap: 8px;
    justify-content: center;
  }

  .chart-skeleton {
    background: var(--card-bg, #1e293b);
    border-radius: 12px;
    padding: 20px;
    display: flex;
    flex-direction: column;
  }

  .chart-skeleton .chart-bars {
    flex: 1;
    display: flex;
    align-items: flex-end;
    gap: 8px;
  }

  .chart-skeleton .bar {
    flex: 1;
    background: var(--bg-tertiary, #334155);
    border-radius: 4px 4px 0 0;
    animation: shimmer 1.5s infinite;
  }

  .chart-skeleton .chart-axis {
    height: 2px;
    background: var(--border-primary, #334155);
  }

  .list-skeleton {
    display: flex;
    flex-direction: column;
    gap: 12px;
  }

  .list-skeleton .list-item {
    display: flex;
    align-items: center;
    gap: 12px;
    padding: 12px;
    background: var(--bg-secondary, #1e293b);
    border-radius: 8px;
  }

  .list-skeleton .list-content {
    flex: 1;
    display: flex;
    flex-direction: column;
    gap: 6px;
  }

  .page-loader {
    position: fixed;
    inset: 0;
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    gap: 16px;
    background: var(--bg-primary, #0f172a);
    z-index: 9999;
  }

  .page-loader p {
    color: var(--text-secondary, #94a3b8);
    font-size: 14px;
  }

  .spinner,
  .spinner-inline {
    border: 3px solid var(--border-primary, #334155);
    border-top-color: var(--accent-primary, #0ea5e9);
    border-radius: 50%;
    animation: spin 0.8s linear infinite;
  }

  .spinner {
    width: 40px;
    height: 40px;
  }

  .spinner-inline {
    width: 24px;
    height: 24px;
  }

  @keyframes spin {
    to { transform: rotate(360deg); }
  }

  .loading-button {
    display: inline-flex;
    align-items: center;
    justify-content: center;
    gap: 8px;
    position: relative;
  }

  .shimmer-container {
    position: relative;
    overflow: hidden;
  }

  .shimmer-overlay {
    position: absolute;
    inset: 0;
    background: linear-gradient(
      90deg,
      transparent 0%,
      rgba(255, 255, 255, 0.1) 50%,
      transparent 100%
    );
    animation: shimmerMove 2s infinite;
  }

  @keyframes shimmerMove {
    0% { transform: translateX(-100%); }
    100% { transform: translateX(100%); }
  }
`;

// Inject styles
if (typeof document !== 'undefined') {
    const styleId = 'loading-styles';
    if (!document.getElementById(styleId)) {
        const style = document.createElement('style');
        style.id = styleId;
        style.textContent = loadingStyles;
        document.head.appendChild(style);
    }
}

export default {
    Skeleton,
    CardSkeleton,
    TableSkeleton,
    StatsSkeleton,
    ChartSkeleton,
    ListSkeleton,
    PageLoader,
    Spinner,
    LoadingButton,
    ShimmerOverlay
};
