/**
 * PWA Install Prompt Component
 * Shows "Add to Home Screen" button when app is installable
 */

import React, { useState, useEffect } from 'react';
import { Download, X, Smartphone, CheckCircle } from 'lucide-react';

interface BeforeInstallPromptEvent extends Event {
    prompt: () => Promise<void>;
    userChoice: Promise<{ outcome: 'accepted' | 'dismissed' }>;
}

export const PWAInstallPrompt: React.FC = () => {
    const [deferredPrompt, setDeferredPrompt] = useState<BeforeInstallPromptEvent | null>(null);
    const [showPrompt, setShowPrompt] = useState(false);
    const [isInstalled, setIsInstalled] = useState(false);
    const [isInstalling, setIsInstalling] = useState(false);

    useEffect(() => {
        // Check if already installed
        if (window.matchMedia('(display-mode: standalone)').matches) {
            setIsInstalled(true);
            return;
        }

        // Listen for install prompt
        const handleBeforeInstall = (e: Event) => {
            e.preventDefault();
            setDeferredPrompt(e as BeforeInstallPromptEvent);

            // Show prompt after a delay (not immediately)
            setTimeout(() => setShowPrompt(true), 3000);
        };

        // Listen for successful install
        const handleAppInstalled = () => {
            setIsInstalled(true);
            setShowPrompt(false);
            setDeferredPrompt(null);
        };

        window.addEventListener('beforeinstallprompt', handleBeforeInstall);
        window.addEventListener('appinstalled', handleAppInstalled);

        return () => {
            window.removeEventListener('beforeinstallprompt', handleBeforeInstall);
            window.removeEventListener('appinstalled', handleAppInstalled);
        };
    }, []);

    const handleInstall = async () => {
        if (!deferredPrompt) return;

        setIsInstalling(true);

        try {
            await deferredPrompt.prompt();
            const { outcome } = await deferredPrompt.userChoice;

            if (outcome === 'accepted') {
                setIsInstalled(true);
            }
        } catch (error) {
            console.error('Install failed:', error);
        } finally {
            setIsInstalling(false);
            setShowPrompt(false);
            setDeferredPrompt(null);
        }
    };

    const handleDismiss = () => {
        setShowPrompt(false);
        // Don't show again for this session
        sessionStorage.setItem('pwa-prompt-dismissed', 'true');
    };

    // Don't show if dismissed this session
    if (sessionStorage.getItem('pwa-prompt-dismissed')) {
        return null;
    }

    if (!showPrompt || isInstalled) return null;

    return (
        <div className="fixed bottom-20 left-4 right-4 md:left-auto md:right-4 md:w-80 z-[90] animate-slide-up">
            <div className="glass rounded-2xl p-4 border border-cyan-500/30 shadow-lg shadow-cyan-500/10">
                <div className="flex items-start gap-3">
                    <div className="p-2 bg-cyan-500/20 rounded-xl">
                        <Smartphone className="text-cyan-400" size={24} />
                    </div>
                    <div className="flex-1">
                        <h4 className="font-bold text-white text-sm">Install RainForge</h4>
                        <p className="text-gray-400 text-xs mt-1">
                            Add to your home screen for quick access and offline use
                        </p>
                    </div>
                    <button
                        onClick={handleDismiss}
                        className="text-gray-400 hover:text-white transition-colors"
                        aria-label="Dismiss"
                    >
                        <X size={18} />
                    </button>
                </div>

                <div className="flex gap-2 mt-4">
                    <button
                        onClick={handleDismiss}
                        className="flex-1 py-2 px-4 text-sm text-gray-400 hover:text-white transition-colors"
                    >
                        Maybe Later
                    </button>
                    <button
                        onClick={handleInstall}
                        disabled={isInstalling}
                        className="flex-1 flex items-center justify-center gap-2 py-2 px-4 bg-gradient-to-r from-cyan-500 to-blue-500 text-white text-sm font-bold rounded-xl hover:scale-105 transition-transform disabled:opacity-50"
                    >
                        {isInstalling ? (
                            <>
                                <div className="w-4 h-4 border-2 border-white/30 border-t-white rounded-full animate-spin" />
                                Installing...
                            </>
                        ) : (
                            <>
                                <Download size={16} />
                                Install
                            </>
                        )}
                    </button>
                </div>
            </div>
        </div>
    );
};

// Also export a hook for programmatic install
export const useInstallPrompt = () => {
    const [canInstall, setCanInstall] = useState(false);
    const [deferredPrompt, setDeferredPrompt] = useState<BeforeInstallPromptEvent | null>(null);

    useEffect(() => {
        const handler = (e: Event) => {
            e.preventDefault();
            setDeferredPrompt(e as BeforeInstallPromptEvent);
            setCanInstall(true);
        };

        window.addEventListener('beforeinstallprompt', handler);
        return () => window.removeEventListener('beforeinstallprompt', handler);
    }, []);

    const install = async () => {
        if (!deferredPrompt) return false;
        await deferredPrompt.prompt();
        const { outcome } = await deferredPrompt.userChoice;
        setDeferredPrompt(null);
        setCanInstall(false);
        return outcome === 'accepted';
    };

    return { canInstall, install };
};

export default PWAInstallPrompt;
