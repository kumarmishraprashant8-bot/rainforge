/**
 * Share Buttons Component
 * WhatsApp, Twitter, Facebook, Copy Link
 */

import { useState } from 'react';
import { Share2, Check, Link2, MessageCircle } from 'lucide-react';

interface ShareButtonsProps {
    title: string;
    text: string;
    url?: string;
}

const ShareButtons = ({ title, text, url = window.location.href }: ShareButtonsProps) => {
    const [copied, setCopied] = useState(false);

    const shareData = {
        whatsapp: `https://wa.me/?text=${encodeURIComponent(`${title}\n\n${text}\n\n${url}`)}`,
        twitter: `https://twitter.com/intent/tweet?text=${encodeURIComponent(text)}&url=${encodeURIComponent(url)}`,
        facebook: `https://www.facebook.com/sharer/sharer.php?u=${encodeURIComponent(url)}`,
        linkedin: `https://www.linkedin.com/sharing/share-offsite/?url=${encodeURIComponent(url)}`,
    };

    const copyToClipboard = async () => {
        try {
            await navigator.clipboard.writeText(url);
            setCopied(true);
            setTimeout(() => setCopied(false), 2000);
        } catch (err) {
            console.error('Failed to copy:', err);
        }
    };

    const handleNativeShare = async () => {
        if (navigator.share) {
            try {
                await navigator.share({ title, text, url });
            } catch (err) {
                console.log('Share cancelled');
            }
        }
    };

    return (
        <div className="flex items-center gap-2">
            {/* WhatsApp - Primary */}
            <a
                href={shareData.whatsapp}
                target="_blank"
                rel="noopener noreferrer"
                className="flex items-center gap-2 px-4 py-2 bg-green-500 hover:bg-green-600 text-white font-semibold rounded-xl transition-colors"
            >
                <MessageCircle size={18} />
                <span className="hidden sm:inline">WhatsApp</span>
            </a>

            {/* Twitter */}
            <a
                href={shareData.twitter}
                target="_blank"
                rel="noopener noreferrer"
                className="p-2 bg-white/10 hover:bg-sky-500 text-white rounded-xl transition-colors"
                title="Share on Twitter"
            >
                <svg className="w-5 h-5" fill="currentColor" viewBox="0 0 24 24">
                    <path d="M18.244 2.25h3.308l-7.227 8.26 8.502 11.24H16.17l-5.214-6.817L4.99 21.75H1.68l7.73-8.835L1.254 2.25H8.08l4.713 6.231zm-1.161 17.52h1.833L7.084 4.126H5.117z" />
                </svg>
            </a>

            {/* Facebook */}
            <a
                href={shareData.facebook}
                target="_blank"
                rel="noopener noreferrer"
                className="p-2 bg-white/10 hover:bg-blue-600 text-white rounded-xl transition-colors"
                title="Share on Facebook"
            >
                <svg className="w-5 h-5" fill="currentColor" viewBox="0 0 24 24">
                    <path d="M24 12.073c0-6.627-5.373-12-12-12s-12 5.373-12 12c0 5.99 4.388 10.954 10.125 11.854v-8.385H7.078v-3.47h3.047V9.43c0-3.007 1.792-4.669 4.533-4.669 1.312 0 2.686.235 2.686.235v2.953H15.83c-1.491 0-1.956.925-1.956 1.874v2.25h3.328l-.532 3.47h-2.796v8.385C19.612 23.027 24 18.062 24 12.073z" />
                </svg>
            </a>

            {/* Copy Link */}
            <button
                onClick={copyToClipboard}
                className={`p-2 rounded-xl transition-all ${copied ? 'bg-green-500 text-white' : 'bg-white/10 hover:bg-white/20 text-white'
                    }`}
                title={copied ? 'Copied!' : 'Copy link'}
            >
                {copied ? <Check size={20} /> : <Link2 size={20} />}
            </button>

            {/* Native Share (Mobile) */}
            {navigator.share && (
                <button
                    onClick={handleNativeShare}
                    className="p-2 bg-white/10 hover:bg-white/20 text-white rounded-xl transition-colors lg:hidden"
                    title="Share"
                >
                    <Share2 size={20} />
                </button>
            )}
        </div>
    );
};

export default ShareButtons;
