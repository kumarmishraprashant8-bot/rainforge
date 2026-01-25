import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import Layout from './layouts/Layout';
import LandingPage from './pages/LandingPage';
import IntakePage from './features/intake/IntakePage';
import AssessPage from './features/assess/AssessPage';
import MarketplacePage from './features/marketplace/MarketplacePage';
import BulkUploadPage from './features/bulk/BulkUploadPage';
import MonitoringPage from './features/monitoring/MonitoringPage';
import VerificationPage from './features/verification/VerificationPage';
import PortfolioDashboard from './features/portfolio/PortfolioDashboard';
import PublicDashboard from './features/public/PublicDashboard';

const App = () => {
  return (
    <Router>
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
        </Route>
      </Routes>
    </Router>
  );
};

export default App;

