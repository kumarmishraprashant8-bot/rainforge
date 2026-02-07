/**
 * Embeddable Water Calculator Widget
 * Can be embedded on any website
 */

(function () {
    'use strict';

    // Widget configuration
    const CONFIG = {
        apiUrl: 'https://rainforge.gov.in/api/v1',
        defaultRainfall: 800, // mm
        runoffCoeff: 0.85,
        colors: {
            primary: '#0ea5e9',
            secondary: '#7c3aed',
            success: '#22c55e',
            background: '#f8fafc',
            text: '#1e293b',
            muted: '#64748b'
        }
    };

    // Widget styles
    const STYLES = `
    .rainforge-widget {
      font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
      max-width: 400px;
      background: linear-gradient(135deg, ${CONFIG.colors.background} 0%, #fff 100%);
      border-radius: 16px;
      box-shadow: 0 10px 40px rgba(0,0,0,0.1);
      overflow: hidden;
    }

    .rainforge-widget * {
      box-sizing: border-box;
      margin: 0;
      padding: 0;
    }

    .rainforge-header {
      background: linear-gradient(135deg, ${CONFIG.colors.primary} 0%, ${CONFIG.colors.secondary} 100%);
      color: white;
      padding: 20px;
      text-align: center;
    }

    .rainforge-header h3 {
      font-size: 18px;
      font-weight: 600;
      margin-bottom: 4px;
    }

    .rainforge-header p {
      font-size: 12px;
      opacity: 0.9;
    }

    .rainforge-body {
      padding: 20px;
    }

    .rainforge-input-group {
      margin-bottom: 16px;
    }

    .rainforge-input-group label {
      display: block;
      font-size: 13px;
      font-weight: 500;
      color: ${CONFIG.colors.text};
      margin-bottom: 6px;
    }

    .rainforge-input-group input,
    .rainforge-input-group select {
      width: 100%;
      padding: 12px;
      border: 2px solid #e2e8f0;
      border-radius: 8px;
      font-size: 14px;
      transition: border-color 0.2s;
    }

    .rainforge-input-group input:focus,
    .rainforge-input-group select:focus {
      outline: none;
      border-color: ${CONFIG.colors.primary};
    }

    .rainforge-button {
      width: 100%;
      padding: 14px;
      background: linear-gradient(135deg, ${CONFIG.colors.primary} 0%, ${CONFIG.colors.secondary} 100%);
      color: white;
      border: none;
      border-radius: 8px;
      font-size: 15px;
      font-weight: 600;
      cursor: pointer;
      transition: transform 0.2s, box-shadow 0.2s;
    }

    .rainforge-button:hover {
      transform: translateY(-2px);
      box-shadow: 0 4px 12px rgba(14, 165, 233, 0.4);
    }

    .rainforge-button:active {
      transform: translateY(0);
    }

    .rainforge-results {
      display: none;
      margin-top: 20px;
      padding-top: 20px;
      border-top: 1px solid #e2e8f0;
    }

    .rainforge-results.show {
      display: block;
      animation: fadeIn 0.3s ease;
    }

    @keyframes fadeIn {
      from { opacity: 0; transform: translateY(10px); }
      to { opacity: 1; transform: translateY(0); }
    }

    .rainforge-result-card {
      display: flex;
      align-items: center;
      padding: 12px;
      background: white;
      border-radius: 10px;
      margin-bottom: 10px;
      box-shadow: 0 2px 8px rgba(0,0,0,0.05);
    }

    .rainforge-result-icon {
      width: 40px;
      height: 40px;
      display: flex;
      align-items: center;
      justify-content: center;
      border-radius: 10px;
      font-size: 20px;
      margin-right: 12px;
    }

    .rainforge-result-icon.water {
      background: linear-gradient(135deg, #e0f2fe, #bae6fd);
    }

    .rainforge-result-icon.tank {
      background: linear-gradient(135deg, #f0fdf4, #bbf7d0);
    }

    .rainforge-result-icon.money {
      background: linear-gradient(135deg, #fef3c7, #fde68a);
    }

    .rainforge-result-icon.eco {
      background: linear-gradient(135deg, #ecfdf5, #a7f3d0);
    }

    .rainforge-result-content {
      flex: 1;
    }

    .rainforge-result-label {
      font-size: 12px;
      color: ${CONFIG.colors.muted};
    }

    .rainforge-result-value {
      font-size: 18px;
      font-weight: 700;
      color: ${CONFIG.colors.text};
    }

    .rainforge-cta {
      display: block;
      text-align: center;
      margin-top: 16px;
      padding: 12px;
      background: linear-gradient(135deg, ${CONFIG.colors.success} 0%, #16a34a 100%);
      color: white;
      text-decoration: none;
      border-radius: 8px;
      font-weight: 600;
      font-size: 14px;
    }

    .rainforge-footer {
      text-align: center;
      padding: 12px;
      background: #f1f5f9;
      font-size: 11px;
      color: ${CONFIG.colors.muted};
    }

    .rainforge-footer a {
      color: ${CONFIG.colors.primary};
      text-decoration: none;
    }
  `;

    // Widget HTML
    const TEMPLATE = `
    <div class="rainforge-widget" id="rainforge-widget">
      <div class="rainforge-header">
        <h3>🌧️ Rainwater Calculator</h3>
        <p>Estimate your harvesting potential</p>
      </div>

      <div class="rainforge-body">
        <div class="rainforge-input-group">
          <label>Roof Area</label>
          <input type="number" id="rf-roof-area" placeholder="e.g., 100" min="10" max="10000">
        </div>

        <div class="rainforge-input-group">
          <label>Unit</label>
          <select id="rf-unit">
            <option value="sqm">Square Meters (sq.m)</option>
            <option value="sqft">Square Feet (sq.ft)</option>
          </select>
        </div>

        <div class="rainforge-input-group">
          <label>City (Optional)</label>
          <select id="rf-city">
            <option value="">Select city</option>
            <option value="mumbai">Mumbai</option>
            <option value="delhi">Delhi</option>
            <option value="bangalore">Bengaluru</option>
            <option value="chennai">Chennai</option>
            <option value="kolkata">Kolkata</option>
            <option value="hyderabad">Hyderabad</option>
            <option value="pune">Pune</option>
            <option value="ahmedabad">Ahmedabad</option>
            <option value="jaipur">Jaipur</option>
            <option value="lucknow">Lucknow</option>
          </select>
        </div>

        <button class="rainforge-button" id="rf-calculate">
          Calculate Potential
        </button>

        <div class="rainforge-results" id="rf-results">
          <div class="rainforge-result-card">
            <div class="rainforge-result-icon water">💧</div>
            <div class="rainforge-result-content">
              <div class="rainforge-result-label">Yearly Collection</div>
              <div class="rainforge-result-value" id="rf-yield">--</div>
            </div>
          </div>

          <div class="rainforge-result-card">
            <div class="rainforge-result-icon tank">🛢️</div>
            <div class="rainforge-result-content">
              <div class="rainforge-result-label">Recommended Tank</div>
              <div class="rainforge-result-value" id="rf-tank">--</div>
            </div>
          </div>

          <div class="rainforge-result-card">
            <div class="rainforge-result-icon money">💰</div>
            <div class="rainforge-result-content">
              <div class="rainforge-result-label">Yearly Savings</div>
              <div class="rainforge-result-value" id="rf-savings">--</div>
            </div>
          </div>

          <div class="rainforge-result-card">
            <div class="rainforge-result-icon eco">🌱</div>
            <div class="rainforge-result-content">
              <div class="rainforge-result-label">CO₂ Offset</div>
              <div class="rainforge-result-value" id="rf-carbon">--</div>
            </div>
          </div>

          <a href="https://rainforge.gov.in/register" class="rainforge-cta" target="_blank">
            Get Full Assessment →
          </a>
        </div>
      </div>

      <div class="rainforge-footer">
        Powered by <a href="https://rainforge.gov.in" target="_blank">RainForge</a> | Jal Shakti Ministry
      </div>
    </div>
  `;

    // City rainfall data (mm/year)
    const CITY_RAINFALL = {
        mumbai: 2200,
        delhi: 800,
        bangalore: 900,
        chennai: 1400,
        kolkata: 1600,
        hyderabad: 800,
        pune: 700,
        ahmedabad: 800,
        jaipur: 600,
        lucknow: 900
    };

    // Initialize widget
    function init() {
        // Inject styles
        const styleEl = document.createElement('style');
        styleEl.textContent = STYLES;
        document.head.appendChild(styleEl);

        // Find container
        const container = document.querySelector('[data-rainforge-widget]') ||
            document.getElementById('rainforge-calculator');

        if (!container) {
            console.warn('RainForge: No widget container found');
            return;
        }

        // Inject HTML
        container.innerHTML = TEMPLATE;

        // Bind events
        const calculateBtn = document.getElementById('rf-calculate');
        calculateBtn.addEventListener('click', calculate);

        // Enter key support
        document.getElementById('rf-roof-area').addEventListener('keypress', (e) => {
            if (e.key === 'Enter') calculate();
        });
    }

    // Calculate potential
    function calculate() {
        const roofAreaInput = document.getElementById('rf-roof-area');
        const unitSelect = document.getElementById('rf-unit');
        const citySelect = document.getElementById('rf-city');
        const resultsDiv = document.getElementById('rf-results');

        let roofArea = parseFloat(roofAreaInput.value);
        const unit = unitSelect.value;
        const city = citySelect.value;

        if (!roofArea || roofArea <= 0) {
            roofAreaInput.style.borderColor = '#ef4444';
            return;
        }
        roofAreaInput.style.borderColor = '#e2e8f0';

        // Convert sqft to sqm
        if (unit === 'sqft') {
            roofArea = roofArea * 0.0929;
        }

        // Get rainfall
        const rainfall = city ? (CITY_RAINFALL[city] || CONFIG.defaultRainfall) : CONFIG.defaultRainfall;

        // Calculate
        const yearlyYield = roofArea * rainfall * CONFIG.runoffCoeff; // liters
        const recommendedTank = Math.ceil(yearlyYield / 52 / 100) * 100; // Weekly average, rounded
        const yearlySavings = yearlyYield * 0.05; // ₹0.05 per liter
        const carbonOffset = yearlyYield * 0.0003; // kg CO2 per liter

        // Update results
        document.getElementById('rf-yield').textContent = formatNumber(yearlyYield) + ' L';
        document.getElementById('rf-tank').textContent = formatNumber(recommendedTank) + ' L';
        document.getElementById('rf-savings').textContent = '₹' + formatNumber(yearlySavings);
        document.getElementById('rf-carbon').textContent = formatNumber(carbonOffset) + ' kg';

        // Show results
        resultsDiv.classList.add('show');
    }

    // Format number with commas
    function formatNumber(num) {
        if (num >= 1000000) {
            return (num / 1000000).toFixed(1) + 'M';
        }
        if (num >= 1000) {
            return (num / 1000).toFixed(1) + 'K';
        }
        return Math.round(num).toLocaleString('en-IN');
    }

    // Initialize on DOM ready
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', init);
    } else {
        init();
    }

    // Expose global API
    window.RainForgeWidget = {
        init: init,
        calculate: calculate
    };

})();
