// Code dành cho Cloudflare Worker (giabac.quyetyhct.workers.dev)
// Cập nhật nguồn sang: https://giabac.phuquygroup.vn/

addEventListener('fetch', event => {
  event.respondWith(handleRequest(event.request))
})

async function handleRequest(request) {
  const corsHeaders = {
    'Access-Control-Allow-Origin': '*',
    'Access-Control-Allow-Methods': 'GET, HEAD, OPTIONS',
    'Access-Control-Allow-Headers': 'Content-Type',
    'Content-Type': 'application/json; charset=utf-8'
  };

  if (request.method === 'OPTIONS') {
    return new Response(null, { headers: corsHeaders });
  }

  try {
    const url = 'https://giabac.phuquygroup.vn/';
    const response = await fetch(url, {
      headers: {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
      }
    });

    const html = await response.text();
    
    // Pattern bóc tách BẠC THỎI PHÚ QUÝ 999 1KILO
    const match = html.match(/1KILO.*?silver-buy-price[^>]*>\s*([\d,]+)\s*<.*?silver-sell-price[^>]*>\s*([\d,]+)\s*/s);

    if (match) {
      const buyRaw = parseInt(match[1].replace(/,/g, ''), 10);
      const sellRaw = parseInt(match[2].replace(/,/g, ''), 10);
      const buy = buyRaw / 1000000;
      const sell = sellRaw / 1000000;

      return new Response(JSON.stringify({
        buy: Math.round(buy * 1000) / 1000,
        sell: Math.round(sell * 1000) / 1000,
        buyRaw: buyRaw,
        sellRaw: sellRaw,
        unit: "triệu đồng/kg",
        source: "giabac.phuquygroup.vn",
        updatedAt: new Date().toISOString()
      }), { headers: corsHeaders });
    }
  } catch (e) {
    console.error("Lỗi Worker parse:", e);
  }

  // Dự phòng giá niêm yết mới nhất nếu bị lỗi mạng
  return new Response(JSON.stringify({
    buy: 58.427,
    sell: 60.240,
    buyRaw: 58427000,
    sellRaw: 60240000,
    unit: "triệu đồng/kg",
    source: "fallback",
    updatedAt: new Date().toISOString()
  }), { headers: corsHeaders });
}
