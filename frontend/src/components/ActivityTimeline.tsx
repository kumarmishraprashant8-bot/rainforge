/**
 * Activity Timeline Component
 * Visual project history with events, milestones, and annotations
 */

import React, { useState } from 'react';

interface TimelineEvent {
    id: string;
    type: 'created' | 'updated' | 'milestone' | 'payment' | 'verification' | 'alert' | 'note';
    title: string;
    description?: string;
    timestamp: string;
    user?: {
        name: string;
        avatar?: string;
    };
    metadata?: Record<string, any>;
}

interface ActivityTimelineProps {
    events: TimelineEvent[];
    maxVisible?: number;
    showLoadMore?: boolean;
    onLoadMore?: () => void;
}

const EVENT_ICONS: Record<TimelineEvent['type'], string> = {
    created: '🎉',
    updated: '✏️',
    milestone: '🎯',
    payment: '💰',
    verification: '✅',
    alert: '⚠️',
    note: '📝'
};

const EVENT_COLORS: Record<TimelineEvent['type'], string> = {
    created: '#22c55e',
    updated: '#0ea5e9',
    milestone: '#7c3aed',
    payment: '#f59e0b',
    verification: '#14b8a6',
    alert: '#ef4444',
    note: '#64748b'
};

export function ActivityTimeline({
    events,
    maxVisible = 10,
    showLoadMore = true,
    onLoadMore
}: ActivityTimelineProps) {
    const [expanded, setExpanded] = useState(false);

    const visibleEvents = expanded ? events : events.slice(0, maxVisible);
    const hasMore = events.length > maxVisible && !expanded;

    return (
        <div className="activity-timeline">
            <div className="timeline-track">
                {visibleEvents.map((event, index) => (
                    <TimelineItem
                        key={event.id}
                        event={event}
                        isLast={index === visibleEvents.length - 1}
                    />
                ))}
            </div>

            {showLoadMore && hasMore && (
                <button
                    className="load-more-btn"
                    onClick={() => {
                        setExpanded(true);
                        onLoadMore?.();
                    }}
                >
                    Show {events.length - maxVisible} more events
                </button>
            )}

            <style>{timelineStyles}</style>
        </div>
    );
}

function TimelineItem({ event, isLast }: { event: TimelineEvent; isLast: boolean }) {
    const [showDetails, setShowDetails] = useState(false);
    const color = EVENT_COLORS[event.type];
    const icon = EVENT_ICONS[event.type];

    return (
        <div className="timeline-item">
            <div className="timeline-indicator">
                <div
                    className="indicator-dot"
                    style={{ backgroundColor: color, borderColor: color }}
                >
                    <span className="indicator-icon">{icon}</span>
                </div>
                {!isLast && <div className="indicator-line" />}
            </div>

            <div className="timeline-content" onClick={() => setShowDetails(!showDetails)}>
                <div className="timeline-header">
                    <span className="timeline-title">{event.title}</span>
                    <span className="timeline-time">{formatTime(event.timestamp)}</span>
                </div>

                {event.description && (
                    <p className="timeline-description">{event.description}</p>
                )}

                {event.user && (
                    <div className="timeline-user">
                        <div className="user-avatar">
                            {event.user.avatar ? (
                                <img src={event.user.avatar} alt={event.user.name} />
                            ) : (
                                <span>{event.user.name[0]}</span>
                            )}
                        </div>
                        <span className="user-name">{event.user.name}</span>
                    </div>
                )}

                {showDetails && event.metadata && (
                    <div className="timeline-metadata">
                        {Object.entries(event.metadata).map(([key, value]) => (
                            <div key={key} className="metadata-item">
                                <span className="metadata-key">{formatKey(key)}:</span>
                                <span className="metadata-value">{formatValue(value)}</span>
                            </div>
                        ))}
                    </div>
                )}
            </div>
        </div>
    );
}

// Compact version for dashboards
export function CompactTimeline({ events, limit = 5 }: { events: TimelineEvent[]; limit?: number }) {
    return (
        <div className="compact-timeline">
            {events.slice(0, limit).map(event => (
                <div key={event.id} className="compact-item">
                    <span className="compact-icon">{EVENT_ICONS[event.type]}</span>
                    <span className="compact-title">{event.title}</span>
                    <span className="compact-time">{formatTimeAgo(event.timestamp)}</span>
                </div>
            ))}

            <style>{`
        .compact-timeline {
          display: flex;
          flex-direction: column;
          gap: 8px;
        }
        
        .compact-item {
          display: flex;
          align-items: center;
          gap: 10px;
          padding: 8px 12px;
          background: var(--bg-secondary);
          border-radius: 8px;
          transition: background 0.2s;
        }
        
        .compact-item:hover {
          background: var(--bg-tertiary);
        }
        
        .compact-icon {
          font-size: 16px;
        }
        
        .compact-title {
          flex: 1;
          font-size: 13px;
          color: var(--text-primary);
        }
        
        .compact-time {
          font-size: 11px;
          color: var(--text-muted);
        }
      `}</style>
        </div>
    );
}

// Helper functions
function formatTime(timestamp: string): string {
    const date = new Date(timestamp);
    const now = new Date();
    const diffMs = now.getTime() - date.getTime();
    const diffDays = Math.floor(diffMs / (1000 * 60 * 60 * 24));

    if (diffDays === 0) {
        return date.toLocaleTimeString('en-IN', { hour: '2-digit', minute: '2-digit' });
    } else if (diffDays === 1) {
        return 'Yesterday';
    } else if (diffDays < 7) {
        return date.toLocaleDateString('en-IN', { weekday: 'short' });
    } else {
        return date.toLocaleDateString('en-IN', { day: 'numeric', month: 'short' });
    }
}

function formatTimeAgo(timestamp: string): string {
    const date = new Date(timestamp);
    const now = new Date();
    const diffMs = now.getTime() - date.getTime();
    const diffMins = Math.floor(diffMs / (1000 * 60));
    const diffHours = Math.floor(diffMs / (1000 * 60 * 60));
    const diffDays = Math.floor(diffMs / (1000 * 60 * 60 * 24));

    if (diffMins < 1) return 'Just now';
    if (diffMins < 60) return `${diffMins}m ago`;
    if (diffHours < 24) return `${diffHours}h ago`;
    if (diffDays < 7) return `${diffDays}d ago`;
    return date.toLocaleDateString('en-IN', { day: 'numeric', month: 'short' });
}

function formatKey(key: string): string {
    return key.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase());
}

function formatValue(value: any): string {
    if (typeof value === 'boolean') return value ? 'Yes' : 'No';
    if (typeof value === 'number') return value.toLocaleString();
    if (value instanceof Date) return value.toLocaleDateString();
    return String(value);
}

const timelineStyles = `
  .activity-timeline {
    position: relative;
  }
  
  .timeline-track {
    display: flex;
    flex-direction: column;
  }
  
  .timeline-item {
    display: flex;
    gap: 16px;
    position: relative;
  }
  
  .timeline-indicator {
    display: flex;
    flex-direction: column;
    align-items: center;
    width: 40px;
    flex-shrink: 0;
  }
  
  .indicator-dot {
    width: 40px;
    height: 40px;
    border-radius: 50%;
    display: flex;
    align-items: center;
    justify-content: center;
    border: 3px solid;
    background: var(--bg-primary);
    z-index: 1;
  }
  
  .indicator-icon {
    font-size: 16px;
  }
  
  .indicator-line {
    width: 2px;
    flex: 1;
    min-height: 30px;
    background: var(--border-primary);
    margin: 4px 0;
  }
  
  .timeline-content {
    flex: 1;
    padding: 8px 16px 24px 0;
    cursor: pointer;
  }
  
  .timeline-header {
    display: flex;
    justify-content: space-between;
    align-items: flex-start;
    gap: 12px;
    margin-bottom: 4px;
  }
  
  .timeline-title {
    font-size: 14px;
    font-weight: 600;
    color: var(--text-primary);
  }
  
  .timeline-time {
    font-size: 12px;
    color: var(--text-muted);
    white-space: nowrap;
  }
  
  .timeline-description {
    margin: 0;
    font-size: 13px;
    color: var(--text-secondary);
    line-height: 1.5;
  }
  
  .timeline-user {
    display: flex;
    align-items: center;
    gap: 8px;
    margin-top: 8px;
  }
  
  .user-avatar {
    width: 24px;
    height: 24px;
    border-radius: 50%;
    background: var(--bg-tertiary);
    display: flex;
    align-items: center;
    justify-content: center;
    overflow: hidden;
    font-size: 11px;
    color: var(--text-secondary);
  }
  
  .user-avatar img {
    width: 100%;
    height: 100%;
    object-fit: cover;
  }
  
  .user-name {
    font-size: 12px;
    color: var(--text-secondary);
  }
  
  .timeline-metadata {
    margin-top: 12px;
    padding: 12px;
    background: var(--bg-secondary);
    border-radius: 8px;
    display: grid;
    grid-template-columns: repeat(auto-fill, minmax(150px, 1fr));
    gap: 8px;
  }
  
  .metadata-item {
    font-size: 12px;
  }
  
  .metadata-key {
    color: var(--text-muted);
  }
  
  .metadata-value {
    color: var(--text-primary);
    margin-left: 4px;
  }
  
  .load-more-btn {
    display: block;
    width: 100%;
    padding: 12px;
    margin-top: 8px;
    background: var(--bg-secondary);
    border: 1px solid var(--border-primary);
    border-radius: 8px;
    color: var(--text-secondary);
    font-size: 13px;
    cursor: pointer;
    transition: all 0.2s;
  }
  
  .load-more-btn:hover {
    background: var(--bg-tertiary);
    color: var(--text-primary);
  }
`;

export default ActivityTimeline;
