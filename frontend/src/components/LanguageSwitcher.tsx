/**
 * Language Switcher Component
 * Dropdown to change app language (simplified version without i18next)
 */

import { useState, useRef, useEffect } from 'react';
import { Globe, Check, ChevronDown } from 'lucide-react';

export const SUPPORTED_LANGUAGES = [
    { code: 'en', name: 'English', nativeName: 'English' },
    { code: 'hi', name: 'Hindi', nativeName: 'हिंदी' },
    { code: 'ta', name: 'Tamil', nativeName: 'தமிழ்' },
    { code: 'te', name: 'Telugu', nativeName: 'తెలుగు' },
];

interface LanguageSwitcherProps {
    compact?: boolean;
}

const LanguageSwitcher = ({ compact = false }: LanguageSwitcherProps) => {
    const [isOpen, setIsOpen] = useState(false);
    const [currentLangCode, setCurrentLangCode] = useState(
        () => localStorage.getItem('rainforge_language') || 'en'
    );
    const dropdownRef = useRef<HTMLDivElement>(null);

    const currentLang = SUPPORTED_LANGUAGES.find(l => l.code === currentLangCode) || SUPPORTED_LANGUAGES[0];

    // Close on outside click
    useEffect(() => {
        const handleClickOutside = (event: MouseEvent) => {
            if (dropdownRef.current && !dropdownRef.current.contains(event.target as Node)) {
                setIsOpen(false);
            }
        };
        document.addEventListener('mousedown', handleClickOutside);
        return () => document.removeEventListener('mousedown', handleClickOutside);
    }, []);

    const handleLanguageChange = (langCode: string) => {
        setCurrentLangCode(langCode);
        localStorage.setItem('rainforge_language', langCode);
        setIsOpen(false);
        // In production, this would trigger i18n language change
        window.location.reload(); // Simple reload to apply language
    };

    if (compact) {
        return (
            <div className="relative" ref={dropdownRef}>
                <button
                    onClick={() => setIsOpen(!isOpen)}
                    className="p-2 bg-white/5 rounded-lg hover:bg-white/10 transition-colors"
                    title="Change Language"
                >
                    <Globe className="text-gray-400" size={18} />
                </button>

                {isOpen && (
                    <div className="absolute right-0 top-full mt-2 w-40 bg-slate-800 border border-white/10 rounded-xl shadow-2xl overflow-hidden z-50">
                        {SUPPORTED_LANGUAGES.map(lang => (
                            <button
                                key={lang.code}
                                onClick={() => handleLanguageChange(lang.code)}
                                className={`w-full px-4 py-2 text-left flex items-center justify-between hover:bg-white/5 transition-colors ${lang.code === currentLangCode ? 'bg-cyan-500/10 text-cyan-400' : 'text-white'
                                    }`}
                            >
                                <span>{lang.nativeName}</span>
                                {lang.code === currentLangCode && <Check size={14} />}
                            </button>
                        ))}
                    </div>
                )}
            </div>
        );
    }

    return (
        <div className="relative" ref={dropdownRef}>
            <button
                onClick={() => setIsOpen(!isOpen)}
                className="flex items-center gap-2 px-4 py-2 bg-white/5 rounded-xl hover:bg-white/10 transition-colors"
            >
                <Globe className="text-gray-400" size={18} />
                <span className="text-white">{currentLang.nativeName}</span>
                <ChevronDown className={`text-gray-400 transition-transform ${isOpen ? 'rotate-180' : ''}`} size={16} />
            </button>

            {isOpen && (
                <div className="absolute right-0 top-full mt-2 w-48 bg-slate-800 border border-white/10 rounded-xl shadow-2xl overflow-hidden z-50">
                    <div className="p-2 border-b border-white/10">
                        <p className="text-gray-500 text-xs px-2">Select Language</p>
                    </div>
                    {SUPPORTED_LANGUAGES.map(lang => (
                        <button
                            key={lang.code}
                            onClick={() => handleLanguageChange(lang.code)}
                            className={`w-full px-4 py-3 text-left flex items-center justify-between hover:bg-white/5 transition-colors ${lang.code === currentLangCode ? 'bg-cyan-500/10' : ''
                                }`}
                        >
                            <div>
                                <div className={lang.code === currentLangCode ? 'text-cyan-400 font-medium' : 'text-white'}>
                                    {lang.nativeName}
                                </div>
                                <div className="text-gray-500 text-xs">{lang.name}</div>
                            </div>
                            {lang.code === currentLangCode && <Check className="text-cyan-400" size={16} />}
                        </button>
                    ))}
                </div>
            )}
        </div>
    );
};

export default LanguageSwitcher;
