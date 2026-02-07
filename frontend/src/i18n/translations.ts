/**
 * RainForge Multi-Language Support (i18n)
 * Languages: English, Hindi, Tamil, Telugu, Marathi, Kannada
 */

export type Language = 'en' | 'hi' | 'ta' | 'te' | 'mr' | 'kn';

export interface Translations {
    [key: string]: string;
}

export const translations: Record<Language, Translations> = {
    // ==================== ENGLISH ====================
    en: {
        // Common
        'app.name': 'RainForge',
        'app.tagline': 'Smart Rainwater Harvesting Platform',
        'common.save': 'Save',
        'common.cancel': 'Cancel',
        'common.submit': 'Submit',
        'common.loading': 'Loading...',
        'common.error': 'Error',
        'common.success': 'Success',
        'common.next': 'Next',
        'common.back': 'Back',
        'common.close': 'Close',
        'common.search': 'Search',
        'common.filter': 'Filter',
        'common.download': 'Download',
        'common.upload': 'Upload',
        'common.view': 'View',
        'common.edit': 'Edit',
        'common.delete': 'Delete',

        // Navigation
        'nav.home': 'Home',
        'nav.dashboard': 'Dashboard',
        'nav.assess': 'New Assessment',
        'nav.projects': 'My Projects',
        'nav.marketplace': 'Marketplace',
        'nav.verification': 'Verification',
        'nav.monitoring': 'Monitoring',
        'nav.reports': 'Reports',
        'nav.settings': 'Settings',
        'nav.logout': 'Logout',

        // Assessment
        'assess.title': 'Rooftop Assessment',
        'assess.location': 'Location',
        'assess.area': 'Roof Area',
        'assess.surface': 'Surface Type',
        'assess.rainfall': 'Annual Rainfall',
        'assess.potential': 'Harvesting Potential',
        'assess.calculate': 'Calculate Potential',
        'assess.result': 'Assessment Result',
        'assess.liters_year': 'liters/year',
        'assess.savings': 'Estimated Savings',

        // Surface types
        'surface.concrete': 'Concrete',
        'surface.metal': 'Metal Sheet',
        'surface.tile': 'Tiles',
        'surface.asphalt': 'Asphalt',
        'surface.other': 'Other',

        // Marketplace
        'market.find_installer': 'Find Installer',
        'market.bid': 'Place Bid',
        'market.award': 'Award Contract',
        'market.rpi': 'RPI Score',
        'market.price': 'Price',
        'market.timeline': 'Timeline',
        'market.warranty': 'Warranty',

        // Verification
        'verify.submit': 'Submit Verification',
        'verify.photo': 'Upload Photo',
        'verify.geo': 'Location Verified',
        'verify.status': 'Status',
        'verify.pending': 'Pending',
        'verify.approved': 'Approved',
        'verify.rejected': 'Rejected',

        // Monitoring
        'monitor.tank_level': 'Tank Level',
        'monitor.flow_rate': 'Flow Rate',
        'monitor.rainfall': 'Rainfall',
        'monitor.temperature': 'Temperature',
        'monitor.last_updated': 'Last Updated',
        'monitor.alerts': 'Alerts',

        // Public Dashboard
        'public.city_stats': 'City-Wide Statistics',
        'public.total_capacity': 'Total Capacity',
        'public.water_saved': 'Water Saved',
        'public.co2_offset': 'CO2 Offset',
        'public.projects': 'Active Projects',

        // Errors
        'error.network': 'Network error. Please check your connection.',
        'error.auth': 'Authentication failed. Please login again.',
        'error.permission': 'You do not have permission for this action.',
    },

    // ==================== HINDI ====================
    hi: {
        'app.name': 'रेनफोर्ज',
        'app.tagline': 'स्मार्ट वर्षा जल संचयन प्लेटफॉर्म',
        'common.save': 'सहेजें',
        'common.cancel': 'रद्द करें',
        'common.submit': 'जमा करें',
        'common.loading': 'लोड हो रहा है...',
        'common.error': 'त्रुटि',
        'common.success': 'सफलता',
        'common.next': 'अगला',
        'common.back': 'वापस',
        'common.close': 'बंद करें',
        'common.search': 'खोजें',
        'common.filter': 'फ़िल्टर',
        'common.download': 'डाउनलोड',
        'common.upload': 'अपलोड',
        'common.view': 'देखें',
        'common.edit': 'संपादित',
        'common.delete': 'हटाएं',

        'nav.home': 'होम',
        'nav.dashboard': 'डैशबोर्ड',
        'nav.assess': 'नया मूल्यांकन',
        'nav.projects': 'मेरी परियोजनाएं',
        'nav.marketplace': 'मार्केटप्लेस',
        'nav.verification': 'सत्यापन',
        'nav.monitoring': 'निगरानी',
        'nav.reports': 'रिपोर्ट',
        'nav.settings': 'सेटिंग्स',
        'nav.logout': 'लॉगआउट',

        'assess.title': 'छत मूल्यांकन',
        'assess.location': 'स्थान',
        'assess.area': 'छत क्षेत्र',
        'assess.surface': 'सतह प्रकार',
        'assess.rainfall': 'वार्षिक वर्षा',
        'assess.potential': 'संचयन क्षमता',
        'assess.calculate': 'क्षमता गणना करें',
        'assess.result': 'मूल्यांकन परिणाम',
        'assess.liters_year': 'लीटर/वर्ष',
        'assess.savings': 'अनुमानित बचत',

        'surface.concrete': 'कंक्रीट',
        'surface.metal': 'धातु शीट',
        'surface.tile': 'टाइल्स',
        'surface.asphalt': 'डामर',
        'surface.other': 'अन्य',

        'market.find_installer': 'इंस्टॉलर खोजें',
        'market.bid': 'बोली लगाएं',
        'market.award': 'अनुबंध प्रदान करें',
        'market.rpi': 'RPI स्कोर',
        'market.price': 'मूल्य',
        'market.timeline': 'समयरेखा',
        'market.warranty': 'वारंटी',

        'verify.submit': 'सत्यापन जमा करें',
        'verify.photo': 'फोटो अपलोड',
        'verify.geo': 'स्थान सत्यापित',
        'verify.status': 'स्थिति',
        'verify.pending': 'लंबित',
        'verify.approved': 'अनुमोदित',
        'verify.rejected': 'अस्वीकृत',

        'monitor.tank_level': 'टैंक स्तर',
        'monitor.flow_rate': 'प्रवाह दर',
        'monitor.rainfall': 'वर्षा',
        'monitor.temperature': 'तापमान',
        'monitor.last_updated': 'अंतिम अपडेट',
        'monitor.alerts': 'अलर्ट',

        'public.city_stats': 'शहर-व्यापी आंकड़े',
        'public.total_capacity': 'कुल क्षमता',
        'public.water_saved': 'बचाया गया पानी',
        'public.co2_offset': 'CO2 ऑफसेट',
        'public.projects': 'सक्रिय परियोजनाएं',

        'error.network': 'नेटवर्क त्रुटि। कृपया अपना कनेक्शन जांचें।',
        'error.auth': 'प्रमाणीकरण विफल। कृपया पुनः लॉगिन करें।',
        'error.permission': 'इस कार्रवाई के लिए आपको अनुमति नहीं है।',
    },

    // ==================== TAMIL ====================
    ta: {
        'app.name': 'ரெயின்ஃபோர்ஜ்',
        'app.tagline': 'ஸ்மார்ட் மழைநீர் சேகரிப்பு தளம்',
        'common.save': 'சேமி',
        'common.cancel': 'ரத்து',
        'common.submit': 'சமர்ப்பி',
        'common.loading': 'ஏற்றுகிறது...',
        'common.error': 'பிழை',
        'common.success': 'வெற்றி',
        'common.next': 'அடுத்து',
        'common.back': 'பின்',

        'nav.home': 'முகப்பு',
        'nav.dashboard': 'டாஷ்போர்டு',
        'nav.assess': 'புதிய மதிப்பீடு',
        'nav.projects': 'எனது திட்டங்கள்',
        'nav.marketplace': 'சந்தை',
        'nav.verification': 'சரிபார்ப்பு',
        'nav.monitoring': 'கண்காணிப்பு',

        'assess.title': 'கூரை மதிப்பீடு',
        'assess.location': 'இடம்',
        'assess.area': 'கூரை பரப்பளவு',
        'assess.surface': 'மேற்பரப்பு வகை',
        'assess.rainfall': 'ஆண்டு மழைப்பொழிவு',
        'assess.potential': 'சேகரிப்பு திறன்',

        'monitor.tank_level': 'தொட்டி நிலை',
        'monitor.flow_rate': 'ஓட்ட விகிதம்',
        'monitor.rainfall': 'மழைப்பொழிவு',

        'public.city_stats': 'நகர புள்ளிவிவரங்கள்',
        'public.water_saved': 'சேமிக்கப்பட்ட நீர்',
    },

    // ==================== TELUGU ====================
    te: {
        'app.name': 'రెయిన్‌ఫోర్జ్',
        'app.tagline': 'స్మార్ట్ వర్షపు నీటి సేకరణ వేదిక',
        'common.save': 'సేవ్',
        'common.cancel': 'రద్దు',
        'common.submit': 'సమర్పించు',
        'common.loading': 'లోడ్ అవుతోంది...',
        'common.error': 'లోపం',
        'common.success': 'విజయం',

        'nav.home': 'హోమ్',
        'nav.dashboard': 'డాష్‌బోర్డ్',
        'nav.assess': 'కొత్త అంచనా',
        'nav.projects': 'నా ప్రాజెక్ట్‌లు',

        'assess.title': 'పైకప్పు అంచనా',
        'assess.location': 'స్థానం',
        'assess.area': 'పైకప్పు విస్తీర్ణం',

        'monitor.tank_level': 'ట్యాంక్ స్థాయి',
        'public.water_saved': 'ఆదా చేసిన నీరు',
    },

    // ==================== MARATHI ====================
    mr: {
        'app.name': 'रेनफोर्ज',
        'app.tagline': 'स्मार्ट पावसाचे पाणी संचयन प्लॅटफॉर्म',
        'common.save': 'जतन करा',
        'common.cancel': 'रद्द करा',
        'common.submit': 'सबमिट करा',
        'common.loading': 'लोड होत आहे...',
        'common.error': 'त्रुटी',
        'common.success': 'यशस्वी',

        'nav.home': 'मुख्यपृष्ठ',
        'nav.dashboard': 'डॅशबोर्ड',
        'nav.assess': 'नवीन मूल्यांकन',
        'nav.projects': 'माझे प्रकल्प',

        'assess.title': 'छप्पर मूल्यांकन',
        'assess.location': 'स्थान',
        'assess.area': 'छप्पर क्षेत्र',

        'monitor.tank_level': 'टाकी पातळी',
        'public.water_saved': 'वाचवलेले पाणी',
    },

    // ==================== KANNADA ====================
    kn: {
        'app.name': 'ರೇನ್‌ಫೋರ್ಜ್',
        'app.tagline': 'ಸ್ಮಾರ್ಟ್ ಮಳೆನೀರು ಕೊಯ್ಲು ವೇದಿಕೆ',
        'common.save': 'ಉಳಿಸಿ',
        'common.cancel': 'ರದ್ದುಮಾಡಿ',
        'common.submit': 'ಸಲ್ಲಿಸಿ',
        'common.loading': 'ಲೋಡ್ ಆಗುತ್ತಿದೆ...',
        'common.error': 'ದೋಷ',
        'common.success': 'ಯಶಸ್ಸು',

        'nav.home': 'ಮುಖಪುಟ',
        'nav.dashboard': 'ಡ್ಯಾಶ್‌ಬೋರ್ಡ್',
        'nav.assess': 'ಹೊಸ ಮೌಲ್ಯಮಾಪನ',
        'nav.projects': 'ನನ್ನ ಯೋಜನೆಗಳು',

        'assess.title': 'ಛಾವಣಿ ಮೌಲ್ಯಮಾಪನ',
        'assess.location': 'ಸ್ಥಳ',
        'assess.area': 'ಛಾವಣಿ ಪ್ರದೇಶ',

        'monitor.tank_level': 'ಟ್ಯಾಂಕ್ ಮಟ್ಟ',
        'public.water_saved': 'ಉಳಿಸಿದ ನೀರು',
    },
};

// Current language state
let currentLanguage: Language = 'en';

/**
 * Get translation for a key
 */
export function t(key: string, params?: Record<string, string>): string {
    const translation = translations[currentLanguage][key] || translations.en[key] || key;

    if (!params) return translation;

    // Replace {{param}} placeholders
    return Object.entries(params).reduce(
        (str, [key, value]) => str.replace(new RegExp(`{{${key}}}`, 'g'), value),
        translation
    );
}

/**
 * Set current language
 */
export function setLanguage(lang: Language): void {
    if (translations[lang]) {
        currentLanguage = lang;
        localStorage.setItem('rainforge-lang', lang);
        document.documentElement.lang = lang;

        // Dispatch event for components to re-render
        window.dispatchEvent(new CustomEvent('languagechange', { detail: { language: lang } }));
    }
}

/**
 * Get current language
 */
export function getLanguage(): Language {
    return currentLanguage;
}

/**
 * Initialize language from localStorage or browser
 */
export function initLanguage(): void {
    const saved = localStorage.getItem('rainforge-lang') as Language;

    if (saved && translations[saved]) {
        currentLanguage = saved;
    } else {
        // Detect from browser
        const browserLang = navigator.language.split('-')[0] as Language;
        if (translations[browserLang]) {
            currentLanguage = browserLang;
        }
    }

    document.documentElement.lang = currentLanguage;
}

/**
 * Get all available languages
 */
export function getAvailableLanguages(): { code: Language; name: string; nativeName: string }[] {
    return [
        { code: 'en', name: 'English', nativeName: 'English' },
        { code: 'hi', name: 'Hindi', nativeName: 'हिंदी' },
        { code: 'ta', name: 'Tamil', nativeName: 'தமிழ்' },
        { code: 'te', name: 'Telugu', nativeName: 'తెలుగు' },
        { code: 'mr', name: 'Marathi', nativeName: 'मराठी' },
        { code: 'kn', name: 'Kannada', nativeName: 'ಕನ್ನಡ' },
    ];
}
