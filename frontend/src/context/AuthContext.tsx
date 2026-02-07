/**
 * Authentication Context
 * Manages user authentication state across the app
 */

import { createContext, useContext, useState, useEffect, ReactNode } from 'react';

interface User {
    id: string;
    name: string;
    email?: string;
    phone?: string;
    avatar?: string;
    waterCredits: number;
    totalWaterSaved: number;
    assessments: string[];
    badges: string[];
    joinedAt: string;
    language: string;
}

interface AuthContextType {
    user: User | null;
    isAuthenticated: boolean;
    isLoading: boolean;
    login: (method: 'google' | 'phone', credential: string) => Promise<void>;
    logout: () => void;
    updateProfile: (data: Partial<User>) => void;
    saveAssessment: (assessmentId: string) => void;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

// Mock user for demo
const DEMO_USER: User = {
    id: 'user_demo_001',
    name: 'Demo User',
    email: 'demo@rainforge.in',
    phone: '+91 98765 43210',
    avatar: '',
    waterCredits: 150,
    totalWaterSaved: 245000,
    assessments: ['ASM-20260206-CF0089'],
    badges: ['early_adopter', 'water_warrior', 'eco_champion'],
    joinedAt: '2026-01-15',
    language: 'en'
};

export const AuthProvider = ({ children }: { children: ReactNode }) => {
    const [user, setUser] = useState<User | null>(null);
    const [isLoading, setIsLoading] = useState(true);

    useEffect(() => {
        // Check for saved session
        const savedUser = localStorage.getItem('rainforge_user');
        if (savedUser) {
            setUser(JSON.parse(savedUser));
        }
        setIsLoading(false);
    }, []);

    const login = async (method: 'google' | 'phone', credential: string) => {
        setIsLoading(true);
        try {
            // Simulate API call
            await new Promise(resolve => setTimeout(resolve, 1000));

            const newUser: User = {
                ...DEMO_USER,
                id: `user_${Date.now()}`,
                name: method === 'google' ? 'Google User' : 'Phone User',
                email: method === 'google' ? credential : undefined,
                phone: method === 'phone' ? credential : undefined,
            };

            setUser(newUser);
            localStorage.setItem('rainforge_user', JSON.stringify(newUser));
        } finally {
            setIsLoading(false);
        }
    };

    const logout = () => {
        setUser(null);
        localStorage.removeItem('rainforge_user');
    };

    const updateProfile = (data: Partial<User>) => {
        if (user) {
            const updated = { ...user, ...data };
            setUser(updated);
            localStorage.setItem('rainforge_user', JSON.stringify(updated));
        }
    };

    const saveAssessment = (assessmentId: string) => {
        if (user && !user.assessments.includes(assessmentId)) {
            const updated = {
                ...user,
                assessments: [...user.assessments, assessmentId]
            };
            setUser(updated);
            localStorage.setItem('rainforge_user', JSON.stringify(updated));
        }
    };

    return (
        <AuthContext.Provider value={{
            user,
            isAuthenticated: !!user,
            isLoading,
            login,
            logout,
            updateProfile,
            saveAssessment
        }}>
            {children}
        </AuthContext.Provider>
    );
};

export const useAuth = () => {
    const context = useContext(AuthContext);
    if (!context) {
        throw new Error('useAuth must be used within AuthProvider');
    }
    return context;
};

export default AuthContext;
