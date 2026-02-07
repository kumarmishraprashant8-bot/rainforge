/**
 * Error Boundary Component
 * Catch and handle React errors gracefully
 */

import React, { Component } from 'react';
import type { ErrorInfo, ReactNode } from 'react';

interface Props {
    children: ReactNode;
    fallback?: ReactNode;
    onError?: (error: Error, errorInfo: ErrorInfo) => void;
}

interface State {
    hasError: boolean;
    error: Error | null;
    errorInfo: ErrorInfo | null;
}

export class ErrorBoundary extends Component<Props, State> {
    constructor(props: Props) {
        super(props);
        this.state = {
            hasError: false,
            error: null,
            errorInfo: null
        };
    }

    static getDerivedStateFromError(error: Error): Partial<State> {
        return { hasError: true, error };
    }

    componentDidCatch(error: Error, errorInfo: ErrorInfo) {
        this.setState({ errorInfo });

        // Log to error tracking service
        this.logError(error, errorInfo);

        // Call custom error handler
        this.props.onError?.(error, errorInfo);
    }

    private logError(error: Error, errorInfo: ErrorInfo) {
        // Log to console in development
        console.error('Error caught by boundary:', error);
        console.error('Component stack:', errorInfo.componentStack);

        // Send to backend error tracking
        try {
            fetch('/api/v1/errors', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    message: error.message,
                    stack: error.stack,
                    componentStack: errorInfo.componentStack,
                    url: window.location.href,
                    userAgent: navigator.userAgent,
                    timestamp: new Date().toISOString()
                })
            }).catch(() => {
                // Silently fail - don't cause more errors
            });
        } catch {
            // Ignore
        }
    }

    private handleRetry = () => {
        this.setState({
            hasError: false,
            error: null,
            errorInfo: null
        });
    };

    private handleReload = () => {
        window.location.reload();
    };

    private handleGoHome = () => {
        window.location.href = '/';
    };

    render() {
        if (this.state.hasError) {
            if (this.props.fallback) {
                return this.props.fallback;
            }

            return (
                <div className="error-boundary">
                    <div className="error-content">
                        <div className="error-icon">⚠️</div>
                        <h1>Something went wrong</h1>
                        <p>We're sorry, but something unexpected happened. Our team has been notified.</p>

                        {import.meta.env.DEV && this.state.error && (
                            <details className="error-details">
                                <summary>Error Details</summary>
                                <pre>{this.state.error.message}</pre>
                                <pre>{this.state.error.stack}</pre>
                                {this.state.errorInfo && (
                                    <pre>{this.state.errorInfo.componentStack}</pre>
                                )}
                            </details>
                        )}

                        <div className="error-actions">
                            <button onClick={this.handleRetry} className="btn-primary">
                                Try Again
                            </button>
                            <button onClick={this.handleReload} className="btn-secondary">
                                Reload Page
                            </button>
                            <button onClick={this.handleGoHome} className="btn-secondary">
                                Go Home
                            </button>
                        </div>
                    </div>

                    <style>{`
            .error-boundary {
              min-height: 100vh;
              display: flex;
              align-items: center;
              justify-content: center;
              padding: 20px;
              background: linear-gradient(135deg, #0f172a 0%, #1e293b 100%);
            }
            
            .error-content {
              max-width: 500px;
              text-align: center;
              color: #f8fafc;
            }
            
            .error-icon {
              font-size: 64px;
              margin-bottom: 20px;
            }
            
            .error-content h1 {
              font-size: 28px;
              margin: 0 0 12px 0;
            }
            
            .error-content p {
              color: #94a3b8;
              margin: 0 0 24px 0;
              line-height: 1.6;
            }
            
            .error-details {
              text-align: left;
              background: #1e293b;
              border-radius: 8px;
              padding: 16px;
              margin-bottom: 24px;
            }
            
            .error-details summary {
              cursor: pointer;
              color: #94a3b8;
              margin-bottom: 12px;
            }
            
            .error-details pre {
              font-size: 12px;
              overflow-x: auto;
              color: #f87171;
              margin: 8px 0;
              padding: 8px;
              background: #0f172a;
              border-radius: 4px;
            }
            
            .error-actions {
              display: flex;
              gap: 12px;
              justify-content: center;
              flex-wrap: wrap;
            }
            
            .error-actions button {
              padding: 12px 24px;
              border-radius: 8px;
              font-size: 14px;
              font-weight: 600;
              cursor: pointer;
              transition: all 0.2s;
              border: none;
            }
            
            .btn-primary {
              background: linear-gradient(135deg, #0ea5e9 0%, #7c3aed 100%);
              color: white;
            }
            
            .btn-primary:hover {
              transform: translateY(-2px);
              box-shadow: 0 4px 12px rgba(14, 165, 233, 0.4);
            }
            
            .btn-secondary {
              background: #334155;
              color: #f8fafc;
            }
            
            .btn-secondary:hover {
              background: #475569;
            }
          `}</style>
                </div>
            );
        }

        return this.props.children;
    }
}

// Hook for functional error handling
export function useErrorHandler() {
    const [error, setError] = React.useState<Error | null>(null);

    const handleError = React.useCallback((error: Error) => {
        console.error('Error handled:', error);
        setError(error);

        // Log to tracking
        fetch('/api/v1/errors', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                message: error.message,
                stack: error.stack,
                url: window.location.href,
                timestamp: new Date().toISOString()
            })
        }).catch(() => { });
    }, []);

    const resetError = React.useCallback(() => {
        setError(null);
    }, []);

    React.useEffect(() => {
        if (error) {
            throw error;
        }
    }, [error]);

    return { handleError, resetError };
}

// Higher-order component for error boundary
export function withErrorBoundary<P extends object>(
    WrappedComponent: React.ComponentType<P>,
    fallback?: ReactNode
) {
    return function WithErrorBoundary(props: P) {
        return (
            <ErrorBoundary fallback={fallback}>
                <WrappedComponent {...props} />
            </ErrorBoundary>
        );
    };
}

export default ErrorBoundary;
