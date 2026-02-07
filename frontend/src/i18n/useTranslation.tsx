/**
 * i18n Hook for React Components
 * Provides easy access to translations with automatic re-render on language change
 */

import { useState, useEffect } from 'react';
import {
    t,
    setLanguage,
    getLanguage,
    getAvailableLanguages,
    initLanguage,
} from './translations';
import type { Language } from './translations';

// Initialize on module load
initLanguage();

/**
 * Hook for using translations in components
 */
export function useTranslation() {
    const [, forceUpdate] = useState({});

    useEffect(() => {
        const handleLanguageChange = () => forceUpdate({});
        window.addEventListener('languagechange', handleLanguageChange);
        return () => window.removeEventListener('languagechange', handleLanguageChange);
    }, []);

    return {
        t,
        language: getLanguage(),
        setLanguage,
        languages: getAvailableLanguages(),
    };
}

/**
 * Language Selector Component
 */
export const LanguageSelector: React.FC<{ className?: string }> = ({ className = '' }) => {
    const { language, setLanguage, languages } = useTranslation();
    const [isOpen, setIsOpen] = useState(false);

    const currentLang = languages.find(l => l.code === language);

    return (
        <div className={`relative ${className}`}>
            <button
                onClick={() => setIsOpen(!isOpen)}
                className="flex items-center gap-2 px-3 py-2 bg-white/5 rounded-lg border border-white/10 hover:bg-white/10 transition-colors text-sm"
                aria-label="Select language"
            >
                <span className="text-lg">{getFlagEmoji(language)}</span>
                <span className="text-gray-300">{currentLang?.nativeName}</span>
                <svg className={`w-4 h-4 text-gray-400 transition-transform ${isOpen ? 'rotate-180' : ''}`} fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 9l-7 7-7-7" />
                </svg>
            </button>

            {isOpen && (
                <>
                    <div className="fixed inset-0 z-40" onClick={() => setIsOpen(false)} />
                    <div className="absolute right-0 mt-2 w-48 glass rounded-xl border border-white/20 shadow-xl z-50 py-2 animate-fade-in">
                        {languages.map((lang) => (
                            <button
                                key={lang.code}
                                onClick={() => {
                                    setLanguage(lang.code);
                                    setIsOpen(false);
                                }}
                                className={`w-full px-4 py-2 flex items-center gap-3 hover:bg-white/10 transition-colors text-left ${language === lang.code ? 'bg-cyan-500/20 text-cyan-400' : 'text-gray-300'
                                    }`}
                            >
                                <span className="text-lg">{getFlagEmoji(lang.code)}</span>
                                <div>
                                    <div className="text-sm">{lang.nativeName}</div>
                                    <div className="text-xs text-gray-500">{lang.name}</div>
                                </div>
                                {language === lang.code && (
                                    <svg className="w-4 h-4 ml-auto" fill="currentColor" viewBox="0 0 20 20">
                                        <path fillRule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clipRule="evenodd" />
                                    </svg>
                                )}
                            </button>
                        ))}
                    </div>
                </>
            )}
        </div>
    );
};

/**
 * Get flag emoji for language code
 */
function getFlagEmoji(langCode: Language): string {
    const flags: Record<Language, string> = {
        en: '🇺🇸',
        hi: '🇮🇳',
        ta: '🇮🇳',  // Tamil Nadu flag would be better
        te: '🇮🇳',
        mr: '🇮🇳',
        kn: '🇮🇳',
    };
    return flags[langCode] || '🌐';
}

export default useTranslation;
