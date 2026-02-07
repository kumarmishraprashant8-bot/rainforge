/**
 * Complete Assessment Form
 * All possible inputs for RWH assessment
 */

import React, { useState } from 'react';

interface CompleteAssessmentFormProps {
    onSubmit: (data: AssessmentFormData) => void;
    loading?: boolean;
}

export interface AssessmentFormData {
    // Required
    roof_area_sqm: number;
    city: string;
    state: string;

    // Location
    latitude?: number;
    longitude?: number;

    // Roof details
    roof_type: 'rcc' | 'metal' | 'tile' | 'asbestos' | 'thatched';
    roof_slope_degrees: number;
    num_floors: number;

    // Building
    num_people: number;
    existing_plumbing: boolean;
    building_age_years: number;

    // Water
    current_water_source: 'municipality' | 'borewell' | 'tanker' | 'well' | 'none';
    monthly_water_bill: number;
    daily_water_usage_liters?: number;

    // Ground
    soil_type: 'sandy' | 'loamy' | 'clayey' | 'rocky';
    ground_water_depth_m: number;
    available_ground_area_sqm: number;

    // Preferences
    storage_preference: 'tank' | 'recharge' | 'hybrid';
    budget_inr?: number;
}

const STATES = [
    "Andhra Pradesh", "Arunachal Pradesh", "Assam", "Bihar", "Chhattisgarh",
    "Delhi", "Goa", "Gujarat", "Haryana", "Himachal Pradesh", "Jharkhand",
    "Karnataka", "Kerala", "Madhya Pradesh", "Maharashtra", "Manipur",
    "Meghalaya", "Mizoram", "Nagaland", "Odisha", "Punjab", "Rajasthan",
    "Sikkim", "Tamil Nadu", "Telangana", "Tripura", "Uttar Pradesh",
    "Uttarakhand", "West Bengal"
];

const CITIES: Record<string, string[]> = {
    "Maharashtra": ["Mumbai", "Pune", "Nagpur", "Nashik", "Aurangabad"],
    "Karnataka": ["Bangalore", "Mysore", "Mangalore", "Hubli"],
    "Tamil Nadu": ["Chennai", "Coimbatore", "Madurai", "Salem"],
    "Delhi": ["New Delhi", "Central Delhi", "South Delhi", "North Delhi"],
    "Gujarat": ["Ahmedabad", "Surat", "Vadodara", "Rajkot"],
    "Rajasthan": ["Jaipur", "Jodhpur", "Udaipur", "Kota"],
    "Kerala": ["Kochi", "Thiruvananthapuram", "Kozhikode"],
    "West Bengal": ["Kolkata", "Howrah", "Darjeeling"],
    "Telangana": ["Hyderabad", "Warangal", "Nizamabad"],
    "Uttar Pradesh": ["Lucknow", "Noida", "Kanpur", "Agra", "Varanasi"],
};

export function CompleteAssessmentForm({ onSubmit, loading }: CompleteAssessmentFormProps) {
    const [step, setStep] = useState(1);
    const [formData, setFormData] = useState<Partial<AssessmentFormData>>({
        roof_type: 'rcc',
        roof_slope_degrees: 0,
        num_floors: 1,
        num_people: 4,
        existing_plumbing: false,
        building_age_years: 5,
        current_water_source: 'municipality',
        monthly_water_bill: 500,
        soil_type: 'loamy',
        ground_water_depth_m: 10,
        available_ground_area_sqm: 10,
        storage_preference: 'tank'
    });

    const updateField = (field: keyof AssessmentFormData, value: any) => {
        setFormData(prev => ({ ...prev, [field]: value }));
    };

    const handleSubmit = (e: React.FormEvent) => {
        e.preventDefault();
        if (formData.roof_area_sqm && formData.city && formData.state) {
            onSubmit(formData as AssessmentFormData);
        }
    };

    const cities = formData.state ? CITIES[formData.state] || [] : [];

    return (
        <form onSubmit={handleSubmit} className="complete-form">
            {/* Progress indicator */}
            <div className="form-progress">
                <div className={`step ${step >= 1 ? 'active' : ''}`}>1. Location</div>
                <div className={`step ${step >= 2 ? 'active' : ''}`}>2. Building</div>
                <div className={`step ${step >= 3 ? 'active' : ''}`}>3. Water</div>
                <div className={`step ${step >= 4 ? 'active' : ''}`}>4. Preferences</div>
            </div>

            {/* Step 1: Location & Roof */}
            {step === 1 && (
                <div className="form-step">
                    <h3>📍 Location & Roof Details</h3>

                    <div className="form-row">
                        <div className="form-group">
                            <label>State *</label>
                            <select
                                value={formData.state || ''}
                                onChange={e => updateField('state', e.target.value)}
                                required
                            >
                                <option value="">Select State</option>
                                {STATES.map(s => <option key={s} value={s}>{s}</option>)}
                            </select>
                        </div>
                        <div className="form-group">
                            <label>City *</label>
                            <select
                                value={formData.city || ''}
                                onChange={e => updateField('city', e.target.value)}
                                required
                                disabled={!formData.state}
                            >
                                <option value="">Select City</option>
                                {cities.map(c => <option key={c} value={c}>{c}</option>)}
                            </select>
                        </div>
                    </div>

                    <div className="form-row">
                        <div className="form-group">
                            <label>Roof Area (sqm) *</label>
                            <input
                                type="number"
                                value={formData.roof_area_sqm || ''}
                                onChange={e => updateField('roof_area_sqm', parseFloat(e.target.value))}
                                placeholder="e.g., 150"
                                min={10}
                                required
                            />
                            <span className="hint">Total catchment area of your roof</span>
                        </div>
                        <div className="form-group">
                            <label>Roof Type *</label>
                            <select
                                value={formData.roof_type}
                                onChange={e => updateField('roof_type', e.target.value)}
                            >
                                <option value="rcc">RCC / Concrete (Flat)</option>
                                <option value="metal">Metal / GI Sheet</option>
                                <option value="tile">Clay / Mangalore Tile</option>
                                <option value="asbestos">Asbestos</option>
                                <option value="thatched">Thatched / Natural</option>
                            </select>
                        </div>
                    </div>

                    <div className="form-row">
                        <div className="form-group">
                            <label>Roof Slope (degrees)</label>
                            <input
                                type="range"
                                min={0}
                                max={45}
                                value={formData.roof_slope_degrees}
                                onChange={e => updateField('roof_slope_degrees', parseInt(e.target.value))}
                            />
                            <span className="range-value">{formData.roof_slope_degrees}°</span>
                        </div>
                        <div className="form-group">
                            <label>Number of Floors</label>
                            <input
                                type="number"
                                value={formData.num_floors}
                                onChange={e => updateField('num_floors', parseInt(e.target.value))}
                                min={1}
                                max={20}
                            />
                        </div>
                    </div>

                    <button type="button" className="btn-next" onClick={() => setStep(2)}>
                        Next: Building Details →
                    </button>
                </div>
            )}

            {/* Step 2: Building Details */}
            {step === 2 && (
                <div className="form-step">
                    <h3>🏠 Building Details</h3>

                    <div className="form-row">
                        <div className="form-group">
                            <label>Number of People</label>
                            <input
                                type="number"
                                value={formData.num_people}
                                onChange={e => updateField('num_people', parseInt(e.target.value))}
                                min={1}
                            />
                            <span className="hint">People living in the building</span>
                        </div>
                        <div className="form-group">
                            <label>Building Age (years)</label>
                            <input
                                type="number"
                                value={formData.building_age_years}
                                onChange={e => updateField('building_age_years', parseInt(e.target.value))}
                                min={0}
                            />
                        </div>
                    </div>

                    <div className="form-row">
                        <div className="form-group checkbox-group">
                            <label>
                                <input
                                    type="checkbox"
                                    checked={formData.existing_plumbing}
                                    onChange={e => updateField('existing_plumbing', e.target.checked)}
                                />
                                Existing rainwater plumbing
                            </label>
                            <span className="hint">Does your building already have rainwater pipes?</span>
                        </div>
                    </div>

                    <div className="form-row">
                        <div className="form-group">
                            <label>Soil Type at Site</label>
                            <select
                                value={formData.soil_type}
                                onChange={e => updateField('soil_type', e.target.value)}
                            >
                                <option value="sandy">Sandy (Fast drainage)</option>
                                <option value="loamy">Loamy (Medium)</option>
                                <option value="clayey">Clayey (Slow drainage)</option>
                                <option value="rocky">Rocky</option>
                            </select>
                        </div>
                        <div className="form-group">
                            <label>Ground Water Depth (meters)</label>
                            <input
                                type="number"
                                value={formData.ground_water_depth_m}
                                onChange={e => updateField('ground_water_depth_m', parseFloat(e.target.value))}
                                min={1}
                            />
                        </div>
                    </div>

                    <div className="form-group">
                        <label>Available Ground Area for Recharge Pit (sqm)</label>
                        <input
                            type="number"
                            value={formData.available_ground_area_sqm}
                            onChange={e => updateField('available_ground_area_sqm', parseFloat(e.target.value))}
                            min={0}
                        />
                    </div>

                    <div className="form-buttons">
                        <button type="button" className="btn-back" onClick={() => setStep(1)}>← Back</button>
                        <button type="button" className="btn-next" onClick={() => setStep(3)}>Next: Water Details →</button>
                    </div>
                </div>
            )}

            {/* Step 3: Water Details */}
            {step === 3 && (
                <div className="form-step">
                    <h3>💧 Current Water Usage</h3>

                    <div className="form-row">
                        <div className="form-group">
                            <label>Current Water Source</label>
                            <select
                                value={formData.current_water_source}
                                onChange={e => updateField('current_water_source', e.target.value)}
                            >
                                <option value="municipality">Municipal Supply</option>
                                <option value="borewell">Borewell</option>
                                <option value="tanker">Water Tanker</option>
                                <option value="well">Open Well</option>
                                <option value="none">No Regular Source</option>
                            </select>
                        </div>
                        <div className="form-group">
                            <label>Monthly Water Bill (₹)</label>
                            <input
                                type="number"
                                value={formData.monthly_water_bill}
                                onChange={e => updateField('monthly_water_bill', parseFloat(e.target.value))}
                                min={0}
                            />
                        </div>
                    </div>

                    <div className="form-group">
                        <label>Daily Water Usage (liters) - Optional</label>
                        <input
                            type="number"
                            value={formData.daily_water_usage_liters || ''}
                            onChange={e => updateField('daily_water_usage_liters', e.target.value ? parseFloat(e.target.value) : undefined)}
                            placeholder="Leave blank for auto-calculation"
                        />
                        <span className="hint">If unknown, we'll estimate based on family size (135 lpcd)</span>
                    </div>

                    <div className="form-buttons">
                        <button type="button" className="btn-back" onClick={() => setStep(2)}>← Back</button>
                        <button type="button" className="btn-next" onClick={() => setStep(4)}>Next: Preferences →</button>
                    </div>
                </div>
            )}

            {/* Step 4: Preferences */}
            {step === 4 && (
                <div className="form-step">
                    <h3>⚙️ Your Preferences</h3>

                    <div className="form-group">
                        <label>Storage Preference</label>
                        <div className="radio-cards">
                            <label className={`radio-card ${formData.storage_preference === 'tank' ? 'selected' : ''}`}>
                                <input
                                    type="radio"
                                    name="storage"
                                    value="tank"
                                    checked={formData.storage_preference === 'tank'}
                                    onChange={() => updateField('storage_preference', 'tank')}
                                />
                                <span className="icon">🪣</span>
                                <span className="title">Tank Storage</span>
                                <span className="desc">Store water in tank for later use</span>
                            </label>
                            <label className={`radio-card ${formData.storage_preference === 'recharge' ? 'selected' : ''}`}>
                                <input
                                    type="radio"
                                    name="storage"
                                    value="recharge"
                                    checked={formData.storage_preference === 'recharge'}
                                    onChange={() => updateField('storage_preference', 'recharge')}
                                />
                                <span className="icon">⬇️</span>
                                <span className="title">Ground Recharge</span>
                                <span className="desc">Recharge groundwater via pit</span>
                            </label>
                            <label className={`radio-card ${formData.storage_preference === 'hybrid' ? 'selected' : ''}`}>
                                <input
                                    type="radio"
                                    name="storage"
                                    value="hybrid"
                                    checked={formData.storage_preference === 'hybrid'}
                                    onChange={() => updateField('storage_preference', 'hybrid')}
                                />
                                <span className="icon">🔄</span>
                                <span className="title">Hybrid</span>
                                <span className="desc">Tank + overflow to recharge</span>
                            </label>
                        </div>
                    </div>

                    <div className="form-group">
                        <label>Budget (₹) - Optional</label>
                        <input
                            type="number"
                            value={formData.budget_inr || ''}
                            onChange={e => updateField('budget_inr', e.target.value ? parseFloat(e.target.value) : undefined)}
                            placeholder="Leave blank for optimal recommendation"
                        />
                    </div>

                    <div className="form-buttons">
                        <button type="button" className="btn-back" onClick={() => setStep(3)}>← Back</button>
                        <button type="submit" className="btn-submit" disabled={loading}>
                            {loading ? 'Calculating...' : '🚀 Get Complete Assessment'}
                        </button>
                    </div>
                </div>
            )}

            <style>{formStyles}</style>
        </form>
    );
}

const formStyles = `
  .complete-form {
    max-width: 700px;
    margin: 0 auto;
  }

  .form-progress {
    display: flex;
    gap: 4px;
    margin-bottom: 32px;
  }

  .form-progress .step {
    flex: 1;
    padding: 12px;
    background: var(--bg-tertiary);
    color: var(--text-muted);
    text-align: center;
    font-size: 13px;
    border-radius: 6px;
    transition: all 0.3s;
  }

  .form-progress .step.active {
    background: linear-gradient(135deg, #0ea5e9, #7c3aed);
    color: white;
  }

  .form-step h3 {
    margin: 0 0 24px 0;
    font-size: 20px;
  }

  .form-row {
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: 16px;
    margin-bottom: 16px;
  }

  @media (max-width: 600px) {
    .form-row { grid-template-columns: 1fr; }
  }

  .form-group {
    display: flex;
    flex-direction: column;
    gap: 6px;
    margin-bottom: 16px;
  }

  .form-group label {
    font-size: 14px;
    font-weight: 500;
    color: var(--text-primary);
  }

  .form-group input,
  .form-group select {
    padding: 12px;
    background: var(--bg-secondary);
    border: 1px solid var(--border-primary);
    border-radius: 8px;
    color: var(--text-primary);
    font-size: 14px;
  }

  .form-group input:focus,
  .form-group select:focus {
    outline: none;
    border-color: #0ea5e9;
  }

  .form-group .hint {
    font-size: 12px;
    color: var(--text-muted);
  }

  .form-group .range-value {
    font-weight: 600;
    color: #0ea5e9;
  }

  .checkbox-group label {
    display: flex;
    align-items: center;
    gap: 8px;
    cursor: pointer;
  }

  .radio-cards {
    display: grid;
    grid-template-columns: repeat(3, 1fr);
    gap: 12px;
  }

  @media (max-width: 600px) {
    .radio-cards { grid-template-columns: 1fr; }
  }

  .radio-card {
    display: flex;
    flex-direction: column;
    align-items: center;
    padding: 20px;
    background: var(--bg-secondary);
    border: 2px solid var(--border-primary);
    border-radius: 12px;
    cursor: pointer;
    transition: all 0.2s;
    text-align: center;
  }

  .radio-card input {
    display: none;
  }

  .radio-card.selected {
    border-color: #0ea5e9;
    background: rgba(14, 165, 233, 0.1);
  }

  .radio-card .icon {
    font-size: 32px;
    margin-bottom: 8px;
  }

  .radio-card .title {
    font-weight: 600;
    margin-bottom: 4px;
  }

  .radio-card .desc {
    font-size: 12px;
    color: var(--text-muted);
  }

  .form-buttons {
    display: flex;
    gap: 12px;
    margin-top: 24px;
  }

  .btn-back {
    padding: 14px 24px;
    background: var(--bg-tertiary);
    border: none;
    border-radius: 8px;
    color: var(--text-primary);
    cursor: pointer;
  }

  .btn-next,
  .btn-submit {
    flex: 1;
    padding: 14px 24px;
    background: linear-gradient(135deg, #0ea5e9, #7c3aed);
    border: none;
    border-radius: 8px;
    color: white;
    font-weight: 600;
    cursor: pointer;
    transition: all 0.2s;
  }

  .btn-next:hover,
  .btn-submit:hover {
    transform: translateY(-2px);
    box-shadow: 0 4px 12px rgba(14, 165, 233, 0.4);
  }

  .btn-submit:disabled {
    opacity: 0.7;
    cursor: not-allowed;
    transform: none;
  }
`;

export default CompleteAssessmentForm;
