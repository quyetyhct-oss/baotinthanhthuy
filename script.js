// API configuration
const API_URL = '/api/prices';
const FETCH_INTERVAL = 15000; // Fetch from server every 15 seconds

// DOM elements
const phuquyBuyEl = document.getElementById('phuquy-buy');
const phuquySellEl = document.getElementById('phuquy-sell');
const phuquyTimeEl = document.getElementById('phuquy-time');
const phuquyStatusEl = document.getElementById('phuquy-status');

const xagusdSpotEl = document.getElementById('xagusd-spot');
const xagusdTimeEl = document.getElementById('xagusd-time');

const xauusdSpotEl = document.getElementById('xauusd-spot');
const xauusdTimeEl = document.getElementById('xauusd-time');

const ukoilSpotEl = document.getElementById('ukoil-spot');
const ukoilTimeEl = document.getElementById('ukoil-time');

const dxySpotEl = document.getElementById('dxy-spot');
const dxyTimeEl = document.getElementById('dxy-time');

// Local cached values that will micro-fluctuate every second to match live charts
let xagusdSpot = 58.18000;
let xauusdSpot = 4048.795;
let ukoilSpot = 87.85;
let dxySpot = 101.037;

// Helper to format currency/index values
function formatNumber(num, decimals = 2, locale = 'vi-VN') {
    if (num === null || num === undefined || isNaN(num)) return '--.--';
    return Number(num).toLocaleString(locale, {
        minimumFractionDigits: decimals,
        maximumFractionDigits: decimals
    });
}

// Fetch prices from local/Vercel server
async function fetchPrices() {
    try {
        const response = await fetch(API_URL);
        if (!response.ok) throw new Error(`HTTP error! status: ${response.status}`);
        
        const data = await response.json();
        if (data.error) throw new Error(data.error);

        // Update Phu Quy Silver Price (STRICTLY matches giabac.vn - NO micro-fluctuation algorithm)
        if (data.phu_quy) {
            phuquyBuyEl.textContent = formatNumber(data.phu_quy.buy, 3, 'vi-VN');
            phuquySellEl.textContent = formatNumber(data.phu_quy.sell, 3, 'vi-VN');
            phuquyTimeEl.textContent = data.timestamp;
        }

        // Sync Spot prices with server values
        if (data.xag_usd) {
            xagusdSpot = data.xag_usd.buy;
            if (xagusdSpotEl) xagusdSpotEl.textContent = formatNumber(xagusdSpot, 5, 'en-US');
            if (xagusdTimeEl) xagusdTimeEl.textContent = data.timestamp;
        }

        if (data.xau_usd) {
            xauusdSpot = data.xau_usd.price;
            if (xauusdSpotEl) xauusdSpotEl.textContent = formatNumber(xauusdSpot, 3, 'en-US');
            if (xauusdTimeEl) xauusdTimeEl.textContent = data.timestamp;
        }

        if (data.uk_oil) {
            ukoilSpot = data.uk_oil.price;
            if (ukoilSpotEl) ukoilSpotEl.textContent = formatNumber(ukoilSpot, 2, 'en-US');
            if (ukoilTimeEl) ukoilTimeEl.textContent = data.timestamp;
        }

        if (data.dxy) {
            dxySpot = data.dxy.price;
            if (dxySpotEl) dxySpotEl.textContent = formatNumber(dxySpot, 3, 'en-US');
            if (dxyTimeEl) dxyTimeEl.textContent = data.timestamp;
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
        const fallbackTime = now.toLocaleTimeString('vi-VN') + ' (Lưu sẵn)';
        if (phuquyTimeEl) phuquyTimeEl.textContent = fallbackTime;
        if (xagusdTimeEl) xagusdTimeEl.textContent = fallbackTime;
        if (xauusdTimeEl) xauusdTimeEl.textContent = fallbackTime;
        if (ukoilTimeEl) ukoilTimeEl.textContent = fallbackTime;
        if (dxyTimeEl) dxyTimeEl.textContent = fallbackTime;
        
        // Show Offline status in Phu Quy Card
        if (phuquyStatusEl) {
            phuquyStatusEl.innerHTML = '<span class="pulse-dot" style="background-color: #f43f5e; box-shadow: 0 0 8px #f43f5e;"></span>giabac.vn (Offline)';
            phuquyStatusEl.style.color = '#f43f5e'; // red color accent
        }
    }
}

// Micro-fluctuate international spot prices in real-time (every 1 second) to match live charts
function tickPrices() {
    // 1. Micro-fluctuate XAGUSD by a tiny random amount (-0.00030 to +0.00030 USD)
    const xagChange = (Math.random() - 0.5) * 0.00060;
    xagusdSpot += xagChange;
    if (xagusdSpotEl) xagusdSpotEl.textContent = formatNumber(xagusdSpot, 5, 'en-US');

    // 2. Micro-fluctuate XAUUSD by a small random amount (-0.020 to +0.020 USD)
    const xauChange = (Math.random() - 0.5) * 0.040;
    xauusdSpot += xauChange;
    if (xauusdSpotEl) xauusdSpotEl.textContent = formatNumber(xauusdSpot, 3, 'en-US');

    // 3. Micro-fluctuate UKOIL by a tiny random amount (-0.005 to +0.005 USD)
    const oilChange = (Math.random() - 0.5) * 0.010;
    ukoilSpot += oilChange;
    if (ukoilSpotEl) ukoilSpotEl.textContent = formatNumber(ukoilSpot, 2, 'en-US');

    // 4. Micro-fluctuate DXY by a tiny random amount (-0.002 to +0.002 index points)
    const dxyChange = (Math.random() - 0.5) * 0.004;
    dxySpot += dxyChange;
    if (dxySpotEl) dxySpotEl.textContent = formatNumber(dxySpot, 3, 'en-US');
}

// Initial setup and timers
document.addEventListener('DOMContentLoaded', () => {
    fetchPrices();
    
    // Fetch prices from server every FETCH_INTERVAL
    setInterval(fetchPrices, FETCH_INTERVAL);
    
    // Micro-fluctuate prices every 1 second
    setInterval(tickPrices, 1000);
});
