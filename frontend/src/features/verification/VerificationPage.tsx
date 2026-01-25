import { useState } from 'react';
import { Camera, MapPin, CheckCircle, XCircle, Clock, Upload, Image } from 'lucide-react';
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
        try {
            await axios.post(`https://rainforge-api.onrender.com/api/v1/verification/${projectId}/submit`, {
                project_id: projectId,
                photo_url: photoUrl || 'https://via.placeholder.com/800x600?text=Installation+Photo',
                geo_lat: geoLat,
                geo_lng: geoLng,
                notes
            });
            setSubmitted(true);
        } catch (err) {
            alert('Submission failed');
        } finally {
            setSubmitting(false);
        }
    };

    if (submitted) {
        return (
            <div className="min-h-screen bg-gradient-to-br from-slate-900 via-blue-900 to-slate-900 flex items-center justify-center">
                <div className="glass rounded-3xl p-12 max-w-md text-center">
                    <div className="w-20 h-20 bg-gradient-to-r from-green-400 to-emerald-500 rounded-full flex items-center justify-center mx-auto mb-6">
                        <CheckCircle size={40} className="text-white" />
                    </div>
                    <h2 className="text-3xl font-black text-white mb-4">Verification Submitted!</h2>
                    <p className="text-gray-300 mb-8">
                        Your installation verification for Project #{projectId} has been submitted.
                        An admin will review and approve within 24-48 hours.
                    </p>
                    <button
                        onClick={() => setSubmitted(false)}
                        className="px-8 py-3 bg-gradient-to-r from-cyan-500 to-blue-500 text-white font-bold rounded-xl"
                    >
                        Submit Another
                    </button>
                </div>
            </div>
        );
    }

    return (
        <div className="min-h-screen bg-gradient-to-br from-slate-900 via-blue-900 to-slate-900 py-12">
            <div className="max-w-2xl mx-auto px-4">
                {/* Header */}
                <div className="text-center mb-12">
                    <div className="inline-flex items-center gap-2 px-4 py-2 bg-purple-500/10 border border-purple-500/20 rounded-full mb-4">
                        <Camera className="text-purple-400" size={16} />
                        <span className="text-purple-300 text-sm font-medium">Installer Portal</span>
                    </div>
                    <h1 className="text-5xl font-black text-white mb-4">Verification</h1>
                    <p className="text-xl text-gray-300">
                        Submit photo evidence of completed RWH installation
                    </p>
                </div>

                {/* Form */}
                <div className="glass rounded-2xl p-8 space-y-6">
                    {/* Project ID */}
                    <div>
                        <label className="block text-white font-semibold mb-2">Project ID</label>
                        <input
                            type="number"
                            value={projectId}
                            onChange={(e) => setProjectId(parseInt(e.target.value))}
                            className="w-full p-3 bg-white/5 border border-white/10 rounded-xl text-white"
                            placeholder="Enter project ID"
                        />
                    </div>

                    {/* Photo Upload */}
                    <div>
                        <label className="block text-white font-semibold mb-2">Installation Photo</label>
                        <div className="border-2 border-dashed border-white/20 rounded-xl p-8 text-center hover:border-purple-500 transition-colors">
                            <Image className="w-12 h-12 text-gray-400 mx-auto mb-3" />
                            <p className="text-gray-400 mb-2">Click to upload or drag photo</p>
                            <p className="text-xs text-gray-500">JPEG, PNG up to 10MB</p>
                            <input
                                type="text"
                                value={photoUrl}
                                onChange={(e) => setPhotoUrl(e.target.value)}
                                className="mt-4 w-full p-2 bg-white/5 border border-white/10 rounded text-white text-sm"
                                placeholder="Or paste image URL..."
                            />
                        </div>
                    </div>

                    {/* Geo Location */}
                    <div>
                        <label className="block text-white font-semibold mb-2">GPS Location</label>
                        <div className="flex gap-4">
                            <div className="flex-1">
                                <input
                                    type="number"
                                    step="0.0001"
                                    value={geoLat}
                                    onChange={(e) => setGeoLat(parseFloat(e.target.value))}
                                    className="w-full p-3 bg-white/5 border border-white/10 rounded-xl text-white"
                                    placeholder="Latitude"
                                />
                            </div>
                            <div className="flex-1">
                                <input
                                    type="number"
                                    step="0.0001"
                                    value={geoLng}
                                    onChange={(e) => setGeoLng(parseFloat(e.target.value))}
                                    className="w-full p-3 bg-white/5 border border-white/10 rounded-xl text-white"
                                    placeholder="Longitude"
                                />
                            </div>
                            <button
                                onClick={handleGetLocation}
                                className="px-4 bg-white/10 hover:bg-white/20 rounded-xl text-white flex items-center gap-2"
                            >
                                <MapPin size={18} />
                            </button>
                        </div>
                    </div>

                    {/* Notes */}
                    <div>
                        <label className="block text-white font-semibold mb-2">Notes (Optional)</label>
                        <textarea
                            value={notes}
                            onChange={(e) => setNotes(e.target.value)}
                            className="w-full p-3 bg-white/5 border border-white/10 rounded-xl text-white h-24 resize-none"
                            placeholder="Any additional details about the installation..."
                        />
                    </div>

                    {/* Submit */}
                    <button
                        onClick={handleSubmit}
                        disabled={submitting}
                        className="w-full py-4 bg-gradient-to-r from-purple-500 to-pink-500 text-white font-bold rounded-xl text-lg hover:scale-105 transition-transform disabled:opacity-50"
                    >
                        {submitting ? 'Submitting...' : 'Submit Verification'}
                    </button>
                </div>

                {/* Info */}
                <div className="mt-6 glass rounded-2xl p-6">
                    <h3 className="text-lg font-bold text-white mb-4">Verification Requirements</h3>
                    <ul className="space-y-3 text-gray-300">
                        <li className="flex items-start gap-2">
                            <CheckCircle size={18} className="text-green-400 mt-0.5" />
                            Clear photo showing installed tank and connections
                        </li>
                        <li className="flex items-start gap-2">
                            <CheckCircle size={18} className="text-green-400 mt-0.5" />
                            GPS location matching project address
                        </li>
                        <li className="flex items-start gap-2">
                            <CheckCircle size={18} className="text-green-400 mt-0.5" />
                            First-flush diverter visible in photo
                        </li>
                    </ul>
                </div>
            </div>
        </div>
    );
};

export default VerificationPage;
