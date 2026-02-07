/**
 * Certificate Generator
 * Generate and download PDF certificates
 */

import { Download, Award, Share2 } from 'lucide-react';

interface CertificateData {
    userName: string;
    waterSaved: number;
    co2Offset: number;
    date: string;
    certificateId: string;
}

interface CertificateGeneratorProps {
    data: CertificateData;
    onShare?: () => void;
}

const CertificateGenerator = ({ data, onShare }: CertificateGeneratorProps) => {

    const generateCertificatePDF = () => {
        const certificateHTML = `
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>RainForge Water Conservation Certificate</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body { 
            font-family: 'Georgia', serif;
            background: linear-gradient(135deg, #1e3a5f 0%, #0f172a 100%);
            min-height: 100vh;
            display: flex;
            justify-content: center;
            align-items: center;
            padding: 20px;
        }
        .certificate {
            background: linear-gradient(180deg, #fefefe 0%, #f8f4e8 100%);
            width: 800px;
            padding: 60px;
            border: 8px double #d4af37;
            box-shadow: 0 20px 60px rgba(0,0,0,0.5);
            position: relative;
        }
        .certificate::before {
            content: '';
            position: absolute;
            top: 20px;
            left: 20px;
            right: 20px;
            bottom: 20px;
            border: 2px solid #d4af37;
            pointer-events: none;
        }
        .header {
            text-align: center;
            margin-bottom: 30px;
        }
        .logo {
            font-size: 28px;
            color: #1e3a5f;
            font-weight: bold;
            margin-bottom: 10px;
        }
        .logo span { color: #06b6d4; }
        .title {
            font-size: 42px;
            color: #1e3a5f;
            text-transform: uppercase;
            letter-spacing: 8px;
            margin: 20px 0;
        }
        .subtitle {
            font-size: 18px;
            color: #666;
            font-style: italic;
        }
        .recipient {
            text-align: center;
            margin: 40px 0;
        }
        .recipient-label {
            font-size: 16px;
            color: #666;
            margin-bottom: 10px;
        }
        .recipient-name {
            font-size: 36px;
            color: #1e3a5f;
            font-family: 'Brush Script MT', cursive;
            border-bottom: 2px solid #d4af37;
            display: inline-block;
            padding: 0 40px 10px;
        }
        .achievement {
            text-align: center;
            margin: 30px 0;
            font-size: 18px;
            color: #444;
            line-height: 1.8;
        }
        .stats {
            display: flex;
            justify-content: center;
            gap: 60px;
            margin: 40px 0;
        }
        .stat {
            text-align: center;
        }
        .stat-value {
            font-size: 32px;
            color: #06b6d4;
            font-weight: bold;
        }
        .stat-label {
            font-size: 14px;
            color: #666;
            margin-top: 5px;
        }
        .footer {
            display: flex;
            justify-content: space-between;
            margin-top: 50px;
            padding-top: 30px;
        }
        .signature {
            text-align: center;
        }
        .signature-line {
            width: 200px;
            border-top: 1px solid #333;
            margin-bottom: 5px;
        }
        .signature-name {
            font-size: 14px;
            color: #666;
        }
        .cert-id {
            position: absolute;
            bottom: 30px;
            right: 40px;
            font-size: 10px;
            color: #999;
        }
        .seal {
            position: absolute;
            bottom: 80px;
            right: 60px;
            width: 100px;
            height: 100px;
            border: 3px solid #d4af37;
            border-radius: 50%;
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 12px;
            color: #d4af37;
            text-align: center;
            font-weight: bold;
        }
    </style>
</head>
<body>
    <div class="certificate">
        <div class="header">
            <div class="logo">🌧️ Rain<span>Forge</span></div>
            <div class="title">Certificate</div>
            <div class="subtitle">of Water Conservation Achievement</div>
        </div>
        
        <div class="recipient">
            <div class="recipient-label">This is to certify that</div>
            <div class="recipient-name">${data.userName}</div>
        </div>
        
        <div class="achievement">
            has demonstrated exceptional commitment to water conservation<br>
            through the implementation of rainwater harvesting solutions,<br>
            contributing to a sustainable future for our planet.
        </div>
        
        <div class="stats">
            <div class="stat">
                <div class="stat-value">${(data.waterSaved / 1000).toFixed(0)}k L</div>
                <div class="stat-label">Water Saved</div>
            </div>
            <div class="stat">
                <div class="stat-value">${data.co2Offset} kg</div>
                <div class="stat-label">CO₂ Offset</div>
            </div>
        </div>
        
        <div class="footer">
            <div class="signature">
                <div class="signature-line"></div>
                <div class="signature-name">Date: ${data.date}</div>
            </div>
            <div class="signature">
                <div class="signature-line"></div>
                <div class="signature-name">RainForge Team</div>
            </div>
        </div>
        
        <div class="seal">VERIFIED<br>✓</div>
        <div class="cert-id">Certificate ID: ${data.certificateId}</div>
    </div>
</body>
</html>`;

        const printWindow = window.open('', '_blank');
        if (printWindow) {
            printWindow.document.write(certificateHTML);
            printWindow.document.close();
            setTimeout(() => {
                printWindow.print();
            }, 500);
        }
    };

    return (
        <div className="glass rounded-2xl p-6 bg-gradient-to-r from-amber-500/10 to-yellow-500/10 border border-amber-500/20">
            <div className="flex items-center gap-4 mb-4">
                <div className="p-3 bg-gradient-to-r from-amber-500 to-yellow-500 rounded-xl">
                    <Award className="text-white" size={28} />
                </div>
                <div>
                    <h3 className="text-xl font-bold text-white">Your Certificate</h3>
                    <p className="text-gray-400 text-sm">Download your water conservation achievement</p>
                </div>
            </div>

            {/* Preview */}
            <div className="bg-gradient-to-br from-slate-800 to-slate-900 rounded-xl p-6 mb-4 border border-white/10">
                <div className="text-center">
                    <div className="text-amber-400 text-sm mb-2">Certificate of Achievement</div>
                    <div className="text-white text-xl font-bold mb-4">{data.userName}</div>
                    <div className="flex justify-center gap-8">
                        <div>
                            <div className="text-cyan-400 text-2xl font-bold">{(data.waterSaved / 1000).toFixed(0)}k L</div>
                            <div className="text-gray-500 text-xs">Saved</div>
                        </div>
                        <div>
                            <div className="text-green-400 text-2xl font-bold">{data.co2Offset} kg</div>
                            <div className="text-gray-500 text-xs">CO₂ Offset</div>
                        </div>
                    </div>
                </div>
            </div>

            {/* Actions */}
            <div className="flex gap-3">
                <button
                    onClick={generateCertificatePDF}
                    className="flex-1 flex items-center justify-center gap-2 py-3 bg-gradient-to-r from-amber-500 to-yellow-500 text-black font-bold rounded-xl hover:opacity-90 transition-opacity"
                >
                    <Download size={18} />
                    Download PDF
                </button>
                {onShare && (
                    <button
                        onClick={onShare}
                        className="px-4 py-3 bg-white/10 text-white rounded-xl hover:bg-white/20 transition-colors"
                    >
                        <Share2 size={18} />
                    </button>
                )}
            </div>
        </div>
    );
};

export default CertificateGenerator;
