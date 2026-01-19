from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import httpx
import os

API_BASE = "https://gotta.bad-rent.xyz"
API_TOKEN = os.getenv("LINK_API_KEY")
USER_ID = 7737524124
SERVICE_ID = "custom_eu"  # или "testcustom_eu" — уточни в кабинете!

app = FastAPI(title="Neko Pay Backend")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
async def root():
    return JSONResponse({
        "status": "alive",
        "message": "Use POST /create with {title, price, email}",
        "debug": "/debug для проверки токена"
    })

@app.post("/")
async def root_post():
    return {"error": "Use /create instead of root POST"}

@app.post("/create")
async def create_link(request: Request):
    if not API_TOKEN:
        raise HTTPException(500, "No LINK_API_KEY — добавь в Environment Variables на Render")

    try:
        data = await request.json()
    except:
        raise HTTPException(400, "Bad JSON")

    title = data.get("title", "Neko Order")
    price = data.get("price", 1000)
    email = data.get("email") or data.get("address", "")

    if not email:
        raise HTTPException(400, "email/address required")

    body = {
        "userId": USER_ID,
        "id": SERVICE_ID,
        "title": title,
        "price": price,
        "address": email,
        "name": "Neko-Project",
        "balanceChecker": "false",
        "billing": "true",
        "multiAd": True,
        "version": 1,
        "about": f"Neko | {title} | {price}"
    }

    headers = {
        "Authorization": f"Bearer {API_TOKEN}",
        "Content-Type": "application/json",
    }

    async with httpx.AsyncClient(timeout=30.0) as client:
        try:
            resp = await client.post(f"{API_BASE}/api/createAd", json=body, headers=headers)
            resp.raise_for_status()
            result = resp.json()
            return {
                "success": True,
                "url": result.get("url"),
                "short": result.get("short"),
                "adId": result.get("adId"),
                "debug_sent": body
            }
        except httpx.HTTPStatusError as e:
            raise HTTPException(e.response.status_code, f"Gotta error: {e.response.text}")
        except Exception as e:
            raise HTTPException(500, str(e))

@app.get("/debug")
async def debug():
    return {
        "token_set": "yes" if API_TOKEN else "NO — добавь LINK_API_KEY",
        "token_preview": (API_TOKEN or "NONE")[:8] + "...",
        "service": SERVICE_ID,
        "user": USER_ID
    }
