from fastapi import APIRouter, Request, Form, Depends
from fastapi.responses import RedirectResponse, HTMLResponse , JSONResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from models.models import Usuario
from database import get_db, usuarios_en_memoria
from auth_utils import create_token, decode_token, set_current_user, current_user

router = APIRouter()
templates = Jinja2Templates(directory="templates")


@router.get("/login", response_class=HTMLResponse)
async def login_get(request: Request):
    return templates.TemplateResponse("login.html", {"request": request})


@router.post("/login")
async def login_post(
    request: Request,
    username: str = Form(...),
    db: Session = Depends(get_db)
):
    user = db.query(Usuario).filter(Usuario.username == username).first()
    if not user:
        return templates.TemplateResponse("login.html", {"request": request, "error": "Usuario no encontrado"})

    token = create_token({"user_id": user.user_id, "username": user.username})
    request.session["user_data"] = {
        "token": token,
        "username": user.username,
        "id": user.user_id
    }

    return RedirectResponse("/", status_code=303)


@router.get("/register", response_class=HTMLResponse)
async def register_get(request: Request):
    return templates.TemplateResponse("register.html", {"request": request})


@router.post("/register")
async def register_post(
    request: Request,
    username: str = Form(...),
    db: Session = Depends(get_db)
    ):
    if db.query(Usuario).filter(Usuario.username == username).first():
        return templates.TemplateResponse("register.html", {"request": request, "error": "Nombre de usuario en uso"})

    nuevo_usuario = Usuario(username=username)
    db.add(nuevo_usuario)
    db.commit()
    db.refresh(nuevo_usuario)

    token = create_token({"user_id": nuevo_usuario.user_id, "username": nuevo_usuario.username})
    request.session["user_data"] = {"token": token}

    return RedirectResponse("/logout", status_code=303)


@router.post("/actualizar_telefono")
async def actualizar_telefono(request: Request):
    user_id = current_user("id")
    if not user_id:
        return JSONResponse(content={"mensaje": "No autorizado"}, status_code=401)

    data = await request.json()
    nuevo_telefono = data.get("telefono")

    persona = usuarios_en_memoria.get(user_id)
    if persona:
        persona.telefono = nuevo_telefono  # Esto actualiza en memoria y en la DB
        return JSONResponse(content={"mensaje": "Teléfono actualizado correctamente."})
    else:
        return JSONResponse(content={"mensaje": "Usuario no encontrado en memoria."}, status_code=404)

@router.get("/logout")
async def logout(request: Request):
    request.session.clear()
    set_current_user(None)
    return RedirectResponse("/login", status_code=303)