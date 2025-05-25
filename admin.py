from sqladmin import Admin, ModelView
from sqladmin.authentication import AuthenticationBackend
from fastapi import Request
from models.models import Usuario, Mensaje, Solicitud
from database import engine

# Backend de autenticación básico: usuario fijo
class AdminAuth(AuthenticationBackend):
    def __init__(self, secret_key: str):
        self.secret_key = secret_key
        self.middlewares = []

    async def login(self, request: Request) -> bool:
        form = await request.form()
        username = form.get("username")
        password = form.get("password")
        if username == "yo" and password == "1234":
            request.session["token"] = "admin_token"  # Esto es clave
            return True
        return False

    async def logout(self, request: Request) -> bool:
        return True

    async def authenticate(self, request: Request) -> bool:
        # Devuelve True si ya está logueado (session guardada por sqladmin)
        return request.session.get("token") is not None

# Vistas del admin
class UsuarioAdmin(ModelView, model=Usuario):
    column_list = [Usuario.user_id, Usuario.username, Usuario.edad, Usuario.telefono]

class MensajeAdmin(ModelView, model=Mensaje):
    column_list = [Mensaje.id, Mensaje.remitente_id, Mensaje.destinatario_id, Mensaje.contenido, Mensaje.timestamp]

class SolicitudAdmin(ModelView, model=Solicitud):
    column_list = [Solicitud.id, Solicitud.de_id, Solicitud.para_id, Solicitud.estado, Solicitud.timestamp]

# Función para registrar el admin
def configurar_admin(app):
    admin = Admin(app, engine, authentication_backend=AdminAuth(secret_key="clav66272772jdhdhdva98ta"))
    admin.add_view(UsuarioAdmin)
    admin.add_view(MensajeAdmin)
    admin.add_view(SolicitudAdmin)
