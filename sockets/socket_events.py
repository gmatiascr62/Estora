from fastapi_socketio import SocketManager
from auth_utils import persona_actual
from database import usuarios_en_memoria

sio = None

def init_socket(app):
    global sio
    sio = SocketManager(app, mount_location="/socket.io", cors_allowed_origins=[])

    @sio.on('connect')
    async def connect(sid, environ):
        print(f"Cliente conectado: {sid}")
        persona_actual().sid = sid
        print("sid en persona actual: ", persona_actual().sid)

    @sio.on('mensaje')
    async def mensaje(sid, data):
        print(f"Se conecto: {data}")
        await sio.emit('respuesta', {'mensaje': 'Hola desde el servidor'}, room=sid)

    
    @sio.on('disconnect')
    async def disconnect(sid):
        print(f"Cliente desconectado: {sid}")
        for persona in usuarios_en_memoria.values():
            if persona.sid == sid:
                print(f"{persona.username} se desconectó.")
                persona.sid = None
                break