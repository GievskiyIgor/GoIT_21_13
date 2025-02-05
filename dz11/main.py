from fastapi import FastAPI, Depends, HTTPException, Request, status
from fastapi.responses import JSONResponse, HTMLResponse
from fastapi_limiter import FastAPILimiter
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from starlette.middleware.cors import CORSMiddleware

from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession
from src.database.db import get_db
from src.routes import contacts, auth, users
from src.conf.config import config

import re
from ipaddress import ip_address
from typing import Callable
from pathlib import Path
import redis.asyncio as redis


app = FastAPI()


banned_ips = [
    ip_address("192.168.1.1"),
    ip_address("192.168.1.2"),
    ip_address("127.0.0.1"),
]
origins = [ 
    "http://localhost:3000"
    ]


app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


user_agent_ban_list = [r"Googlebot", r"Python-urllib"]


@app.add_middleware("http")
async def user_ban_middleware(request: Request, call_next: Callable):
    
    print(request.headers.get("Authorization"))
    
    user_agent = request.headers.get("user-agent")
    print(user_agent)

    for ban_pattern in user_agent_ban_list:
        if re.search(ban_pattern, user_agent):
            return JSONResponse(status_code=status.HTTP_403_FORBIDDEN, content={"detail": "You are banned"},)
    
    response = await call_next(request)
    
    return response


BASE_DIR = Path(".")
app.mount("/static", StaticFiles(directory=BASE_DIR / "src" / "static"), name="static")

app.include_router(auth.router, prefix="/api")
app.include_router(contacts.router, prefix="/api")
app.include_router(users.router, prefix="/api")


@app.on_event("startup")
async def startup():
    r = await redis.Redis(
        host=config.REDIS_DOMAIN,
        port=config.REDIS_PORT,
        db=0,
        password=config.REDIS_PASSWORD,
        )
       
    await FastAPILimiter.init(r)


templates = Jinja2Templates(directory=BASE_DIR/ "src" / "templates")


@app.get("/", response_class=HTMLResponse)
def index(request: Request):
    # return {"message": "Contact App"}
    return templates.TemplateResponse("index.html", {"request": request, "our": "Build group WebPython #16"})


@app.get("/api/healthchecker")
async def healthchecker(db: AsyncSession = Depends(get_db)):
    try:
        result = await db.execute(text("SELECT 1"))
        result = result.fetchone()
        if result is None:
            raise HTTPException(status_code=500, detail="Database is not configured correctly")
        return {"message": "Welcome to FastAPI!"}
    except Exception as err:
        print (err)
        raise HTTPException(status_code=500, detail="Error connecting to the database") 