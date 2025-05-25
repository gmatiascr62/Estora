from fastapi import FastAPI, Request, Depends, HTTPException, Form
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from starlette.middleware.sessions import SessionMiddleware
from fastapi.middleware.cors import CORSMiddleware
from functools import wraps
from typing import Optional
import sqlite3
import hashlib
import uvicorn
import secrets
from contextvars import ContextVar

app = FastAPI()

# Variable contextvar para almacenar el usuario actual por-request
_current_user: ContextVar[Optional[str]] = ContextVar("current_user", default=None)

# Middleware para setear el current_user automáticamente
@app.middleware("http")
async def add_current_user_to_context(request: Request, call_next):
    user = request.session.get("user")
    _current_user.set(user)
    response = await call_next(request)
    return response

# Función accesible globalmente para obtener el usuario actual
def current_user() -> Optional[str]:
    return _current_user.get()


def borrar():
    print(current_user())

# Configura SessionMiddleware (¡Clave secreta aleatoria!)
app.add_middleware(
    SessionMiddleware,
    secret_key=secrets.token_hex(32),
    session_cookie="session_cookie"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

def init_db():
    conn = sqlite3.connect("database.db")
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY,
            username TEXT UNIQUE,
            password TEXT,
            token_activo TEXT
        )
    """)
    conn.commit()
    conn.close()

init_db()

def hash_password(password: str):
    return hashlib.sha256(password.encode()).hexdigest()

# Decorador de autenticación
def login_required(func):
    @wraps(func)
    async def wrapper(request: Request, *args, **kwargs):
        if not request.session.get("user"):
            return RedirectResponse(url="/login", status_code=303)
        return await func(request, *args, **kwargs)
    return wrapper

@app.get("/", response_class=HTMLResponse)
@login_required
async def home(request: Request):
    return templates.TemplateResponse("home.html", {"request": request})

@app.get("/login", response_class=HTMLResponse)
async def login_page(request: Request):
    return templates.TemplateResponse("login.html", {"request": request})

@app.post("/login")
async def login(request: Request, username: str = Form(...), password: str = Form(...)):
    conn = sqlite3.connect("database.db")
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM users WHERE username = ?", (username,))
    user = cursor.fetchone()
    
    if not user or user[2] != hash_password(password):
        return templates.TemplateResponse("login.html", {
            "request": request,
            "error": "Credenciales incorrectas"
        })
    
    response = RedirectResponse(url="/", status_code=303)
    request.session["user"] = username
    return response

@app.get("/register", response_class=HTMLResponse)
async def register_page(request: Request):
    return templates.TemplateResponse("register.html", {"request": request})

@app.post("/register")
async def register(request: Request, username: str = Form(...), password: str = Form(...)):
    conn = sqlite3.connect("database.db")
    cursor = conn.cursor()
    
    try:
        cursor.execute(
            "INSERT INTO users (username, password) VALUES (?, ?)",
            (username, hash_password(password))
        )
        conn.commit()
    except sqlite3.IntegrityError:
        return templates.TemplateResponse("register.html", {
            "request": request,
            "error": "El usuario ya existe"
        })
    finally:
        conn.close()
    
    return RedirectResponse(url="/login", status_code=303)

@app.get("/perfil")
@login_required
async def perfil(request: Request):
    user = current_user()
    if not user:
        return RedirectResponse(url="/login", status_code=303)
    return {"usuario_logueado": user}

@app.get("/prueba", response_class=HTMLResponse)
async def prueba(request: Request):
    borrar()
    return f"Hola {current_user()}! Estás en /prueba"

uvicorn.run(app)