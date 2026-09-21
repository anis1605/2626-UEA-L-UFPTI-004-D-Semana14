"""
Módulo de Modelos - Sistema Ferretería El Tornillo Dorado
Define la entidad Usuario compatible con Flask-Login y las operaciones relacionales asociadas.
"""
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from conexion.conexion import obtener_conexion


class Usuario(UserMixin):
    """
    Representa a un usuario del sistema compatible con Flask-Login.
    Hereda de UserMixin para implementar automáticamente is_authenticated,
    is_active, is_anonymous y get_id().
    """
    def __init__(self, id, usuario, password, nombre='', rol='admin', fecha_creacion=None):
        self.id = str(id)
        self.usuario = usuario
        self.password = password
        self.nombre = nombre
        self.rol = rol
        self.fecha_creacion = fecha_creacion

    def verificar_password(self, password_plano):
        """
        Verifica si la contraseña en texto plano coincide con el hash almacenado.
        Nunca compara directamente texto plano.
        """
        return check_password_hash(self.password, password_plano)

    @classmethod
    def obtener_por_id(cls, user_id):
        """
        Recupera un usuario desde MySQL mediante su identificador primario (ID).
        Utilizado principalmente por el callback load_user de Flask-Login.
        """
        conn = obtener_conexion()
        try:
            cursor = conn.cursor(dictionary=True)
            cursor.execute(
                "SELECT id, usuario, password, nombre, rol, fecha_creacion FROM usuarios WHERE id = %s",
                (user_id,)
            )
            row = cursor.fetchone()
            if row:
                return cls(
                    id=row['id'],
                    usuario=row['usuario'],
                    password=row['password'],
                    nombre=row.get('nombre', ''),
                    rol=row.get('rol', 'admin'),
                    fecha_creacion=row.get('fecha_creacion')
                )
            return None
        finally:
            cursor.close()
            conn.close()

    @classmethod
    def obtener_por_usuario(cls, nombre_usuario):
        """
        Recupera un usuario desde MySQL mediante su nombre de usuario único.
        """
        conn = obtener_conexion()
        try:
            cursor = conn.cursor(dictionary=True)
            cursor.execute(
                "SELECT id, usuario, password, nombre, rol, fecha_creacion FROM usuarios WHERE usuario = %s",
                (nombre_usuario,)
            )
            row = cursor.fetchone()
            if row:
                return cls(
                    id=row['id'],
                    usuario=row['usuario'],
                    password=row['password'],
                    nombre=row.get('nombre', ''),
                    rol=row.get('rol', 'admin'),
                    fecha_creacion=row.get('fecha_creacion')
                )
            return None
        finally:
            cursor.close()
            conn.close()

    @classmethod
    def crear_usuario(cls, usuario, password_plano, nombre='', rol='admin'):
        """
        Inserta un nuevo usuario en MySQL con la contraseña protegida mediante un hash seguro (scrypt).
        """
        password_hash = generate_password_hash(password_plano, method='scrypt')
        conn = obtener_conexion()
        try:
            cursor = conn.cursor()
            cursor.execute(
                "INSERT INTO usuarios (usuario, password, nombre, rol) VALUES (%s, %s, %s, %s)",
                (usuario, password_hash, nombre, rol)
            )
            conn.commit()
            nuevo_id = cursor.lastrowid
            return cls.obtener_por_id(nuevo_id)
        finally:
            cursor.close()
            conn.close()
