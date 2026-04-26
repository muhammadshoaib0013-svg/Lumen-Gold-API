from fastapi import FastAPI, HTTPException, Security, Depends, Query
from fastapi.security.api_key import APIKeyHeader
import requests
import time

app = FastAPI(title="LUMEN Gold API", version="1.0.0")

# --- SECURITY GATEWAY ---
SHOAIB_OFFICIAL_KEY = "shoaib-gold-v1-786"
api_key_header = APIKeyHeader(name="X-API-KEY", auto_error=False)

def get_api_key(header_key: str = Security(api_key_header)):
    if header_key == SHOAIB_OFFICIAL_KEY:
        return header_key
    raise HTTPException(status_code=403, detail="Unauthorized Access! Valid API Key required.")

# --- CACHE SYSTEM (10ms Latency) ---
cache = {
    "data": {"gold_usd": None, "rates": {}},
    "last_updated": 0
}
CACHE_TTL = 60  # 60 seconds tak cache fresh rahega

# --- PRECISION CONSTANTS ---
TROY_OUNCE_TO_GRAMS = 31.1034768
UNIT_MULTIPLIERS = {
    "gram": 1,
    "tola": 11.6638038,
    "masha": 0.9719836,
    "ratti": 0.1214979,
    "ounce": TROY_OUNCE_TO_GRAMS,
    "kilo": 1000
}

PURITY_MULTIPLIERS = {
    "24k": 1.0,
    "22k": 22/24,
    "21k": 21/24,
    "18k": 18/24
}

# --- MULTI-SOURCE FETCH ENGINE ---
def fetch_market_data():
    current_time = time.time()
    
    # Agar 60 seconds nahi guzre, to server memory se fast data wapis bhej do
    if current_time - cache["last_updated"] < CACHE_TTL and cache["data"]["gold_usd"]:
        return cache["data"]

    # 1. Fetch Gold Price (Source: GoldAPI)
    gold_price_usd = None
    try:
        headers = {"x-access-token": "goldapi-ccb53beddb6dec2e96fe0ead4bfad163-io"}
        resp = requests.get("https://www.goldapi.io/api/XAU/USD", headers=headers, timeout=5)
        if resp.status_code == 200:
            gold_price_usd = resp.json().get("price")
    except Exception:
        pass # Future Sprint: Yahan hum fallback Source 2 lagayenge

    if not gold_price_usd:
        raise HTTPException(status_code=503, detail="Market Sources Temporary Offline")

    # 2. Fetch Live Currency Rates (Forex Open API)
    rates = {"USD": 1.0}
    try:
        fx_resp = requests.get("https://api.exchangerate-api.com/v4/latest/USD", timeout=5)
        if fx_resp.status_code == 200:
            rates = fx_resp.json().get("rates", {})
    except Exception:
        pass 

    # Update Cache with fresh data
    cache["data"] = {"gold_usd": gold_price_usd, "rates": rates}
    cache["last_updated"] = current_time
    
    return cache["data"]

# --- THE UNFAIR ADVANTAGE ENDPOINT ---
@app.get("/v1/gold/price/local")
def get_local_price(
    currency: str = Query("PKR", description="Target Currency (e.g., PKR, INR, AED)"),
    unit: str = Query("tola", description="Weight unit (gram, tola, ounce)"),
    purity: str = Query("24k", description="Gold purity (24k, 22k, 21k, 18k)"),
    authenticated: str = Depends(get_api_key)
):
    currency = currency.upper()
    unit = unit.lower()
    purity = purity.lower()

    if unit not in UNIT_MULTIPLIERS:
        raise HTTPException(status_code=400, detail=f"Invalid unit. Choose from: {list(UNIT_MULTIPLIERS.keys())}")
    if purity not in PURITY_MULTIPLIERS:
        raise HTTPException(status_code=400, detail=f"Invalid purity. Choose from: {list(PURITY_MULTIPLIERS.keys())}")

    # Core Data mangwao
    market = fetch_market_data()
    gold_usd_per_ounce = market["gold_usd"]
    fx_rates = market["rates"]

    if currency not in fx_rates:
        raise HTTPException(status_code=400, detail=f"Currency {currency} not supported yet")

    # LUMEN Mathematics Engine
    usd_per_gram = gold_usd_per_ounce / TROY_OUNCE_TO_GRAMS
    usd_per_unit = usd_per_gram * UNIT_MULTIPLIERS[unit]
    local_currency_price = usd_per_unit * fx_rates[currency]
    final_price = local_currency_price * PURITY_MULTIPLIERS[purity]

    return {
        "status": "success",
        "metal": "Gold",
        "currency": currency,
        "unit": unit,
        "purity": purity,
        "price_value": round(final_price, 2), # Rounding to 2 decimal points for professional look
        "meta": {
            "source": "LUMEN Core Aggregator",
            "latency_type": "Cached (60s TTL)"
        }
    }