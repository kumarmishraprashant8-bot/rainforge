import React, { useState, Suspense, lazy } from 'react';
import { useNavigate } from 'react-router-dom';
import { ArrowRight, MapPin, Home, Sparkles, Ruler } from 'lucide-react';
import axios from 'axios';

// Lazy load the map to avoid SSR issues
const RoofMap = lazy(() => import('../../components/RoofMap'));

const IntakePage = () => {
    const navigate = useNavigate();
    const [formData, setFormData] = useState({
        address: '',
        roof_material: 'concrete',
        roof_area: 0,
        geometry: null as any
    });
    const [loading, setLoading] = useState(false);
    const [polygonDrawn, setPolygonDrawn] = useState(false);
    const [manualArea, setManualArea] = useState('');
    const [useManualInput, setUseManualInput] = useState(false);

    const handlePolygonUpdate = (area: number, geojson: any) => {
        setFormData(prev => ({ ...prev, geometry: geojson, roof_area: area || 120 }));
        setPolygonDrawn(true);
    };

    const submit = async () => {
        setLoading(true);
        const areaToUse = useManualInput && manualArea ? parseFloat(manualArea) : formData.roof_area || 120;

        try {
            const response = await axios.post('https://rainforge-api.onrender.com/api/v1/assessments/quick', {
                address: formData.address || '123 Rain Street, New Delhi',
                roof_material: formData.roof_material,
                roof_area_sqm: areaToUse,
                polygon_geojson: formData.geometry || null
            });
            navigate(`/assess/${response.data.project_id}`, { state: { result: response.data } });
        } catch (error: any) {
            console.error(error);
            const errorMsg = error.response?.data?.detail || error.message || 'Unknown error';
            alert(`Failed: ${errorMsg}`);
        } finally {
            setLoading(false);
        }
    };

    return (
        <div className="min-h-screen bg-gradient-to-br from-slate-900 via-blue-900 to-slate-900 py-12">
            <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
                {/* Header */}
                <div className="text-center mb-12">
                    <div className="inline-flex items-center gap-2 px-4 py-2 bg-cyan-500/10 border border-cyan-500/20 rounded-full mb-4">
                        <Sparkles className="text-cyan-400" size={16} />
                        <span className="text-cyan-300 text-sm font-medium">AI-Powered Assessment</span>
                    </div>
                    <h1 className="text-5xl font-black text-white mb-4">
                        Start Your Assessment
                    </h1>
                    <p className="text-xl text-gray-300">
                        Draw your roof on the map or enter area manually
                    </p>
                </div>

                <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
                    {/* Sidebar Form */}
                    <div className="lg:col-span-1 space-y-6">
                        <div className="glass rounded-2xl p-6 space-y-6">
                            <div>
                                <label className="block text-sm font-semibold text-white mb-2">
                                    📍 Property Address
                                </label>
                                <div className="relative">
                                    <MapPin className="absolute left-4 top-4 text-gray-400 h-5 w-5" />
                                    <input
                                        type="text"
                                        className="pl-12 w-full rounded-xl bg-white/5 border border-white/10 text-white placeholder-gray-400 p-3 focus:border-cyan-500 focus:ring-2 focus:ring-cyan-500/20 transition-all"
                                        placeholder="123 Rain Street, Delhi"
                                        value={formData.address}
                                        onChange={e => setFormData({ ...formData, address: e.target.value })}
                                    />
                                </div>
                            </div>

                            <div>
                                <label className="block text-sm font-semibold text-white mb-2">
                                    🏠 Roof Material
                                </label>
                                <div className="relative">
                                    <Home className="absolute left-4 top-4 text-gray-400 h-5 w-5 pointer-events-none z-10" />
                                    <select
                                        className="pl-12 w-full rounded-xl bg-white/5 border border-white/10 text-white p-3 focus:border-cyan-500 focus:ring-2 focus:ring-cyan-500/20 transition-all appearance-none cursor-pointer"
                                        value={formData.roof_material}
                                        onChange={e => setFormData({ ...formData, roof_material: e.target.value })}
                                    >
                                        <option value="concrete" className="bg-slate-800">Concrete / Flat (C=0.85)</option>
                                        <option value="metal" className="bg-slate-800">Metal (C=0.90)</option>
                                        <option value="tiles" className="bg-slate-800">Tiles (C=0.80)</option>
                                        <option value="asbestos" className="bg-slate-800">Asbestos (C=0.85)</option>
                                        <option value="thatched" className="bg-slate-800">Thatched (C=0.60)</option>
                                    </select>
                                </div>
                            </div>

                            {/* Manual Area Input Toggle */}
                            <div className="border border-white/10 rounded-xl p-4">
                                <label className="flex items-center gap-3 cursor-pointer">
                                    <input
                                        type="checkbox"
                                        checked={useManualInput}
                                        onChange={(e) => setUseManualInput(e.target.checked)}
                                        className="w-4 h-4 rounded bg-white/10 border-white/20 text-cyan-500 focus:ring-cyan-500"
                                    />
                                    <span className="text-white font-medium">Enter area manually</span>
                                </label>

                                {useManualInput && (
                                    <div className="mt-3 relative">
                                        <Ruler className="absolute left-4 top-4 text-gray-400 h-5 w-5" />
                                        <input
                                            type="number"
                                            className="pl-12 w-full rounded-xl bg-white/5 border border-white/10 text-white placeholder-gray-400 p-3 focus:border-cyan-500 transition-all"
                                            placeholder="Roof area in m²"
                                            value={manualArea}
                                            onChange={e => setManualArea(e.target.value)}
                                        />
                                    </div>
                                )}
                            </div>

                            {/* Area Display */}
                            {(polygonDrawn || (useManualInput && manualArea)) && (
                                <div className="bg-gradient-to-r from-green-500/10 to-emerald-500/10 border border-green-500/20 rounded-xl p-4">
                                    <div className="text-sm text-gray-400 mb-1">Roof Area</div>
                                    <div className="text-3xl font-black text-green-400">
                                        {useManualInput ? manualArea : formData.roof_area} m²
                                    </div>
                                </div>
                            )}

                            <button
                                onClick={submit}
                                disabled={loading}
                                className={`w-full flex items-center justify-center gap-2 py-4 px-6 rounded-xl text-white font-bold text-lg transition-all duration-300 transform
                                    ${loading ? 'bg-gray-600 cursor-not-allowed' : 'bg-gradient-to-r from-cyan-500 to-blue-500 hover:scale-105 shadow-2xl hover:shadow-cyan-500/50'}
                                `}
                            >
                                {loading ? (
                                    <>
                                        <div className="animate-spin rounded-full h-5 w-5 border-b-2 border-white"></div>
                                        Analyzing...
                                    </>
                                ) : (
                                    <>
                                        Run Assessment
                                        <ArrowRight size={20} />
                                    </>
                                )}
                            </button>
                        </div>
                    </div>

                    {/* Map Area */}
                    <div className="lg:col-span-2">
                        <div className="glass rounded-2xl p-2 h-[600px]">
                            <Suspense fallback={
                                <div className="w-full h-full rounded-xl bg-slate-800 flex items-center justify-center">
                                    <div className="text-center">
                                        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-cyan-400 mx-auto mb-4"></div>
                                        <div className="text-white font-semibold">Loading map...</div>
                                    </div>
                                </div>
                            }>
                                <RoofMap onPolygonUpdate={handlePolygonUpdate} />
                            </Suspense>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    );
};

export default IntakePage;
