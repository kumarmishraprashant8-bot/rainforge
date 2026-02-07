/**
 * i18n Configuration
 * Multi-language support for RainForge
 */

import i18n from 'i18next';
import { initReactI18next } from 'react-i18next';

// Translation resources
const resources = {
    en: {
        translation: {
            // Navigation
            'nav.home': 'Home',
            'nav.assessment': 'Assessment',
            'nav.portfolio': 'Portfolio',
            'nav.monitoring': 'Monitoring',
            'nav.verification': 'Verification',
            'nav.marketplace': 'Find Pros',
            'nav.profile': 'Profile',

            // Home Page
            'home.hero.title': 'Every Drop Counts',
            'home.hero.subtitle': 'AI-Powered Rainwater Harvesting Assessment',
            'home.hero.cta': 'Start Free Assessment',
            'home.stats.liters': 'Liters Saved',
            'home.stats.homes': 'Homes Assessed',
            'home.stats.co2': 'CO₂ Offset (kg)',

            // Assessment
            'assess.title': 'Property Assessment',
            'assess.location': 'Location',
            'assess.roof_area': 'Roof Area (m²)',
            'assess.roof_material': 'Roof Material',
            'assess.people': 'Number of People',
            'assess.submit': 'Calculate Potential',

            // Results
            'results.title': 'Assessment Complete',
            'results.annual_yield': 'Annual Yield',
            'results.tank_size': 'Recommended Tank',
            'results.net_cost': 'Net Cost',
            'results.payback': 'Payback Period',
            'results.download': 'Download Report',

            // Common
            'common.loading': 'Loading...',
            'common.error': 'An error occurred',
            'common.retry': 'Try Again',
            'common.save': 'Save',
            'common.cancel': 'Cancel',
            'common.next': 'Next',
            'common.back': 'Back',
            'common.submit': 'Submit',

            // Units
            'units.liters': 'L',
            'units.liters_full': 'Liters',
            'units.rupees': '₹',
            'units.years': 'years',
            'units.sqm': 'm²',
            'units.kg': 'kg',
        }
    },
    hi: {
        translation: {
            // Navigation
            'nav.home': 'होम',
            'nav.assessment': 'मूल्यांकन',
            'nav.portfolio': 'पोर्टफोलियो',
            'nav.monitoring': 'निगरानी',
            'nav.verification': 'सत्यापन',
            'nav.marketplace': 'पेशेवर खोजें',
            'nav.profile': 'प्रोफ़ाइल',

            // Home Page
            'home.hero.title': 'हर बूंद मायने रखती है',
            'home.hero.subtitle': 'AI-संचालित वर्षा जल संचयन मूल्यांकन',
            'home.hero.cta': 'मुफ्त मूल्यांकन शुरू करें',
            'home.stats.liters': 'लीटर बचाए',
            'home.stats.homes': 'घरों का मूल्यांकन',
            'home.stats.co2': 'CO₂ ऑफसेट (किग्रा)',

            // Assessment
            'assess.title': 'संपत्ति मूल्यांकन',
            'assess.location': 'स्थान',
            'assess.roof_area': 'छत का क्षेत्रफल (वर्ग मीटर)',
            'assess.roof_material': 'छत की सामग्री',
            'assess.people': 'लोगों की संख्या',
            'assess.submit': 'संभावना की गणना करें',

            // Results
            'results.title': 'मूल्यांकन पूर्ण',
            'results.annual_yield': 'वार्षिक उपज',
            'results.tank_size': 'अनुशंसित टैंक',
            'results.net_cost': 'शुद्ध लागत',
            'results.payback': 'पेबैक अवधि',
            'results.download': 'रिपोर्ट डाउनलोड करें',

            // Common
            'common.loading': 'लोड हो रहा है...',
            'common.error': 'एक त्रुटि हुई',
            'common.retry': 'पुनः प्रयास करें',
            'common.save': 'सहेजें',
            'common.cancel': 'रद्द करें',
            'common.next': 'अगला',
            'common.back': 'वापस',
            'common.submit': 'जमा करें',

            // Units
            'units.liters': 'ली',
            'units.liters_full': 'लीटर',
            'units.rupees': '₹',
            'units.years': 'वर्ष',
            'units.sqm': 'वर्ग मी',
            'units.kg': 'किग्रा',
        }
    },
    ta: {
        translation: {
            // Navigation
            'nav.home': 'முகப்பு',
            'nav.assessment': 'மதிப்பீடு',
            'nav.portfolio': 'போர்ட்ஃபோலியோ',
            'nav.monitoring': 'கண்காணிப்பு',
            'nav.verification': 'சரிபார்ப்பு',
            'nav.marketplace': 'நிபுணர்களைக் கண்டுபிடி',
            'nav.profile': 'சுயவிவரம்',

            // Home Page
            'home.hero.title': 'ஒவ்வொரு துளியும் முக்கியம்',
            'home.hero.subtitle': 'AI-இயக்கப்படும் மழைநீர் சேகரிப்பு மதிப்பீடு',
            'home.hero.cta': 'இலவச மதிப்பீட்டைத் தொடங்கு',
            'home.stats.liters': 'லிட்டர் சேமிக்கப்பட்டது',
            'home.stats.homes': 'வீடுகள் மதிப்பிடப்பட்டன',
            'home.stats.co2': 'CO₂ ஈடுசெய்தல் (கிகி)',

            // Results
            'results.title': 'மதிப்பீடு முடிந்தது',
            'results.annual_yield': 'ஆண்டு விளைச்சல்',
            'results.tank_size': 'பரிந்துரைக்கப்பட்ட தொட்டி',
            'results.net_cost': 'நிகர செலவு',
            'results.download': 'அறிக்கையைப் பதிவிறக்கு',
        }
    },
    te: {
        translation: {
            // Navigation
            'nav.home': 'హోమ్',
            'nav.assessment': 'అంచనా',
            'nav.portfolio': 'పోర్ట్‌ఫోలియో',
            'nav.monitoring': 'పర్యవేక్షణ',
            'nav.verification': 'ధృవీకరణ',
            'nav.marketplace': 'నిపుణులను కనుగొనండి',
            'nav.profile': 'ప్రొఫైల్',

            // Home Page
            'home.hero.title': 'ప్రతి చుక్క ముఖ్యం',
            'home.hero.subtitle': 'AI-ఆధారిత వర్షపు నీటి సేకరణ అంచనా',
            'home.hero.cta': 'ఉచిత అంచనాను ప్రారంభించండి',
        }
    }
};

// Initialize i18n
i18n
    .use(initReactI18next)
    .init({
        resources,
        lng: localStorage.getItem('rainforge_language') || 'en',
        fallbackLng: 'en',
        interpolation: {
            escapeValue: false
        }
    });

export const changeLanguage = (lang: string) => {
    i18n.changeLanguage(lang);
    localStorage.setItem('rainforge_language', lang);
};

export const SUPPORTED_LANGUAGES = [
    { code: 'en', name: 'English', nativeName: 'English' },
    { code: 'hi', name: 'Hindi', nativeName: 'हिंदी' },
    { code: 'ta', name: 'Tamil', nativeName: 'தமிழ்' },
    { code: 'te', name: 'Telugu', nativeName: 'తెలుగు' },
];

export default i18n;
