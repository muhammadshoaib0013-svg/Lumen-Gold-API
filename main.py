from fastapi import FastAPI, HTTPException, Security, Depends
from fastapi.security.api_key import APIKeyHeader
from fastapi.responses import HTMLResponse
import requests

app = FastAPI()

# Security & API Keys
SHOAIB_OFFICIAL_KEY = "shoaib-gold-v1-786"
api_key_header = APIKeyHeader(name="X-API-KEY", auto_error=False)
API_KEY_PROVIDER = "goldapi-ccb53beddb6dec2e96fe0ead4bfad163-io"

def get_api_key(header_key: str = Security(api_key_header)):
    if header_key == SHOAIB_OFFICIAL_KEY:
        return header_key
    else:
        raise HTTPException(status_code=403, detail="Ghalat API Key!")

# API Endpoint (Jo data deta hai)
@app.get("/gold-price")
def get_gold_price(authenticated: str = Depends(get_api_key)):
    url = "https://www.goldapi.io/api/XAU/USD"
    headers = {"x-access-token": API_KEY_PROVIDER, "Content-Type": "application/json"}
    
    try:
        response = requests.get(url, headers=headers)
        data = response.json()
        return {
            "price": data.get("price")
        }
    except Exception:
        raise HTTPException(status_code=500, detail="Server Error")

# Frontend Dashboard Endpoint (Jo khoobsurat design dikhata hai)
@app.get("/", response_class=HTMLResponse)
def dashboard():
    html_content = """
    <!DOCTYPE html>
    <html>
    <head>
        <title>LUMEN - Gold Dashboard</title>
        <style>
            body { 
                background-color: #1a1c23; /* Deep Charcoal */
                color: #ffffff; 
                font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; 
                display: flex; 
                justify-content: center; 
                align-items: center; 
                height: 100vh; 
                margin: 0; 
            }
            .card { 
                background-color: #2d3139; /* Slate */
                padding: 40px; 
                border-radius: 12px; 
                box-shadow: 0 8px 16px rgba(0,0,0,0.5); 
                text-align: center; 
                border-top: 4px solid #d4af37; /* Matte Gold Accent */
                width: 350px; 
            }
            h1 { color: #d4af37; margin-bottom: 5px; font-size: 28px; letter-spacing: 1px; }
            p.subtitle { color: #8892b0; font-size: 14px; margin-top: 0; margin-bottom: 30px; }
            .price-box { font-size: 48px; font-weight: bold; margin: 20px 0; color: #ffd700; text-shadow: 0 0 10px rgba(255, 215, 0, 0.2); }
            button { 
                background-color: #d4af37; 
                color: #121212; 
                border: none; 
                padding: 12px 24px; 
                font-size: 16px; 
                font-weight: bold; 
                border-radius: 6px; 
                cursor: pointer; 
                transition: 0.3s; 
                width: 100%; 
            }
            button:hover { background-color: #ffd700; box-shadow: 0 0 15px rgba(212, 175, 55, 0.4); }
            .status { margin-top: 20px; font-size: 12px; color: #4caf50; }
        </style>
    </head>
    <body>
        <div class="card">
            <h1>Gold Market Live</h1>
            <p class="subtitle">API Built by Muhammad Shoaib</p>
            <div class="price-box" id="price-display">Loading...</div>
            <button onclick="fetchPrice()">Refresh Live Price</button>
            <div class="status" id="status-text">Connecting to secure server...</div>
        </div>

        <script>
            async function fetchPrice() {
                document.getElementById('price-display').innerText = 'Loading...';
                document.getElementById('status-text').innerText = 'Fetching secure data...';
                document.getElementById('status-text').style.color = '#8892b0';
                
                try {
                    // Yahan aapka frontend automatically aapki secret key bhej raha hai
                    const response = await fetch('/gold-price', {
                        method: 'GET',
                        headers: {
                            'X-API-KEY': 'shoaib-gold-v1-786' 
                        }
                    });
                    
                    if (response.ok) {
                        const data = await response.json();
                        document.getElementById('price-display').innerText = '$' + data.price;
                        document.getElementById('status-text').innerText = 'Live data fetched successfully!';
                        document.getElementById('status-text').style.color = '#4caf50';
                    } else {
                        document.getElementById('price-display').innerText = 'Error';
                        document.getElementById('status-text').innerText = 'Unauthorized or Server Error';
                        document.getElementById('status-text').style.color = '#ff5252';
                    }
                } catch (error) {
                    document.getElementById('price-display').innerText = 'Error';
                    document.getElementById('status-text').innerText = 'Connection failed';
                    document.getElementById('status-text').style.color = '#ff5252';
                }
            }
            
            // Jaise hi page open ho, automatically price fetch kar lo
            window.onload = fetchPrice;
        </script>
    </body>
    </html>
    """
    return html_content