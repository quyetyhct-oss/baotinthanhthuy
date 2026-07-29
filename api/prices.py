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

class handler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()
        
        # Scrape data
        phu_quy = parse_phu_quy_silver()
        
        # Calculate GMT+7 time (Vietnam Time)
        vn_time = datetime.datetime.utcnow() + datetime.timedelta(hours=7)
        
        data = {
            "timestamp": vn_time.strftime("%H:%M:%S"),
            "date": vn_time.strftime("%d/%m/%Y"),
            "phu_quy": phu_quy
        }
        
        self.wfile.write(json.dumps(data).encode('utf-8'))
