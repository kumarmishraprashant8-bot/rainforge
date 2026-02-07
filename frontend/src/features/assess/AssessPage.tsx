import { useLocation } from 'react-router-dom';
import {
    Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer,
    AreaChart, Area, ComposedChart, Line, PieChart, Pie, Cell
} from 'recharts';
import {
    CloudRain, Database, DollarSign, FileText, TrendingUp, Droplets,
    Zap, Download, Info, ChevronDown, ChevronUp, CheckCircle, Leaf,
    Shield, Calendar, Wrench, AlertTriangle, Award, MapPin, Building2,
    Users, Wallet, Target, Clock, Thermometer, FileCheck, Phone
} from 'lucide-react';
import { useState } from 'react';
import API_BASE_URL from '../../config/api';
import ImpactCard from '../../components/ImpactCard';

const AssessPage = () => {
    const { state } = useLocation();
    const result = state?.result;
    const formData = state?.formData;
    const [showExplanation, setShowExplanation] = useState<string | null>(null);
    const [activeScenario, setActiveScenario] = useState('cost_optimized');
    const [activeTab, setActiveTab] = useState('overview');

    // Calculate derived values based on form data (Fallback if result not present)
    const roofArea = formData?.roof_area_sqm || 120;
    const annualRainfall = formData?.annual_rainfall_mm || 800;
    const runoffCoeff = { rcc: 0.85, metal: 0.90, tile: 0.80, asbestos: 0.85, thatched: 0.60, plastic: 0.90 }[formData?.roof_material || 'rcc'] || 0.85;
    const annualYield = result?.runoff_potential_liters || (roofArea * annualRainfall * runoffCoeff * 0.9);
    const dailyDemand = formData?.daily_water_consumption_lpd || 540;
    const recommendedTank = result?.recommended_tank_size || Math.ceil(dailyDemand * 60 / 1000) * 1000;

    // Cost calculations
    const baseCost = recommendedTank * 8; // ₹8 per liter capacity
    const materialCost = Math.round(baseCost * 0.6);
    const laborCost = Math.round(baseCost * 0.3);
    const permitCost = 2500;
    const totalCost = materialCost + laborCost + permitCost;

    // Subsidy calculation based on income category
    const subsidyPercent = { bpl: 90, low: 75, middle: 50, high: 25 }[formData?.income_category || 'middle'] || 50;
    const subsidyAmount = Math.min(Math.round(totalCost * subsidyPercent / 100), 100000);
    const netCost = totalCost - subsidyAmount;

    // ROI calculation
    const monthlyWaterBill = formData?.monthly_water_bill_inr || 500;
    const annualSavings = monthlyWaterBill * 12 * 0.6; // 60% savings
    const paybackYears = netCost / annualSavings;

    // CO2 offset (0.5 kg CO2 per 1000L of water saved)
    const co2Offset = Math.round(annualYield * 0.0005);

    // Scenarios (Frontend estimation for comparison, backend gives single detailed result)
    const scenarios = [
        {
            id: 'cost_optimized',
            name: 'Cost Optimized',
            tank: recommendedTank,
            cost: totalCost,
            subsidy: subsidyAmount,
            netCost: netCost,
            savings: annualSavings,
            payback: paybackYears.toFixed(1),
            reliability: 85,
            desc: 'Minimizes investment while meeting 80% of demand'
        },
        {
            id: 'max_capture',
            name: 'Maximum Capture',
            tank: Math.round(annualYield * 0.15),
            cost: Math.round(totalCost * 1.8),
            subsidy: Math.min(Math.round(totalCost * 1.8 * subsidyPercent / 100), 100000),
            netCost: Math.round(totalCost * 1.8) - Math.min(Math.round(totalCost * 1.8 * subsidyPercent / 100), 100000),
            savings: Math.round(annualSavings * 1.4),
            payback: ((Math.round(totalCost * 1.8) - Math.min(Math.round(totalCost * 1.8 * subsidyPercent / 100), 100000)) / (annualSavings * 1.4)).toFixed(1),
            reliability: 98,
            desc: 'Captures all available rainfall, maximum water security'
        },
        {
            id: 'budget',
            name: 'Budget Friendly',
            tank: Math.round(recommendedTank * 0.6),
            cost: Math.round(totalCost * 0.6),
            subsidy: Math.min(Math.round(totalCost * 0.6 * subsidyPercent / 100), 100000),
            netCost: Math.round(totalCost * 0.6) - Math.min(Math.round(totalCost * 0.6 * subsidyPercent / 100), 100000),
            savings: Math.round(annualSavings * 0.7),
            payback: ((Math.round(totalCost * 0.6) - Math.min(Math.round(totalCost * 0.6 * subsidyPercent / 100), 100000)) / (annualSavings * 0.7)).toFixed(1),
            reliability: 70,
            desc: 'Lowest cost option for basic coverage'
        },
    ];

    const activeScenarioData = scenarios.find(s => s.id === activeScenario) || scenarios[0];

    // Monthly breakdown chart data
    const monthlyMultipliers = [0.02, 0.02, 0.03, 0.05, 0.08, 0.15, 0.20, 0.18, 0.12, 0.07, 0.05, 0.03];
    const chartData = monthlyMultipliers.map((mult, idx) => ({
        month: ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"][idx],
        yield: Math.round(annualYield * mult),
        demand: Math.round(dailyDemand * 30),
        cumulative: monthlyMultipliers.slice(0, idx + 1).reduce((a, b) => a + b, 0) * annualYield
    }));

    // Bill of Materials (Fallback if result.materials not present)
    const billOfMaterialsFallback = [
        { item: "Storage Tank", spec: `${Math.round(activeScenarioData.tank / 1000)} kL ${formData?.tank_material_preference || 'Concrete'}`, qty: 1, rate: Math.round(activeScenarioData.tank * 5), total: Math.round(activeScenarioData.tank * 5) },
        { item: "PVC Pipes (110mm)", spec: "ISI marked, pressure rated", qty: Math.ceil(formData?.num_floors || 1) * 10, rate: 180, total: Math.ceil(formData?.num_floors || 1) * 10 * 180 },
        { item: "Gutter System", spec: `${Math.ceil(roofArea / 20)}m galvanized`, qty: Math.ceil(roofArea / 20), rate: 350, total: Math.ceil(roofArea / 20) * 350 },
        { item: "First Flush Diverter", spec: "20L auto-reset type", qty: 1, rate: 1500, total: 1500 },
        { item: "Mesh Filter", spec: "Stainless steel 2-stage", qty: 1, rate: 2500, total: 2500 },
        { item: "Overflow Pipe", spec: "110mm PVC", qty: 5, rate: 180, total: 900 },
        { item: "Submersible Pump", spec: "0.5 HP, 2000 LPH", qty: 1, rate: 4500, total: 4500 },
        { item: "Float Valve", spec: "Brass, 1 inch", qty: 1, rate: 800, total: 800 },
    ];
    const materialTotalFallback = billOfMaterialsFallback.reduce((sum, item) => sum + item.total, 0);

    // Maintenance schedule (Fallback)
    const maintenanceScheduleFallback = [
        { task: "Clean gutters and downspouts", frequency: "Monthly", priority: "High" },
        { task: "Inspect first flush diverter", frequency: "Monthly", priority: "High" },
        { task: "Clean mesh filters", frequency: "Bi-weekly during monsoon", priority: "High" },
        { task: "Check tank for sediment", frequency: "Quarterly", priority: "Medium" },
        { task: "Inspect pump operation", frequency: "Monthly", priority: "Medium" },
        { task: "Test water quality", frequency: "Quarterly", priority: "Medium" },
        { task: "Professional tank cleaning", frequency: "Annually", priority: "High" },
        { task: "Check overflow drainage", frequency: "Before monsoon", priority: "High" },
    ];

    // Permits required (Fallback)
    const permitsRequiredFallback = [
        { permit: "Municipal RWH Permission", authority: "Municipal Corporation", time: "7-15 days", required: true },
        { permit: "NOC from Water Board", authority: "State Water Board", time: "15-30 days", required: formData?.property_type === 'commercial' || formData?.property_type === 'industrial' },
        { permit: "Building Modification Approval", authority: "Building Dept", time: "15-30 days", required: formData?.num_floors > 3 },
        { permit: "Environmental Clearance", authority: "Pollution Control Board", time: "30-45 days", required: formData?.property_type === 'industrial' },
    ].filter(p => p.required);

    // Water quality grade based on purpose and filtration
    const waterQualityGrade = formData?.water_quality_requirement === 'potable' ? 'A' : formData?.water_quality_requirement === 'non_potable' ? 'B' : 'C';

    if (!result && !formData) return (
        <div className="min-h-screen bg-gradient-to-br from-slate-900 via-blue-900 to-slate-900 flex items-center justify-center">
            <div className="text-center glass rounded-2xl p-12 max-w-md">
                <div className="text-6xl mb-6">📊</div>
                <h2 className="text-2xl font-bold text-white mb-2">No Assessment Data</h2>
                <p className="text-gray-400 mb-6">Please complete the intake form first</p>
                <a href="/intake" className="px-6 py-3 bg-gradient-to-r from-cyan-500 to-blue-500 text-white font-bold rounded-xl">
                    Start Assessment →
                </a>
            </div>
        </div>
    );

    const downloadReport = async () => {
        try {
            const pdfUrl = result?.pdf_url
                ? `${API_BASE_URL}${result.pdf_url}`
                : `${API_BASE_URL}/api/v1/assessments/${result?.project_id}/report`;
            const response = await fetch(pdfUrl);
            if (!response.ok) throw new Error(`HTTP ${response.status}`);
            const blob = await response.blob();
            const url = window.URL.createObjectURL(blob);
            const a = document.createElement('a');
            a.href = url;
            a.download = `RainForge_Report_${result?.project_id || result?.assessment_id || 'demo'}.pdf`;
            a.click();
        } catch {
            // Fallback: Generate detailed PDF using HTML template and print
            const printContent = `
<!DOCTYPE html>
<html>
<head>
    <title>RainForge Assessment Report</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body { font-family: 'Segoe UI', Arial, sans-serif; line-height: 1.6; color: #1e293b; padding: 40px; max-width: 800px; margin: 0 auto; }
        .header { background: linear-gradient(135deg, #0ea5e9, #6366f1); color: white; padding: 30px; border-radius: 12px; margin-bottom: 30px; }
        .header h1 { font-size: 28px; margin-bottom: 8px; }
        .header p { opacity: 0.9; }
        .section { background: #f8fafc; border: 1px solid #e2e8f0; border-radius: 12px; padding: 24px; margin-bottom: 20px; }
        .section h2 { color: #0ea5e9; font-size: 18px; margin-bottom: 16px; border-bottom: 2px solid #0ea5e9; padding-bottom: 8px; }
        .grid { display: grid; grid-template-columns: repeat(2, 1fr); gap: 16px; }
        .metric { background: white; padding: 16px; border-radius: 8px; border: 1px solid #e2e8f0; }
        .metric-label { font-size: 12px; color: #64748b; text-transform: uppercase; letter-spacing: 0.5px; }
        .metric-value { font-size: 24px; font-weight: 700; color: #1e293b; margin-top: 4px; }
        .metric-value.highlight { color: #0ea5e9; }
        .metric-value.green { color: #10b981; }
        table { width: 100%; border-collapse: collapse; margin-top: 12px; }
        th, td { padding: 12px; text-align: left; border-bottom: 1px solid #e2e8f0; }
        th { background: #f1f5f9; font-weight: 600; font-size: 12px; text-transform: uppercase; }
        .total-row { background: #f0fdf4; font-weight: 700; }
        .total-row td { color: #10b981; }
        .recommendation { display: flex; gap: 12px; padding: 12px; background: white; border-radius: 8px; margin-bottom: 8px; border: 1px solid #e2e8f0; }
        .rec-icon { font-size: 24px; }
        .rec-title { font-weight: 600; color: #1e293b; }
        .rec-desc { font-size: 14px; color: #64748b; }
        .footer { text-align: center; margin-top: 40px; padding-top: 20px; border-top: 2px solid #e2e8f0; color: #64748b; font-size: 12px; }
        .badge { display: inline-block; padding: 4px 12px; border-radius: 20px; font-size: 12px; font-weight: 600; }
        .badge-blue { background: #dbeafe; color: #1d4ed8; }
        .badge-green { background: #dcfce7; color: #16a34a; }
        .badge-purple { background: #f3e8ff; color: #7c3aed; }
        @media print { body { padding: 20px; } .section { break-inside: avoid; } }
    </style>
</head>
<body>
    <div class="header">
        <h1>🌧️ RainForge Assessment Report</h1>
        <p>Project ID: ${result?.project_id || 'DEMO'} | Generated: ${new Date().toLocaleDateString('en-IN', { day: 'numeric', month: 'long', year: 'numeric' })}</p>
    </div>

    <div class="section">
        <h2>📍 Property Details</h2>
        <div class="grid">
            <div class="metric">
                <div class="metric-label">Location</div>
                <div class="metric-value">${formData?.city || 'New Delhi'}, ${formData?.state || 'Delhi'}</div>
            </div>
            <div class="metric">
                <div class="metric-label">Property Type</div>
                <div class="metric-value">${formData?.property_type || 'Residential'}</div>
            </div>
            <div class="metric">
                <div class="metric-label">Roof Area</div>
                <div class="metric-value highlight">${roofArea} m²</div>
            </div>
            <div class="metric">
                <div class="metric-label">Roof Material</div>
                <div class="metric-value">${formData?.roof_material?.toUpperCase() || 'RCC'} (C=${runoffCoeff})</div>
            </div>
            <div class="metric">
                <div class="metric-label">Number of Floors</div>
                <div class="metric-value">${formData?.num_floors || 1}</div>
            </div>
            <div class="metric">
                <div class="metric-label">Occupants</div>
                <div class="metric-value">${formData?.num_people || 4} people</div>
            </div>
        </div>
    </div>

    <div class="section">
        <h2>💧 Water Analysis</h2>
        <div class="grid">
            <div class="metric">
                <div class="metric-label">Annual Rainfall</div>
                <div class="metric-value">${annualRainfall} mm</div>
            </div>
            <div class="metric">
                <div class="metric-label">Annual Yield Potential</div>
                <div class="metric-value highlight">${Math.round(annualYield).toLocaleString()} L</div>
            </div>
            <div class="metric">
                <div class="metric-label">Daily Demand</div>
                <div class="metric-value">${dailyDemand} L/day</div>
            </div>
            <div class="metric">
                <div class="metric-label">Demand Coverage</div>
                <div class="metric-value green">${Math.round((annualYield / (dailyDemand * 365)) * 100)}%</div>
            </div>
            <div class="metric">
                <div class="metric-label">Recommended Tank Size</div>
                <div class="metric-value highlight">${activeScenarioData.tank.toLocaleString()} L (${(activeScenarioData.tank / 1000).toFixed(1)} kL)</div>
            </div>
            <div class="metric">
                <div class="metric-label">System Reliability</div>
                <div class="metric-value">${activeScenarioData.reliability}%</div>
            </div>
        </div>
        <p style="margin-top: 16px; padding: 12px; background: #f0f9ff; border-radius: 8px; font-size: 14px;">
            <strong>Formula:</strong> Q = C × R × A × η = ${runoffCoeff} × ${annualRainfall}mm × ${roofArea}m² × 0.9 = <strong>${Math.round(annualYield).toLocaleString()} L/year</strong>
        </p>
    </div>

    <div class="section">
        <h2>💰 Cost & Financial Analysis</h2>
        <table>
            <tr><th>Component</th><th style="text-align: right">Amount (₹)</th></tr>
            <tr><td>Material Cost</td><td style="text-align: right">${materialCost.toLocaleString()}</td></tr>
            <tr><td>Labor Cost</td><td style="text-align: right">${laborCost.toLocaleString()}</td></tr>
            <tr><td>Permit & Documentation</td><td style="text-align: right">${permitCost.toLocaleString()}</td></tr>
            <tr style="font-weight: 600"><td>Total Cost</td><td style="text-align: right">₹${totalCost.toLocaleString()}</td></tr>
            <tr style="color: #10b981"><td>Subsidy (${subsidyPercent}% - ${formData?.income_category || 'middle'} income)</td><td style="text-align: right">-₹${subsidyAmount.toLocaleString()}</td></tr>
            <tr class="total-row"><td><strong>Net Investment</strong></td><td style="text-align: right"><strong>₹${netCost.toLocaleString()}</strong></td></tr>
        </table>
        <div class="grid" style="margin-top: 16px">
            <div class="metric">
                <div class="metric-label">Annual Savings</div>
                <div class="metric-value green">₹${Math.round(annualSavings).toLocaleString()}/year</div>
            </div>
            <div class="metric">
                <div class="metric-label">Payback Period</div>
                <div class="metric-value">${activeScenarioData.payback} years</div>
            </div>
        </div>
    </div>

    <div class="section">
        <h2>🛠️ Bill of Materials</h2>
        <table>
            <tr><th>Item</th><th>Specification</th><th style="text-align: center">Qty</th><th style="text-align: right">Amount (₹)</th></tr>
            ${billOfMaterialsFallback.map(m => `<tr><td>${m.item}</td><td style="font-size: 13px; color: #64748b">${m.spec}</td><td style="text-align: center">${m.qty}</td><td style="text-align: right">${m.total.toLocaleString()}</td></tr>`).join('')}
            <tr class="total-row"><td colspan="3"><strong>Total Materials</strong></td><td style="text-align: right"><strong>₹${materialTotalFallback.toLocaleString()}</strong></td></tr>
        </table>
    </div>

    <div class="section">
        <h2>✅ System Recommendations</h2>
        <div class="recommendation"><span class="rec-icon">💧</span><div><div class="rec-title">First Flush Diverter</div><div class="rec-desc">20L capacity, auto-reset type to divert initial contaminated runoff</div></div></div>
        <div class="recommendation"><span class="rec-icon">🔧</span><div><div class="rec-title">Filtration System</div><div class="rec-desc">2-stage filtering: gravel bed + mesh filter before tank entry</div></div></div>
        <div class="recommendation"><span class="rec-icon">🌊</span><div><div class="rec-title">Overflow Management</div><div class="rec-desc">Route excess to ${formData?.storage_preference === 'recharge' ? 'groundwater recharge pit' : 'stormwater drain'}</div></div></div>
        <div class="recommendation"><span class="rec-icon">⚡</span><div><div class="rec-title">Pump Specification</div><div class="rec-desc">0.5 HP submersible pump, 2000 LPH capacity recommended</div></div></div>
    </div>

    <div class="section">
        <h2>🌍 Environmental Impact</h2>
        <div class="grid">
            <div class="metric">
                <div class="metric-label">CO₂ Offset</div>
                <div class="metric-value green">${co2Offset} kg/year</div>
            </div>
            <div class="metric">
                <div class="metric-label">Water Credits Earned</div>
                <div class="metric-value highlight">${Math.floor(annualYield / 1000)} credits</div>
            </div>
        </div>
    </div>

    <div class="footer">
        <p><strong>RainForge</strong> - AI-Powered Rainwater Harvesting Platform</p>
        <p>Reference: IS 15797:2008 Guidelines for Rainwater Harvesting</p>
        <p style="margin-top: 8px">This report is auto-generated. For official certification, please consult a licensed engineer.</p>
    </div>
</body>
</html>`;

            // Open print dialog for PDF
            const printWindow = window.open('', '_blank');
            if (printWindow) {
                printWindow.document.write(printContent);
                printWindow.document.close();
                printWindow.focus();
                setTimeout(() => {
                    printWindow.print();
                }, 500);
            }
        }
    };

    const ExplainPanel = ({ title, children, id }: { title: string; children: React.ReactNode; id: string }) => (
        <div className="mt-2">
            <button
                onClick={() => setShowExplanation(showExplanation === id ? null : id)}
                className="flex items-center gap-2 text-sm text-cyan-400 hover:text-cyan-300"
            >
                <Info size={14} />
                Explain Calculation
                {showExplanation === id ? <ChevronUp size={14} /> : <ChevronDown size={14} />}
            </button>
            {showExplanation === id && (
                <div className="mt-3 p-4 bg-white/5 rounded-lg text-sm text-gray-300 space-y-2">
                    <div className="font-semibold text-white">{title}</div>
                    {children}
                </div>
            )}
        </div>
    );

    const TabButton = ({ id, label, icon: Icon }: { id: string; label: string; icon: any }) => (
        <button
            onClick={() => setActiveTab(id)}
            className={`flex items-center gap-2 px-4 py-2 rounded-lg font-medium transition-all ${activeTab === id
                ? 'bg-gradient-to-r from-cyan-500 to-blue-500 text-white'
                : 'text-gray-400 hover:text-white hover:bg-white/10'
                }`}
        >
            <Icon size={18} />
            {label}
        </button>
    );

    return (
        <div className="min-h-screen bg-gradient-to-br from-slate-900 via-blue-900 to-slate-900 py-8">
            <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 space-y-6">
                {/* Header */}
                <div className="glass rounded-2xl p-6">
                    <div className="flex flex-col lg:flex-row justify-between items-start lg:items-center gap-4">
                        <div>
                            <div className="flex items-center gap-3 mb-2">
                                <div className="p-2 bg-gradient-to-r from-cyan-500 to-blue-500 rounded-lg">
                                    <Droplets className="text-white" size={24} />
                                </div>
                                <div>
                                    <h1 className="text-3xl font-black text-white">Assessment Complete</h1>
                                    <p className="text-gray-400 text-sm">Project #{result?.project_id || 'DEMO'}</p>
                                </div>
                            </div>
                            {formData && (
                                <div className="flex flex-wrap gap-2 mt-3">
                                    <span className="px-2 py-1 bg-purple-500/20 text-purple-300 rounded text-xs flex items-center gap-1">
                                        <Building2 size={12} /> {formData.property_type}
                                    </span>
                                    <span className="px-2 py-1 bg-cyan-500/20 text-cyan-300 rounded text-xs flex items-center gap-1">
                                        <MapPin size={12} /> {formData.city}, {formData.state}
                                    </span>
                                    <span className="px-2 py-1 bg-green-500/20 text-green-300 rounded text-xs flex items-center gap-1">
                                        <Users size={12} /> {formData.num_people} people
                                    </span>
                                </div>
                            )}
                        </div>
                        <button
                            onClick={downloadReport}
                            className="flex items-center gap-2 px-6 py-3 bg-gradient-to-r from-cyan-500 to-blue-500 text-white font-bold rounded-xl hover:scale-105 transition-transform shadow-lg"
                        >
                            <Download size={20} />
                            Download Report
                        </button>
                    </div>
                </div>

                {/* Tab Navigation */}
                <div className="flex flex-wrap gap-2 bg-white/5 p-2 rounded-xl">
                    <TabButton id="overview" label="Overview" icon={TrendingUp} />
                    <TabButton id="scenarios" label="Scenarios" icon={Zap} />
                    <TabButton id="materials" label="Bill of Materials" icon={Wrench} />
                    <TabButton id="subsidy" label="Subsidies" icon={Wallet} />
                    <TabButton id="compliance" label="Compliance" icon={Shield} />
                    <TabButton id="maintenance" label="Maintenance" icon={Calendar} />
                </div>

                {/* Overview Tab */}
                {activeTab === 'overview' && (
                    <>
                        {/* Key Metrics */}
                        <div className="grid grid-cols-2 lg:grid-cols-4 gap-4">
                            <div className="glass rounded-xl p-5">
                                <div className="flex items-center gap-3 mb-3">
                                    <div className="p-2 bg-gradient-to-br from-blue-500 to-cyan-500 rounded-lg">
                                        <CloudRain className="text-white" size={20} />
                                    </div>
                                    <span className="text-gray-400 text-sm">Annual Yield</span>
                                </div>
                                <div className="text-2xl font-black text-white">
                                    {Math.round(annualYield).toLocaleString()} L
                                </div>
                                <ExplainPanel id="yield" title="Yield Calculation">
                                    <p><strong>Formula:</strong> Q = C × R × A × η</p>
                                    <p><strong>C:</strong> Runoff coefficient ({runoffCoeff})</p>
                                    <p><strong>R:</strong> Rainfall ({annualRainfall} mm/year)</p>
                                    <p><strong>A:</strong> Roof area ({roofArea} m²)</p>
                                    <p><strong>η:</strong> Collection efficiency (90%)</p>
                                    <p className="text-xs text-gray-500 mt-2">Reference: IS 15797:2008</p>
                                </ExplainPanel>
                            </div>

                            <div className="glass rounded-xl p-5">
                                <div className="flex items-center gap-3 mb-3">
                                    <div className="p-2 bg-gradient-to-br from-indigo-500 to-purple-500 rounded-lg">
                                        <Database className="text-white" size={20} />
                                    </div>
                                    <span className="text-gray-400 text-sm">Tank Size</span>
                                </div>
                                <div className="text-2xl font-black text-white">
                                    {Math.round(activeScenarioData.tank).toLocaleString()} L
                                </div>
                                <ExplainPanel id="tank" title="Tank Sizing">
                                    <p><strong>Method:</strong> 2-month carryover capacity</p>
                                    <p><strong>Daily demand:</strong> {dailyDemand} L</p>
                                    <p><strong>Calculation:</strong> {dailyDemand} × 60 days</p>
                                </ExplainPanel>
                            </div>

                            <div className="glass rounded-xl p-5">
                                <div className="flex items-center gap-3 mb-3">
                                    <div className="p-2 bg-gradient-to-br from-green-500 to-emerald-500 rounded-lg">
                                        <DollarSign className="text-white" size={20} />
                                    </div>
                                    <span className="text-gray-400 text-sm">Net Cost</span>
                                </div>
                                <div className="text-2xl font-black text-white">
                                    ₹{activeScenarioData.netCost.toLocaleString()}
                                </div>
                                <p className="text-xs text-green-400 mt-1">After ₹{activeScenarioData.subsidy.toLocaleString()} subsidy</p>
                            </div>

                            <div className="glass rounded-xl p-5">
                                <div className="flex items-center gap-3 mb-3">
                                    <div className="p-2 bg-gradient-to-br from-yellow-500 to-orange-500 rounded-lg">
                                        <Leaf className="text-white" size={20} />
                                    </div>
                                    <span className="text-gray-400 text-sm">CO₂ Offset</span>
                                </div>
                                <div className="text-2xl font-black text-white">{co2Offset} kg/yr</div>
                                <p className="text-xs text-gray-500 mt-1">From reduced pumping</p>
                            </div>
                        </div>

                        {/* Additional Key Outputs */}
                        <div className="grid grid-cols-2 lg:grid-cols-5 gap-4">
                            <div className="glass rounded-xl p-4 text-center">
                                <div className="text-3xl mb-2">💧</div>
                                <div className="text-xl font-bold text-white">{activeScenarioData.reliability}%</div>
                                <div className="text-xs text-gray-400">Reliability</div>
                            </div>
                            <div className="glass rounded-xl p-4 text-center">
                                <div className="text-3xl mb-2">⏱️</div>
                                <div className="text-xl font-bold text-white">{activeScenarioData.payback} yrs</div>
                                <div className="text-xs text-gray-400">Payback Period</div>
                            </div>
                            <div className="glass rounded-xl p-4 text-center">
                                <div className="text-3xl mb-2">💰</div>
                                <div className="text-xl font-bold text-green-400">₹{Math.round(activeScenarioData.savings).toLocaleString()}</div>
                                <div className="text-xs text-gray-400">Annual Savings</div>
                            </div>
                            <div className="glass rounded-xl p-4 text-center">
                                <div className="text-3xl mb-2">🏆</div>
                                <div className="text-xl font-bold text-purple-400">Grade {waterQualityGrade}</div>
                                <div className="text-xs text-gray-400">Water Quality</div>
                            </div>
                            <div className="glass rounded-xl p-4 text-center">
                                <div className="text-3xl mb-2">📊</div>
                                <div className="text-xl font-bold text-cyan-400">{Math.round((annualYield / (dailyDemand * 365)) * 100)}%</div>
                                <div className="text-xs text-gray-400">Demand Met</div>
                            </div>
                        </div>

                        {/* Your impact + Share (grand success features) */}
                        <ImpactCard
                            waterSecurityIndex={result?.water_security_index}
                            waterCredits={result?.water_credits ?? (annualYield ? Math.floor(annualYield / 1000) : undefined)}
                            annualYieldLiters={annualYield}
                            equivalentShowers={annualYield ? Math.floor(annualYield / 50) : undefined}
                            shareMessage={result?.impact?.share_message}
                            badges={result?.badges}
                        />

                        {/* Charts */}
                        <div className="grid lg:grid-cols-2 gap-6">
                            <div className="glass rounded-2xl p-6">
                                <h3 className="text-lg font-bold text-white mb-4 flex items-center gap-2">
                                    <TrendingUp className="text-cyan-400" size={20} />
                                    Water Balance Simulation
                                </h3>
                                <div className="h-72">
                                    <ResponsiveContainer width="100%" height="100%">
                                        <ComposedChart data={chartData}>
                                            <CartesianGrid strokeDasharray="3 3" stroke="#334155" vertical={false} />
                                            <XAxis dataKey="month" stroke="#94a3b8" fontSize={12} />
                                            <YAxis stroke="#94a3b8" fontSize={12} />
                                            <Tooltip contentStyle={{ backgroundColor: '#1e293b', border: '1px solid #334155', borderRadius: '8px' }} />
                                            <Bar dataKey="yield" fill="#06b6d4" radius={[4, 4, 0, 0]} name="Supply" />
                                            <Line type="monotone" dataKey="demand" stroke="#f59e0b" strokeWidth={2} name="Demand" />
                                        </ComposedChart>
                                    </ResponsiveContainer>
                                </div>
                            </div>

                            <div className="glass rounded-2xl p-6">
                                <h3 className="text-lg font-bold text-white mb-4 flex items-center gap-2">
                                    <Droplets className="text-green-400" size={20} />
                                    Cumulative Capture
                                </h3>
                                <div className="h-72">
                                    <ResponsiveContainer width="100%" height="100%">
                                        <AreaChart data={chartData}>
                                            <CartesianGrid strokeDasharray="3 3" stroke="#334155" vertical={false} />
                                            <XAxis dataKey="month" stroke="#94a3b8" fontSize={12} />
                                            <YAxis stroke="#94a3b8" fontSize={12} />
                                            <Tooltip contentStyle={{ backgroundColor: '#1e293b', border: '1px solid #334155', borderRadius: '8px' }} />
                                            <Area type="monotone" dataKey="cumulative" stroke="#10b981" fill="url(#colorGreen)" />
                                            <defs>
                                                <linearGradient id="colorGreen" x1="0" y1="0" x2="0" y2="1">
                                                    <stop offset="0%" stopColor="#10b981" stopOpacity={0.8} />
                                                    <stop offset="100%" stopColor="#10b981" stopOpacity={0.1} />
                                                </linearGradient>
                                            </defs>
                                        </AreaChart>
                                    </ResponsiveContainer>
                                </div>
                            </div>
                        </div>
                    </>
                )}

                {/* Scenarios Tab */}
                {activeTab === 'scenarios' && (
                    <div className="glass rounded-2xl p-6">
                        <h3 className="text-xl font-bold text-white mb-6 flex items-center gap-2">
                            <Zap className="text-yellow-400" size={24} />
                            Scenario Comparison
                        </h3>
                        <div className="grid lg:grid-cols-3 gap-4">
                            {scenarios.map(s => (
                                <button
                                    key={s.id}
                                    onClick={() => setActiveScenario(s.id)}
                                    className={`p-6 rounded-xl text-left transition-all ${activeScenario === s.id
                                        ? 'bg-gradient-to-r from-cyan-500/20 to-blue-500/20 border-2 border-cyan-500'
                                        : 'bg-white/5 border-2 border-transparent hover:border-white/20'
                                        }`}
                                >
                                    <div className="flex justify-between items-start mb-3">
                                        <span className="font-bold text-white text-lg">{s.name}</span>
                                        {activeScenario === s.id && <CheckCircle className="text-cyan-400" size={20} />}
                                    </div>
                                    <p className="text-sm text-gray-400 mb-4">{s.desc}</p>
                                    <div className="space-y-2">
                                        <div className="flex justify-between">
                                            <span className="text-gray-500">Tank Size</span>
                                            <span className="text-white font-semibold">{(s.tank / 1000).toFixed(1)} kL</span>
                                        </div>
                                        <div className="flex justify-between">
                                            <span className="text-gray-500">Total Cost</span>
                                            <span className="text-white">₹{s.cost.toLocaleString()}</span>
                                        </div>
                                        <div className="flex justify-between">
                                            <span className="text-gray-500">Subsidy</span>
                                            <span className="text-green-400">-₹{s.subsidy.toLocaleString()}</span>
                                        </div>
                                        <div className="flex justify-between border-t border-white/10 pt-2">
                                            <span className="text-gray-400 font-semibold">Net Cost</span>
                                            <span className="text-cyan-400 font-bold">₹{s.netCost.toLocaleString()}</span>
                                        </div>
                                        <div className="flex justify-between">
                                            <span className="text-gray-500">Payback</span>
                                            <span className="text-white">{s.payback} years</span>
                                        </div>
                                        <div className="flex justify-between">
                                            <span className="text-gray-500">Reliability</span>
                                            <span className="text-purple-400">{s.reliability}%</span>
                                        </div>
                                    </div>
                                </button>
                            ))}
                        </div>
                    </div>
                )}

                {/* Bill of Materials Tab */}
                {activeTab === 'materials' && (
                    <div className="glass rounded-2xl p-6">
                        <h3 className="text-xl font-bold text-white mb-6 flex items-center gap-2">
                            <Wrench className="text-orange-400" size={24} />
                            Bill of Materials
                        </h3>
                        <div className="overflow-x-auto">
                            <table className="w-full">
                                <thead>
                                    <tr className="border-b border-white/10">
                                        <th className="text-left py-3 px-4 text-gray-400 font-medium">Item</th>
                                        <th className="text-left py-3 px-4 text-gray-400 font-medium">Specification</th>
                                        <th className="text-center py-3 px-4 text-gray-400 font-medium">Qty</th>
                                        <th className="text-right py-3 px-4 text-gray-400 font-medium">Rate (₹)</th>
                                        <th className="text-right py-3 px-4 text-gray-400 font-medium">Total (₹)</th>
                                    </tr>
                                </thead>
                                <tbody>
                                    {(result?.materials || billOfMaterialsFallback).map((item: any, idx: number) => (
                                        <tr key={idx} className="border-b border-white/5 hover:bg-white/5">
                                            <td className="py-3 px-4 text-white font-medium">{item.name || item.item}</td>
                                            <td className="py-3 px-4 text-gray-400 text-sm">{item.category || item.spec}</td>
                                            <td className="py-3 px-4 text-center text-white">{item.quantity || item.qty} {item.unit}</td>
                                            <td className="py-3 px-4 text-right text-gray-400">{(item.unit_cost || item.rate).toLocaleString()}</td>
                                            <td className="py-3 px-4 text-right text-white font-semibold">{(item.total_cost || item.total).toLocaleString()}</td>
                                        </tr>
                                    ))}
                                </tbody>
                                <tfoot>
                                    <tr className="border-t-2 border-white/20">
                                        <td colSpan={4} className="py-4 px-4 text-right text-white font-bold">Material Total</td>
                                        <td className="py-4 px-4 text-right text-cyan-400 font-bold text-lg">
                                            ₹{(result?.material_cost || materialTotalFallback).toLocaleString()}
                                        </td>
                                    </tr>
                                    <tr>
                                        <td colSpan={4} className="py-2 px-4 text-right text-gray-400">Labor (30%)</td>
                                        <td className="py-2 px-4 text-right text-white">
                                            ₹{(result?.labor_cost || Math.round(materialTotalFallback * 0.3)).toLocaleString()}
                                        </td>
                                    </tr>
                                    <tr className="border-t border-white/10">
                                        <td colSpan={4} className="py-4 px-4 text-right text-white font-bold">Grand Total</td>
                                        <td className="py-4 px-4 text-right text-green-400 font-bold text-xl">
                                            ₹{(result?.total_system_cost || Math.round(materialTotalFallback * 1.3)).toLocaleString()}
                                        </td>
                                    </tr>
                                </tfoot>
                            </table>
                        </div>
                    </div>
                )}

                {/* Subsidy Tab */}
                {activeTab === 'subsidy' && (
                    <div className="space-y-6">
                        <div className="glass rounded-2xl p-6 bg-gradient-to-r from-green-500/10 to-emerald-500/10 border-green-500/20">
                            <h3 className="text-xl font-bold text-white mb-6 flex items-center gap-2">
                                <Wallet className="text-green-400" size={24} />
                                Policy & Subsidy Benefits
                            </h3>
                            <div className="grid lg:grid-cols-3 gap-6">
                                <div className="bg-white/5 rounded-xl p-5">
                                    <p className="text-gray-400 text-sm mb-2">Eligible Scheme</p>
                                    <p className="text-white font-semibold text-lg">
                                        {result?.mandatory_by_law ? "Mandatory Compliance" : "Jal Shakti Abhiyan RWH"}
                                    </p>
                                    <p className="text-xs text-gray-500 mt-2">+ State {formData?.state} RWH Scheme</p>
                                </div>
                                <div className="bg-white/5 rounded-xl p-5">
                                    <p className="text-gray-400 text-sm mb-2">Subsidy Amount</p>
                                    <p className="text-green-400 font-bold text-3xl">
                                        ₹{(result?.subsidy_amount || activeScenarioData.subsidy).toLocaleString()}
                                    </p>
                                    <p className="text-xs text-gray-500 mt-2">
                                        {result?.subsidy_percent || subsidyPercent}% of cost ({formData?.income_category} level)
                                    </p>
                                </div>
                                <div className="bg-white/5 rounded-xl p-5">
                                    <p className="text-gray-400 text-sm mb-2">Your Net Investment</p>
                                    <p className="text-cyan-400 font-bold text-3xl">
                                        ₹{(result?.net_cost_after_subsidy || activeScenarioData.netCost).toLocaleString()}
                                    </p>
                                    <p className="text-xs text-gray-500 mt-2">
                                        Payback: {result?.payback_months ? (result.payback_months / 12).toFixed(1) : activeScenarioData.payback} years
                                    </p>
                                </div>
                            </div>

                            <div className="mt-6 p-4 bg-yellow-500/10 border border-yellow-500/20 rounded-xl">
                                <div className="flex items-start gap-3">
                                    <AlertTriangle className="text-yellow-400 flex-shrink-0" size={20} />
                                    <div>
                                        <p className="text-white font-semibold">Documents Required for Subsidy</p>
                                        <ul className="text-sm text-gray-400 mt-2 space-y-1">
                                            <li>• Property ownership proof / Rent agreement</li>
                                            <li>• Aadhaar card copy</li>
                                            <li>• Income certificate (for {formData?.income_category} category)</li>
                                            <li>• Water bill copy (last 3 months)</li>
                                            <li>• Site photographs</li>
                                        </ul>
                                    </div>
                                </div>
                            </div>
                        </div>
                    </div>
                )}

                {/* Compliance Tab */}
                {activeTab === 'compliance' && (
                    <div className="glass rounded-2xl p-6">
                        <h3 className="text-xl font-bold text-white mb-6 flex items-center gap-2">
                            <Shield className="text-purple-400" size={24} />
                            Permits & Compliance
                        </h3>

                        <div className="space-y-4">
                            {result?.permit_required !== undefined ? (
                                <>
                                    <div className="flex items-center gap-4 p-4 bg-white/5 rounded-xl">
                                        <div className="p-2 bg-purple-500/20 rounded-lg">
                                            <FileCheck className="text-purple-400" size={20} />
                                        </div>
                                        <div className="flex-1">
                                            <p className="text-white font-semibold">
                                                {result.permit_required ? "Municipal Permit Required" : "No Permit Required"}
                                            </p>
                                            <p className="text-gray-400 text-sm">Authority: {result.permit_authority}</p>
                                        </div>
                                        <div className="text-right">
                                            <p className="text-cyan-400 font-medium">{result.estimated_permit_time_days} days</p>
                                            <p className="text-gray-500 text-xs">Processing time</p>
                                        </div>
                                    </div>
                                    {result.mandatory_by_law && (
                                        <div className="flex items-center gap-4 p-4 bg-red-500/10 border border-red-500/20 rounded-xl">
                                            <div className="p-2 bg-red-500/20 rounded-lg">
                                                <AlertTriangle className="text-red-400" size={20} />
                                            </div>
                                            <div>
                                                <p className="text-white font-semibold">Compulsory by Law</p>
                                                <p className="text-gray-400 text-sm">RWH is mandatory for your property size in {formData?.state}.</p>
                                            </div>
                                        </div>
                                    )}
                                </>
                            ) : (
                                permitsRequiredFallback.map((permit, idx) => (
                                    <div key={idx} className="flex items-center gap-4 p-4 bg-white/5 rounded-xl">
                                        <div className="p-2 bg-purple-500/20 rounded-lg">
                                            <FileCheck className="text-purple-400" size={20} />
                                        </div>
                                        <div className="flex-1">
                                            <p className="text-white font-semibold">{permit.permit}</p>
                                            <p className="text-gray-400 text-sm">{permit.authority}</p>
                                        </div>
                                        <div className="text-right">
                                            <p className="text-cyan-400 font-medium">{permit.time}</p>
                                            <p className="text-gray-500 text-xs">Processing time</p>
                                        </div>
                                    </div>
                                ))
                            )}
                        </div>

                        <div className="mt-6 p-4 bg-cyan-500/10 border border-cyan-500/20 rounded-xl">
                            <p className="text-cyan-400 font-semibold mb-2">📋 RainForge Assistance</p>
                            <p className="text-gray-300 text-sm">
                                {formData?.needs_permit_assistance
                                    ? "We will assist you with all permit applications. Our team will contact you within 24 hours."
                                    : "Need help with permits? Enable 'Permit Assistance' during intake."}
                            </p>
                        </div>
                    </div>
                )}

                {/* Maintenance Tab */}
                {activeTab === 'maintenance' && (
                    <div className="glass rounded-2xl p-6">
                        <h3 className="text-xl font-bold text-white mb-6 flex items-center gap-2">
                            <Calendar className="text-orange-400" size={24} />
                            Maintenance Schedule
                        </h3>

                        <div className="space-y-3">
                            {(result?.maintenance_schedule || maintenanceScheduleFallback).map((item: any, idx: number) => (
                                <div key={idx} className="flex items-center gap-4 p-4 bg-white/5 rounded-xl hover:bg-white/10 transition-all">
                                    <div className={`p-2 rounded-lg ${item.priority === 'High' ? 'bg-red-500/20' : 'bg-yellow-500/20'
                                        }`}>
                                        <Wrench size={18} className={item.priority === 'High' ? 'text-red-400' : 'text-yellow-400'} />
                                    </div>
                                    <div className="flex-1">
                                        <p className="text-white font-medium">{item.task}</p>
                                        <p className="text-gray-500 text-xs">{item.next_due ? `Next due: ${item.next_due}` : (item.priority || "Normal") + " Priority"}</p>
                                    </div>
                                    <div className="text-right">
                                        <p className="text-cyan-400">{item.frequency}</p>
                                    </div>
                                </div>
                            ))}
                        </div>

                        {formData?.wants_iot_monitoring && (
                            <div className="mt-6 p-4 bg-green-500/10 border border-green-500/20 rounded-xl">
                                <p className="text-green-400 font-semibold mb-2">🔔 IoT Monitoring Enabled</p>
                                <p className="text-gray-300 text-sm">
                                    You'll receive automatic alerts for tank levels, filter cleaning reminders, and water quality anomalies via the RainForge mobile app.
                                </p>
                            </div>
                        )}
                    </div>
                )}

                {/* Recommendations */}
                <div className="glass rounded-2xl p-6">
                    <h3 className="text-xl font-bold text-white mb-6 flex items-center gap-2">
                        <Award className="text-yellow-400" size={24} />
                        System Recommendations
                    </h3>
                    <div className="grid md:grid-cols-2 lg:grid-cols-4 gap-4">
                        {[
                            { title: "First Flush Diverter", desc: "20L capacity, auto-reset type", icon: "💧" },
                            { title: "Filtration System", desc: "2-stage: gravel + mesh before tank", icon: "🔧" },
                            { title: "Overflow Management", desc: `Route to ${formData?.storage_preference === 'recharge' ? 'recharge pit' : 'drain'}`, icon: "🌊" },
                            { title: "Pump Specification", desc: "0.5 HP submersible, 2000 LPH", icon: "⚡" }
                        ].map((rec, i) => (
                            <div key={i} className="flex items-start gap-4 p-4 bg-white/5 rounded-xl hover:bg-white/10 transition-all">
                                <div className="text-3xl">{rec.icon}</div>
                                <div>
                                    <h4 className="font-bold text-white mb-1">{rec.title}</h4>
                                    <p className="text-sm text-gray-400">{rec.desc}</p>
                                </div>
                            </div>
                        ))}
                    </div>
                </div>

                {/* Find Contractors CTA */}
                <div className="glass rounded-2xl p-6 bg-gradient-to-r from-purple-500/10 to-pink-500/10 border-purple-500/20">
                    <div className="flex flex-col lg:flex-row items-center justify-between gap-4">
                        <div>
                            <h3 className="text-xl font-bold text-white mb-2">Ready to Install?</h3>
                            <p className="text-gray-400">Find verified RWH contractors in {formData?.city || 'your area'}</p>
                        </div>
                        <a
                            href="/marketplace"
                            className="flex items-center gap-2 px-6 py-3 bg-gradient-to-r from-purple-500 to-pink-500 text-white font-bold rounded-xl hover:scale-105 transition-transform"
                        >
                            <Phone size={20} />
                            Find Contractors
                        </a>
                    </div>
                </div>
            </div>
        </div>
    );
};

export default AssessPage;
