// API configuration
const API_URL = '/api/prices';
const FETCH_INTERVAL = 30000; // 30 seconds (Gentle and standard for Phu Quy VN)

// DOM elements
const phuquyBuyEl = document.getElementById('phuquy-buy');
const phuquySellEl = document.getElementById('phuquy-sell');
const phuquyTimeEl = document.getElementById('phuquy-time');
const phuquyStatusEl = document.getElementById('phuquy-status');

// Helper to format currency values with thousand separators
function formatNumber(num, decimals = 2) {
    if (num === null || num === undefined || isNaN(num)) return '--.--';
    return Number(num).toLocaleString('vi-VN', {
        minimumFractionDigits: decimals,
        maximumFractionDigits: decimals
    });
}

// TV and Browser detection to dynamically shrink layout on restricted viewports (Android TV, BrowseHere)
function detectAndAdjustTV() {
    const userAgent = navigator.userAgent.toLowerCase();
    const isTV = userAgent.includes('tv') || 
                 userAgent.includes('smarttv') || 
                 userAgent.includes('googletv') || 
                 userAgent.includes('androidtv') || 
                 userAgent.includes('browsehere') ||
                 userAgent.includes('sony') ||
                 userAgent.includes('webos') ||
                 userAgent.includes('tizen');

    if (isTV) {
        document.body.classList.add('device-tv');
        console.log('TV Browser detected: BrowseHere/Smart TV. Applying TV specific viewport constraints.');
    }
}

// Fetch prices from local/Vercel server
async function fetchPrices() {
    try {
        const response = await fetch(API_URL);
        if (!response.ok) throw new Error(`HTTP error! status: ${response.status}`);
        
        const data = await response.json();
        if (data.error) throw new Error(data.error);

        // Update Phu Quy Silver Price (matches giabac.vn exactly, no fluctuations)
        if (data.phu_quy) {
            phuquyBuyEl.textContent = formatNumber(data.phu_quy.buy, 3, 'vi-VN');
            phuquySellEl.textContent = formatNumber(data.phu_quy.sell, 3, 'vi-VN');
            if (phuquyTimeEl) {
                phuquyTimeEl.textContent = data.timestamp;
            }
        }

        // Show Online Status in Phu Quy Card
        if (phuquyStatusEl) {
            phuquyStatusEl.innerHTML = '<span class="pulse-dot"></span>giabac.vn';
            phuquyStatusEl.style.color = '#10b981'; // green color accent
        }
    } catch (error) {
        console.warn('Backend server is offline or unreachable. Using cache values.', error);
        
        // Fallback: update timestamp to show local computer time
        const now = new Date();
        if (phuquyTimeEl) {
            phuquyTimeEl.textContent = now.toLocaleTimeString('vi-VN') + ' (Lưu sẵn)';
        }
        
        // Show Offline status in Phu Quy Card
        if (phuquyStatusEl) {
            phuquyStatusEl.innerHTML = '<span class="pulse-dot" style="background-color: #f43f5e; box-shadow: 0 0 8px #f43f5e;"></span>giabac.vn (Offline)';
            phuquyStatusEl.style.color = '#f43f5e'; // red color accent
        }
    }
}

// Initial fetch and schedule periodic updates
document.addEventListener('DOMContentLoaded', () => {
    detectAndAdjustTV();
    fetchPrices();
    setInterval(fetchPrices, FETCH_INTERVAL);
});
