from contextvars import ContextVar
from datetime import datetime, timedelta
from fastapi import Request, HTTPException
from starlette.status import HTTP_401_UNAUTHORIZED
from database import usuarios_en_memoria
from typing import Optional
from fastapi import Request
from functools import wraps
from fastapi.responses import RedirectResponse
import jwt
import hashlib


_current_user: ContextVar[Optional[str]] = ContextVar("current_user", default=None)

# Clave secreta para firmar el token (¡cambiá esto en producción!)
SECRET_KEY = "clav66272772jdhdhdva98ta"
ALGORITHM = "HS256"
EXPIRATION_MINUTES = 60

def create_token(data: dict):
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=EXPIRATION_MINUTES)
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

def decode_token(token: str):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        print("payload: ", payload)
        return payload
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=HTTP_401_UNAUTHORIZED, detail="Token expirado")
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=HTTP_401_UNAUTHORIZED, detail="Token inválido")

def hash_password(password: str) -> str:
    return hashlib.sha256(password.encode()).hexdigest()

def set_current_user(user: Optional[str]):
    _current_user.set(user)

def current_user(valor: Optional[str] = None) -> Optional[str]:
    user = _current_user.get()
    if not user:
        return None
    
    if valor:
        return user.get(valor)
        
    user_sin_token = {key: value for key, value in user.items() if key != "token"}
    return user_sin_token


def persona_actual():
    user_id = current_user("id")
    return usuarios_en_memoria.get(user_id)


def login_required(func):
    @wraps(func)
    async def wrapper(request: Request, *args, **kwargs):
        if not request.session.get("user_data"):
            return RedirectResponse(url="/login", status_code=303)
        return await func(request, *args, **kwargs)
    return wrapper
    
