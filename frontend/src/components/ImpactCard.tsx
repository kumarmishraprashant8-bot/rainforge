import { Share2, Award, Droplets } from 'lucide-react';

interface ImpactCardProps {
  waterSecurityIndex?: number;
  waterCredits?: number;
  annualYieldLiters?: number;
  equivalentShowers?: number;
  shareMessage?: string;
  badges?: Array<{ id: string; name: string; description: string }>;
}

const ImpactCard = ({
  waterSecurityIndex,
  waterCredits,
  annualYieldLiters,
  equivalentShowers,
  shareMessage,
  badges = [],
}: ImpactCardProps) => {
  const handleShare = () => {
    const text = shareMessage || `I'm harvesting rainwater with RainForge. ${annualYieldLiters ? `${(annualYieldLiters / 1000).toFixed(0)}k L/year potential.` : ''} Join the movement.`;
    const url = window.location.origin;
    if (navigator.share) {
      navigator.share({
        title: 'RainForge – My water impact',
        text,
        url,
      }).catch(() => {
        navigator.clipboard?.writeText(`${text}\n${url}`);
      });
    } else {
      navigator.clipboard?.writeText(`${text}\n${url}`);
    }
  };

  return (
    <div className="glass rounded-2xl p-6 border border-cyan-500/20">
      <h3 className="text-lg font-bold text-white mb-4 flex items-center gap-2">
        <Droplets className="text-cyan-400" size={20} />
        Your impact
      </h3>
      <div className="grid grid-cols-2 sm:grid-cols-4 gap-4 mb-4">
        {waterSecurityIndex != null && (
          <div className="text-center p-3 rounded-xl bg-white/5">
            <div className="text-2xl font-black text-cyan-400">{waterSecurityIndex}</div>
            <div className="text-xs text-gray-400">Water Security Index</div>
          </div>
        )}
        {waterCredits != null && (
          <div className="text-center p-3 rounded-xl bg-white/5">
            <div className="text-2xl font-black text-emerald-400">{waterCredits}</div>
            <div className="text-xs text-gray-400">Water credits</div>
          </div>
        )}
        {equivalentShowers != null && (
          <div className="text-center p-3 rounded-xl bg-white/5">
            <div className="text-2xl font-black text-blue-400">{equivalentShowers.toLocaleString()}</div>
            <div className="text-xs text-gray-400">Showers equiv./yr</div>
          </div>
        )}
        {annualYieldLiters != null && (
          <div className="text-center p-3 rounded-xl bg-white/5">
            <div className="text-2xl font-black text-white">{(annualYieldLiters / 1000).toFixed(0)}k</div>
            <div className="text-xs text-gray-400">Liters/year</div>
          </div>
        )}
      </div>
      {badges.length > 0 && (
        <div className="flex flex-wrap gap-2 mb-4">
          {badges.map((b) => (
            <span
              key={b.id}
              className="inline-flex items-center gap-1 px-2.5 py-1 rounded-lg bg-amber-500/20 text-amber-200 text-xs"
            >
              <Award size={12} />
              {b.name}
            </span>
          ))}
        </div>
      )}
      <button
        onClick={handleShare}
        className="w-full flex items-center justify-center gap-2 py-2.5 rounded-xl bg-cyan-500/20 text-cyan-300 hover:bg-cyan-500/30 font-medium transition-colors"
      >
        <Share2 size={18} />
        Share my impact
      </button>
    </div>
  );
};

export default ImpactCard;
