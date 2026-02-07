/**
 * Offline Indicator Component
 * Shows a banner when user loses internet connection
 */

import React, { useState, useEffect } from 'react';
import { WifiOff, Wifi, RefreshCw } from 'lucide-react';

export const OfflineIndicator: React.FC = () => {
    const [isOnline, setIsOnline] = useState(navigator.onLine);
    const [showBanner, setShowBanner] = useState(false);
    const [wasOffline, setWasOffline] = useState(false);

    useEffect(() => {
        const handleOnline = () => {
            setIsOnline(true);
            if (wasOffline) {
                // Show "back online" message briefly
                setShowBanner(true);
                setTimeout(() => setShowBanner(false), 3000);
            }
        };

        const handleOffline = () => {
            setIsOnline(false);
            setWasOffline(true);
            setShowBanner(true);
        };

        window.addEventListener('online', handleOnline);
        window.addEventListener('offline', handleOffline);

        return () => {
            window.removeEventListener('online', handleOnline);
            window.removeEventListener('offline', handleOffline);
        };
    }, [wasOffline]);

    if (!showBanner) return null;

    return (
        <div
            className={`fixed top-0 left-0 right-0 z-[150] transform transition-transform duration-300 ${showBanner ? 'translate-y-0' : '-translate-y-full'
                }`}
        >
            <div
                className={`flex items-center justify-center gap-3 py-3 px-4 text-sm font-medium ${isOnline
                        ? 'bg-green-500/90 text-white'
                        : 'bg-red-500/90 text-white'
                    }`}
            >
                {isOnline ? (
                    <>
                        <Wifi size={18} />
                        <span>Back online! Connection restored.</span>
                    </>
                ) : (
                    <>
                        <WifiOff size={18} className="animate-pulse" />
                        <span>You're offline. Some features may be unavailable.</span>
                        <button
                            onClick={() => window.location.reload()}
                            className="ml-2 flex items-center gap-1 px-3 py-1 bg-white/20 rounded-full hover:bg-white/30 transition-colors"
                        >
                            <RefreshCw size={14} />
                            Retry
                        </button>
                    </>
                )}
            </div>
        </div>
    );
};

export default OfflineIndicator;
