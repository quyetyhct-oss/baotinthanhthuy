from http.server import BaseHTTPRequestHandler
import json
import urllib.request
import re
import ssl
import datetime

ssl_context = ssl._create_unverified_context()

def fetch_url(url):
    req = urllib.request.Request(
        url, 
        headers={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'}
    )
    with urllib.request.urlopen(req, context=ssl_context, timeout=5) as response:
        return response.read().decode('utf-8')

def parse_phu_quy_silver():
    # Try giabac.vn
    try:
        html = fetch_url("https://giabac.vn")
        match = re.search(
            r'Bạc thỏi Ph&#250; Qu&#253; 999 1Kilo.*?text-center fw-bolder">([\d,]+)<.*?text-center fw-bolder">([\d,]+)<', 
            html, 
            re.DOTALL
        )
        if match:
            buy = float(match.group(1).replace(",", "")) / 1_000_000
            sell = float(match.group(2).replace(",", "")) / 1_000_000
            return {"buy": round(buy, 3), "sell": round(sell, 3), "source": "giabac.vn"}
    except Exception:
        pass

    # Fallback to giabac.phuquygroup.vn
    try:
        html = fetch_url("https://giabac.phuquygroup.vn")
        match = re.search(
            r'BẠC THỎI PH&#218; QU&#221; 999 1KILO.*?col-buy-cell[^>]*>([\d,]+)<.*?col-buy-cell[^>]*>([\d,]+)<', 
            html, 
            re.DOTALL
        )
        if match:
            buy = float(match.group(1).replace(",", "")) / 1_000_000
            sell = float(match.group(2).replace(",", "")) / 1_000_000
            return {"buy": round(buy, 3), "sell": round(sell, 3), "source": "giabac.phuquygroup.vn"}
    except Exception:
        pass

    # Hard fallback
    return {"buy": 57.093, "sell": 58.853, "source": "fallback"}

def fetch_xag_usd():
    try:
        data_str = fetch_url("https://api.gold-api.com/price/XAG")
        res = json.loads(data_str)
        price = float(res.get("price"))
        if price > 0:
            return {
                "buy": round(price, 3), 
                "sell": round(price + 0.10, 3), 
                "source": "gold-api.com"
            }
    except Exception:
        pass
    return {"buy": 57.160, "sell": 57.260, "source": "fallback"}

def fetch_xau_usd():
    try:
        data_str = fetch_url("https://api.gold-api.com/price/XAU")
        res = json.loads(data_str)
        price = float(res.get("price"))
        if price > 0:
            return {"price": round(price, 3), "source": "gold-api.com"}
    except Exception:
        pass
    return {"price": 4048.795, "source": "fallback"}

def fetch_yahoo_symbol(symbol):
    try:
        data_str = fetch_url(f"https://query1.finance.yahoo.com/v8/finance/chart/{symbol}?interval=1m&range=1d")
        res = json.loads(data_str)
        price = float(res['chart']['result'][0]['meta']['regularMarketPrice'])
        if price > 0:
            return {"price": price, "source": "yahoo"}
    except Exception:
        pass
    return None

class handler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()
        
        # Scrape data
        phu_quy = parse_phu_quy_silver()
        xag_usd = fetch_xag_usd()
        xau_usd = fetch_xau_usd()
        uk_oil = fetch_yahoo_symbol("BZ=F") or {"price": 87.85, "source": "fallback"}
        dxy = fetch_yahoo_symbol("DX-Y.NYB") or {"price": 101.037, "source": "fallback"}
        
        # Calculate GMT+7 time (Vietnam Time)
        vn_time = datetime.datetime.utcnow() + datetime.timedelta(hours=7)
        
        data = {
            "timestamp": vn_time.strftime("%H:%M:%S"),
            "date": vn_time.strftime("%d/%m/%Y"),
            "phu_quy": phu_quy,
            "xag_usd": xag_usd,
            "xau_usd": xau_usd,
            "uk_oil": uk_oil,
            "dxy": dxy
        }
        
        self.wfile.write(json.dumps(data).encode('utf-8'))
