import { useState, useEffect } from 'react';
import './CarbonMarketplace.css';

interface CarbonNFT {
    token_id: string;
    owner_name: string;
    co2_offset_kg: number;
    water_saved_liters: number;
    price_inr: number | null;
    status: string;
    minted_at: string;
}

interface MarketplaceStats {
    total_nfts_minted: number;
    total_co2_offset_kg: number;
    total_traded_volume_inr: number;
    active_listings: number;
}

export default function CarbonMarketplace() {
    const [listings, setListings] = useState<CarbonNFT[]>([]);
    const [myNFTs, setMyNFTs] = useState<CarbonNFT[]>([]);
    const [stats, setStats] = useState<MarketplaceStats | null>(null);
    const [loading, setLoading] = useState(true);
    const [activeTab, setActiveTab] = useState<'marketplace' | 'portfolio' | 'mint'>('marketplace');
    const [selectedNFT, setSelectedNFT] = useState<CarbonNFT | null>(null);

    useEffect(() => {
        loadData();
    }, []);

    const loadData = async () => {
        setLoading(true);
        // Mock data - replace with actual API calls
        setTimeout(() => {
            setListings([
                { token_id: 'RAIN-2026-A1B2C3D4', owner_name: 'Green Housing Society', co2_offset_kg: 150, water_saved_liters: 250000, price_inr: 7500, status: 'for_sale', minted_at: '2026-01-15' },
                { token_id: 'RAIN-2026-E5F6G7H8', owner_name: 'Eco Apartments', co2_offset_kg: 320, water_saved_liters: 520000, price_inr: 16000, status: 'for_sale', minted_at: '2026-01-20' },
                { token_id: 'RAIN-2026-I9J0K1L2', owner_name: 'Tech Park Campus', co2_offset_kg: 890, water_saved_liters: 1450000, price_inr: 44500, status: 'for_sale', minted_at: '2026-01-22' },
            ]);
            setMyNFTs([
                { token_id: 'RAIN-2026-M3N4O5P6', owner_name: 'My Building', co2_offset_kg: 75, water_saved_liters: 125000, price_inr: null, status: 'minted', minted_at: '2026-01-25' },
            ]);
            setStats({
                total_nfts_minted: 127,
                total_co2_offset_kg: 15420,
                total_traded_volume_inr: 1250000,
                active_listings: 23
            });
            setLoading(false);
        }, 500);
    };

    const formatCurrency = (amount: number) => {
        return new Intl.NumberFormat('en-IN', { style: 'currency', currency: 'INR', maximumFractionDigits: 0 }).format(amount);
    };

    const handleBuy = (nft: CarbonNFT) => {
        setSelectedNFT(nft);
    };

    const confirmPurchase = () => {
        if (!selectedNFT) return;
        alert(`Purchase confirmed for ${selectedNFT.token_id}!`);
        setSelectedNFT(null);
        loadData();
    };

    if (loading) {
        return (
            <div className="carbon-loading">
                <div className="spinner"></div>
                <p>Loading Carbon Marketplace...</p>
            </div>
        );
    }

    return (
        <div className="carbon-marketplace">
            <header className="carbon-header">
                <h1>🌱 Carbon Credit Marketplace</h1>
                <p>Trade verified carbon credits from rainwater harvesting</p>
            </header>

            {stats && (
                <div className="carbon-stats">
                    <div className="stat">
                        <span className="stat-value">{stats.total_nfts_minted}</span>
                        <span className="stat-label">NFTs Minted</span>
                    </div>
                    <div className="stat">
                        <span className="stat-value">{(stats.total_co2_offset_kg / 1000).toFixed(1)}t</span>
                        <span className="stat-label">CO₂ Offset</span>
                    </div>
                    <div className="stat">
                        <span className="stat-value">{formatCurrency(stats.total_traded_volume_inr)}</span>
                        <span className="stat-label">Traded Volume</span>
                    </div>
                    <div className="stat">
                        <span className="stat-value">{stats.active_listings}</span>
                        <span className="stat-label">Active Listings</span>
                    </div>
                </div>
            )}

            <div className="tab-bar">
                <button className={activeTab === 'marketplace' ? 'active' : ''} onClick={() => setActiveTab('marketplace')}>
                    🏪 Marketplace
                </button>
                <button className={activeTab === 'portfolio' ? 'active' : ''} onClick={() => setActiveTab('portfolio')}>
                    💼 My Portfolio
                </button>
                <button className={activeTab === 'mint' ? 'active' : ''} onClick={() => setActiveTab('mint')}>
                    ✨ Mint New
                </button>
            </div>

            {activeTab === 'marketplace' && (
                <div className="nft-grid">
                    {listings.map(nft => (
                        <div key={nft.token_id} className="nft-card">
                            <div className="nft-visual">
                                <div className="nft-badge">🌿</div>
                                <div className="nft-amount">{nft.co2_offset_kg} kg</div>
                                <div className="nft-label">CO₂ Offset</div>
                            </div>
                            <div className="nft-details">
                                <h3>{nft.token_id}</h3>
                                <p className="nft-owner">by {nft.owner_name}</p>
                                <div className="nft-meta">
                                    <span>💧 {(nft.water_saved_liters / 1000).toFixed(0)} kL saved</span>
                                </div>
                                <div className="nft-price">{formatCurrency(nft.price_inr!)}</div>
                                <button className="buy-btn" onClick={() => handleBuy(nft)}>Buy Now</button>
                            </div>
                        </div>
                    ))}
                </div>
            )}

            {activeTab === 'portfolio' && (
                <div className="portfolio-section">
                    <h2>Your Carbon Credits</h2>
                    {myNFTs.length === 0 ? (
                        <div className="empty-state">
                            <p>You don't have any carbon credits yet.</p>
                            <button onClick={() => setActiveTab('mint')}>Mint Your First NFT</button>
                        </div>
                    ) : (
                        <div className="nft-grid">
                            {myNFTs.map(nft => (
                                <div key={nft.token_id} className="nft-card owned">
                                    <div className="nft-visual">
                                        <div className="nft-badge">🌿</div>
                                        <div className="nft-amount">{nft.co2_offset_kg} kg</div>
                                        <div className="nft-label">CO₂ Offset</div>
                                    </div>
                                    <div className="nft-details">
                                        <h3>{nft.token_id}</h3>
                                        <span className={`status-badge ${nft.status}`}>{nft.status}</span>
                                        <div className="nft-meta">
                                            <span>💧 {(nft.water_saved_liters / 1000).toFixed(0)} kL saved</span>
                                        </div>
                                        <div className="nft-actions">
                                            <button className="action-btn">List for Sale</button>
                                            <button className="action-btn secondary">Retire</button>
                                        </div>
                                    </div>
                                </div>
                            ))}
                        </div>
                    )}
                </div>
            )}

            {activeTab === 'mint' && (
                <div className="mint-section">
                    <h2>Mint New Carbon Credit</h2>
                    <p>Create a verified carbon credit NFT from your RWH installation</p>
                    <form className="mint-form" onSubmit={e => { e.preventDefault(); alert('NFT minted!'); }}>
                        <div className="form-group">
                            <label>Project Name</label>
                            <input type="text" placeholder="e.g., Green Residency RWH" required />
                        </div>
                        <div className="form-row">
                            <div className="form-group">
                                <label>CO₂ Offset (kg)</label>
                                <input type="number" placeholder="150" required />
                            </div>
                            <div className="form-group">
                                <label>Water Saved (liters)</label>
                                <input type="number" placeholder="250000" required />
                            </div>
                        </div>
                        <div className="form-group">
                            <label>Verification Document</label>
                            <input type="file" accept=".pdf,.jpg,.png" />
                        </div>
                        <button type="submit" className="mint-btn">🌱 Mint Carbon Credit NFT</button>
                    </form>
                </div>
            )}

            {selectedNFT && (
                <div className="modal-overlay" onClick={() => setSelectedNFT(null)}>
                    <div className="modal" onClick={e => e.stopPropagation()}>
                        <h3>Confirm Purchase</h3>
                        <div className="purchase-details">
                            <p><strong>Token:</strong> {selectedNFT.token_id}</p>
                            <p><strong>CO₂ Offset:</strong> {selectedNFT.co2_offset_kg} kg</p>
                            <p><strong>Seller:</strong> {selectedNFT.owner_name}</p>
                            <p className="purchase-price">{formatCurrency(selectedNFT.price_inr!)}</p>
                        </div>
                        <div className="modal-actions">
                            <button className="cancel" onClick={() => setSelectedNFT(null)}>Cancel</button>
                            <button className="confirm" onClick={confirmPurchase}>Confirm Purchase</button>
                        </div>
                    </div>
                </div>
            )}
        </div>
    );
}
