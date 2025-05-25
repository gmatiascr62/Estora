from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse, RedirectResponse
from starlette.middleware.sessions import SessionMiddleware
from fastapi.middleware.cors import CORSMiddleware
from fastapi.templating import Jinja2Templates
from auth_utils import login_required, persona_actual, set_current_user, decode_token
from routes.auth_routes import router as auth_router
from admin import configurar_admin
from sockets.socket_events import init_socket
from database import Base, engine, cargar_usuarios_en_memoria, usuarios_en_memoria
import uvicorn

app = FastAPI(debug=True)
init_socket(app)
# panel admin
configurar_admin(app)
'''
tu_proyecto/
│
├── main.py                      # Importa y configura SQLAdmin
├── admin.py                     # NUEVO archivo para el admin
├── database.py
├── database.db
├── auth_utils.py
│
├── models/
│   ├── __init__.py
│   ├── models.py
│   └── persona_memoria.py
│
├── routers/
│   ├── __init__.py
│   └── usuarios.py
│
├── templates/
│   └── index.html
│
└── static/
    └── ...
'''

# Middleware para el current_user
@app.middleware("http")
async def add_current_user_to_context(request: Request, call_next):
    user_data = request.session.get("user_data")
    set_current_user(user_data)
    response = await call_next(request)
    return response

# Configuración
app.add_middleware(SessionMiddleware, secret_key="hdhduwjdjjdjdjdjudi6662u", session_cookie="session_cookie", max_age=60*60*60)
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_credentials=True, allow_methods=["*"], allow_headers=["*"])
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

# DB init (ahora con SQLAlchemy)
def init_db():
    Base.metadata.create_all(bind=engine)

init_db()

# Rutas
app.include_router(auth_router)

@app.get("/", response_class=HTMLResponse)
@login_required
async def home(request: Request):
    token = request.cookies.get("session")
    return templates.TemplateResponse("home.html", {"request": request, "current": persona_actual(), "usuarios": usuarios_en_memoria})

@app.get("/perfil")
@login_required
async def perfil(request: Request):
    return usuarios_en_memoria



def crear_base():
    from models import Base
    from database import engine
    Base.metadata.create_all(bind=engine)

if __name__ == "__main__":
    #crear_base()
    cargar_usuarios_en_memoria()
    print("Iniciando app...")
    uvicorn.run(app, log_level="warning")
    