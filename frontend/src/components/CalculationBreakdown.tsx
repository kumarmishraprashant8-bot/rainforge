import React, { useState } from 'react';

interface CalculationBreakdownProps {
    roofAreaSqm: number;
    annualRainfallMm: number;
    runoffCoefficient: number;
    rainfallSource: string;
    tankSizeLiters: number;
    totalCostInr: number;
    subsidyAmountInr: number;
    annualYieldLiters: number;
    confidenceGrade: string;
}

const CalculationBreakdown: React.FC<CalculationBreakdownProps> = ({
    roofAreaSqm,
    annualRainfallMm,
    runoffCoefficient,
    rainfallSource,
    tankSizeLiters,
    totalCostInr,
    subsidyAmountInr,
    annualYieldLiters,
    confidenceGrade,
}) => {
    const [isOpen, setIsOpen] = useState(false);
    const [activeSection, setActiveSection] = useState<string | null>(null);

    const netCost = totalCostInr - subsidyAmountInr;
    const subsidyPct = (subsidyAmountInr / totalCostInr) * 100;
    const dailyYield = annualYieldLiters / 365;
    const storageDays = tankSizeLiters / dailyYield;

    const toggleSection = (section: string) => {
        setActiveSection(activeSection === section ? null : section);
    };

    const getConfidenceColor = (grade: string) => {
        const colors: Record<string, string> = {
            A: 'text-green-600 bg-green-100',
            B: 'text-blue-600 bg-blue-100',
            C: 'text-yellow-600 bg-yellow-100',
            D: 'text-orange-600 bg-orange-100',
            F: 'text-red-600 bg-red-100',
        };
        return colors[grade] || 'text-gray-600 bg-gray-100';
    };

    const getConfidenceLabel = (grade: string) => {
        const labels: Record<string, string> = {
            A: 'Excellent',
            B: 'Good',
            C: 'Moderate',
            D: 'Limited',
            F: 'Insufficient',
        };
        return labels[grade] || 'Unknown';
    };

    return (
        <div className="mt-6 border border-gray-200 rounded-lg overflow-hidden">
            {/* Main Toggle Header */}
            <button
                onClick={() => setIsOpen(!isOpen)}
                className="w-full px-4 py-3 bg-gradient-to-r from-blue-50 to-indigo-50 flex items-center justify-between hover:from-blue-100 hover:to-indigo-100 transition-colors"
            >
                <div className="flex items-center gap-2">
                    <svg
                        className={`w-5 h-5 text-blue-600 transition-transform ${isOpen ? 'rotate-90' : ''}`}
                        fill="none"
                        stroke="currentColor"
                        viewBox="0 0 24 24"
                    >
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5l7 7-7 7" />
                    </svg>
                    <span className="font-medium text-gray-800">
                        📊 How This Was Calculated
                    </span>
                </div>
                <span className={`px-2 py-1 rounded-full text-xs font-medium ${getConfidenceColor(confidenceGrade)}`}>
                    Grade {confidenceGrade} — {getConfidenceLabel(confidenceGrade)}
                </span>
            </button>

            {/* Collapsible Content */}
            {isOpen && (
                <div className="bg-white divide-y divide-gray-100">

                    {/* Section 1: Rainfall Data Source */}
                    <div className="border-b border-gray-100">
                        <button
                            onClick={() => toggleSection('rainfall')}
                            className="w-full px-4 py-3 flex items-center justify-between hover:bg-gray-50 transition-colors"
                        >
                            <span className="font-medium text-gray-700">1. Rainfall Data Source</span>
                            <svg
                                className={`w-4 h-4 text-gray-500 transition-transform ${activeSection === 'rainfall' ? 'rotate-180' : ''}`}
                                fill="none"
                                stroke="currentColor"
                                viewBox="0 0 24 24"
                            >
                                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 9l-7 7-7-7" />
                            </svg>
                        </button>
                        {activeSection === 'rainfall' && (
                            <div className="px-4 pb-4 text-sm text-gray-600 bg-gray-50">
                                <div className="space-y-2">
                                    <p><strong>Source:</strong> {rainfallSource === 'IMD' ? 'India Meteorological Department (IMD)' : 'Open-Meteo Climate API'}</p>
                                    <p><strong>Annual Rainfall:</strong> {annualRainfallMm.toLocaleString()} mm/year</p>
                                    <p><strong>Data Quality:</strong> {rainfallSource === 'IMD' ? 'Official government data (high reliability)' : 'Global reanalysis data (good reliability)'}</p>
                                    {rainfallSource !== 'IMD' && (
                                        <div className="mt-2 p-2 bg-yellow-50 border border-yellow-200 rounded text-yellow-800">
                                            ⚠️ IMD data unavailable for this location. Using Open-Meteo fallback.
                                        </div>
                                    )}
                                </div>
                            </div>
                        )}
                    </div>

                    {/* Section 2: Annual Yield Calculation */}
                    <div className="border-b border-gray-100">
                        <button
                            onClick={() => toggleSection('yield')}
                            className="w-full px-4 py-3 flex items-center justify-between hover:bg-gray-50 transition-colors"
                        >
                            <span className="font-medium text-gray-700">2. Annual Yield Formula</span>
                            <svg
                                className={`w-4 h-4 text-gray-500 transition-transform ${activeSection === 'yield' ? 'rotate-180' : ''}`}
                                fill="none"
                                stroke="currentColor"
                                viewBox="0 0 24 24"
                            >
                                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 9l-7 7-7-7" />
                            </svg>
                        </button>
                        {activeSection === 'yield' && (
                            <div className="px-4 pb-4 text-sm text-gray-600 bg-gray-50">
                                <div className="p-3 bg-white border border-gray-200 rounded-lg font-mono text-xs mb-3">
                                    <p className="text-gray-500 mb-1">Formula (IS 15797):</p>
                                    <p className="text-blue-700">Annual Yield = Roof Area × Annual Rainfall × Runoff Coefficient</p>
                                    <p className="mt-2 text-gray-700">
                                        = {roofAreaSqm} m² × {(annualRainfallMm / 1000).toFixed(3)} m × {runoffCoefficient}
                                    </p>
                                    <p className="text-green-700 font-bold mt-1">
                                        = {annualYieldLiters.toLocaleString()} litres/year
                                    </p>
                                </div>
                                <table className="w-full text-xs">
                                    <thead className="bg-gray-100">
                                        <tr>
                                            <th className="px-2 py-1 text-left">Material</th>
                                            <th className="px-2 py-1 text-left">Runoff Coefficient</th>
                                        </tr>
                                    </thead>
                                    <tbody>
                                        <tr className="border-b"><td className="px-2 py-1">Concrete (RCC)</td><td className="px-2 py-1">0.90</td></tr>
                                        <tr className="border-b"><td className="px-2 py-1">Metal/GI Sheet</td><td className="px-2 py-1">0.95</td></tr>
                                        <tr className="border-b"><td className="px-2 py-1">Clay Tiles</td><td className="px-2 py-1">0.75</td></tr>
                                        <tr><td className="px-2 py-1">Asbestos</td><td className="px-2 py-1">0.85</td></tr>
                                    </tbody>
                                </table>
                            </div>
                        )}
                    </div>

                    {/* Section 3: Tank Sizing */}
                    <div className="border-b border-gray-100">
                        <button
                            onClick={() => toggleSection('tank')}
                            className="w-full px-4 py-3 flex items-center justify-between hover:bg-gray-50 transition-colors"
                        >
                            <span className="font-medium text-gray-700">3. Tank Sizing Logic</span>
                            <svg
                                className={`w-4 h-4 text-gray-500 transition-transform ${activeSection === 'tank' ? 'rotate-180' : ''}`}
                                fill="none"
                                stroke="currentColor"
                                viewBox="0 0 24 24"
                            >
                                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 9l-7 7-7-7" />
                            </svg>
                        </button>
                        {activeSection === 'tank' && (
                            <div className="px-4 pb-4 text-sm text-gray-600 bg-gray-50">
                                <div className="space-y-2">
                                    <p><strong>Selected Tank Size:</strong> {tankSizeLiters.toLocaleString()} litres</p>
                                    <p><strong>Daily Average Yield:</strong> {dailyYield.toFixed(0)} litres/day</p>
                                    <p><strong>Storage Buffer:</strong> ~{storageDays.toFixed(0)} days of water</p>
                                    <div className="mt-3 p-2 bg-blue-50 border border-blue-200 rounded">
                                        <p className="text-blue-800 text-xs">
                                            <strong>Three Scenarios:</strong><br />
                                            • Cost Optimized: 60-day buffer<br />
                                            • Max Capture: Minimizes overflow<br />
                                            • Dry Season: 120-day monsoon gap
                                        </p>
                                    </div>
                                </div>
                            </div>
                        )}
                    </div>

                    {/* Section 4: Cost Breakdown */}
                    <div className="border-b border-gray-100">
                        <button
                            onClick={() => toggleSection('cost')}
                            className="w-full px-4 py-3 flex items-center justify-between hover:bg-gray-50 transition-colors"
                        >
                            <span className="font-medium text-gray-700">4. Cost Estimation</span>
                            <svg
                                className={`w-4 h-4 text-gray-500 transition-transform ${activeSection === 'cost' ? 'rotate-180' : ''}`}
                                fill="none"
                                stroke="currentColor"
                                viewBox="0 0 24 24"
                            >
                                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 9l-7 7-7-7" />
                            </svg>
                        </button>
                        {activeSection === 'cost' && (
                            <div className="px-4 pb-4 text-sm text-gray-600 bg-gray-50">
                                <table className="w-full text-xs mb-3">
                                    <thead className="bg-gray-100">
                                        <tr>
                                            <th className="px-2 py-1 text-left">Component</th>
                                            <th className="px-2 py-1 text-right">Est. Cost (₹)</th>
                                        </tr>
                                    </thead>
                                    <tbody>
                                        <tr className="border-b"><td className="px-2 py-1">Tank & Structure</td><td className="px-2 py-1 text-right">₹{(totalCostInr * 0.50).toLocaleString()}</td></tr>
                                        <tr className="border-b"><td className="px-2 py-1">Piping & Fittings</td><td className="px-2 py-1 text-right">₹{(totalCostInr * 0.15).toLocaleString()}</td></tr>
                                        <tr className="border-b"><td className="px-2 py-1">First-Flush Diverter</td><td className="px-2 py-1 text-right">₹{(totalCostInr * 0.08).toLocaleString()}</td></tr>
                                        <tr className="border-b"><td className="px-2 py-1">Filter System</td><td className="px-2 py-1 text-right">₹{(totalCostInr * 0.10).toLocaleString()}</td></tr>
                                        <tr className="border-b"><td className="px-2 py-1">Labour & Installation</td><td className="px-2 py-1 text-right">₹{(totalCostInr * 0.17).toLocaleString()}</td></tr>
                                        <tr className="bg-gray-100 font-bold"><td className="px-2 py-1">Total Cost</td><td className="px-2 py-1 text-right">₹{totalCostInr.toLocaleString()}</td></tr>
                                    </tbody>
                                </table>
                                <div className="p-2 bg-green-50 border border-green-200 rounded">
                                    <p className="text-green-800 text-xs">
                                        <strong>Subsidy Applied:</strong> ₹{subsidyAmountInr.toLocaleString()} ({subsidyPct.toFixed(0)}%)<br />
                                        <strong>Net Cost to You:</strong> ₹{netCost.toLocaleString()}
                                    </p>
                                </div>
                            </div>
                        )}
                    </div>

                    {/* Section 5: Confidence Grade */}
                    <div className="border-b border-gray-100">
                        <button
                            onClick={() => toggleSection('confidence')}
                            className="w-full px-4 py-3 flex items-center justify-between hover:bg-gray-50 transition-colors"
                        >
                            <span className="font-medium text-gray-700">5. Confidence Grade Explained</span>
                            <svg
                                className={`w-4 h-4 text-gray-500 transition-transform ${activeSection === 'confidence' ? 'rotate-180' : ''}`}
                                fill="none"
                                stroke="currentColor"
                                viewBox="0 0 24 24"
                            >
                                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 9l-7 7-7-7" />
                            </svg>
                        </button>
                        {activeSection === 'confidence' && (
                            <div className="px-4 pb-4 text-sm text-gray-600 bg-gray-50">
                                <div className={`p-3 rounded-lg mb-3 ${getConfidenceColor(confidenceGrade)}`}>
                                    <p className="font-bold text-lg">Grade {confidenceGrade} — {getConfidenceLabel(confidenceGrade)}</p>
                                </div>
                                <table className="w-full text-xs">
                                    <thead className="bg-gray-100">
                                        <tr>
                                            <th className="px-2 py-1 text-left">Grade</th>
                                            <th className="px-2 py-1 text-left">Meaning</th>
                                        </tr>
                                    </thead>
                                    <tbody>
                                        <tr className="border-b"><td className="px-2 py-1 font-bold text-green-600">A</td><td className="px-2 py-1">Highly reliable, official data</td></tr>
                                        <tr className="border-b"><td className="px-2 py-1 font-bold text-blue-600">B</td><td className="px-2 py-1">Reliable, minor verification recommended</td></tr>
                                        <tr className="border-b"><td className="px-2 py-1 font-bold text-yellow-600">C</td><td className="px-2 py-1">Preliminary, site visit recommended</td></tr>
                                        <tr className="border-b"><td className="px-2 py-1 font-bold text-orange-600">D</td><td className="px-2 py-1">Limited, professional consultation needed</td></tr>
                                        <tr><td className="px-2 py-1 font-bold text-red-600">F</td><td className="px-2 py-1">Insufficient for decision-making</td></tr>
                                    </tbody>
                                </table>
                            </div>
                        )}
                    </div>

                    {/* Section 6: Assumptions */}
                    <div>
                        <button
                            onClick={() => toggleSection('assumptions')}
                            className="w-full px-4 py-3 flex items-center justify-between hover:bg-gray-50 transition-colors"
                        >
                            <span className="font-medium text-gray-700">6. Assumptions & Safety Margins</span>
                            <svg
                                className={`w-4 h-4 text-gray-500 transition-transform ${activeSection === 'assumptions' ? 'rotate-180' : ''}`}
                                fill="none"
                                stroke="currentColor"
                                viewBox="0 0 24 24"
                            >
                                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 9l-7 7-7-7" />
                            </svg>
                        </button>
                        {activeSection === 'assumptions' && (
                            <div className="px-4 pb-4 text-sm text-gray-600 bg-gray-50">
                                <ul className="list-disc list-inside space-y-1">
                                    <li>Rainfall distribution: Monsoon-weighted (70-80% in June-Sept)</li>
                                    <li>First-flush loss: 1-2 mm per event discarded</li>
                                    <li>System efficiency: 85% (evaporation, splashing)</li>
                                    <li>Tank availability: 90% (maintenance downtime)</li>
                                    <li>Safety factor: 1.1x on structural calculations</li>
                                </ul>
                                <div className="mt-3 p-2 bg-indigo-50 border border-indigo-200 rounded">
                                    <p className="text-indigo-800 text-xs">
                                        <strong>No AI/ML used:</strong> All calculations follow IS 15797 deterministic formulas.
                                        Monte-Carlo simulations (P50/P90) use 1000+ runs with known uncertainty ranges.
                                    </p>
                                </div>
                            </div>
                        )}
                    </div>

                    {/* Disclaimer Footer */}
                    <div className="px-4 py-3 bg-gray-50 text-xs text-gray-500 border-t">
                        <p>
                            This assessment follows IS 15797:2018 guidelines for rooftop rainwater harvesting design.
                            Actual installation may vary based on site inspection by certified engineer.
                        </p>
                    </div>
                </div>
            )}
        </div>
    );
};

export default CalculationBreakdown;
