import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import { Suspense, lazy } from 'react';
import { ErrorBoundary } from './components/ErrorBoundary';
import { ToastProvider } from './components/ToastProvider';
import { ThemeProvider } from './components/ThemeToggle';
import { CommandPalette } from './components/CommandPalette';
import { OfflineIndicator } from './components/OfflineIndicator';
import { PWAInstallPrompt } from './components/PWAInstallPrompt';
import { AuthProvider } from './context/AuthContext';
import { Droplets } from 'lucide-react';

// Lazy load all page components for better performance
const Layout = lazy(() => import('./layouts/Layout'));
const LandingPage = lazy(() => import('./pages/LandingPage'));
const NotFoundPage = lazy(() => import('./pages/NotFoundPage'));
const IntakePage = lazy(() => import('./features/intake/IntakePage'));
const AssessPage = lazy(() => import('./features/assess/AssessPage'));
const MarketplacePage = lazy(() => import('./features/marketplace/MarketplacePage'));
const BulkUploadPage = lazy(() => import('./features/bulk/BulkUploadPage'));
const MonitoringPage = lazy(() => import('./features/monitoring/MonitoringPage'));
const VerificationPage = lazy(() => import('./features/verification/VerificationPage'));
const PortfolioDashboard = lazy(() => import('./features/portfolio/PortfolioDashboard'));
const PublicDashboard = lazy(() => import('./features/public/PublicDashboard'));
// Existing Feature Pages
const ARTankPlacement = lazy(() => import('./features/ar/ARTankPlacement'));
const CommunityMap = lazy(() => import('./features/community/CommunityMap'));
const CarbonMarketplace = lazy(() => import('./features/carbon/CarbonMarketplace'));
const VideoTutorials = lazy(() => import('./features/tutorials/VideoTutorials'));
// NEW Beast Mode Feature Pages
const ProfilePage = lazy(() => import('./features/profile/ProfilePage'));
const IoTDashboard = lazy(() => import('./features/iot/IoTDashboard'));
const CommunityPage = lazy(() => import('./features/community/CommunityPage'));
const InstallerBookingPage = lazy(() => import('./features/booking/InstallerBookingPage'));
const HelpCenterPage = lazy(() => import('./features/help/HelpCenterPage'));
const ImpactTrackerPage = lazy(() => import('./features/impact/ImpactTrackerPage'));
const ProjectHistoryPage = lazy(() => import('./features/history/ProjectHistoryPage'));
const UserDashboard = lazy(() => import('./features/dashboard/UserDashboard'));

// Beautiful loading fallback
const LoadingFallback = () => (
  <div className="min-h-screen flex items-center justify-center bg-slate-900">
    <div className="text-center">
      <div className="relative">
        <Droplets className="w-16 h-16 text-cyan-400 animate-bounce mx-auto" />
        <div className="absolute inset-0 flex items-center justify-center">
          <div className="w-20 h-20 rounded-full border-4 border-cyan-400/30 border-t-cyan-400 animate-spin" />
        </div>
      </div>
      <p className="mt-6 text-gray-400 animate-pulse">Loading RainForge...</p>
    </div>
  </div>
);

const App = () => {
  return (
    <ErrorBoundary>
      <AuthProvider>
        <ThemeProvider>
          <ToastProvider>
            <Router>
              {/* Global Components */}
              <OfflineIndicator />
              <CommandPalette />
              <PWAInstallPrompt />

              <Suspense fallback={<LoadingFallback />}>
                <Routes>
                  {/* Public Landing */}
                  <Route path="/" element={<LandingPage />} />

                  {/* Public Transparency Dashboard */}
                  <Route path="/public" element={<PublicDashboard />} />
                  <Route path="/public/ward/:wardId" element={<PublicDashboard />} />

                  {/* Main App with Layout */}
                  <Route element={<Layout />}>
                    <Route path="/intake" element={<IntakePage />} />
                    <Route path="/assess/:projectId" element={<AssessPage />} />
                    <Route path="/marketplace" element={<MarketplacePage />} />

                    {/* Government Platform Features */}
                    <Route path="/bulk" element={<BulkUploadPage />} />
                    <Route path="/monitoring" element={<MonitoringPage />} />
                    <Route path="/verification" element={<VerificationPage />} />
                    <Route path="/portfolio" element={<PortfolioDashboard />} />

                    {/* New Advanced Features */}
                    <Route path="/ar" element={<ARTankPlacement />} />
                    <Route path="/community-map" element={<CommunityMap />} />
                    <Route path="/carbon" element={<CarbonMarketplace />} />
                    <Route path="/tutorials" element={<VideoTutorials />} />

                    {/* BEAST MODE Features */}
                    <Route path="/profile" element={<ProfilePage />} />
                    <Route path="/iot" element={<IoTDashboard />} />
                    <Route path="/community" element={<CommunityPage />} />
                    <Route path="/book-installer" element={<InstallerBookingPage />} />
                    <Route path="/help" element={<HelpCenterPage />} />
                    <Route path="/impact" element={<ImpactTrackerPage />} />
                    <Route path="/history" element={<ProjectHistoryPage />} />
                    <Route path="/dashboard" element={<UserDashboard />} />
                  </Route>

                  {/* 404 Catch-all */}
                  <Route path="*" element={<NotFoundPage />} />
                </Routes>
              </Suspense>
            </Router>
          </ToastProvider>
        </ThemeProvider>
      </AuthProvider>
    </ErrorBoundary>
  );
};

export default App;
