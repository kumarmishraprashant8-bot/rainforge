import { useState } from 'react';
import { Camera, MapPin, CheckCircle, Image, Send } from 'lucide-react';
import axios from 'axios';

const VerificationPage = () => {
    const [projectId, setProjectId] = useState<number>(123);
    const [photoUrl, setPhotoUrl] = useState('');
    const [geoLat, setGeoLat] = useState(28.6139);
    const [geoLng, setGeoLng] = useState(77.209);
    const [notes, setNotes] = useState('');
    const [submitting, setSubmitting] = useState(false);
    const [submitted, setSubmitted] = useState(false);

    const handleGetLocation = () => {
        if (navigator.geolocation) {
            navigator.geolocation.getCurrentPosition((pos) => {
                setGeoLat(pos.coords.latitude);
                setGeoLng(pos.coords.longitude);
            });
        }
    };

    const handleSubmit = async () => {
        setSubmitting(true);
        // For demo: simulate instant success
        await new Promise(resolve => setTimeout(resolve, 800));
        setSubmitted(true);
        setSubmitting(false);
    };

    if (submitted) {
        return (
            <div className="min-h-screen flex items-center justify-center py-12 px-4">
                <div className="card-premium card-glow rounded-3xl p-12 max-w-md text-center animate-fade-in-up">
                    <div className="w-20 h-20 rounded-2xl bg-[var(--color-accent-success)]/20 flex items-center justify-center mx-auto mb-6">
                        <CheckCircle size={40} className="text-[var(--color-accent-success)]" />
                    </div>
                    <h2 className="text-2xl font-bold text-[var(--color-text-primary)] mb-4">
                        Verification Submitted!
                    </h2>
                    <p className="text-[var(--color-text-secondary)] mb-8">
                        Your installation verification for Project #{projectId} has been submitted.
                        An admin will review and approve within 24-48 hours.
                    </p>
                    <button
                        onClick={() => setSubmitted(false)}
                        className="btn-primary px-8 py-3"
                    >
                        Submit Another
                    </button>
                </div>
            </div>
        );
    }

    return (
        <div className="min-h-screen py-12">
            <div className="max-w-2xl mx-auto px-4 sm:px-6">
                {/* Header */}
                <div className="text-center mb-12 animate-fade-in-up">
                    <div className="inline-flex items-center gap-2 px-4 py-2 rounded-full bg-[var(--color-accent-secondary)]/10 border border-[var(--color-accent-secondary)]/20 mb-6">
                        <Camera className="text-[var(--color-accent-secondary)]" size={16} />
                        <span className="text-[var(--color-accent-secondary)] text-sm font-medium">Installer Portal</span>
                    </div>
                    <h1 className="text-4xl sm:text-5xl font-bold text-[var(--color-text-primary)] mb-4">
                        Verification
                    </h1>
                    <p className="text-lg text-[var(--color-text-secondary)]">
                        Submit photo evidence of completed RWH installation
                    </p>
                </div>

                {/* Form */}
                <div className="card-premium rounded-2xl p-8 space-y-6 animate-fade-in-up stagger-1">
                    {/* Project ID */}
                    <div>
                        <label className="block text-[var(--color-text-primary)] font-medium mb-2">Project ID</label>
                        <input
                            type="number"
                            value={projectId}
                            onChange={(e) => setProjectId(parseInt(e.target.value))}
                            className="w-full p-3 bg-[var(--color-bg-elevated)] border border-[var(--color-border)] rounded-xl text-[var(--color-text-primary)] focus:border-[var(--color-accent-primary)]"
                            placeholder="Enter project ID"
                        />
                    </div>

                    {/* Photo Upload */}
                    <div>
                        <label className="block text-[var(--color-text-primary)] font-medium mb-2">Installation Photo</label>
                        <div className="border-2 border-dashed border-[var(--color-border)] rounded-xl p-8 text-center hover:border-[var(--color-accent-primary)]/50 transition-colors">
                            <div className="w-14 h-14 mx-auto mb-3 rounded-xl bg-[var(--color-border)] flex items-center justify-center">
                                <Image className="text-[var(--color-text-muted)]" size={24} />
                            </div>
                            <p className="text-[var(--color-text-muted)] mb-2">Click to upload or drag photo</p>
                            <p className="text-xs text-[var(--color-text-muted)]">JPEG, PNG up to 10MB</p>
                            <input
                                type="text"
                                value={photoUrl}
                                onChange={(e) => setPhotoUrl(e.target.value)}
                                className="mt-4 w-full p-2 bg-[var(--color-bg-elevated)] border border-[var(--color-border)] rounded-lg text-[var(--color-text-primary)] text-sm"
                                placeholder="Or paste image URL..."
                            />
                        </div>
                    </div>

                    {/* Geo Location */}
                    <div>
                        <label className="block text-[var(--color-text-primary)] font-medium mb-2">GPS Location</label>
                        <div className="flex gap-3">
                            <input
                                type="number"
                                step="0.0001"
                                value={geoLat}
                                onChange={(e) => setGeoLat(parseFloat(e.target.value))}
                                className="flex-1 p-3 bg-[var(--color-bg-elevated)] border border-[var(--color-border)] rounded-xl text-[var(--color-text-primary)]"
                                placeholder="Latitude"
                            />
                            <input
                                type="number"
                                step="0.0001"
                                value={geoLng}
                                onChange={(e) => setGeoLng(parseFloat(e.target.value))}
                                className="flex-1 p-3 bg-[var(--color-bg-elevated)] border border-[var(--color-border)] rounded-xl text-[var(--color-text-primary)]"
                                placeholder="Longitude"
                            />
                            <button
                                onClick={handleGetLocation}
                                className="btn-secondary px-4 flex items-center gap-2"
                            >
                                <MapPin size={18} />
                            </button>
                        </div>
                    </div>

                    {/* Notes */}
                    <div>
                        <label className="block text-[var(--color-text-primary)] font-medium mb-2">Notes (Optional)</label>
                        <textarea
                            value={notes}
                            onChange={(e) => setNotes(e.target.value)}
                            className="w-full p-3 bg-[var(--color-bg-elevated)] border border-[var(--color-border)] rounded-xl text-[var(--color-text-primary)] h-24 resize-none"
                            placeholder="Any additional details about the installation..."
                        />
                    </div>

                    {/* Submit */}
                    <button
                        onClick={handleSubmit}
                        disabled={submitting}
                        className="w-full btn-primary py-4 text-lg flex items-center justify-center gap-2"
                    >
                        {submitting ? (
                            <>
                                <span className="animate-spin">⏳</span>
                                Submitting...
                            </>
                        ) : (
                            <>
                                <Send size={18} />
                                Submit Verification
                            </>
                        )}
                    </button>
                </div>

                {/* Info */}
                <div className="mt-6 card-premium rounded-2xl p-6 animate-fade-in-up stagger-2">
                    <h3 className="text-lg font-semibold text-[var(--color-text-primary)] mb-4">Verification Requirements</h3>
                    <ul className="space-y-3">
                        <li className="flex items-start gap-3 text-[var(--color-text-secondary)]">
                            <CheckCircle size={18} className="text-[var(--color-accent-success)] mt-0.5 flex-shrink-0" />
                            Clear photo showing installed tank and connections
                        </li>
                        <li className="flex items-start gap-3 text-[var(--color-text-secondary)]">
                            <CheckCircle size={18} className="text-[var(--color-accent-success)] mt-0.5 flex-shrink-0" />
                            GPS location matching project address
                        </li>
                        <li className="flex items-start gap-3 text-[var(--color-text-secondary)]">
                            <CheckCircle size={18} className="text-[var(--color-accent-success)] mt-0.5 flex-shrink-0" />
                            First-flush diverter visible in photo
                        </li>
                    </ul>
                </div>
            </div>
        </div>
    );
};

export default VerificationPage;
