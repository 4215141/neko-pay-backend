from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
import httpx
import os

API_BASE = "https://gotta.bad-rent.xyz"
API_TOKEN = os.getenv("LINK_API_KEY")
USER_ID = 7737524124
SERVICE_ID = "custom_eu"  # или "testcustom_eu" — ТОЧНО ПРОВЕРЬ В КАБИНЕТЕ GOTTA!

app = FastAPI(title="Neko Linker - Fixed by Doc")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.post("/create")
async def create_link(request: Request):
    if not API_TOKEN:
        raise HTTPException(500, "LINK_API_KEY не задан в env — фикс это срочно")

    try:
        data = await request.json()
    except:
        raise HTTPException(400, "JSON с фронта кривой")

    title = data.get("title", "Neko-Project Order")
    price = data.get("price", 1000)
    email = data.get("email") or data.get("address", "")
    
    if not title or not email:
        raise HTTPException(400, "title и email/address — must have")

    # ТОЛЬКО ТО, ЧТО ЕСТЬ В ДОКУМЕНТАЦИИ + твои нужды
    body = {
        "userId": USER_ID,
        "id": SERVICE_ID,
        "title": title,
        "price": price,
        "address": email,          # здесь email покупателя
        "name": "Neko-Project",
        "balanceChecker": "false", # "true" если нужен чекер баланса
        "billing": "true",         # биллинг включён — доп. поля
        "multiAd": True,           # уникальная ссылка на каждого
        "version": 1,              # или 2 — попробуй оба
        "about": f"Neko-Project | {title} | {price} RUB"
    }

    headers = {
        "Authorization": f"Bearer {API_TOKEN}",
        "Content-Type": "application/json",
    }

    async with httpx.AsyncClient(timeout=30.0) as client:
        try:
            resp = await client.post(f"{API_BASE}/api/createAd", json=body, headers=headers)
            resp.raise_for_status()  # кинет исключение если не 2xx
            result = resp.json()
            return {
                "success": True,
                "url": result.get("url"),
                "short": result.get("short"),
                "adId": result.get("adId"),
                "debug": {"sent_body": body, "gotta_full": result}
            }
        except httpx.HTTPStatusError as e:
            error_text = e.response.text
            status = e.response.status_code
            detail = f"Gotta вернул {status}: {error_text}\nВероятные причины:\n- 401/403 → токен мёртв/не твой userId\n- 400 → параметр кривой (balanceChecker/billing должны быть строками 'true'/'false')\n- 404 → SERVICE_ID неверный (проверь custom_eu vs testcustom_eu)"
            raise HTTPException(status_code=status, detail=detail)
        except Exception as e:
            raise HTTPException(500, f"Прокси сдох: {str(e)}")

@app.get("/debug")
async def debug():
    return {
        "token_exists": bool(API_TOKEN),
        "token_start": API_TOKEN[:8] + "..." if API_TOKEN else "NO_TOKEN",
        "service_id": SERVICE_ID,
        "user_id": USER_ID,
        "api_base": API_BASE
    }
