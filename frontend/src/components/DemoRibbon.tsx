/**
 * Demo Mode Ribbon Component
 * Shows "🎯 DEMO MODE – SAFE DATA" ribbon when DEMO_MODE is active
 */

import React, { useState, useEffect } from 'react';

interface DemoStatus {
    demo_mode: boolean;
    demo_ribbon: string | null;
    counts: {
        assessments: number;
        verifications: number;
    };
}

const DemoRibbon: React.FC = () => {
    const [demoStatus, setDemoStatus] = useState<DemoStatus | null>(null);

    useEffect(() => {
        // Check demo status on mount
        fetch('/api/v1/demo/status')
            .then(res => res.json())
            .then(data => setDemoStatus(data))
            .catch(() => {
                // Default to demo mode for dev
                setDemoStatus({
                    demo_mode: true,
                    demo_ribbon: '🎯 DEMO MODE – SAFE DATA',
                    counts: { assessments: 0, verifications: 0 }
                });
            });
    }, []);

    if (!demoStatus?.demo_mode) return null;

    return (
        <div style={{
            position: 'fixed',
            top: 0,
            left: 0,
            right: 0,
            zIndex: 9999,
            background: 'linear-gradient(90deg, #ff6b35 0%, #f7c600 50%, #ff6b35 100%)',
            color: '#000',
            textAlign: 'center',
            padding: '8px 16px',
            fontSize: '14px',
            fontWeight: 700,
            letterSpacing: '1px',
            textTransform: 'uppercase',
            boxShadow: '0 2px 8px rgba(0,0,0,0.2)',
            animation: 'shimmer 3s linear infinite'
        }}>
            {demoStatus.demo_ribbon || '🎯 DEMO MODE – SAFE DATA'}
            <style>{`
        @keyframes shimmer {
          0% { background-position: -200% center; }
          100% { background-position: 200% center; }
        }
      `}</style>
        </div>
    );
};

export default DemoRibbon;
