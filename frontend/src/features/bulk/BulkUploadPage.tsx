import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { Upload, FileSpreadsheet, Download, MapPin, TrendingUp, DollarSign, Users, Droplets } from 'lucide-react';
import axios from 'axios';

interface SiteResult {
    site_id: string;
    address: string;
    annual_yield_liters: number;
    tank_size_liters: number;
    cost_inr: number;
    lat?: number;
    lng?: number;
}

interface BatchResult {
    batch_id: string;
    batch_name: string;
    total_sites: number;
    processed_sites: number;
    total_capture_liters: number;
    total_cost_inr: number;
    avg_payback_years: number;
    site_results: SiteResult[];
    summary: {
        water_saved_million_liters: number;
        investment_lakhs: number;
        co2_offset_tons: number;
    };
}

const BulkUploadPage = () => {
    const [file, setFile] = useState<File | null>(null);
    const [scenario, setScenario] = useState('cost_optimized');
    const [loading, setLoading] = useState(false);
    const [results, setResults] = useState<BatchResult | null>(null);

    const downloadSampleCSV = async () => {
        const response = await axios.get('https://rainforge-api.onrender.com/api/v1/bulk/sample-csv');
        const blob = new Blob([response.data.content], { type: 'text/csv' });
        const url = window.URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = 'rainforge_bulk_template.csv';
        a.click();
    };

    const handleUpload = async () => {
        if (!file) return;

        setLoading(true);
        try {
            const formData = new FormData();
            formData.append('file', file);
            formData.append('scenario', scenario);

            const response = await axios.post(
                `https://rainforge-api.onrender.com/api/v1/bulk/upload-csv?scenario=${scenario}`,
                formData,
                { headers: { 'Content-Type': 'multipart/form-data' } }
            );
            setResults(response.data);
        } catch (err: any) {
            alert(err.response?.data?.detail || 'Upload failed');
        } finally {
            setLoading(false);
        }
    };

    if (results) {
        return <BulkResults results={results} onReset={() => setResults(null)} />;
    }

    return (
        <div className="min-h-screen bg-gradient-to-br from-slate-900 via-blue-900 to-slate-900 py-12">
            <div className="max-w-4xl mx-auto px-4">
                {/* Header */}
                <div className="text-center mb-12">
                    <div className="inline-flex items-center gap-2 px-4 py-2 bg-green-500/10 border border-green-500/20 rounded-full mb-4">
                        <FileSpreadsheet className="text-green-400" size={16} />
                        <span className="text-green-300 text-sm font-medium">City-Scale Deployment</span>
                    </div>
                    <h1 className="text-5xl font-black text-white mb-4">Bulk Assessment</h1>
                    <p className="text-xl text-gray-300">
                        Upload multiple sites for batch processing • 10 to 10,000 locations
                    </p>
                </div>

                {/* Upload Card */}
                <div className="glass rounded-2xl p-8 mb-6">
                    <div
                        className={`border-2 border-dashed rounded-xl p-12 text-center transition-colors ${file ? 'border-green-500 bg-green-500/10' : 'border-white/20 hover:border-cyan-500'
                            }`}
                        onDrop={(e) => {
                            e.preventDefault();
                            const f = e.dataTransfer.files[0];
                            if (f?.name.endsWith('.csv')) setFile(f);
                        }}
                        onDragOver={(e) => e.preventDefault()}
                    >
                        {file ? (
                            <div className="space-y-4">
                                <FileSpreadsheet className="w-16 h-16 text-green-400 mx-auto" />
                                <div>
                                    <p className="text-xl font-bold text-white">{file.name}</p>
                                    <p className="text-gray-400">{(file.size / 1024).toFixed(1)} KB</p>
                                </div>
                                <button
                                    onClick={() => setFile(null)}
                                    className="text-red-400 hover:text-red-300"
                                >
                                    Remove
                                </button>
                            </div>
                        ) : (
                            <div className="space-y-4">
                                <Upload className="w-16 h-16 text-gray-400 mx-auto" />
                                <div>
                                    <p className="text-xl font-semibold text-white">
                                        Drag & drop your CSV file here
                                    </p>
                                    <p className="text-gray-400">or click to browse</p>
                                </div>
                                <input
                                    type="file"
                                    accept=".csv"
                                    onChange={(e) => setFile(e.target.files?.[0] || null)}
                                    className="hidden"
                                    id="file-upload"
                                />
                                <label
                                    htmlFor="file-upload"
                                    className="inline-block px-6 py-3 bg-white/10 hover:bg-white/20 text-white font-semibold rounded-lg cursor-pointer"
                                >
                                    Choose File
                                </label>
                            </div>
                        )}
                    </div>

                    {/* Scenario Selection */}
                    <div className="mt-6">
                        <label className="block text-white font-semibold mb-3">Assessment Scenario</label>
                        <div className="grid grid-cols-3 gap-4">
                            {[
                                { id: 'cost_optimized', label: 'Cost Optimized', desc: 'Minimize investment' },
                                { id: 'max_capture', label: 'Maximum Capture', desc: 'Maximize water saved' },
                                { id: 'dry_season', label: 'Dry Season', desc: 'Focus on reliability' },
                            ].map(s => (
                                <button
                                    key={s.id}
                                    onClick={() => setScenario(s.id)}
                                    className={`p-4 rounded-xl text-left transition-all ${scenario === s.id
                                        ? 'bg-cyan-500 text-white'
                                        : 'bg-white/5 text-gray-300 hover:bg-white/10'
                                        }`}
                                >
                                    <div className="font-bold">{s.label}</div>
                                    <div className="text-sm opacity-75">{s.desc}</div>
                                </button>
                            ))}
                        </div>
                    </div>

                    {/* Actions */}
                    <div className="mt-8 flex gap-4">
                        <button
                            onClick={handleUpload}
                            disabled={!file || loading}
                            className={`flex-1 py-4 rounded-xl font-bold text-lg transition-all ${file && !loading
                                ? 'bg-gradient-to-r from-cyan-500 to-blue-500 text-white hover:scale-105'
                                : 'bg-gray-700 text-gray-500 cursor-not-allowed'
                                }`}
                        >
                            {loading ? 'Processing...' : 'Run Batch Assessment'}
                        </button>
                        <button
                            onClick={downloadSampleCSV}
                            className="px-6 py-4 bg-white/10 hover:bg-white/20 text-white font-semibold rounded-xl flex items-center gap-2"
                        >
                            <Download size={20} />
                            Sample CSV
                        </button>
                    </div>
                </div>

                {/* Instructions */}
                <div className="glass rounded-2xl p-6">
                    <h3 className="text-lg font-bold text-white mb-4">CSV Format</h3>
                    <div className="overflow-x-auto">
                        <table className="w-full text-sm">
                            <thead>
                                <tr className="text-left text-cyan-400 border-b border-white/10">
                                    <th className="pb-2">Column</th>
                                    <th className="pb-2">Required</th>
                                    <th className="pb-2">Example</th>
                                </tr>
                            </thead>
                            <tbody className="text-gray-300">
                                <tr className="border-b border-white/5">
                                    <td className="py-2 font-mono">site_id</td>
                                    <td>Yes</td>
                                    <td>SITE001</td>
                                </tr>
                                <tr className="border-b border-white/5">
                                    <td className="py-2 font-mono">address</td>
                                    <td>Yes</td>
                                    <td>Municipal School Sector 5</td>
                                </tr>
                                <tr className="border-b border-white/5">
                                    <td className="py-2 font-mono">roof_area_sqm</td>
                                    <td>Yes</td>
                                    <td>250</td>
                                </tr>
                                <tr className="border-b border-white/5">
                                    <td className="py-2 font-mono">roof_material</td>
                                    <td>No</td>
                                    <td>concrete</td>
                                </tr>
                                <tr>
                                    <td className="py-2 font-mono">lat, lng</td>
                                    <td>No</td>
                                    <td>28.6139, 77.2090</td>
                                </tr>
                            </tbody>
                        </table>
                    </div>
                </div>
            </div>
        </div>
    );
};

const BulkResults = ({ results, onReset }: { results: BatchResult; onReset: () => void }) => {
    return (
        <div className="min-h-screen bg-gradient-to-br from-slate-900 via-blue-900 to-slate-900 py-12">
            <div className="max-w-7xl mx-auto px-4">
                {/* Header */}
                <div className="flex justify-between items-start mb-8">
                    <div>
                        <h1 className="text-4xl font-black text-white mb-2">{results.batch_name}</h1>
                        <p className="text-gray-400">Batch ID: {results.batch_id} • {results.processed_sites} sites processed</p>
                    </div>
                    <button
                        onClick={onReset}
                        className="px-6 py-3 bg-white/10 hover:bg-white/20 text-white font-semibold rounded-xl"
                    >
                        New Upload
                    </button>
                </div>

                {/* Key Metrics */}
                <div className="grid grid-cols-2 md:grid-cols-4 gap-6 mb-8">
                    <div className="glass rounded-2xl p-6">
                        <div className="flex items-center gap-3 mb-2">
                            <Droplets className="text-cyan-400" size={24} />
                            <span className="text-gray-400 font-medium">Total Capture</span>
                        </div>
                        <div className="text-3xl font-black text-white">
                            {results.summary.water_saved_million_liters.toFixed(1)}M L
                        </div>
                        <div className="text-sm text-gray-400">per year</div>
                    </div>

                    <div className="glass rounded-2xl p-6">
                        <div className="flex items-center gap-3 mb-2">
                            <DollarSign className="text-green-400" size={24} />
                            <span className="text-gray-400 font-medium">Investment</span>
                        </div>
                        <div className="text-3xl font-black text-white">
                            ₹{results.summary.investment_lakhs.toFixed(1)}L
                        </div>
                        <div className="text-sm text-gray-400">total cost</div>
                    </div>

                    <div className="glass rounded-2xl p-6">
                        <div className="flex items-center gap-3 mb-2">
                            <TrendingUp className="text-purple-400" size={24} />
                            <span className="text-gray-400 font-medium">Avg Payback</span>
                        </div>
                        <div className="text-3xl font-black text-white">
                            {results.avg_payback_years.toFixed(1)} yrs
                        </div>
                        <div className="text-sm text-gray-400">ROI period</div>
                    </div>

                    <div className="glass rounded-2xl p-6">
                        <div className="flex items-center gap-3 mb-2">
                            <Users className="text-yellow-400" size={24} />
                            <span className="text-gray-400 font-medium">Beneficiaries</span>
                        </div>
                        <div className="text-3xl font-black text-white">
                            {(results.processed_sites * 4).toLocaleString()}
                        </div>
                        <div className="text-sm text-gray-400">people impacted</div>
                    </div>
                </div>

                {/* Results Table */}
                <div className="glass rounded-2xl p-6">
                    <h3 className="text-xl font-bold text-white mb-4">Site-wise Results</h3>
                    <div className="overflow-x-auto">
                        <table className="w-full">
                            <thead>
                                <tr className="text-left text-gray-400 border-b border-white/10">
                                    <th className="pb-3 font-medium">Site ID</th>
                                    <th className="pb-3 font-medium">Address</th>
                                    <th className="pb-3 font-medium text-right">Annual Yield</th>
                                    <th className="pb-3 font-medium text-right">Tank Size</th>
                                    <th className="pb-3 font-medium text-right">Cost</th>
                                </tr>
                            </thead>
                            <tbody>
                                {results.site_results.map((site, idx) => (
                                    <tr key={idx} className="border-b border-white/5 hover:bg-white/5">
                                        <td className="py-3 text-cyan-400 font-mono">{site.site_id}</td>
                                        <td className="py-3 text-white">{site.address}</td>
                                        <td className="py-3 text-right text-white font-semibold">
                                            {(site.annual_yield_liters / 1000).toFixed(1)} kL
                                        </td>
                                        <td className="py-3 text-right text-gray-300">
                                            {(site.tank_size_liters / 1000).toFixed(1)} kL
                                        </td>
                                        <td className="py-3 text-right text-green-400 font-semibold">
                                            ₹{(site.cost_inr / 1000).toFixed(0)}k
                                        </td>
                                    </tr>
                                ))}
                            </tbody>
                        </table>
                    </div>
                </div>

                {/* CO2 Impact */}
                <div className="mt-6 glass rounded-2xl p-6 bg-gradient-to-r from-green-500/10 to-emerald-500/10 border-green-500/20">
                    <div className="flex items-center justify-between">
                        <div>
                            <h3 className="text-xl font-bold text-white">Environmental Impact</h3>
                            <p className="text-gray-300">CO₂ offset from reduced water pumping</p>
                        </div>
                        <div className="text-4xl font-black text-green-400">
                            {results.summary.co2_offset_tons.toFixed(1)} tons/year
                        </div>
                    </div>
                </div>
            </div>
        </div>
    );
};

export default BulkUploadPage;
