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

def fetch_tradingview_price(symbol_path):
    try:
        url = f"https://www.tradingview.com/symbols/{symbol_path}/"
        req = urllib.request.Request(
            url, 
            headers={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'}
        )
        with urllib.request.urlopen(req, context=ssl_context, timeout=5) as response:
            html = response.read().decode('utf-8')
            match = re.search(r'"price":\s*([\d\.]+)', html)
            if match:
                return {"price": float(match.group(1)), "source": "tradingview.com"}
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
        
        # Scrape directly from TradingView for 100% chart matching
        xag_data = fetch_tradingview_price("OANDA-XAGUSD") or {"buy": 58.180, "sell": 58.280, "source": "fallback"}
        xau_data = fetch_tradingview_price("OANDA-XAUUSD") or {"price": 4048.795, "source": "fallback"}
        uk_oil = fetch_tradingview_price("TVC-UKOIL") or {"price": 88.03, "source": "fallback"}
        dxy = fetch_tradingview_price("CAPITALCOM-DXY") or {"price": 100.622, "source": "fallback"}
        
        # Format XAG and XAU to match expected JSON structure
        if "price" in xag_data:
            xag_usd = {
                "buy": xag_data["price"],
                "sell": xag_data["price"] + 0.10,
                "source": "tradingview.com"
            }
        else:
            xag_usd = xag_data

        if "price" in xau_data:
            xau_usd = {
                "price": xau_data["price"],
                "source": "tradingview.com"
            }
        else:
            xau_usd = xau_data
        
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
