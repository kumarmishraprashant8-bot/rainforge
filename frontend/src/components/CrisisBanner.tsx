import { useState, useEffect } from 'react';
import { AlertTriangle, X } from 'lucide-react';
import API_BASE_URL from '../config/api';

interface CrisisAlert {
  active: boolean;
  title?: string;
  message?: string;
  severity?: 'info' | 'warning' | 'critical';
}

const CrisisBanner = () => {
  const [alert, setAlert] = useState<CrisisAlert | null>(null);
  const [dismissed, setDismissed] = useState(false);

  useEffect(() => {
    fetch(`${API_BASE_URL}/api/v1/success/crisis`)
      .then((res) => res.json())
      .then((data) => setAlert(data))
      .catch(() => setAlert(null));
  }, []);

  if (!alert?.active || dismissed) return null;

  const severityStyles = {
    info: 'bg-blue-500/20 border-blue-500/40 text-blue-200',
    warning: 'bg-amber-500/20 border-amber-500/40 text-amber-200',
    critical: 'bg-red-500/20 border-red-500/40 text-red-200',
  };
  const style = severityStyles[alert.severity || 'info'];

  return (
    <div className={`sticky top-0 z-[60] border-b ${style} px-4 py-2.5 flex items-center justify-between gap-4`}>
      <div className="flex items-center gap-2 min-w-0">
        <AlertTriangle className="flex-shrink-0" size={18} />
        <span className="font-semibold truncate">{alert.title}</span>
        <span className="hidden sm:inline truncate text-sm opacity-90">{alert.message}</span>
      </div>
      <button
        onClick={() => setDismissed(true)}
        className="p-1 rounded hover:bg-white/10 transition-colors flex-shrink-0"
        aria-label="Dismiss"
      >
        <X size={18} />
      </button>
    </div>
  );
};

export default CrisisBanner;
