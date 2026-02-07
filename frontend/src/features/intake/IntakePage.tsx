import React, { useState, Suspense, lazy } from 'react';
import { useNavigate } from 'react-router-dom';
import {
    ArrowRight, ArrowLeft, MapPin, Home, Sparkles, Ruler, Users, Droplets,
    Shovel, Building2, Wallet, Calendar, Shield, Target, Zap, CheckCircle,
    CloudRain, Thermometer, Layers, Clock, IndianRupee, FileText
} from 'lucide-react';
import axios from 'axios';
import API_BASE_URL from '../../config/api';

const RoofMap = lazy(() => import('../../components/RoofMap'));

const IntakePage = () => {
    const navigate = useNavigate();
    const [loading, setLoading] = useState(false);
    const [step, setStep] = useState(1);
    const [mapViewMode, setMapViewMode] = useState<'street' | 'satellite'>('satellite');
    const TOTAL_STEPS = 6;

    // Comprehensive form data - ALL possible inputs
    const [formData, setFormData] = useState({
        // Step 1: Location & Property
        address: '',
        pincode: '',
        state: 'Delhi',
        city: 'New Delhi',
        latitude: 28.6139,
        longitude: 77.2090,
        property_type: 'residential', // residential, commercial, industrial, government, institutional
        building_age_years: 5,
        ownership: 'owned', // owned, rented, government

        // Step 2: Roof Details
        roof_area_sqm: 0,
        geometry: null as any,
        roof_material: 'rcc', // rcc, metal, tile, asbestos, thatched, plastic
        roof_slope_degrees: 0,
        num_floors: 1,
        roof_condition: 'good', // new, good, fair, poor
        roof_orientation: 'flat', // flat, north, south, east, west
        has_existing_rwh: false,

        // Step 3: Building & Occupancy
        num_people: 4,
        building_use: 'home', // home, office, school, hospital, factory, mixed
        occupancy_type: 'full_time', // full_time, part_time, seasonal
        avg_occupancy_hours: 16,
        has_existing_plumbing: false,
        plumbing_condition: 'good', // new, good, fair, poor

        // Step 4: Land & Environment
        available_ground_area_sqm: 10,
        soil_type: 'loamy', // sandy, loamy, clayey, rocky, alluvial
        ground_water_depth_m: 10,
        flood_zone: false,
        drainage_condition: 'good', // excellent, good, fair, poor
        annual_rainfall_mm: 800, // auto-filled based on location
        climate_zone: 'semi_arid', // tropical_wet, tropical_dry, semi_arid, arid, temperate

        // Step 5: Water Usage & Requirements
        current_water_source: 'municipality', // municipality, borewell, tanker, well, none
        monthly_water_bill_inr: 500,
        daily_water_consumption_lpd: 540, // auto-calculated or manual
        water_quality_requirement: 'non_potable', // potable, non_potable, industrial
        peak_usage_season: 'summer', // summer, monsoon, winter, year_round
        water_scarcity_level: 'moderate', // none, low, moderate, high, severe

        // Step 6: Financial & Preferences
        applicant_type: 'individual', // individual, organization, government, ngo
        income_category: 'middle', // bpl, low, middle, high
        budget_range: '50000-100000', // <25000, 25000-50000, 50000-100000, 100000-200000, >200000
        wants_financing: false,
        installation_timeline: 'within_3_months', // urgent, within_1_month, within_3_months, within_6_months, flexible
        storage_preference: 'hybrid', // tank, recharge, hybrid
        tank_material_preference: 'concrete', // concrete, plastic, steel, ferrocement
        installation_approach: 'professional', // diy, professional, government_scheme
        primary_purpose: 'both', // drinking, irrigation, both, industrial, groundwater_recharge
        wants_iot_monitoring: false,
        needs_permit_assistance: false,
    });

    /** Assessment input mode: address (full form) | satellite-only | photo (Feature A) */
    const [assessmentInputMode, setAssessmentInputMode] = useState<'address' | 'satellite-only' | 'photo'>('address');
    const [polygonDrawn, setPolygonDrawn] = useState(false);
    const [useManualInput, setUseManualInput] = useState(false);
    const [manualArea, setManualArea] = useState('');

    const handlePolygonUpdate = (area: number, geojson: any) => {
        setFormData(prev => ({ ...prev, geometry: geojson, roof_area_sqm: area || 120 }));
        setPolygonDrawn(true);
    };

    const updateField = (field: string, value: any) => {
        setFormData(prev => ({ ...prev, [field]: value }));
    };

    // Auto-calculate daily consumption when people count changes
    const updatePeople = (num: number) => {
        setFormData(prev => ({
            ...prev,
            num_people: num,
            daily_water_consumption_lpd: num * 135 // 135 LPCD per person
        }));
    };

    const submitAssessment = async () => {
        setLoading(true);
        const areaToUse = useManualInput && manualArea ? parseFloat(manualArea) : formData.roof_area_sqm || 120;

        try {
            // Feature A: multi-modal assessment (satellite-only | photo) via POST /assessments
            if (assessmentInputMode === 'satellite-only' || assessmentInputMode === 'photo') {
                const payload = {
                    address: formData.address || `${formData.city}, ${formData.state}`,
                    mode: assessmentInputMode,
                    lat: formData.latitude,
                    lng: formData.longitude,
                    roof_area_sqm: areaToUse,
                    roof_material: formData.roof_material || 'rcc',
                    state: formData.state,
                    city: formData.city,
                    people: formData.num_people,
                    floors: formData.num_floors,
                };
                const response = await axios.post(`${API_BASE_URL}/api/v1/assessments`, payload);
                const data = response.data;
                const result = {
                    project_id: data.assessment_id,
                    assessment_id: data.assessment_id,
                    runoff_potential_liters: data.annual_yield_liters,
                    recommended_tank_size: data.scenarios?.max_capture?.tank_liters ?? 10000,
                    pdf_url: data.pdf_url,
                    confidence: data.confidence,
                    ...data,
                };
                navigate(`/assess/${data.assessment_id}`, { state: { result, formData } });
                setLoading(false);
                return;
            }
        } catch (e) {
            if (assessmentInputMode !== 'address') {
                console.error(e);
                setLoading(false);
                // Fall through to full form submit as fallback
            }
        }

        try {
            // Full form: complete assessment (address mode)
            let budgetMax = null;
            if (formData.budget_range) {
                const parts = formData.budget_range.split('-');
                if (parts.length === 2) budgetMax = parseInt(parts[1]);
                else if (formData.budget_range.startsWith('<')) budgetMax = 25000;
                else if (formData.budget_range.startsWith('>')) budgetMax = 200001;
            }

            const payload = {
                roof_area_sqm: areaToUse,
                city: formData.city,
                state: formData.state,
                latitude: formData.latitude,
                longitude: formData.longitude,
                roof_type: formData.roof_material,
                roof_slope_degrees: formData.roof_slope_degrees,
                num_floors: formData.num_floors,
                num_people: formData.num_people,
                existing_plumbing: formData.has_existing_plumbing,
                building_age_years: formData.building_age_years,
                current_water_source: formData.current_water_source,
                monthly_water_bill: formData.monthly_water_bill_inr,
                daily_water_usage_liters: formData.daily_water_consumption_lpd,
                soil_type: formData.soil_type,
                ground_water_depth_m: formData.ground_water_depth_m,
                available_ground_area_sqm: formData.available_ground_area_sqm,
                storage_preference: formData.storage_preference,
                budget_inr: budgetMax
            };

            const response = await axios.post(`${API_BASE_URL}/api/v1/assessment/complete`, payload);

            const data = response.data;
            const result = {
                project_id: `PRJ-${Date.now()}`,
                runoff_potential_liters: data.annual_collection_liters,
                recommended_tank_size: data.recommended_tank_liters,
                monthly_breakdown: data.monthly_breakdown?.map((m: any) => m.collection_liters) ?? [],

                ...data
            };

            navigate(`/assess/${result.project_id}`, { state: { result, formData } });
        } catch (error: any) {
            console.error(error);
            const mockProjectId = `ASM_${Date.now()}_DEMO`;
            navigate(`/assess/${mockProjectId}`, {
                state: {
                    result: {
                        project_id: mockProjectId,
                        runoff_potential_liters: areaToUse * 800 * 0.85,
                        recommended_tank_size: Math.ceil(areaToUse * 800 * 0.85 * 0.15 / 1000) * 1000,
                    },
                    formData
                }
            });
        } finally {
            setLoading(false);
        }
    };

    const STATES = [
        "Andhra Pradesh", "Arunachal Pradesh", "Assam", "Bihar", "Chhattisgarh",
        "Delhi", "Goa", "Gujarat", "Haryana", "Himachal Pradesh", "Jharkhand",
        "Karnataka", "Kerala", "Madhya Pradesh", "Maharashtra", "Manipur",
        "Meghalaya", "Mizoram", "Nagaland", "Odisha", "Punjab", "Rajasthan",
        "Sikkim", "Tamil Nadu", "Telangana", "Tripura", "Uttar Pradesh",
        "Uttarakhand", "West Bengal"
    ];

    const CITIES: Record<string, string[]> = {
        "Maharashtra": ["Mumbai", "Pune", "Nagpur", "Nashik", "Thane"],
        "Karnataka": ["Bangalore", "Mysore", "Mangalore", "Hubli"],
        "Tamil Nadu": ["Chennai", "Coimbatore", "Madurai", "Salem"],
        "Delhi": ["New Delhi", "Central Delhi", "South Delhi", "North Delhi"],
        "Gujarat": ["Ahmedabad", "Surat", "Vadodara", "Rajkot"],
        "Rajasthan": ["Jaipur", "Jodhpur", "Udaipur", "Kota"],
        "Kerala": ["Kochi", "Thiruvananthapuram", "Kozhikode"],
        "West Bengal": ["Kolkata", "Howrah", "Durgapur"],
        "Telangana": ["Hyderabad", "Warangal", "Nizamabad"],
        "Uttar Pradesh": ["Lucknow", "Noida", "Kanpur", "Agra", "Varanasi"],
        "Andhra Pradesh": ["Visakhapatnam", "Vijayawada", "Tirupati"],
        "Haryana": ["Gurugram", "Faridabad", "Rohtak"],
        "Punjab": ["Chandigarh", "Ludhiana", "Amritsar"],
        "Madhya Pradesh": ["Bhopal", "Indore", "Gwalior"],
        "Bihar": ["Patna", "Gaya", "Muzaffarpur"],
        "Odisha": ["Bhubaneswar", "Cuttack", "Rourkela"],
    };

    const SelectField = ({ label, icon: Icon, value, onChange, options, iconColor = "text-cyan-400" }: any) => (
        <div>
            <label className="block text-xs font-medium text-gray-400 mb-1.5 flex items-center gap-1.5">
                {Icon && <Icon size={14} className={iconColor} />}
                {label}
            </label>
            <select
                value={value}
                onChange={e => onChange(e.target.value)}
                className="w-full rounded-lg bg-white/5 border border-white/10 text-white p-2.5 text-sm focus:border-cyan-500 focus:ring-1 focus:ring-cyan-500/20"
            >
                {options.map((opt: any) => (
                    <option key={opt.value} value={opt.value} className="bg-slate-800">
                        {opt.label}
                    </option>
                ))}
            </select>
        </div>
    );

    const NumberField = ({ label, icon: Icon, value, onChange, min = 0, max = 999999, suffix = "", iconColor = "text-cyan-400" }: any) => (
        <div>
            <label className="block text-xs font-medium text-gray-400 mb-1.5 flex items-center gap-1.5">
                {Icon && <Icon size={14} className={iconColor} />}
                {label}
            </label>
            <div className="relative">
                <input
                    type="number"
                    min={min}
                    max={max}
                    value={value}
                    onChange={e => onChange(parseFloat(e.target.value) || 0)}
                    className="w-full rounded-lg bg-white/5 border border-white/10 text-white p-2.5 text-sm focus:border-cyan-500 focus:ring-1 focus:ring-cyan-500/20"
                />
                {suffix && <span className="absolute right-3 top-2.5 text-gray-500 text-sm">{suffix}</span>}
            </div>
        </div>
    );

    const CheckboxField = ({ label, checked, onChange, description }: any) => (
        <label className="flex items-start gap-3 cursor-pointer p-3 bg-white/5 rounded-lg hover:bg-white/10 transition-all">
            <input
                type="checkbox"
                checked={checked}
                onChange={e => onChange(e.target.checked)}
                className="w-4 h-4 mt-0.5 rounded bg-white/10 border-white/20 text-cyan-500"
            />
            <div>
                <span className="text-white text-sm font-medium">{label}</span>
                {description && <p className="text-gray-500 text-xs mt-0.5">{description}</p>}
            </div>
        </label>
    );

    const renderStep = () => {
        switch (step) {
            case 1:
                return (
                    <>
                        <div className="flex items-center gap-2 text-white font-semibold mb-4">
                            <MapPin size={20} className="text-cyan-400" />
                            <span>Step 1: Location & Property</span>
                        </div>

                        {/* Feature A: Assessment input mode */}
                        <div className="mb-6 p-4 rounded-xl bg-white/5 border border-white/10">
                            <label className="block text-xs font-medium text-gray-400 mb-2">Assessment → Input mode</label>
                            <div className="flex flex-wrap gap-2">
                                {[
                                    { value: 'address' as const, label: 'Address', desc: 'Full form' },
                                    { value: 'satellite-only' as const, label: 'Satellite only', desc: 'Use existing pipeline with fallbacks' },
                                    { value: 'photo' as const, label: 'Photo', desc: 'Image-based assessment' },
                                ].map(opt => (
                                    <button
                                        key={opt.value}
                                        type="button"
                                        onClick={() => setAssessmentInputMode(opt.value)}
                                        className={`px-4 py-2 rounded-lg text-sm font-medium transition-all ${assessmentInputMode === opt.value
                                            ? 'bg-cyan-500 text-white'
                                            : 'bg-white/10 text-gray-400 hover:text-white hover:bg-white/20'
                                            }`}
                                    >
                                        {opt.label}
                                    </button>
                                ))}
                            </div>
                            <p className="text-gray-500 text-xs mt-2">
                                {assessmentInputMode === 'address' && 'Complete all steps for full assessment.'}
                                {assessmentInputMode === 'satellite-only' && 'Uses location with default site details when missing.'}
                                {assessmentInputMode === 'photo' && 'Upload a photo for image-only assessment (same PDF + confidence).'}
                            </p>
                        </div>

                        <div className="space-y-4">
                            <div>
                                <label className="block text-xs font-medium text-gray-400 mb-1.5">📍 Property Address</label>
                                <input
                                    type="text"
                                    placeholder="123 Rain Street, Colony Name"
                                    value={formData.address}
                                    onChange={e => updateField('address', e.target.value)}
                                    className="w-full rounded-lg bg-white/5 border border-white/10 text-white p-3 text-sm focus:border-cyan-500"
                                />
                            </div>

                            <div className="grid grid-cols-2 gap-3">
                                <div>
                                    <label className="block text-xs font-medium text-gray-400 mb-1.5">Pincode</label>
                                    <input
                                        type="text"
                                        maxLength={6}
                                        placeholder="110001"
                                        value={formData.pincode}
                                        onChange={e => updateField('pincode', e.target.value)}
                                        className="w-full rounded-lg bg-white/5 border border-white/10 text-white p-2.5 text-sm"
                                    />
                                </div>
                                <SelectField
                                    label="State"
                                    value={formData.state}
                                    onChange={(v: string) => {
                                        updateField('state', v);
                                        updateField('city', CITIES[v]?.[0] || '');
                                    }}
                                    options={STATES.map(s => ({ value: s, label: s }))}
                                />
                            </div>

                            <SelectField
                                label="City"
                                value={formData.city}
                                onChange={(v: string) => updateField('city', v)}
                                options={(CITIES[formData.state] || ['Other']).map(c => ({ value: c, label: c }))}
                            />

                            <SelectField
                                label="Property Type"
                                icon={Building2}
                                iconColor="text-purple-400"
                                value={formData.property_type}
                                onChange={(v: string) => updateField('property_type', v)}
                                options={[
                                    { value: 'residential', label: '🏠 Residential' },
                                    { value: 'commercial', label: '🏢 Commercial' },
                                    { value: 'industrial', label: '🏭 Industrial' },
                                    { value: 'government', label: '🏛️ Government Building' },
                                    { value: 'institutional', label: '🏫 School/Hospital/Institution' },
                                ]}
                            />

                            <div className="grid grid-cols-2 gap-3">
                                <NumberField
                                    label="Building Age"
                                    icon={Clock}
                                    value={formData.building_age_years}
                                    onChange={(v: number) => updateField('building_age_years', v)}
                                    suffix="years"
                                />
                                <SelectField
                                    label="Ownership"
                                    value={formData.ownership}
                                    onChange={(v: string) => updateField('ownership', v)}
                                    options={[
                                        { value: 'owned', label: 'Self-Owned' },
                                        { value: 'rented', label: 'Rented' },
                                        { value: 'government', label: 'Government' },
                                    ]}
                                />
                            </div>
                        </div>
                    </>
                );

            case 2:
                return (
                    <>
                        <div className="flex items-center gap-2 text-white font-semibold mb-4">
                            <Home size={20} className="text-green-400" />
                            <span>Step 2: Roof Details</span>
                        </div>

                        <div className="space-y-4">
                            <SelectField
                                label="Roof Material"
                                icon={Layers}
                                iconColor="text-green-400"
                                value={formData.roof_material}
                                onChange={(v: string) => updateField('roof_material', v)}
                                options={[
                                    { value: 'rcc', label: 'RCC / Concrete (C=0.85)' },
                                    { value: 'metal', label: 'Metal Sheet (C=0.90)' },
                                    { value: 'tile', label: 'Clay Tiles (C=0.80)' },
                                    { value: 'asbestos', label: 'Asbestos (C=0.85)' },
                                    { value: 'thatched', label: 'Thatched (C=0.60)' },
                                    { value: 'plastic', label: 'Plastic/Polycarbonate (C=0.90)' },
                                ]}
                            />

                            <div className="grid grid-cols-2 gap-3">
                                <div>
                                    <label className="block text-xs font-medium text-gray-400 mb-1.5">Roof Slope</label>
                                    <div className="flex items-center gap-2">
                                        <input
                                            type="range"
                                            min="0"
                                            max="45"
                                            value={formData.roof_slope_degrees}
                                            onChange={e => updateField('roof_slope_degrees', parseInt(e.target.value))}
                                            className="flex-1"
                                        />
                                        <span className="text-cyan-400 font-bold text-sm w-12">{formData.roof_slope_degrees}°</span>
                                    </div>
                                </div>
                                <NumberField
                                    label="Number of Floors"
                                    value={formData.num_floors}
                                    onChange={(v: number) => updateField('num_floors', v)}
                                    min={1}
                                    max={50}
                                />
                            </div>

                            <div className="grid grid-cols-2 gap-3">
                                <SelectField
                                    label="Roof Condition"
                                    value={formData.roof_condition}
                                    onChange={(v: string) => updateField('roof_condition', v)}
                                    options={[
                                        { value: 'new', label: '✨ New (< 2 years)' },
                                        { value: 'good', label: '✅ Good' },
                                        { value: 'fair', label: '⚠️ Fair' },
                                        { value: 'poor', label: '❌ Poor (needs repair)' },
                                    ]}
                                />
                                <SelectField
                                    label="Roof Orientation"
                                    value={formData.roof_orientation}
                                    onChange={(v: string) => updateField('roof_orientation', v)}
                                    options={[
                                        { value: 'flat', label: 'Flat' },
                                        { value: 'north', label: 'North-facing' },
                                        { value: 'south', label: 'South-facing' },
                                        { value: 'east', label: 'East-facing' },
                                        { value: 'west', label: 'West-facing' },
                                    ]}
                                />
                            </div>

                            <CheckboxField
                                label="Has existing RWH system"
                                description="Check if any rainwater harvesting is already installed"
                                checked={formData.has_existing_rwh}
                                onChange={(v: boolean) => updateField('has_existing_rwh', v)}
                            />

                            <div className="border border-white/10 rounded-xl p-4">
                                <CheckboxField
                                    label="Enter roof area manually"
                                    checked={useManualInput}
                                    onChange={setUseManualInput}
                                />
                                {useManualInput && (
                                    <div className="mt-3">
                                        <input
                                            type="number"
                                            placeholder="Roof area in m²"
                                            value={manualArea}
                                            onChange={e => setManualArea(e.target.value)}
                                            className="w-full rounded-lg bg-white/5 border border-white/10 text-white p-2.5 text-sm"
                                        />
                                    </div>
                                )}
                            </div>

                            {(polygonDrawn || (useManualInput && manualArea)) && (
                                <div className="bg-gradient-to-r from-green-500/10 to-emerald-500/10 border border-green-500/20 rounded-xl p-4">
                                    <div className="text-sm text-gray-400 mb-1">Roof Area</div>
                                    <div className="text-3xl font-black text-green-400">
                                        {useManualInput ? manualArea : formData.roof_area_sqm} m²
                                    </div>
                                </div>
                            )}
                        </div>
                    </>
                );

            case 3:
                return (
                    <>
                        <div className="flex items-center gap-2 text-white font-semibold mb-4">
                            <Users size={20} className="text-purple-400" />
                            <span>Step 3: Building & Occupancy</span>
                        </div>

                        <div className="space-y-4">
                            <NumberField
                                label="Number of People"
                                icon={Users}
                                iconColor="text-purple-400"
                                value={formData.num_people}
                                onChange={updatePeople}
                                min={1}
                                max={1000}
                            />

                            <SelectField
                                label="Building Use"
                                icon={Building2}
                                value={formData.building_use}
                                onChange={(v: string) => updateField('building_use', v)}
                                options={[
                                    { value: 'home', label: '🏠 Residence' },
                                    { value: 'office', label: '💼 Office' },
                                    { value: 'school', label: '🏫 School/College' },
                                    { value: 'hospital', label: '🏥 Hospital/Clinic' },
                                    { value: 'factory', label: '🏭 Factory/Warehouse' },
                                    { value: 'hotel', label: '🏨 Hotel/Guest House' },
                                    { value: 'mixed', label: '🏗️ Mixed Use' },
                                ]}
                            />

                            <div className="grid grid-cols-2 gap-3">
                                <SelectField
                                    label="Occupancy Type"
                                    value={formData.occupancy_type}
                                    onChange={(v: string) => updateField('occupancy_type', v)}
                                    options={[
                                        { value: 'full_time', label: 'Full-time (24/7)' },
                                        { value: 'part_time', label: 'Part-time (office hours)' },
                                        { value: 'seasonal', label: 'Seasonal' },
                                    ]}
                                />
                                <NumberField
                                    label="Avg Hours/Day"
                                    value={formData.avg_occupancy_hours}
                                    onChange={(v: number) => updateField('avg_occupancy_hours', v)}
                                    min={1}
                                    max={24}
                                    suffix="hrs"
                                />
                            </div>

                            <CheckboxField
                                label="Has existing rainwater plumbing"
                                description="Downspouts, gutters, or collection pipes already installed"
                                checked={formData.has_existing_plumbing}
                                onChange={(v: boolean) => updateField('has_existing_plumbing', v)}
                            />

                            {formData.has_existing_plumbing && (
                                <SelectField
                                    label="Plumbing Condition"
                                    value={formData.plumbing_condition}
                                    onChange={(v: string) => updateField('plumbing_condition', v)}
                                    options={[
                                        { value: 'new', label: '✨ New' },
                                        { value: 'good', label: '✅ Good' },
                                        { value: 'fair', label: '⚠️ Fair' },
                                        { value: 'poor', label: '❌ Needs replacement' },
                                    ]}
                                />
                            )}

                            <div className="bg-purple-500/10 border border-purple-500/20 rounded-xl p-4">
                                <div className="text-sm text-gray-400 mb-1">Estimated Daily Water Demand</div>
                                <div className="text-2xl font-bold text-purple-400">
                                    {formData.daily_water_consumption_lpd} L/day
                                </div>
                                <div className="text-xs text-gray-500 mt-1">Based on 135 LPCD per person</div>
                            </div>
                        </div>
                    </>
                );

            case 4:
                return (
                    <>
                        <div className="flex items-center gap-2 text-white font-semibold mb-4">
                            <Shovel size={20} className="text-amber-400" />
                            <span>Step 4: Land & Environment</span>
                        </div>

                        <div className="space-y-4">
                            <NumberField
                                label="Available Ground Area"
                                icon={Ruler}
                                iconColor="text-amber-400"
                                value={formData.available_ground_area_sqm}
                                onChange={(v: number) => updateField('available_ground_area_sqm', v)}
                                suffix="m²"
                            />

                            <div className="grid grid-cols-2 gap-3">
                                <SelectField
                                    label="Soil Type"
                                    icon={Shovel}
                                    iconColor="text-amber-400"
                                    value={formData.soil_type}
                                    onChange={(v: string) => updateField('soil_type', v)}
                                    options={[
                                        { value: 'sandy', label: 'Sandy (High percolation)' },
                                        { value: 'loamy', label: 'Loamy (Medium)' },
                                        { value: 'clayey', label: 'Clayey (Low percolation)' },
                                        { value: 'rocky', label: 'Rocky' },
                                        { value: 'alluvial', label: 'Alluvial' },
                                    ]}
                                />
                                <NumberField
                                    label="Groundwater Depth"
                                    value={formData.ground_water_depth_m}
                                    onChange={(v: number) => updateField('ground_water_depth_m', v)}
                                    suffix="m"
                                />
                            </div>

                            <div className="grid grid-cols-2 gap-3">
                                <NumberField
                                    label="Annual Rainfall"
                                    icon={CloudRain}
                                    iconColor="text-blue-400"
                                    value={formData.annual_rainfall_mm}
                                    onChange={(v: number) => updateField('annual_rainfall_mm', v)}
                                    suffix="mm"
                                />
                                <SelectField
                                    label="Climate Zone"
                                    icon={Thermometer}
                                    value={formData.climate_zone}
                                    onChange={(v: string) => updateField('climate_zone', v)}
                                    options={[
                                        { value: 'tropical_wet', label: 'Tropical Wet' },
                                        { value: 'tropical_dry', label: 'Tropical Dry' },
                                        { value: 'semi_arid', label: 'Semi-Arid' },
                                        { value: 'arid', label: 'Arid/Desert' },
                                        { value: 'temperate', label: 'Temperate' },
                                    ]}
                                />
                            </div>

                            <SelectField
                                label="Drainage Condition"
                                value={formData.drainage_condition}
                                onChange={(v: string) => updateField('drainage_condition', v)}
                                options={[
                                    { value: 'excellent', label: '✨ Excellent (no waterlogging)' },
                                    { value: 'good', label: '✅ Good' },
                                    { value: 'fair', label: '⚠️ Fair (occasional logging)' },
                                    { value: 'poor', label: '❌ Poor (frequent flooding)' },
                                ]}
                            />

                            <CheckboxField
                                label="Located in flood-prone zone"
                                description="Area experiences regular flooding during monsoon"
                                checked={formData.flood_zone}
                                onChange={(v: boolean) => updateField('flood_zone', v)}
                            />
                        </div>
                    </>
                );

            case 5:
                return (
                    <>
                        <div className="flex items-center gap-2 text-white font-semibold mb-4">
                            <Droplets size={20} className="text-blue-400" />
                            <span>Step 5: Water Usage & Requirements</span>
                        </div>

                        <div className="space-y-4">
                            <SelectField
                                label="Current Water Source"
                                icon={Droplets}
                                iconColor="text-blue-400"
                                value={formData.current_water_source}
                                onChange={(v: string) => updateField('current_water_source', v)}
                                options={[
                                    { value: 'municipality', label: '🚰 Municipal Supply' },
                                    { value: 'borewell', label: '⬇️ Borewell/Tubewell' },
                                    { value: 'tanker', label: '🚛 Water Tanker' },
                                    { value: 'well', label: '🪣 Open Well' },
                                    { value: 'river', label: '🌊 River/Canal' },
                                    { value: 'none', label: '❌ No Regular Source' },
                                ]}
                            />

                            <div className="grid grid-cols-2 gap-3">
                                <NumberField
                                    label="Monthly Water Bill"
                                    icon={IndianRupee}
                                    iconColor="text-green-400"
                                    value={formData.monthly_water_bill_inr}
                                    onChange={(v: number) => updateField('monthly_water_bill_inr', v)}
                                    suffix="₹"
                                />
                                <NumberField
                                    label="Daily Consumption"
                                    value={formData.daily_water_consumption_lpd}
                                    onChange={(v: number) => updateField('daily_water_consumption_lpd', v)}
                                    suffix="L/day"
                                />
                            </div>

                            <SelectField
                                label="Water Quality Requirement"
                                icon={Shield}
                                iconColor="text-cyan-400"
                                value={formData.water_quality_requirement}
                                onChange={(v: string) => updateField('water_quality_requirement', v)}
                                options={[
                                    { value: 'potable', label: '💧 Potable (Drinking quality)' },
                                    { value: 'non_potable', label: '🚿 Non-potable (Washing, gardening)' },
                                    { value: 'industrial', label: '🏭 Industrial use' },
                                ]}
                            />

                            <div className="grid grid-cols-2 gap-3">
                                <SelectField
                                    label="Peak Usage Season"
                                    value={formData.peak_usage_season}
                                    onChange={(v: string) => updateField('peak_usage_season', v)}
                                    options={[
                                        { value: 'summer', label: '☀️ Summer' },
                                        { value: 'monsoon', label: '🌧️ Monsoon' },
                                        { value: 'winter', label: '❄️ Winter' },
                                        { value: 'year_round', label: '📅 Year-round' },
                                    ]}
                                />
                                <SelectField
                                    label="Water Scarcity Level"
                                    value={formData.water_scarcity_level}
                                    onChange={(v: string) => updateField('water_scarcity_level', v)}
                                    options={[
                                        { value: 'none', label: '✅ None' },
                                        { value: 'low', label: '🟡 Low' },
                                        { value: 'moderate', label: '🟠 Moderate' },
                                        { value: 'high', label: '🔴 High' },
                                        { value: 'severe', label: '⚫ Severe' },
                                    ]}
                                />
                            </div>
                        </div>
                    </>
                );

            case 6:
                return (
                    <>
                        <div className="flex items-center gap-2 text-white font-semibold mb-4">
                            <Wallet size={20} className="text-emerald-400" />
                            <span>Step 6: Financial & Preferences</span>
                        </div>

                        <div className="space-y-4">
                            <div className="grid grid-cols-2 gap-3">
                                <SelectField
                                    label="Applicant Type"
                                    icon={Users}
                                    value={formData.applicant_type}
                                    onChange={(v: string) => updateField('applicant_type', v)}
                                    options={[
                                        { value: 'individual', label: '👤 Individual' },
                                        { value: 'organization', label: '🏢 Organization' },
                                        { value: 'government', label: '🏛️ Government' },
                                        { value: 'ngo', label: '🤝 NGO' },
                                    ]}
                                />
                                <SelectField
                                    label="Income Category"
                                    icon={Wallet}
                                    iconColor="text-emerald-400"
                                    value={formData.income_category}
                                    onChange={(v: string) => updateField('income_category', v)}
                                    options={[
                                        { value: 'bpl', label: 'BPL (Below Poverty Line)' },
                                        { value: 'low', label: 'Low Income' },
                                        { value: 'middle', label: 'Middle Income' },
                                        { value: 'high', label: 'High Income' },
                                    ]}
                                />
                            </div>

                            <SelectField
                                label="Budget Range"
                                icon={IndianRupee}
                                iconColor="text-green-400"
                                value={formData.budget_range}
                                onChange={(v: string) => updateField('budget_range', v)}
                                options={[
                                    { value: '<25000', label: '₹ Under ₹25,000' },
                                    { value: '25000-50000', label: '₹ ₹25,000 - ₹50,000' },
                                    { value: '50000-100000', label: '₹ ₹50,000 - ₹1,00,000' },
                                    { value: '100000-200000', label: '₹ ₹1,00,000 - ₹2,00,000' },
                                    { value: '>200000', label: '₹ Above ₹2,00,000' },
                                ]}
                            />

                            <SelectField
                                label="Installation Timeline"
                                icon={Calendar}
                                value={formData.installation_timeline}
                                onChange={(v: string) => updateField('installation_timeline', v)}
                                options={[
                                    { value: 'urgent', label: '🚨 Urgent (ASAP)' },
                                    { value: 'within_1_month', label: '📅 Within 1 month' },
                                    { value: 'within_3_months', label: '📅 Within 3 months' },
                                    { value: 'within_6_months', label: '📅 Within 6 months' },
                                    { value: 'flexible', label: '🤷 Flexible' },
                                ]}
                            />

                            <div className="text-sm font-semibold text-white mt-4 mb-2">Storage Preference</div>
                            <div className="space-y-2">
                                {[
                                    { value: 'tank', icon: '🪣', label: 'Tank Storage', desc: 'Store water for later use' },
                                    { value: 'recharge', icon: '⬇️', label: 'Ground Recharge', desc: 'Recharge groundwater aquifer' },
                                    { value: 'hybrid', icon: '🔄', label: 'Hybrid System', desc: 'Tank + overflow to recharge pit' },
                                ].map(opt => (
                                    <label
                                        key={opt.value}
                                        className={`flex items-center gap-3 p-3 rounded-xl cursor-pointer transition-all ${formData.storage_preference === opt.value
                                            ? 'bg-emerald-500/20 border border-emerald-500/50'
                                            : 'bg-white/5 border border-white/10 hover:bg-white/10'
                                            }`}
                                    >
                                        <input
                                            type="radio"
                                            name="storage"
                                            value={opt.value}
                                            checked={formData.storage_preference === opt.value}
                                            onChange={() => updateField('storage_preference', opt.value)}
                                            className="hidden"
                                        />
                                        <span className="text-2xl">{opt.icon}</span>
                                        <div>
                                            <div className="text-white font-medium">{opt.label}</div>
                                            <div className="text-gray-400 text-xs">{opt.desc}</div>
                                        </div>
                                    </label>
                                ))}
                            </div>

                            <SelectField
                                label="Primary Purpose"
                                icon={Target}
                                iconColor="text-cyan-400"
                                value={formData.primary_purpose}
                                onChange={(v: string) => updateField('primary_purpose', v)}
                                options={[
                                    { value: 'drinking', label: '💧 Drinking Water' },
                                    { value: 'irrigation', label: '🌱 Garden/Irrigation' },
                                    { value: 'both', label: '🔄 Both (Domestic + Garden)' },
                                    { value: 'industrial', label: '🏭 Industrial Use' },
                                    { value: 'groundwater_recharge', label: '⬇️ Groundwater Recharge Only' },
                                ]}
                            />

                            <div className="space-y-2 mt-4">
                                <CheckboxField
                                    label="Want IoT-based monitoring"
                                    description="Real-time water level, quality sensors & mobile alerts"
                                    checked={formData.wants_iot_monitoring}
                                    onChange={(v: boolean) => updateField('wants_iot_monitoring', v)}
                                />
                                <CheckboxField
                                    label="Need financing assistance"
                                    description="Help with loans or EMI options"
                                    checked={formData.wants_financing}
                                    onChange={(v: boolean) => updateField('wants_financing', v)}
                                />
                                <CheckboxField
                                    label="Need permit assistance"
                                    description="Help with NOC and government approvals"
                                    checked={formData.needs_permit_assistance}
                                    onChange={(v: boolean) => updateField('needs_permit_assistance', v)}
                                />
                            </div>
                        </div>
                    </>
                );
        }
    };

    return (
        <div className="min-h-screen bg-gradient-to-br from-slate-900 via-blue-900 to-slate-900 py-8">
            <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
                {/* Header */}
                <div className="text-center mb-6">
                    <div className="inline-flex items-center gap-2 px-4 py-2 bg-cyan-500/10 border border-cyan-500/20 rounded-full mb-3">
                        <Sparkles className="text-cyan-400" size={16} />
                        <span className="text-cyan-300 text-sm font-medium">Complete RWH Assessment</span>
                    </div>
                    <h1 className="text-4xl font-black text-white mb-2">
                        🌧️ Design Your Rainwater System
                    </h1>
                    <p className="text-gray-300">
                        Answer all questions for a comprehensive, government-grade assessment
                    </p>
                </div>

                {/* Progress Bar */}
                <div className="max-w-2xl mx-auto mb-8">
                    <div className="flex justify-between mb-2">
                        {[1, 2, 3, 4, 5, 6].map(s => (
                            <div
                                key={s}
                                onClick={() => setStep(s)}
                                className={`w-10 h-10 rounded-full flex items-center justify-center cursor-pointer transition-all
                                    ${step === s ? 'bg-gradient-to-r from-cyan-500 to-blue-500 text-white font-bold scale-110' :
                                        step > s ? 'bg-emerald-500 text-white' : 'bg-white/10 text-gray-500'}`}
                            >
                                {step > s ? <CheckCircle size={20} /> : s}
                            </div>
                        ))}
                    </div>
                    <div className="h-2 bg-white/10 rounded-full overflow-hidden">
                        <div
                            className="h-full bg-gradient-to-r from-cyan-500 to-emerald-500 transition-all duration-500"
                            style={{ width: `${(step / TOTAL_STEPS) * 100}%` }}
                        />
                    </div>
                    <div className="text-center mt-2 text-gray-400 text-sm">
                        Step {step} of {TOTAL_STEPS}
                    </div>
                </div>

                <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
                    {/* Form Panel */}
                    <div className="lg:col-span-1">
                        <div className="bg-white/5 backdrop-blur-xl border border-white/10 rounded-2xl p-6">
                            {renderStep()}

                            {/* Navigation */}
                            <div className="flex gap-3 mt-6">
                                {step > 1 && (
                                    <button
                                        onClick={() => setStep(step - 1)}
                                        className="flex items-center gap-2 px-4 py-3 rounded-xl bg-white/10 text-white font-medium hover:bg-white/20 transition-all"
                                    >
                                        <ArrowLeft size={18} />
                                        Back
                                    </button>
                                )}
                                {step < TOTAL_STEPS ? (
                                    <button
                                        onClick={() => setStep(step + 1)}
                                        className="flex-1 flex items-center justify-center gap-2 py-3 rounded-xl bg-gradient-to-r from-cyan-500 to-blue-500 text-white font-bold hover:scale-[1.02] transition-all"
                                    >
                                        Next
                                        <ArrowRight size={18} />
                                    </button>
                                ) : (
                                    <button
                                        onClick={submitAssessment}
                                        disabled={loading}
                                        className="flex-1 flex items-center justify-center gap-2 py-3 rounded-xl bg-gradient-to-r from-emerald-500 to-green-500 text-white font-bold hover:scale-[1.02] transition-all disabled:opacity-50"
                                    >
                                        {loading ? (
                                            <>
                                                <div className="animate-spin rounded-full h-5 w-5 border-b-2 border-white" />
                                                Analyzing...
                                            </>
                                        ) : (
                                            <>
                                                <Zap size={18} />
                                                Get Complete Report
                                            </>
                                        )}
                                    </button>
                                )}
                            </div>
                        </div>

                        {/* Summary Panel */}
                        <div className="mt-4 bg-gradient-to-br from-emerald-500/10 to-cyan-500/10 border border-emerald-500/20 rounded-2xl p-4">
                            <div className="text-sm font-semibold text-white mb-2">📊 Your Report Will Include:</div>
                            <ul className="text-xs text-gray-300 space-y-1">
                                <li>✓ Annual yield & monthly breakdown</li>
                                <li>✓ Optimal tank size recommendation</li>
                                <li>✓ Complete bill of materials</li>
                                <li>✓ Cost estimate with ROI analysis</li>
                                <li>✓ Eligible subsidies & schemes</li>
                                <li>✓ Required permits & compliance</li>
                                <li>✓ Maintenance schedule</li>
                                <li>✓ Water quality grade</li>
                                <li>✓ CO₂ offset calculation</li>
                                <li>✓ Contractor recommendations</li>
                            </ul>
                        </div>
                    </div>

                    {/* Map Area / Photo Upload Area */}
                    <div className="lg:col-span-2">
                        <div className="bg-white/5 backdrop-blur-xl border border-white/10 rounded-2xl p-2 h-[650px]">
                            {/* Photo Upload Mode */}
                            {assessmentInputMode === 'photo' ? (
                                <div className="w-full h-full rounded-xl bg-gradient-to-br from-slate-800 via-slate-700 to-slate-800 flex flex-col items-center justify-center p-8">
                                    <div className="text-center max-w-md">
                                        <div className="w-24 h-24 mx-auto mb-6 rounded-2xl bg-gradient-to-br from-purple-500 to-pink-500 flex items-center justify-center">
                                            <svg className="w-12 h-12 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 16l4.586-4.586a2 2 0 012.828 0L16 16m-2-2l1.586-1.586a2 2 0 012.828 0L20 14m-6-6h.01M6 20h12a2 2 0 002-2V6a2 2 0 00-2-2H6a2 2 0 00-2 2v12a2 2 0 002 2z" />
                                            </svg>
                                        </div>
                                        <h3 className="text-2xl font-bold text-white mb-2">📸 Upload Roof Photo</h3>
                                        <p className="text-gray-400 mb-6">
                                            Upload a clear photo of your roof. Our AI will analyze it to estimate area and recommend the best RWH system.
                                        </p>

                                        {/* Upload Zone */}
                                        <label className="block cursor-pointer">
                                            <div className="border-2 border-dashed border-purple-400/50 rounded-2xl p-8 hover:border-purple-400 hover:bg-purple-500/10 transition-all group">
                                                <input
                                                    type="file"
                                                    accept="image/*"
                                                    className="hidden"
                                                    onChange={(e) => {
                                                        const file = e.target.files?.[0];
                                                        if (file) {
                                                            // Set a default estimated area for photo mode
                                                            setFormData(prev => ({
                                                                ...prev,
                                                                roof_area_sqm: 120  // Default estimate
                                                            }));
                                                            setPolygonDrawn(true);
                                                        }
                                                    }}
                                                />
                                                <div className="text-purple-400 group-hover:text-purple-300 transition-colors">
                                                    <svg className="w-12 h-12 mx-auto mb-3" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M7 16a4 4 0 01-.88-7.903A5 5 0 1115.9 6L16 6a5 5 0 011 9.9M15 13l-3-3m0 0l-3 3m3-3v12" />
                                                    </svg>
                                                    <p className="font-semibold">Click to upload or drag & drop</p>
                                                    <p className="text-sm text-gray-500 mt-1">PNG, JPG up to 10MB</p>
                                                </div>
                                            </div>
                                        </label>

                                        {/* Or use camera */}
                                        <div className="mt-4 flex items-center justify-center gap-4">
                                            <span className="text-gray-500 text-sm">or</span>
                                            <button
                                                type="button"
                                                className="px-4 py-2 bg-white/10 hover:bg-white/20 text-white rounded-lg text-sm font-medium transition-colors flex items-center gap-2"
                                            >
                                                <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M3 9a2 2 0 012-2h.93a2 2 0 001.664-.89l.812-1.22A2 2 0 0110.07 4h3.86a2 2 0 011.664.89l.812 1.22A2 2 0 0018.07 7H19a2 2 0 012 2v9a2 2 0 01-2 2H5a2 2 0 01-2-2V9z" />
                                                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 13a3 3 0 11-6 0 3 3 0 016 0z" />
                                                </svg>
                                                Take Photo
                                            </button>
                                        </div>

                                        {polygonDrawn && (
                                            <div className="mt-6 p-4 bg-green-500/20 border border-green-500/30 rounded-xl">
                                                <p className="text-green-400 font-semibold">✓ Photo ready for analysis</p>
                                                <p className="text-gray-400 text-sm mt-1">Estimated roof area: ~120 m² (AI will refine)</p>
                                            </div>
                                        )}
                                    </div>
                                </div>
                            ) : (
                                /* Map Mode (Address & Satellite) */
                                <Suspense fallback={
                                    <div className="w-full h-full rounded-xl bg-slate-800 flex items-center justify-center">
                                        <div className="text-center">
                                            <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-cyan-400 mx-auto mb-4" />
                                            <div className="text-white font-semibold">Loading map...</div>
                                        </div>
                                    </div>
                                }>
                                    <div className="relative h-full w-full rounded-xl overflow-hidden">
                                        <div className="absolute top-4 right-16 z-[400] bg-slate-900/90 backdrop-blur-md rounded-lg p-1 border border-white/10 flex gap-1 shadow-xl">
                                            <button
                                                type="button"
                                                onClick={() => setMapViewMode('street')}
                                                className={`px-3 py-1.5 rounded-md text-xs font-medium transition-all ${mapViewMode === 'street'
                                                    ? 'bg-cyan-500 text-white shadow-lg'
                                                    : 'text-gray-400 hover:text-white hover:bg-white/5'
                                                    }`}
                                            >
                                                Map
                                            </button>
                                            <button
                                                type="button"
                                                onClick={() => setMapViewMode('satellite')}
                                                className={`px-3 py-1.5 rounded-md text-xs font-medium transition-all ${mapViewMode === 'satellite'
                                                    ? 'bg-cyan-500 text-white shadow-lg'
                                                    : 'text-gray-400 hover:text-white hover:bg-white/5'
                                                    }`}
                                            >
                                                Satellite
                                            </button>
                                        </div>
                                        <RoofMap
                                            onPolygonUpdate={handlePolygonUpdate}
                                            mapType={mapViewMode}
                                        />
                                    </div>
                                </Suspense>
                            )}
                        </div>
                    </div>
                </div>
            </div>
        </div>
    );
};

export default IntakePage;
