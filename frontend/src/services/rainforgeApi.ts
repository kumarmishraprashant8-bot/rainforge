/**
 * RainForge API Service
 * Minimal wiring for frontend components to call demo endpoints
 */

const API_BASE = '/api/v1';

// Types
export interface AssessmentInput {
    site_id: string;
    address: string;
    lat: number;
    lng: number;
    roof_area_sqm: number;
    roof_material?: string;
    demand_l_per_day?: number;
    floors?: number;
    people?: number;
    state?: string;
    city?: string;
}

export interface Scenario {
    name: string;
    tank_liters: number;
    cost_inr: number;
    capture_liters: number;
    coverage_days: number;
    roi_years: number;
}

export interface AssessmentResponse {
    assessment_id: string;
    site_id: string;
    annual_rainfall_mm: number;
    annual_yield_liters: number;
    scenarios: {
        cost_optimized: Scenario;
        max_capture: Scenario;
        dry_season: Scenario;
    };
    recommended_scenario: string;
    subsidy_pct: number;
    subsidy_amount_inr: number;
    co2_avoided_kg: number;
    pdf_url: string;
    verify_url: string;
    created_at: string;
}

export interface Installer {
    id: number;
    name: string;
    company: string;
    rpi_score: number;
    capacity_available: number;
    capacity_max: number;
    cert_level: string;
    warranty_months: number;
    jobs_completed: number;
    service_areas: string[];
}

export interface VerificationResult {
    verification_id: string;
    job_id: string;
    status: string;
    fraud_score: number;
    fraud_flags: string[];
    geo_distance_m: number | null;
    recommendation: string;
    audit_trail: Array<{ timestamp: string; action: string }>;
}

export interface TelemetryData {
    project_id: number;
    current_level: {
        liters: number;
        percent: number;
        last_updated: string;
    };
    statistics: {
        average_liters: number;
        max_liters: number;
        min_liters: number;
    };
    trend_24h: Array<{ timestamp: string; value: number }>;
    days_until_empty: number;
    alerts: Array<{ type: string; message: string; severity: string }>;
}

// API Functions

/**
 * Create a new RWH assessment
 */
export async function createAssessment(input: AssessmentInput): Promise<AssessmentResponse> {
    const response = await fetch(`${API_BASE}/assessments/assess?site_id=${input.site_id}&address=${encodeURIComponent(input.address)}&lat=${input.lat}&lng=${input.lng}&roof_area_sqm=${input.roof_area_sqm}&roof_material=${input.roof_material || 'concrete'}&floors=${input.floors || 1}&people=${input.people || 4}&state=${input.state || 'Delhi'}&city=${input.city || 'New Delhi'}`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(input)
    });

    if (!response.ok) {
        const error = await response.json();
        throw new Error(error.detail || 'Failed to create assessment');
    }

    return response.json();
}

/**
 * Get assessment details
 */
export async function getAssessment(assessmentId: string): Promise<AssessmentResponse> {
    const response = await fetch(`${API_BASE}/assess/${assessmentId}`);

    if (!response.ok) {
        throw new Error('Assessment not found');
    }

    return response.json();
}

/**
 * Download assessment PDF
 */
export function getAssessmentPdfUrl(assessmentId: string): string {
    return `${API_BASE}/assess/${assessmentId}/pdf`;
}

/**
 * List installers with optional filters
 */
export async function listInstallers(minRpi: number = 0): Promise<{ installers: Installer[]; total: number }> {
    const response = await fetch(`${API_BASE}/installers?min_rpi=${minRpi}`);

    if (!response.ok) {
        throw new Error('Failed to fetch installers');
    }

    return response.json();
}

/**
 * Get installer RPI breakdown
 */
export async function getInstallerRpi(installerId: number): Promise<{
    installer_id: number;
    name: string;
    rpi_score: number;
    grade: string;
    components: Record<string, { value: number; weight: number; contribution: number }>;
}> {
    const response = await fetch(`${API_BASE}/installers/${installerId}/rpi`);

    if (!response.ok) {
        throw new Error('Installer not found');
    }

    return response.json();
}

/**
 * Create auction for a job
 */
export async function createAuction(jobId: string, deadlineHours: number = 72): Promise<{
    auction_id: string;
    job_id: string;
    status: string;
    deadline: string;
}> {
    const response = await fetch(`${API_BASE}/auction/create`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ job_id: jobId, deadline_hours: deadlineHours })
    });

    if (!response.ok) {
        const error = await response.json();
        throw new Error(error.detail || 'Failed to create auction');
    }

    return response.json();
}

/**
 * Submit a bid for an auction
 */
export async function submitBid(
    auctionId: string,
    installerId: number,
    priceInr: number,
    timelineDays: number,
    warrantyMonths: number = 12
): Promise<{
    bid_id: string;
    score: number;
    status: string;
}> {
    const response = await fetch(`${API_BASE}/auction/${auctionId}/bid`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
            installer_id: installerId,
            price_inr: priceInr,
            timeline_days: timelineDays,
            warranty_months: warrantyMonths
        })
    });

    if (!response.ok) {
        const error = await response.json();
        throw new Error(error.detail || 'Failed to submit bid');
    }

    return response.json();
}

/**
 * Get auction history with all bids
 */
export async function getAuctionHistory(auctionId: string): Promise<{
    auction_id: string;
    status: string;
    deadline: string;
    bids_count: number;
    bids: Array<{
        bid_id: string;
        installer_name: string;
        installer_rpi: number;
        price_inr: number;
        timeline_days: number;
        score: number;
        status: string;
    }>;
}> {
    const response = await fetch(`${API_BASE}/auction/${auctionId}/history`);

    if (!response.ok) {
        throw new Error('Auction not found');
    }

    return response.json();
}

/**
 * Allocate installers to jobs
 */
export async function allocateJobs(
    jobIds: string[],
    mode: 'gov_optimized' | 'equitable' | 'user_choice',
    forceInstallerId?: number
): Promise<{
    allocations: Array<{
        job_id: string;
        installer_id?: number;
        installer_name?: string;
        allocation_score?: number;
        status?: string;
        error?: string;
    }>;
}> {
    const response = await fetch(`${API_BASE}/allocate`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
            job_ids: jobIds,
            mode,
            force_installer_id: forceInstallerId
        })
    });

    if (!response.ok) {
        throw new Error('Allocation failed');
    }

    return response.json();
}

/**
 * Submit verification photos
 */
export async function submitVerification(
    jobId: string,
    lat: number,
    lng: number,
    photos: File[]
): Promise<VerificationResult> {
    const formData = new FormData();
    formData.append('job_id', jobId);
    formData.append('lat', lat.toString());
    formData.append('lng', lng.toString());
    photos.forEach(photo => formData.append('photos', photo));

    const response = await fetch(`${API_BASE}/verify`, {
        method: 'POST',
        body: formData
    });

    if (!response.ok) {
        const error = await response.json();
        throw new Error(error.detail || 'Verification failed');
    }

    return response.json();
}

/**
 * Verify assessment via QR code
 */
export async function verifyQrCode(code: string): Promise<{
    verified: boolean;
    assessment_id: string;
    site_id: string;
    address: string;
    created_at: string;
    status: string;
    audit_trail: Array<{ timestamp: string; action: string; entity: string }>;
}> {
    const response = await fetch(`${API_BASE}/verify/${code}`);

    if (!response.ok) {
        throw new Error('Invalid verification code');
    }

    return response.json();
}

/**
 * Get telemetry data for a project
 */
export async function getTelemetry(projectId: number, hours: number = 24): Promise<TelemetryData> {
    const response = await fetch(`${API_BASE}/monitoring/${projectId}?hours=${hours}`);

    if (!response.ok) {
        throw new Error('Failed to fetch telemetry');
    }

    return response.json();
}

/**
 * Release escrow milestone
 */
export async function releaseEscrow(
    jobId: string,
    milestoneId: string
): Promise<{
    escrow_id: string;
    milestone_id: string;
    amount_released: number;
    status: string;
}> {
    const response = await fetch(`${API_BASE}/escrow/${jobId}/release`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ milestone_id: milestoneId })
    });

    if (!response.ok) {
        const error = await response.json();
        throw new Error(error.detail || 'Failed to release escrow');
    }

    return response.json();
}

/**
 * Get public dashboard data
 */
export async function getPublicDashboard(state?: string): Promise<{
    summary: {
        total_projects: number;
        total_capture_liters: number;
        total_investment_inr: number;
        co2_avoided_kg: number;
        states_covered: number;
        avg_roi_years: number;
    };
    wards: Array<{
        ward_id: string;
        ward_name: string;
        city: string;
        total_projects: number;
        verified_projects: number;
        total_capture_liters: number;
    }>;
    by_state: Record<string, number>;
}> {
    const url = state
        ? `${API_BASE}/public/dashboard?state=${encodeURIComponent(state)}`
        : `${API_BASE}/public/dashboard`;

    const response = await fetch(url);

    if (!response.ok) {
        throw new Error('Failed to fetch dashboard');
    }

    return response.json();
}

/**
 * Export public data
 */
export function getExportUrl(format: 'csv' | 'geojson'): string {
    return `${API_BASE}/public/export?format=${format}`;
}

/**
 * Health check
 */
export async function healthCheck(): Promise<{
    status: string;
    version: string;
    timestamp: string;
}> {
    const response = await fetch(`${API_BASE}/health`);
    return response.json();
}
