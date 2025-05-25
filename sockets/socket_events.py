from fastapi_socketio import SocketManager

sio = None

def init_socket(app):
    global sio
    sio = SocketManager(app, mount_location="/socket.io", cors_allowed_origins=[])

    @sio.on('connect')
    async def connect(sid, environ):
        print(f"Cliente conectado: {sid}")

    @sio.on('mensaje')
    async def mensaje(sid, data):
        print(f"Se conecto: {data}")
        await sio.emit('respuesta', {'mensaje': 'Hola desde el servidor'}, room=sid)

    @sio.on('disconnect')
    async def disconnect(sid):
        print(f"Cliente desconectado: {sid}")