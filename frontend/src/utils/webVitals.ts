/**
 * Web Vitals Monitoring
 * Track Core Web Vitals for performance monitoring
 */

// Web Vitals v4 - FID removed, INP is the replacement
import { onCLS, onLCP, onFCP, onTTFB, onINP } from 'web-vitals';

interface VitalMetric {
    name: string;
    value: number;
    rating: 'good' | 'needs-improvement' | 'poor';
    delta: number;
    id: string;
}

// Thresholds based on Google's recommendations
const thresholds = {
    CLS: { good: 0.1, poor: 0.25 },
    INP: { good: 200, poor: 500 },
    LCP: { good: 2500, poor: 4000 },
    FCP: { good: 1800, poor: 3000 },
    TTFB: { good: 800, poor: 1800 },
};

function getRating(name: string, value: number): 'good' | 'needs-improvement' | 'poor' {
    const threshold = thresholds[name as keyof typeof thresholds];
    if (!threshold) return 'good';

    if (value <= threshold.good) return 'good';
    if (value <= threshold.poor) return 'needs-improvement';
    return 'poor';
}

// Store vitals for debugging
const vitalsStore: VitalMetric[] = [];

function handleVital(metric: { name: string; value: number; delta: number; id: string }) {
    const vital: VitalMetric = {
        name: metric.name,
        value: metric.value,
        rating: getRating(metric.name, metric.value),
        delta: metric.delta,
        id: metric.id,
    };

    vitalsStore.push(vital);

    // Log to console in development
    if (import.meta.env.DEV) {
        const emoji = vital.rating === 'good' ? '✅' : vital.rating === 'needs-improvement' ? '⚠️' : '❌';
        console.log(`${emoji} ${vital.name}: ${vital.value.toFixed(2)} (${vital.rating})`);
    }

    // Send to analytics endpoint in production
    if (import.meta.env.PROD) {
        sendToAnalytics(vital);
    }
}

async function sendToAnalytics(vital: VitalMetric) {
    try {
        // Use sendBeacon for reliability
        if (navigator.sendBeacon) {
            const blob = new Blob([JSON.stringify(vital)], { type: 'application/json' });
            navigator.sendBeacon('/api/v1/analytics/vitals', blob);
        } else {
            // Fallback to fetch
            await fetch('/api/v1/analytics/vitals', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(vital),
                keepalive: true,
            });
        }
    } catch (error) {
        // Silently fail - don't impact user experience
        console.debug('Failed to send vital:', error);
    }
}

// Initialize Web Vitals tracking
export function initWebVitals() {
    onCLS(handleVital);
    onLCP(handleVital);
    onFCP(handleVital);
    onTTFB(handleVital);
    onINP(handleVital);
}

// Get all collected vitals
export function getWebVitals(): VitalMetric[] {
    return [...vitalsStore];
}

// Performance monitoring hook
export function usePerformanceMonitor() {
    const getPerformanceScore = () => {
        if (vitalsStore.length === 0) return null;

        const scores = vitalsStore.map(v => {
            if (v.rating === 'good') return 100;
            if (v.rating === 'needs-improvement') return 70;
            return 40;
        });

        return Math.round(scores.reduce((a, b) => a + b, 0) / scores.length);
    };

    return {
        vitals: vitalsStore,
        score: getPerformanceScore(),
    };
}

export default initWebVitals;
