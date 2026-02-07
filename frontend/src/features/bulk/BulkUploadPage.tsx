import { useState } from 'react';
import { Upload, FileSpreadsheet, Download, TrendingUp, DollarSign, Users, Droplets, CheckCircle, ArrowRight } from 'lucide-react';
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
        // Generate sample CSV content directly
        const sampleContent = `site_id,address,roof_area_sqm,roof_material,lat,lng
SITE001,Municipal School Sector 5,250,concrete,28.6139,77.2090
SITE002,Community Center Phase 2,180,tiles,28.5789,77.2156
SITE003,Government Hospital Building,450,concrete,28.6298,77.1890
SITE004,District Court Complex,320,metal,28.6512,77.2298
SITE005,Public Library Block A,150,concrete,28.5923,77.2465`;
        const blob = new Blob([sampleContent], { type: 'text/csv' });
        const url = window.URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = 'rainforge_bulk_template.csv';
        a.click();
    };

    const handleUpload = async () => {
        if (!file) return;

        setLoading(true);
        await new Promise(resolve => setTimeout(resolve, 1500)); // Simulate processing

        // Generate mock results
        const mockSites: SiteResult[] = [
            { site_id: 'SITE001', address: 'Municipal School Sector 5', annual_yield_liters: 106250, tank_size_liters: 10000, cost_inr: 85000 },
            { site_id: 'SITE002', address: 'Community Center Phase 2', annual_yield_liters: 76500, tank_size_liters: 8000, cost_inr: 68000 },
            { site_id: 'SITE003', address: 'Government Hospital Building', annual_yield_liters: 191250, tank_size_liters: 20000, cost_inr: 145000 },
            { site_id: 'SITE004', address: 'District Court Complex', annual_yield_liters: 136000, tank_size_liters: 15000, cost_inr: 112000 },
            { site_id: 'SITE005', address: 'Public Library Block A', annual_yield_liters: 63750, tank_size_liters: 6000, cost_inr: 52000 },
        ];

        const totalCapture = mockSites.reduce((sum, s) => sum + s.annual_yield_liters, 0);
        const totalCost = mockSites.reduce((sum, s) => sum + s.cost_inr, 0);

        setResults({
            batch_id: `BATCH-${Date.now().toString(36).toUpperCase()}`,
            batch_name: file.name.replace('.csv', ''),
            total_sites: mockSites.length,
            processed_sites: mockSites.length,
            total_capture_liters: totalCapture,
            total_cost_inr: totalCost,
            avg_payback_years: 4.2,
            site_results: mockSites,
            summary: {
                water_saved_million_liters: totalCapture / 1000000,
                investment_lakhs: totalCost / 100000,
                co2_offset_tons: (totalCapture / 1000) * 0.255 / 1000
            }
        });
        setLoading(false);
    };

    if (results) {
        return <BulkResults results={results} onReset={() => setResults(null)} />;
    }

    const scenarios = [
        {
            id: 'cost_optimized',
            label: 'Cost Optimized',
            desc: 'Minimize investment',
            icon: '💰'
        },
        {
            id: 'max_capture',
            label: 'Maximum Capture',
            desc: 'Maximize water saved',
            icon: '💧'
        },
        {
            id: 'dry_season',
            label: 'Dry Season',
            desc: 'Focus on reliability',
            icon: '☀️'
        },
    ];

    return (
        <div className="min-h-screen py-12">
            <div className="max-w-4xl mx-auto px-4 sm:px-6">
                {/* Header */}
                <div className="text-center mb-12 animate-fade-in-up">
                    <div className="inline-flex items-center gap-2 px-4 py-2 rounded-full bg-[var(--color-accent-success)]/10 border border-[var(--color-accent-success)]/20 mb-6">
                        <FileSpreadsheet className="text-[var(--color-accent-success)]" size={16} />
                        <span className="text-[var(--color-accent-success)] text-sm font-medium">City-Scale Deployment</span>
                    </div>
                    <h1 className="text-4xl sm:text-5xl font-bold text-[var(--color-text-primary)] mb-4">
                        Bulk Assessment
                    </h1>
                    <p className="text-lg text-[var(--color-text-secondary)] max-w-xl mx-auto">
                        Upload multiple sites for batch processing • 10 to 10,000 locations
                    </p>
                </div>

                {/* Upload Card */}
                <div className="card-premium rounded-2xl p-8 mb-6 animate-fade-in-up stagger-1">
                    <div
                        className={`border-2 border-dashed rounded-2xl p-12 text-center transition-all duration-300 ${file
                            ? 'border-[var(--color-accent-success)] bg-[var(--color-accent-success)]/5'
                            : 'border-[var(--color-border)] hover:border-[var(--color-accent-primary)]/50 hover:bg-[var(--color-accent-primary)]/5'
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
                                <div className="w-16 h-16 mx-auto rounded-2xl bg-[var(--color-accent-success)]/15 flex items-center justify-center">
                                    <CheckCircle className="text-[var(--color-accent-success)]" size={32} />
                                </div>
                                <div>
                                    <p className="text-xl font-semibold text-[var(--color-text-primary)]">{file.name}</p>
                                    <p className="text-[var(--color-text-muted)]">{(file.size / 1024).toFixed(1)} KB</p>
                                </div>
                                <button
                                    onClick={() => setFile(null)}
                                    className="text-[var(--color-accent-danger)] hover:underline text-sm"
                                >
                                    Remove file
                                </button>
                            </div>
                        ) : (
                            <div className="space-y-4">
                                <div className="w-16 h-16 mx-auto rounded-2xl bg-[var(--color-border)] flex items-center justify-center">
                                    <Upload className="text-[var(--color-text-muted)]" size={28} />
                                </div>
                                <div>
                                    <p className="text-lg font-medium text-[var(--color-text-primary)]">
                                        Drag & drop your CSV file here
                                    </p>
                                    <p className="text-[var(--color-text-muted)] text-sm mt-1">or click to browse</p>
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
                                    className="btn-secondary inline-block cursor-pointer"
                                >
                                    Choose File
                                </label>
                            </div>
                        )}
                    </div>

                    {/* Scenario Selection */}
                    <div className="mt-8">
                        <label className="block text-[var(--color-text-primary)] font-medium mb-4">
                            Assessment Scenario
                        </label>
                        <div className="grid grid-cols-1 sm:grid-cols-3 gap-3">
                            {scenarios.map(s => (
                                <button
                                    key={s.id}
                                    onClick={() => setScenario(s.id)}
                                    className={`p-4 rounded-xl text-left transition-all duration-200 border ${scenario === s.id
                                        ? 'bg-[var(--color-accent-primary)]/15 border-[var(--color-accent-primary)]/30 text-[var(--color-text-primary)]'
                                        : 'bg-transparent border-[var(--color-border)] text-[var(--color-text-secondary)] hover:border-[var(--color-border-hover)] hover:bg-[var(--color-bg-elevated)]'
                                        }`}
                                >
                                    <div className="flex items-center gap-3">
                                        <span className="text-xl">{s.icon}</span>
                                        <div>
                                            <div className="font-medium">{s.label}</div>
                                            <div className="text-sm opacity-70">{s.desc}</div>
                                        </div>
                                    </div>
                                </button>
                            ))}
                        </div>
                    </div>

                    {/* Actions */}
                    <div className="mt-8 flex flex-col sm:flex-row gap-3">
                        <button
                            onClick={handleUpload}
                            disabled={!file || loading}
                            className={`flex-1 py-4 rounded-xl font-semibold text-lg transition-all flex items-center justify-center gap-2 ${file && !loading
                                ? 'btn-primary'
                                : 'bg-[var(--color-border)] text-[var(--color-text-muted)] cursor-not-allowed'
                                }`}
                        >
                            {loading ? (
                                <>
                                    <span className="animate-spin">⏳</span>
                                    Processing...
                                </>
                            ) : (
                                <>
                                    Run Batch Assessment
                                    <ArrowRight size={18} />
                                </>
                            )}
                        </button>
                        <button
                            onClick={downloadSampleCSV}
                            className="btn-secondary px-6 py-4 flex items-center justify-center gap-2"
                        >
                            <Download size={18} />
                            Sample CSV
                        </button>
                    </div>
                </div>

                {/* Instructions */}
                <div className="card-premium rounded-2xl p-6 animate-fade-in-up stagger-2">
                    <h3 className="text-lg font-semibold text-[var(--color-text-primary)] mb-4">CSV Format</h3>
                    <div className="overflow-x-auto">
                        <table className="table-premium">
                            <thead>
                                <tr>
                                    <th className="text-left">Column</th>
                                    <th className="text-left">Required</th>
                                    <th className="text-left">Example</th>
                                </tr>
                            </thead>
                            <tbody>
                                <tr>
                                    <td className="font-mono text-sm">site_id</td>
                                    <td><span className="badge-success">Yes</span></td>
                                    <td className="text-[var(--color-text-muted)]">SITE001</td>
                                </tr>
                                <tr>
                                    <td className="font-mono text-sm">address</td>
                                    <td><span className="badge-success">Yes</span></td>
                                    <td className="text-[var(--color-text-muted)]">Municipal School Sector 5</td>
                                </tr>
                                <tr>
                                    <td className="font-mono text-sm">roof_area_sqm</td>
                                    <td><span className="badge-success">Yes</span></td>
                                    <td className="text-[var(--color-text-muted)]">250</td>
                                </tr>
                                <tr>
                                    <td className="font-mono text-sm">roof_material</td>
                                    <td><span className="badge-neutral">No</span></td>
                                    <td className="text-[var(--color-text-muted)]">concrete</td>
                                </tr>
                                <tr>
                                    <td className="font-mono text-sm">lat, lng</td>
                                    <td><span className="badge-neutral">No</span></td>
                                    <td className="text-[var(--color-text-muted)]">28.6139, 77.2090</td>
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
        <div className="min-h-screen py-12">
            <div className="max-w-7xl mx-auto px-4 sm:px-6">
                {/* Header */}
                <div className="flex flex-col sm:flex-row justify-between items-start gap-4 mb-8 animate-fade-in-up">
                    <div>
                        <h1 className="text-3xl sm:text-4xl font-bold text-[var(--color-text-primary)] mb-2">
                            {results.batch_name}
                        </h1>
                        <p className="text-[var(--color-text-muted)]">
                            Batch ID: {results.batch_id} • {results.processed_sites} sites processed
                        </p>
                    </div>
                    <button onClick={onReset} className="btn-secondary">
                        ← New Upload
                    </button>
                </div>

                {/* Key Metrics */}
                <div className="grid grid-cols-2 lg:grid-cols-4 gap-4 mb-8">
                    <div className="stat-card animate-fade-in-up stagger-1">
                        <div className="stat-icon stat-icon-indigo mb-4">
                            <Droplets size={20} />
                        </div>
                        <div className="text-2xl sm:text-3xl font-bold text-[var(--color-text-primary)]">
                            {results.summary.water_saved_million_liters.toFixed(1)}M L
                        </div>
                        <div className="text-sm text-[var(--color-text-muted)] mt-1">Total Capture / year</div>
                    </div>

                    <div className="stat-card animate-fade-in-up stagger-2">
                        <div className="stat-icon stat-icon-emerald mb-4">
                            <DollarSign size={20} />
                        </div>
                        <div className="text-2xl sm:text-3xl font-bold text-[var(--color-text-primary)]">
                            ₹{results.summary.investment_lakhs.toFixed(1)}L
                        </div>
                        <div className="text-sm text-[var(--color-text-muted)] mt-1">Total Investment</div>
                    </div>

                    <div className="stat-card animate-fade-in-up stagger-3">
                        <div className="stat-icon stat-icon-amber mb-4">
                            <TrendingUp size={20} />
                        </div>
                        <div className="text-2xl sm:text-3xl font-bold text-[var(--color-text-primary)]">
                            {results.avg_payback_years.toFixed(1)} yrs
                        </div>
                        <div className="text-sm text-[var(--color-text-muted)] mt-1">Avg Payback</div>
                    </div>

                    <div className="stat-card animate-fade-in-up stagger-4">
                        <div className="stat-icon stat-icon-rose mb-4">
                            <Users size={20} />
                        </div>
                        <div className="text-2xl sm:text-3xl font-bold text-[var(--color-text-primary)]">
                            {(results.processed_sites * 4).toLocaleString()}
                        </div>
                        <div className="text-sm text-[var(--color-text-muted)] mt-1">Beneficiaries</div>
                    </div>
                </div>

                {/* Results Table */}
                <div className="card-premium rounded-2xl p-6 mb-6 animate-fade-in-up stagger-5">
                    <h3 className="text-lg font-semibold text-[var(--color-text-primary)] mb-4">Site-wise Results</h3>
                    <div className="overflow-x-auto">
                        <table className="table-premium">
                            <thead>
                                <tr>
                                    <th className="text-left">Site ID</th>
                                    <th className="text-left">Address</th>
                                    <th className="text-right">Annual Yield</th>
                                    <th className="text-right">Tank Size</th>
                                    <th className="text-right">Cost</th>
                                </tr>
                            </thead>
                            <tbody>
                                {results.site_results.map((site, idx) => (
                                    <tr key={idx}>
                                        <td className="font-mono text-sm text-[var(--color-accent-secondary)]">
                                            {site.site_id}
                                        </td>
                                        <td>{site.address}</td>
                                        <td className="text-right font-medium">
                                            {(site.annual_yield_liters / 1000).toFixed(1)} kL
                                        </td>
                                        <td className="text-right text-[var(--color-text-secondary)]">
                                            {(site.tank_size_liters / 1000).toFixed(1)} kL
                                        </td>
                                        <td className="text-right font-medium text-[var(--color-accent-success)]">
                                            ₹{(site.cost_inr / 1000).toFixed(0)}k
                                        </td>
                                    </tr>
                                ))}
                            </tbody>
                        </table>
                    </div>
                </div>

                {/* CO2 Impact */}
                <div className="card-premium card-glow rounded-2xl p-6 animate-fade-in-up">
                    <div className="flex flex-col sm:flex-row items-center justify-between gap-4">
                        <div>
                            <h3 className="text-lg font-semibold text-[var(--color-text-primary)]">Environmental Impact</h3>
                            <p className="text-[var(--color-text-muted)] text-sm mt-1">
                                CO₂ offset from reduced water pumping
                            </p>
                        </div>
                        <div className="text-3xl sm:text-4xl font-bold text-[var(--color-accent-success)]">
                            {results.summary.co2_offset_tons.toFixed(1)} tons/year
                        </div>
                    </div>
                </div>
            </div>
        </div>
    );
};

export default BulkUploadPage;
