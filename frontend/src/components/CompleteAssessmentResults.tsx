/**
 * Complete Assessment Results Display
 * Shows all outputs from RWH assessment
 */

import React, { useState } from 'react';
import CalculationBreakdown from './CalculationBreakdown';

interface AssessmentResult {
    // Basic
    annual_rainfall_mm: number;
    annual_collection_liters: number;
    recommended_tank_liters: number;
    roi_years: number;
    carbon_offset_kg: number;

    // Financial
    total_system_cost: number;
    material_cost: number;
    labor_cost: number;
    annual_savings: number;
    payback_months: number;
    lifetime_savings_20yr: number;

    // Subsidy
    subsidy_available: boolean;
    subsidy_percent: number;
    subsidy_amount: number;
    net_cost_after_subsidy: number;

    // Coverage
    daily_demand_liters: number;
    days_of_coverage: number;
    monsoon_collection_liters: number;
    dry_season_deficit_liters: number;

    // Monthly
    monthly_breakdown: Array<{
        month: string;
        rainfall_mm: number;
        collection_liters: number;
        demand_liters: number;
        surplus_deficit: number;
    }>;

    // Materials
    materials: Array<{
        name: string;
        quantity: number;
        unit: string;
        unit_cost: number;
        total_cost: number;
        category: string;
    }>;

    // Maintenance
    maintenance_schedule: Array<{
        task: string;
        frequency: string;
        estimated_cost: number;
        next_due: string;
    }>;
    annual_maintenance_cost: number;

    // System
    pipe_diameter_mm: number;
    filter_type: string;
    first_flush_liters: number;
    tank_dimensions: { diameter_m: number; height_m: number; footprint_sqm: number };
    recharge_pit_required: boolean;
    recharge_pit_dimensions?: { diameter_m: number; depth_m: number; area_sqm: number };

    // Quality
    water_quality_grade: string;
    suitable_uses: string[];
    treatment_required: boolean;
    treatment_recommendations: string[];

    // Compliance
    permit_required: boolean;
    permit_authority: string;
    estimated_permit_time_days: number;
    mandatory_by_law: boolean;

    // Environmental
    groundwater_recharge_potential: number;
    flood_mitigation_liters: number;

    // Scores
    rpi_score: number;
    feasibility_score: number;
    priority_score: number;
}

interface Props {
    result: AssessmentResult;
    onDownloadPDF?: () => void;
    onShare?: () => void;
}

export function CompleteAssessmentResults({ result, onDownloadPDF, onShare }: Props) {
    const [activeTab, setActiveTab] = useState('overview');

    const formatCurrency = (n: number) => `₹${n.toLocaleString('en-IN')}`;
    const formatLiters = (n: number) => n > 1000 ? `${(n / 1000).toFixed(1)}kL` : `${n}L`;

    return (
        <div className="assessment-results">
            {/* Header with scores */}
            <div className="results-header">
                <div className="main-stats">
                    <div className="stat highlight">
                        <span className="value">{formatLiters(result.annual_collection_liters)}</span>
                        <span className="label">Annual Collection</span>
                    </div>
                    <div className="stat">
                        <span className="value">{formatCurrency(result.net_cost_after_subsidy)}</span>
                        <span className="label">Net Cost</span>
                    </div>
                    <div className="stat">
                        <span className="value">{result.roi_years}y</span>
                        <span className="label">Payback</span>
                    </div>
                    <div className="stat">
                        <span className="value">{result.days_of_coverage}</span>
                        <span className="label">Days Coverage</span>
                    </div>
                </div>

                <div className="scores">
                    <div className="score">
                        <span className="score-value">{result.rpi_score}</span>
                        <span className="score-label">RPI Score</span>
                    </div>
                    <div className="score">
                        <span className="score-value">{result.feasibility_score}</span>
                        <span className="score-label">Feasibility</span>
                    </div>
                </div>
            </div>

            {/* Tab navigation */}
            <div className="results-tabs">
                {['overview', 'monthly', 'materials', 'maintenance', 'compliance'].map(tab => (
                    <button
                        key={tab}
                        className={`tab ${activeTab === tab ? 'active' : ''}`}
                        onClick={() => setActiveTab(tab)}
                    >
                        {tab.charAt(0).toUpperCase() + tab.slice(1)}
                    </button>
                ))}
            </div>

            {/* Tab content */}
            <div className="results-content">
                {activeTab === 'overview' && (
                    <div className="tab-panel">
                        {/* Financial Summary */}
                        <section className="result-section">
                            <h3>💰 Financial Summary</h3>
                            <div className="data-grid">
                                <div className="data-item">
                                    <span className="label">Material Cost</span>
                                    <span className="value">{formatCurrency(result.material_cost)}</span>
                                </div>
                                <div className="data-item">
                                    <span className="label">Labor Cost</span>
                                    <span className="value">{formatCurrency(result.labor_cost)}</span>
                                </div>
                                <div className="data-item">
                                    <span className="label">Total Cost</span>
                                    <span className="value">{formatCurrency(result.total_system_cost)}</span>
                                </div>
                                {result.subsidy_available && (
                                    <div className="data-item highlight-green">
                                        <span className="label">Subsidy ({result.subsidy_percent}%)</span>
                                        <span className="value">-{formatCurrency(result.subsidy_amount)}</span>
                                    </div>
                                )}
                                <div className="data-item total">
                                    <span className="label">Net Cost</span>
                                    <span className="value">{formatCurrency(result.net_cost_after_subsidy)}</span>
                                </div>
                            </div>

                            <div className="savings-box">
                                <div className="savings-item">
                                    <span className="label">Annual Savings</span>
                                    <span className="value">{formatCurrency(result.annual_savings)}</span>
                                </div>
                                <div className="savings-item">
                                    <span className="label">20-Year Lifetime Savings</span>
                                    <span className="value large">{formatCurrency(result.lifetime_savings_20yr)}</span>
                                </div>
                            </div>
                        </section>

                        {/* System Design */}
                        <section className="result-section">
                            <h3>🔧 System Design</h3>
                            <div className="data-grid">
                                <div className="data-item">
                                    <span className="label">Recommended Tank</span>
                                    <span className="value">{formatLiters(result.recommended_tank_liters)}</span>
                                </div>
                                <div className="data-item">
                                    <span className="label">Tank Size</span>
                                    <span className="value">
                                        {result.tank_dimensions.diameter_m}m × {result.tank_dimensions.height_m}m
                                    </span>
                                </div>
                                <div className="data-item">
                                    <span className="label">Pipe Diameter</span>
                                    <span className="value">{result.pipe_diameter_mm}mm</span>
                                </div>
                                <div className="data-item">
                                    <span className="label">Filter Type</span>
                                    <span className="value">{result.filter_type}</span>
                                </div>
                                <div className="data-item">
                                    <span className="label">First Flush</span>
                                    <span className="value">{result.first_flush_liters}L</span>
                                </div>
                                {result.recharge_pit_required && result.recharge_pit_dimensions && (
                                    <div className="data-item">
                                        <span className="label">Recharge Pit</span>
                                        <span className="value">
                                            {result.recharge_pit_dimensions.diameter_m}m dia × {result.recharge_pit_dimensions.depth_m}m
                                        </span>
                                    </div>
                                )}
                            </div>
                        </section>

                        {/* Water Quality */}
                        <section className="result-section">
                            <h3>💧 Water Quality</h3>
                            <div className="quality-badge grade-{result.water_quality_grade.toLowerCase()}">
                                Grade {result.water_quality_grade}
                            </div>
                            <div className="uses-list">
                                <p><strong>Suitable for:</strong></p>
                                <ul>
                                    {result.suitable_uses.map((use, i) => (
                                        <li key={i}>✓ {use}</li>
                                    ))}
                                </ul>
                            </div>
                            {result.treatment_required && (
                                <div className="treatment-box">
                                    <p><strong>Treatment Needed:</strong></p>
                                    <ul>
                                        {result.treatment_recommendations.map((r, i) => (
                                            <li key={i}>{r}</li>
                                        ))}
                                    </ul>
                                </div>
                            )}
                        </section>

                        {/* Environmental Impact */}
                        <section className="result-section">
                            <h3>🌱 Environmental Impact</h3>
                            <div className="impact-cards">
                                <div className="impact-card">
                                    <span className="icon">🌍</span>
                                    <span className="value">{result.carbon_offset_kg} kg</span>
                                    <span className="label">CO₂ Offset/Year</span>
                                </div>
                                <div className="impact-card">
                                    <span className="icon">💧</span>
                                    <span className="value">{formatLiters(result.groundwater_recharge_potential)}</span>
                                    <span className="label">Groundwater Recharge</span>
                                </div>
                                <div className="impact-card">
                                    <span className="icon">🌊</span>
                                    <span className="value">{formatLiters(result.flood_mitigation_liters)}</span>
                                    <span className="label">Flood Mitigation</span>
                                </div>
                            </div>
                        </section>
                    </div>
                )}

                {activeTab === 'monthly' && (
                    <div className="tab-panel">
                        <h3>📊 Monthly Breakdown</h3>
                        <table className="data-table">
                            <thead>
                                <tr>
                                    <th>Month</th>
                                    <th>Rainfall</th>
                                    <th>Collection</th>
                                    <th>Demand</th>
                                    <th>Surplus/Deficit</th>
                                </tr>
                            </thead>
                            <tbody>
                                {result.monthly_breakdown.map((m, i) => (
                                    <tr key={i} className={m.surplus_deficit >= 0 ? 'surplus' : 'deficit'}>
                                        <td>{m.month}</td>
                                        <td>{m.rainfall_mm}mm</td>
                                        <td>{formatLiters(m.collection_liters)}</td>
                                        <td>{formatLiters(m.demand_liters)}</td>
                                        <td className="surplus-value">
                                            {m.surplus_deficit >= 0 ? '+' : ''}{formatLiters(m.surplus_deficit)}
                                        </td>
                                    </tr>
                                ))}
                            </tbody>
                        </table>
                        <div className="chart-placeholder">
                            [Monthly Collection Chart Would Render Here]
                        </div>
                    </div>
                )}

                {activeTab === 'materials' && (
                    <div className="tab-panel">
                        <h3>🛒 Bill of Materials</h3>
                        <table className="data-table">
                            <thead>
                                <tr>
                                    <th>Item</th>
                                    <th>Qty</th>
                                    <th>Unit Cost</th>
                                    <th>Total</th>
                                </tr>
                            </thead>
                            <tbody>
                                {result.materials.map((m, i) => (
                                    <tr key={i}>
                                        <td>
                                            <span className="item-name">{m.name}</span>
                                            <span className="item-category">{m.category}</span>
                                        </td>
                                        <td>{m.quantity} {m.unit}</td>
                                        <td>{formatCurrency(m.unit_cost)}</td>
                                        <td>{formatCurrency(m.total_cost)}</td>
                                    </tr>
                                ))}
                            </tbody>
                            <tfoot>
                                <tr>
                                    <td colSpan={3}><strong>Material Total</strong></td>
                                    <td><strong>{formatCurrency(result.material_cost)}</strong></td>
                                </tr>
                                <tr>
                                    <td colSpan={3}>Labor (30%)</td>
                                    <td>{formatCurrency(result.labor_cost)}</td>
                                </tr>
                                <tr className="grand-total">
                                    <td colSpan={3}><strong>Grand Total</strong></td>
                                    <td><strong>{formatCurrency(result.total_system_cost)}</strong></td>
                                </tr>
                            </tfoot>
                        </table>
                    </div>
                )}

                {activeTab === 'maintenance' && (
                    <div className="tab-panel">
                        <h3>🔧 Maintenance Schedule</h3>
                        <div className="maintenance-list">
                            {result.maintenance_schedule.map((m, i) => (
                                <div key={i} className="maintenance-item">
                                    <div className="task-info">
                                        <span className="task-name">{m.task}</span>
                                        <span className="task-freq">{m.frequency}</span>
                                    </div>
                                    <div className="task-meta">
                                        <span className="cost">{m.estimated_cost > 0 ? formatCurrency(m.estimated_cost) : 'Free'}</span>
                                        <span className="due">Next: {m.next_due}</span>
                                    </div>
                                </div>
                            ))}
                        </div>
                        <div className="annual-cost">
                            <span>Estimated Annual Maintenance</span>
                            <strong>{formatCurrency(result.annual_maintenance_cost)}</strong>
                        </div>
                    </div>
                )}

                {activeTab === 'compliance' && (
                    <div className="tab-panel">
                        <h3>📋 Legal & Compliance</h3>

                        <div className={`compliance-status ${result.mandatory_by_law ? 'mandatory' : 'optional'}`}>
                            {result.mandatory_by_law ? (
                                <>
                                    <span className="icon">⚠️</span>
                                    <span>RWH is MANDATORY by law in your area</span>
                                </>
                            ) : (
                                <>
                                    <span className="icon">ℹ️</span>
                                    <span>RWH is optional but recommended in your area</span>
                                </>
                            )}
                        </div>

                        <div className="data-grid">
                            <div className="data-item">
                                <span className="label">Permit Required</span>
                                <span className="value">{result.permit_required ? 'Yes' : 'No'}</span>
                            </div>
                            {result.permit_required && (
                                <>
                                    <div className="data-item">
                                        <span className="label">Authority</span>
                                        <span className="value">{result.permit_authority}</span>
                                    </div>
                                    <div className="data-item">
                                        <span className="label">Estimated Time</span>
                                        <span className="value">{result.estimated_permit_time_days} days</span>
                                    </div>
                                </>
                            )}
                        </div>

                        {result.subsidy_available && (
                            <div className="subsidy-info">
                                <h4>💰 Subsidy Available</h4>
                                <p>
                                    Your state offers up to <strong>{result.subsidy_percent}%</strong> subsidy
                                    (max {formatCurrency(result.subsidy_amount)}) for RWH installations.
                                </p>
                            </div>
                        )}
                    </div>
                )}
            </div>

            {/* Actions */}
            <div className="results-actions">
                {onDownloadPDF && (
                    <button className="btn-action" onClick={onDownloadPDF}>
                        📄 Download PDF Report
                    </button>
                )}
                {onShare && (
                    <button className="btn-action secondary" onClick={onShare}>
                        📤 Share
                    </button>
                )}
            </div>

            {/* Calculation Breakdown - Collapsible Verification Panel */}
            <CalculationBreakdown
                roofAreaSqm={result.recommended_tank_liters / 1000 * 1.2} // Estimate from tank size
                annualRainfallMm={result.annual_rainfall_mm}
                runoffCoefficient={0.85}
                rainfallSource="IMD"
                tankSizeLiters={result.recommended_tank_liters}
                totalCostInr={result.total_system_cost}
                subsidyAmountInr={result.subsidy_amount}
                annualYieldLiters={result.annual_collection_liters}
                confidenceGrade={result.water_quality_grade === 'A' ? 'A' : result.water_quality_grade === 'B' ? 'B' : 'C'}
            />

            <style>{resultsStyles}</style>
        </div>
    );
}

const resultsStyles = `
  .assessment-results {
    max-width: 900px;
    margin: 0 auto;
  }

  .results-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: 24px;
    background: linear-gradient(135deg, rgba(14, 165, 233, 0.1), rgba(124, 58, 237, 0.1));
    border-radius: 16px;
    margin-bottom: 24px;
  }

  .main-stats {
    display: flex;
    gap: 32px;
  }

  .main-stats .stat {
    display: flex;
    flex-direction: column;
  }

  .main-stats .stat.highlight .value {
    color: #0ea5e9;
    font-size: 28px;
  }

  .main-stats .value {
    font-size: 24px;
    font-weight: 700;
  }

  .main-stats .label {
    font-size: 12px;
    color: var(--text-muted);
  }

  .scores {
    display: flex;
    gap: 16px;
  }

  .score {
    display: flex;
    flex-direction: column;
    align-items: center;
    padding: 16px;
    background: var(--bg-secondary);
    border-radius: 12px;
  }

  .score-value {
    font-size: 32px;
    font-weight: 700;
    color: #10b981;
  }

  .score-label {
    font-size: 11px;
    color: var(--text-muted);
  }

  .results-tabs {
    display: flex;
    gap: 8px;
    margin-bottom: 24px;
    border-bottom: 1px solid var(--border-primary);
    padding-bottom: 8px;
  }

  .results-tabs .tab {
    padding: 10px 20px;
    background: none;
    border: none;
    color: var(--text-muted);
    cursor: pointer;
    border-radius: 6px;
    transition: all 0.2s;
  }

  .results-tabs .tab.active {
    background: var(--bg-secondary);
    color: var(--text-primary);
  }

  .result-section {
    margin-bottom: 32px;
  }

  .result-section h3 {
    margin: 0 0 16px 0;
    font-size: 18px;
  }

  .data-grid {
    display: grid;
    grid-template-columns: repeat(auto-fill, minmax(200px, 1fr));
    gap: 12px;
  }

  .data-item {
    display: flex;
    justify-content: space-between;
    padding: 12px;
    background: var(--bg-secondary);
    border-radius: 8px;
  }

  .data-item.highlight-green .value {
    color: #10b981;
  }

  .data-item.total {
    background: linear-gradient(135deg, #0ea5e9, #7c3aed);
    color: white;
  }

  .savings-box {
    margin-top: 16px;
    padding: 20px;
    background: linear-gradient(135deg, rgba(16, 185, 129, 0.1), rgba(16, 185, 129, 0.05));
    border: 1px solid rgba(16, 185, 129, 0.3);
    border-radius: 12px;
    display: flex;
    justify-content: space-between;
    align-items: center;
  }

  .savings-item .value.large {
    font-size: 28px;
    color: #10b981;
    font-weight: 700;
  }

  .impact-cards {
    display: grid;
    grid-template-columns: repeat(3, 1fr);
    gap: 16px;
  }

  .impact-card {
    display: flex;
    flex-direction: column;
    align-items: center;
    padding: 20px;
    background: var(--bg-secondary);
    border-radius: 12px;
    text-align: center;
  }

  .impact-card .icon {
    font-size: 32px;
    margin-bottom: 8px;
  }

  .impact-card .value {
    font-size: 20px;
    font-weight: 600;
  }

  .data-table {
    width: 100%;
    border-collapse: collapse;
  }

  .data-table th,
  .data-table td {
    padding: 12px;
    text-align: left;
    border-bottom: 1px solid var(--border-primary);
  }

  .data-table th {
    font-weight: 600;
    color: var(--text-muted);
    font-size: 12px;
    text-transform: uppercase;
  }

  .data-table .surplus .surplus-value { color: #10b981; }
  .data-table .deficit .surplus-value { color: #ef4444; }

  .data-table tfoot tr {
    background: var(--bg-secondary);
  }

  .data-table .grand-total {
    background: linear-gradient(135deg, #0ea5e9, #7c3aed);
    color: white;
  }

  .maintenance-list {
    display: flex;
    flex-direction: column;
    gap: 12px;
  }

  .maintenance-item {
    display: flex;
    justify-content: space-between;
    padding: 16px;
    background: var(--bg-secondary);
    border-radius: 8px;
  }

  .task-name {
    font-weight: 600;
    display: block;
  }

  .task-freq {
    font-size: 12px;
    color: var(--text-muted);
  }

  .compliance-status {
    display: flex;
    align-items: center;
    gap: 12px;
    padding: 16px;
    border-radius: 8px;
    margin-bottom: 20px;
  }

  .compliance-status.mandatory {
    background: rgba(239, 68, 68, 0.1);
    border: 1px solid rgba(239, 68, 68, 0.3);
    color: #ef4444;
  }

  .compliance-status.optional {
    background: rgba(14, 165, 233, 0.1);
    border: 1px solid rgba(14, 165, 233, 0.3);
  }

  .subsidy-info {
    margin-top: 20px;
    padding: 20px;
    background: rgba(16, 185, 129, 0.1);
    border-radius: 12px;
  }

  .results-actions {
    display: flex;
    gap: 12px;
    margin-top: 32px;
  }

  .btn-action {
    flex: 1;
    padding: 16px;
    background: linear-gradient(135deg, #0ea5e9, #7c3aed);
    border: none;
    border-radius: 8px;
    color: white;
    font-weight: 600;
    cursor: pointer;
  }

  .btn-action.secondary {
    background: var(--bg-secondary);
    color: var(--text-primary);
  }

  @media (max-width: 768px) {
    .results-header { flex-direction: column; gap: 20px; }
    .main-stats { flex-wrap: wrap; }
    .impact-cards { grid-template-columns: 1fr; }
  }
`;

export default CompleteAssessmentResults;
