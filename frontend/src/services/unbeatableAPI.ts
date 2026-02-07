/**
 * Unbeatable Platform API Service
 * Frontend API client for all new features
 */

import axios from 'axios';

const API_BASE = import.meta.env.VITE_API_URL || 'http://localhost:8000/api/v1';
const api = axios.create({ baseURL: API_BASE });

// ==================== INDIA STACK ====================

export const indiaStackAPI = {
  // Aadhaar
  sendAadhaarOTP: (aadhaarNumber: string, userId: string) =>
    api.post('/india-stack/aadhaar/send-otp', { aadhaar_number: aadhaarNumber, user_id: userId }),
  
  verifyAadhaarOTP: (txnId: string, otp: string) =>
    api.post('/india-stack/aadhaar/verify-otp', { txn_id: txnId, otp }),
  
  getVerificationStatus: (userId: string) =>
    api.get(`/india-stack/aadhaar/status/${userId}`),
  
  // DigiLocker
  initiateDigiLocker: (userId: string, redirectUri: string) =>
    api.post('/india-stack/digilocker/auth', { user_id: userId, redirect_uri: redirectUri }),
  
  getDigiLockerDocuments: (userId: string) =>
    api.get(`/india-stack/digilocker/documents/${userId}`),
  
  extractPropertyData: (userId: string) =>
    api.get(`/india-stack/digilocker/extract/${userId}`),
  
  // DBT
  registerBeneficiary: (data: any) =>
    api.post('/india-stack/dbt/register', data),
  
  checkSubsidyEligibility: (userId: string, projectCost: number, propertyType: string, cityTier: string) =>
    api.post('/india-stack/dbt/check-eligibility', {
      user_id: userId, project_cost: projectCost,
      property_type: propertyType, city_tier: cityTier
    }),
  
  initiateDbtPayment: (beneficiaryId: string, scheme: string, amount: number, purpose: string) =>
    api.post('/india-stack/dbt/initiate', {
      beneficiary_id: beneficiaryId, scheme, amount, purpose
    }),
  
  getDbtStatus: (transactionId: string) =>
    api.get(`/india-stack/dbt/status/${transactionId}`),
  
  getUserTransactions: (userId: string) =>
    api.get(`/india-stack/dbt/transactions/${userId}`)
};

// ==================== AI COPILOT ====================

export const copilotAPI = {
  chat: (userId: string, message: string, sessionId?: string, context?: any) =>
    api.post('/copilot/chat', { user_id: userId, message, session_id: sessionId, context }),
  
  parseDocument: (userId: string, file: File, documentType?: string) => {
    const formData = new FormData();
    formData.append('file', file);
    formData.append('user_id', userId);
    formData.append('document_name', file.name);
    if (documentType) formData.append('document_type', documentType);
    return api.post('/copilot/parse-document', formData);
  },
  
  getRecommendations: (userId: string, projectId?: number) =>
    api.get(`/copilot/recommendations/${userId}`, { params: { project_id: projectId } })
};

// ==================== FINANCIAL SERVICES ====================

export const financeAPI = {
  // Credit
  checkLoanEligibility: (userId: string, amount: number, monthlyIncome: number) =>
    api.post('/finance/credit/check-eligibility', {
      user_id: userId, requested_amount: amount, monthly_income: monthlyIncome
    }),
  
  applyForLoan: (userId: string, partner: string, amount: number, tenure: number) =>
    api.post('/finance/credit/apply', {
      user_id: userId, partner, amount, tenure_months: tenure
    }),
  
  getLoanDashboard: (userId: string) =>
    api.get(`/finance/credit/dashboard/${userId}`),
  
  // Insurance
  getInsuranceQuotes: (projectId: string, coverageAmount: number) =>
    api.post('/finance/insurance/quotes', { project_id: projectId, coverage_amount: coverageAmount }),
  
  purchaseInsurance: (userId: string, projectId: string, insuranceType: string, coverage: number) =>
    api.post('/finance/insurance/purchase', {
      user_id: userId, project_id: projectId, insurance_type: insuranceType, coverage
    }),
  
  fileClaim: (policyId: string, claimType: string, amount: number, description: string) =>
    api.post('/finance/insurance/claim', {
      policy_id: policyId, claim_type: claimType, amount, description
    })
};

// ==================== ACADEMY ====================

export const academyAPI = {
  getCourses: (level?: string) =>
    api.get('/academy/courses', { params: { level } }),
  
  getCourseDetails: (courseId: string) =>
    api.get(`/academy/courses/${courseId}`),
  
  enroll: (userId: string, courseId: string) =>
    api.post('/academy/enroll', { user_id: userId, course_id: courseId }),
  
  updateProgress: (enrollmentId: string, moduleId: string, quizScore?: number) =>
    api.post('/academy/progress', { enrollment_id: enrollmentId, module_id: moduleId, quiz_score: quizScore }),
  
  submitExam: (userId: string, courseId: string, answers: any[]) =>
    api.post('/academy/exam', { user_id: userId, course_id: courseId, answers }),
  
  getCertifications: (userId: string) =>
    api.get(`/academy/certifications/${userId}`),
  
  verifyCertification: (certId: string) =>
    api.get(`/academy/verify/${certId}`)
};

// ==================== SUSTAINABILITY ====================

export const sustainabilityAPI = {
  // Water Credits
  issueCredits: (userId: string, projectId: string, waterSaved: number) =>
    api.post('/sustainability/water-credits/issue', {
      user_id: userId, project_id: projectId, water_saved_liters: waterSaved
    }),
  
  listCreditsForSale: (creditId: string, userId: string, pricePerUnit: number) =>
    api.post('/sustainability/water-credits/list', {
      credit_id: creditId, user_id: userId, price_per_unit: pricePerUnit
    }),
  
  buyCredits: (orderId: string, buyerId: string) =>
    api.post('/sustainability/water-credits/buy', { order_id: orderId, buyer_id: buyerId }),
  
  retireCredits: (creditId: string, userId: string, reason: string) =>
    api.post('/sustainability/water-credits/retire', {
      credit_id: creditId, user_id: userId, reason
    }),
  
  getMarketplace: (minUnits = 0, maxPrice = 1000) =>
    api.get('/sustainability/water-credits/marketplace', { params: { min_units: minUnits, max_price: maxPrice } }),
  
  getPortfolio: (userId: string) =>
    api.get(`/sustainability/water-credits/portfolio/${userId}`),
  
  // CSR
  createCampaign: (data: any) =>
    api.post('/sustainability/csr/campaigns', data),
  
  makeDonation: (campaignId: string, corporateId: string, amount: number) =>
    api.post('/sustainability/csr/donate', { campaign_id: campaignId, corporate_id: corporateId, amount }),
  
  getCampaignDashboard: (campaignId: string) =>
    api.get(`/sustainability/csr/campaigns/${campaignId}`),
  
  getPublicCampaigns: () =>
    api.get('/sustainability/csr/campaigns'),
  
  getImpactReport: (campaignId: string) =>
    api.get(`/sustainability/csr/report/${campaignId}`)
};

export default {
  indiaStack: indiaStackAPI,
  copilot: copilotAPI,
  finance: financeAPI,
  academy: academyAPI,
  sustainability: sustainabilityAPI
};
