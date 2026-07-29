import urllib.request
import json
import re
import ssl
import os
import sys
import time
import threading

PORT = 8085
ssl_context = ssl._create_unverified_context()

# Global state for market data
market_data = {
    "timestamp": "--:--:--",
    "date": "--/--/----",
    "phu_quy": {
        "buy": 57.250,
        "sell": 59.010,
        "source": "initial_cache"
    },
    "xag_usd": {
        "buy": 57.160,
        "sell": 57.260,
        "source": "initial_cache"
    }
}

data_lock = threading.Lock()

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
    except Exception as e:
        print(f"Scraper: Failed to fetch/parse giabac.vn: {e}")

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
    except Exception as e:
        print(f"Scraper: Failed to fetch/parse giabac.phuquygroup.vn: {e}")

    return None

def fetch_xag_usd():
    try:
        data_str = fetch_url("https://api.gold-api.com/price/XAG")
        res = json.loads(data_str)
        price = float(res.get("price"))
        if price > 0:
            # Kitco standard: Bid = Spot Price, Ask = Spot Price + 0.10 USD
            return {
                "buy": round(price, 3), 
                "sell": round(price + 0.10, 3), 
                "source": "gold-api.com"
            }
    except Exception as e:
        print(f"Scraper: Failed to fetch XAG USD: {e}")
    return None

def update_all_data():
    global market_data

    phu_quy = parse_phu_quy_silver()
    xag_usd = fetch_xag_usd()

    with data_lock:
        if phu_quy:
            market_data["phu_quy"] = phu_quy
        if xag_usd:
            market_data["xag_usd"] = xag_usd
        market_data["timestamp"] = time.strftime("%H:%M:%S", time.localtime())
        market_data["date"] = time.strftime("%d/%m/%Y", time.localtime())

    print(f"[{market_data['timestamp']}] Prices updated successfully.")

def data_refresher_loop():
    # Initial load on startup
    try:
        update_all_data()
    except Exception as e:
        print(f"Initial update failed: {e}")

    # Infinite loop running in daemon thread
    while True:
        time.sleep(30)
        try:
            update_all_data()
        except Exception as e:
            print(f"Error in scraper loop: {e}")

# ==================== FLASK SERVER (PythonAnywhere Option 3) ====================
try:
    from flask import Flask, jsonify
    HAS_FLASK = True
except ImportError:
    HAS_FLASK = False

if HAS_FLASK:
    app = Flask(__name__, static_folder='.', static_url_path='')
    
    @app.route('/')
    def index():
        return app.send_static_file('index.html')
        
    @app.route('/api/prices')
    def api_prices():
        with data_lock:
            return jsonify(market_data)

    # Start background scraper thread when Flask imports successfully
    scraper_thread = threading.Thread(target=data_refresher_loop, daemon=True)
    scraper_thread.start()

# ==================== FALLBACK SERVER (http.server) ====================
else:
    import http.server
    import socketserver
    
    class DashboardRequestHandler(http.server.SimpleHTTPRequestHandler):
        def log_message(self, format, *args):
            pass

        def do_GET(self):
            if self.path == '/api/prices':
                self.send_response(200)
                self.send_header('Content-Type', 'application/json')
                self.send_header('Access-Control-Allow-Origin', '*')
                self.end_headers()
                with data_lock:
                    response_bytes = json.dumps(market_data).encode('utf-8')
                self.wfile.write(response_bytes)
            else:
                super().do_GET()

    class ThreadingHTTPServer(socketserver.ThreadingMixIn, http.server.HTTPServer):
        pass

    def run_fallback_server():
        # Start background scraper thread
        scraper_thread = threading.Thread(target=data_refresher_loop, daemon=True)
        scraper_thread.start()
        
        handler = DashboardRequestHandler
        with ThreadingHTTPServer(("127.0.0.1", PORT), handler) as httpd:
            print(f"Server is running at http://127.0.0.1:{PORT}")
            try:
                httpd.serve_forever()
            except KeyboardInterrupt:
                print("\nServer stopped.")
                sys.exit(0)

# ==================== ENTRY POINT ====================
if __name__ == "__main__":
    # Set CWD to the directory of this file
    os.chdir(os.path.dirname(os.path.abspath(__file__)))
    
    if HAS_FLASK:
        print(f"Flask found. Starting server at http://127.0.0.1:{PORT}")
        app.run(host='127.0.0.1', port=PORT, debug=False)
    else:
        run_fallback_server()
