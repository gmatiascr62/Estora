from sqlalchemy import Column, Integer, String, ForeignKey, DateTime
from sqlalchemy.orm import relationship, declarative_base
from datetime import datetime

Base = declarative_base()

class Usuario(Base):
    __tablename__ = "usuarios"
    user_id = Column(Integer, primary_key=True, autoincrement=True)
    username = Column(String, unique=True, index=True)
    edad = Column(Integer, nullable=True)
    telefono = Column(String, nullable=True)
    token = Column(String, nullable=True)
    sid = Column(String, nullable=True)

    def __repr__(self):
        return f"<Usuario - {self.username}>"
    
    def to_dict(self):
        return {
            "user_id": self.user_id,
            "username": self.username,
            "edad": self.edad,
            "telefono": self.telefono,
            "token": self.token,
            "sid": self.sid,
        }

class Mensaje(Base):
    __tablename__ = "mensajes"

    id = Column(Integer, primary_key=True, autoincrement=True)
    remitente_id = Column(Integer, ForeignKey("usuarios.user_id"), nullable=False)
    destinatario_id = Column(Integer, ForeignKey("usuarios.user_id"), nullable=False)
    contenido = Column(String, nullable=False)
    timestamp = Column(DateTime, default=datetime.utcnow)

    remitente = relationship("Usuario", foreign_keys=[remitente_id])
    destinatario = relationship("Usuario", foreign_keys=[destinatario_id])

    def __repr__(self):
        return f"<Mensaje de {self.remitente_id} a {self.destinatario_id} - {self.timestamp}>"


class Solicitud(Base):
    __tablename__ = "solicitudes"

    id = Column(Integer, primary_key=True, autoincrement=True)
    de_id = Column(Integer, ForeignKey("usuarios.user_id"), nullable=False)
    para_id = Column(Integer, ForeignKey("usuarios.user_id"), nullable=False)
    estado = Column(String, default="pendiente")
    timestamp = Column(DateTime, default=datetime.utcnow)

    de_usuario = relationship("Usuario", foreign_keys=[de_id])
    para_usuario = relationship("Usuario", foreign_keys=[para_id])

    def __repr__(self):
        return f"<Solicitud de {self.de_id} a {self.para_id} - {self.estado}>"
        