/**
 * SEO and Meta Tags Component
 * Dynamic OpenGraph, Twitter Cards, and structured data
 */

import React from 'react';

interface SEOProps {
    title?: string;
    description?: string;
    keywords?: string[];
    image?: string;
    url?: string;
    type?: 'website' | 'article' | 'product';
    author?: string;
    publishedTime?: string;
    modifiedTime?: string;
    section?: string;
    twitterCard?: 'summary' | 'summary_large_image';
    noindex?: boolean;
    structuredData?: object;
}

const DEFAULT_SEO = {
    siteName: 'RainForge',
    title: 'RainForge - Rainwater Harvesting Platform',
    description: 'Complete rainwater harvesting assessment, installation, and monitoring platform. Get instant RWH system recommendations and connect with verified installers.',
    image: 'https://rainforge.gov.in/og-image.png',
    url: 'https://rainforge.gov.in',
    twitterHandle: '@RainForgeIndia',
    locale: 'en_IN'
};

export function SEO({
    title,
    description,
    keywords,
    image,
    url,
    type = 'website',
    author,
    publishedTime,
    modifiedTime,
    section,
    twitterCard = 'summary_large_image',
    noindex = false,
    structuredData
}: SEOProps) {
    const fullTitle = title ? `${title} | ${DEFAULT_SEO.siteName}` : DEFAULT_SEO.title;
    const pageDescription = description || DEFAULT_SEO.description;
    const pageImage = image || DEFAULT_SEO.image;
    const pageUrl = url || DEFAULT_SEO.url;

    // Generate structured data
    const baseStructuredData = {
        '@context': 'https://schema.org',
        '@type': 'WebApplication',
        name: DEFAULT_SEO.siteName,
        description: pageDescription,
        url: pageUrl,
        applicationCategory: 'UtilitiesApplication',
        operatingSystem: 'Any',
        offers: {
            '@type': 'Offer',
            price: '0',
            priceCurrency: 'INR'
        },
        author: {
            '@type': 'Organization',
            name: 'Jal Shakti Ministry, Government of India'
        }
    };

    const organizationData = {
        '@context': 'https://schema.org',
        '@type': 'GovernmentOrganization',
        name: 'Jal Shakti Ministry',
        url: 'https://jalshakti-ddws.gov.in',
        logo: 'https://rainforge.gov.in/logo.png',
        sameAs: [
            'https://twitter.com/jaboronMoJS',
            'https://www.facebook.com/MoJSOfficial'
        ]
    };

    const allStructuredData = structuredData || baseStructuredData;

    return (
        <>
            {/* Primary Meta Tags */}
            <title>{fullTitle}</title>
            <meta name="title" content={fullTitle} />
            <meta name="description" content={pageDescription} />
            {keywords && <meta name="keywords" content={keywords.join(', ')} />}
            {author && <meta name="author" content={author} />}
            {noindex && <meta name="robots" content="noindex, nofollow" />}

            {/* Open Graph / Facebook */}
            <meta property="og:type" content={type} />
            <meta property="og:url" content={pageUrl} />
            <meta property="og:title" content={fullTitle} />
            <meta property="og:description" content={pageDescription} />
            <meta property="og:image" content={pageImage} />
            <meta property="og:image:alt" content={fullTitle} />
            <meta property="og:site_name" content={DEFAULT_SEO.siteName} />
            <meta property="og:locale" content={DEFAULT_SEO.locale} />

            {/* Article specific */}
            {publishedTime && <meta property="article:published_time" content={publishedTime} />}
            {modifiedTime && <meta property="article:modified_time" content={modifiedTime} />}
            {author && <meta property="article:author" content={author} />}
            {section && <meta property="article:section" content={section} />}

            {/* Twitter */}
            <meta property="twitter:card" content={twitterCard} />
            <meta property="twitter:url" content={pageUrl} />
            <meta property="twitter:title" content={fullTitle} />
            <meta property="twitter:description" content={pageDescription} />
            <meta property="twitter:image" content={pageImage} />
            <meta property="twitter:site" content={DEFAULT_SEO.twitterHandle} />

            {/* Additional */}
            <meta name="theme-color" content="#0ea5e9" />
            <meta name="mobile-web-app-capable" content="yes" />
            <meta name="apple-mobile-web-app-capable" content="yes" />
            <meta name="apple-mobile-web-app-status-bar-style" content="black-translucent" />
            <meta name="apple-mobile-web-app-title" content={DEFAULT_SEO.siteName} />

            {/* Canonical */}
            <link rel="canonical" href={pageUrl} />

            {/* Structured Data */}
            <script type="application/ld+json">
                {JSON.stringify(allStructuredData)}
            </script>
            <script type="application/ld+json">
                {JSON.stringify(organizationData)}
            </script>
        </>
    );
}

// Pre-built SEO configs for common pages
export const SEO_CONFIGS = {
    home: {
        title: 'Home',
        description: 'RainForge - India\'s premier rainwater harvesting platform. Get instant assessment, connect with installers, and monitor your water collection.',
        keywords: ['rainwater harvesting', 'RWH', 'water conservation', 'India', 'Jal Shakti']
    },

    assessment: {
        title: 'RWH Assessment',
        description: 'Get instant rainwater harvesting potential assessment for your property. Calculate water collection, tank size, and ROI.',
        keywords: ['RWH assessment', 'rainwater calculator', 'roof area', 'water collection']
    },

    projects: {
        title: 'My Projects',
        description: 'View and manage your rainwater harvesting projects. Track installation progress and monitor water collection.',
        keywords: ['RWH projects', 'installation tracking', 'water monitoring']
    },

    monitoring: {
        title: 'Tank Monitoring',
        description: 'Real-time monitoring of your rainwater tank levels. Get alerts and optimize water usage.',
        keywords: ['tank monitoring', 'water level', 'IoT sensors', 'real-time']
    },

    marketplace: {
        title: 'Installer Marketplace',
        description: 'Find verified RWH installers in your area. Compare quotes and read reviews.',
        keywords: ['RWH installers', 'contractors', 'verified', 'quotes']
    },

    verification: {
        title: 'Installation Verification',
        description: 'Submit photos for installation verification. Get your official RWH certificate.',
        keywords: ['verification', 'certificate', 'compliance', 'subsidy']
    }
};

// Utility to generate dynamic page SEO
export function generateArticleSEO(article: {
    title: string;
    description: string;
    image?: string;
    author: string;
    publishedAt: string;
    updatedAt?: string;
    tags?: string[];
}): SEOProps {
    return {
        title: article.title,
        description: article.description,
        image: article.image,
        type: 'article',
        author: article.author,
        publishedTime: article.publishedAt,
        modifiedTime: article.updatedAt,
        keywords: article.tags,
        twitterCard: 'summary_large_image'
    };
}

export function generateProjectSEO(project: {
    name: string;
    city: string;
    tankCapacity: number;
}): SEOProps {
    return {
        title: `${project.name} - RWH Project`,
        description: `Rainwater harvesting project in ${project.city} with ${project.tankCapacity}L capacity. View installation details and water collection data.`,
        type: 'website',
        keywords: ['RWH project', project.city, 'rainwater harvesting']
    };
}

export default SEO;
