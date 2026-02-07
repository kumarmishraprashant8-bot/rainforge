/**
 * Toast Notification System
 * Animated toast notifications for user feedback
 */

import React, { createContext, useContext, useState, useCallback, useEffect } from 'react';
import { CheckCircle, XCircle, AlertTriangle, Info, X } from 'lucide-react';

type ToastType = 'success' | 'error' | 'warning' | 'info';

interface Toast {
    id: string;
    type: ToastType;
    title: string;
    message?: string;
    duration?: number;
}

interface ToastContextType {
    toasts: Toast[];
    addToast: (toast: Omit<Toast, 'id'>) => void;
    removeToast: (id: string) => void;
    success: (title: string, message?: string) => void;
    error: (title: string, message?: string) => void;
    warning: (title: string, message?: string) => void;
    info: (title: string, message?: string) => void;
}

const ToastContext = createContext<ToastContextType | undefined>(undefined);

export const useToast = () => {
    const context = useContext(ToastContext);
    if (!context) {
        throw new Error('useToast must be used within a ToastProvider');
    }
    return context;
};

const ToastIcon: React.FC<{ type: ToastType }> = ({ type }) => {
    const icons = {
        success: <CheckCircle className="text-green-400" size={20} />,
        error: <XCircle className="text-red-400" size={20} />,
        warning: <AlertTriangle className="text-yellow-400" size={20} />,
        info: <Info className="text-blue-400" size={20} />,
    };
    return icons[type];
};

const ToastItem: React.FC<{ toast: Toast; onRemove: (id: string) => void }> = ({ toast, onRemove }) => {
    const [isExiting, setIsExiting] = useState(false);

    const handleRemove = useCallback(() => {
        setIsExiting(true);
        setTimeout(() => onRemove(toast.id), 300);
    }, [toast.id, onRemove]);

    useEffect(() => {
        const duration = toast.duration || 5000;
        const timer = setTimeout(handleRemove, duration);
        return () => clearTimeout(timer);
    }, [handleRemove, toast.duration]);

    const bgColors = {
        success: 'from-green-500/20 to-green-600/10 border-green-500/30',
        error: 'from-red-500/20 to-red-600/10 border-red-500/30',
        warning: 'from-yellow-500/20 to-yellow-600/10 border-yellow-500/30',
        info: 'from-blue-500/20 to-blue-600/10 border-blue-500/30',
    };

    return (
        <div
            className={`
                toast-item
                flex items-start gap-3 p-4 rounded-xl border backdrop-blur-xl
                bg-gradient-to-r ${bgColors[toast.type]}
                transform transition-all duration-300 ease-out
                ${isExiting ? 'opacity-0 translate-x-full' : 'opacity-100 translate-x-0'}
                animate-slide-in-right
            `}
        >
            <ToastIcon type={toast.type} />
            <div className="flex-1 min-w-0">
                <h4 className="font-semibold text-white text-sm">{toast.title}</h4>
                {toast.message && (
                    <p className="text-gray-300 text-xs mt-1">{toast.message}</p>
                )}
            </div>
            <button
                onClick={handleRemove}
                className="text-gray-400 hover:text-white transition-colors"
                aria-label="Dismiss notification"
            >
                <X size={16} />
            </button>
        </div>
    );
};

export const ToastProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
    const [toasts, setToasts] = useState<Toast[]>([]);

    const addToast = useCallback((toast: Omit<Toast, 'id'>) => {
        const id = `toast-${Date.now()}-${Math.random().toString(36).substr(2, 9)}`;
        setToasts((prev) => [...prev, { ...toast, id }]);
    }, []);

    const removeToast = useCallback((id: string) => {
        setToasts((prev) => prev.filter((t) => t.id !== id));
    }, []);

    const success = useCallback((title: string, message?: string) => {
        addToast({ type: 'success', title, message });
    }, [addToast]);

    const error = useCallback((title: string, message?: string) => {
        addToast({ type: 'error', title, message });
    }, [addToast]);

    const warning = useCallback((title: string, message?: string) => {
        addToast({ type: 'warning', title, message });
    }, [addToast]);

    const info = useCallback((title: string, message?: string) => {
        addToast({ type: 'info', title, message });
    }, [addToast]);

    return (
        <ToastContext.Provider value={{ toasts, addToast, removeToast, success, error, warning, info }}>
            {children}
            {/* Toast Container */}
            <div className="fixed bottom-4 right-4 z-[100] flex flex-col gap-2 max-w-sm w-full pointer-events-none">
                {toasts.map((toast) => (
                    <div key={toast.id} className="pointer-events-auto">
                        <ToastItem toast={toast} onRemove={removeToast} />
                    </div>
                ))}
            </div>
        </ToastContext.Provider>
    );
};

export default ToastProvider;
