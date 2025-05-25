from sqlalchemy.orm import Session
from models.models import Usuario
from database import engine, SessionLocal

class Persona:
    def __init__(self, usuario: Usuario):
        self.id = usuario.user_id
        self._username = usuario.username
        self._edad = usuario.edad
        self._telefono = usuario.telefono

    @property
    def username(self):
        return self._username

    @property
    def edad(self):
        return self._edad

    @edad.setter
    def edad(self, nueva_edad):
        self._edad = nueva_edad
        self._actualizar_campo("edad", nueva_edad)

    @property
    def telefono(self):
        return self._telefono

    @telefono.setter
    def telefono(self, nuevo_tel):
        self._telefono = nuevo_tel
        self._actualizar_campo("telefono", nuevo_tel)

    def _actualizar_campo(self, campo, valor):
        db: Session = SessionLocal()
        usuario = db.query(Usuario).filter_by(user_id=self.id).first()
        if usuario:
            setattr(usuario, campo, valor)
            db.commit()
        db.close()

    def to_dict(self):
        return {
            "id": self.id,
            "username": self.username,
            "edad": self.edad,
            "telefono": self.telefono
        }
    
    def __repr__(self):
        return f"<Persona {self.id} - {self.username}>"