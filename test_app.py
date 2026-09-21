"""
Suite de Pruebas Automatizadas - Semana 14: Sistema de Login Funcional con Flask-Login y MySQL
Verifica:
1. Conexión y existencia de la tabla usuarios en MySQL
2. Registro de nuevo usuario mediante formulario Flask-WTF
3. Comprobación en base de datos de contraseña encriptada (scrypt hash, nunca texto plano)
4. Rechazo de credenciales incorrectas
5. Inicio de sesión exitoso con credenciales correctas
6. Redirección obligatoria al login al intentar acceder a rutas privadas sin autenticación (@login_required)
7. Acceso a rutas protegidas con sesión activa y despliegue del usuario autenticado
8. Cierre de sesión seguro con logout_user()
9. Revocación inmediata del acceso a rutas privadas tras logout
10. Preservación del CRUD de productos de la Semana 13
"""
import pytest
from app import app
from conexion.conexion import obtener_conexion
from models import Usuario


@pytest.fixture
def client():
    app.config['TESTING'] = True
    app.config['WTF_CSRF_ENABLED'] = False
    with app.test_client() as client:
        yield client


def test_01_tabla_usuarios_existe_en_mysql():
    """Comprueba que la tabla usuarios existe en MySQL y contiene registros válidos."""
    conn = obtener_conexion()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SHOW TABLES LIKE 'usuarios'")
    tabla = cursor.fetchone()
    assert tabla is not None, "La tabla 'usuarios' no existe en ferreteria_db."

    cursor.execute("SELECT id, usuario, password FROM usuarios WHERE usuario = 'admin'")
    admin_user = cursor.fetchone()
    assert admin_user is not None, "El usuario admin inicial debe existir en la base de datos."
    assert admin_user['password'].startswith(('scrypt:', 'pbkdf2:')), "La contraseña debe estar hasheada."
    cursor.close()
    conn.close()


def test_02_registro_nuevo_usuario_y_hash_en_mysql(client):
    """
    Prueba 1, 2 y 3 del avance:
    Registra un nuevo usuario y comprueba directamente en MySQL que se guardó
    y que la contraseña NO está en texto plano.
    """
    test_username = "test_clara_2026"
    test_password = "PasswordSeguro2026!"

    # Limpiar si existía previamente
    conn = obtener_conexion()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM usuarios WHERE usuario = %s", (test_username,))
    conn.commit()

    # Registro mediante petición POST
    response = client.post('/registro', data={
        'usuario': test_username,
        'nombre': 'Clara González Pruebas',
        'rol': 'admin',
        'password': test_password,
        'confirm_password': test_password
    }, follow_redirects=True)

    assert response.status_code == 200
    assert b"registrado exitosamente" in response.data or b"login" in response.data.lower()

    # Comprobación directa en MySQL
    cursor.execute("SELECT id, usuario, password, nombre FROM usuarios WHERE usuario = %s", (test_username,))
    row = cursor.fetchone()
    assert row is not None, f"El usuario {test_username} debe existir en MySQL."
    stored_hash = row[2]

    # Verificar que NO sea texto plano
    assert stored_hash != test_password, "¡FALLO CRÍTICO: La contraseña se almacenó en texto plano!"
    assert stored_hash.startswith(('scrypt:', 'pbkdf2:')), f"El hash debe tener formato seguro, obtenido: {stored_hash}"

    # Validar verificación de contraseña a nivel de modelo
    usuario_obj = Usuario.obtener_por_usuario(test_username)
    assert usuario_obj is not None
    assert usuario_obj.verificar_password(test_password) is True
    assert usuario_obj.verificar_password("ContraseñaEquivocada") is False

    cursor.close()
    conn.close()


def test_03_login_credenciales_incorrectas_rechazadas(client):
    """
    Prueba 4 del avance:
    Intenta iniciar sesión con una contraseña incorrecta y comprueba el rechazo.
    """
    response = client.post('/login', data={
        'usuario': 'admin',
        'password': 'password_totalmente_incorrecto',
        'remember_me': False
    }, follow_redirects=True)

    assert response.status_code == 200
    assert (b"incorrectos" in response.data or 
            b"Verifique sus credenciales" in response.data)


def test_04_rutas_protegidas_redirigen_a_login_sin_autenticacion(client):
    """
    Prueba obligatoria:
    Comprueba que el acceso no autenticado a rutas privadas redirija a /login.
    """
    rutas_protegidas = [
        '/dashboard',
        '/productos',
        '/productos/nuevo',
        '/clientes',
        '/proveedores',
        '/facturacion'
    ]

    for ruta in rutas_protegidas:
        response = client.get(ruta, follow_redirects=False)
        assert response.status_code == 302, f"La ruta '{ruta}' debió redirigir con 302 hacia /login"
        assert '/login' in response.headers.get('Location', ''), f"La redirección de '{ruta}' debe apuntar a /login"


def test_05_flujo_login_acceso_protegido_y_visualizacion_usuario(client):
    """
    Pruebas 5, 6 y 7 del avance:
    Inicia sesión con credenciales correctas, comprueba acceso a rutas protegidas
    y verifica que se muestre el usuario en la interfaz.
    """
    login_res = client.post('/login', data={
        'usuario': 'admin',
        'password': 'admin123',
        'remember_me': False
    }, follow_redirects=True)

    assert login_res.status_code == 200
    assert b"Ha iniciado sesi" in login_res.data or b"Dashboard" in login_res.data

    # Acceder a dashboard protegido
    dash_res = client.get('/dashboard')
    assert dash_res.status_code == 200
    assert b"admin" in dash_res.data or b"Administrador General" in dash_res.data
    assert b"Cerrar Sesi" in dash_res.data or b"Cerrar Sesi\xc3\xb3n" in dash_res.data

    # Acceder a productos protegido
    prod_res = client.get('/productos')
    assert prod_res.status_code == 200
    assert b"Cemento" in prod_res.data or b"Cat\xc3\xa1logo" in prod_res.data


def test_06_cierre_sesion_logout_y_bloqueo_inmediato(client):
    """
    Pruebas 8, 9 y 10 del avance:
    Cierra sesión (logout), comprueba redirección y confirma que el acceso a rutas
    protegidas vuelve a estar bloqueado.
    """
    # Iniciar sesión primero
    client.post('/login', data={
        'usuario': 'admin',
        'password': 'admin123'
    }, follow_redirects=True)

    # Cerrar sesión
    logout_res = client.get('/logout', follow_redirects=True)
    assert logout_res.status_code == 200
    assert b"cerrado sesi" in logout_res.data or b"Iniciar Sesi" in logout_res.data

    # Intentar acceder nuevamente a ruta protegida
    reintento = client.get('/dashboard', follow_redirects=False)
    assert reintento.status_code == 302
    assert '/login' in reintento.headers.get('Location', '')


def test_07_continuidad_crud_mysql_productos(client):
    """
    Comprueba que las operaciones CRUD de la Semana 13 sobre MySQL continúan operativas.
    """
    # Iniciar sesión como usuario autorizado
    client.post('/login', data={
        'usuario': 'admin',
        'password': 'admin123'
    }, follow_redirects=True)

    test_prod_id = "PROD-TEST-14"
    conn = obtener_conexion()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM productos WHERE id = %s", (test_prod_id,))
    conn.commit()

    # INSERT
    cursor.execute(
        "INSERT INTO productos (id, nombre, categoria, unidad, stock, precio, proveedor_ruc) VALUES (%s, %s, %s, %s, %s, %s, %s)",
        (test_prod_id, "Tornillo de Acero Grado 8", "Fijaciones", "Caja", 80, 14.50, "1790056789001")
    )
    conn.commit()

    # SELECT con JOIN
    cursor = conn.cursor(dictionary=True)
    cursor.execute("""
        SELECT p.*, pr.empresa 
        FROM productos p 
        LEFT JOIN proveedores pr ON p.proveedor_ruc = pr.ruc 
        WHERE p.id = %s
    """, (test_prod_id,))
    row = cursor.fetchone()
    assert row is not None
    assert row['empresa'] == "Adelca C.A."

    # UPDATE
    cursor.execute("UPDATE productos SET precio = 16.75, stock = 95 WHERE id = %s", (test_prod_id,))
    conn.commit()

    cursor.execute("SELECT precio, stock FROM productos WHERE id = %s", (test_prod_id,))
    actualizado = cursor.fetchone()
    assert float(actualizado['precio']) == 16.75
    assert actualizado['stock'] == 95

    # DELETE
    cursor.execute("DELETE FROM productos WHERE id = %s", (test_prod_id,))
    conn.commit()

    cursor.execute("SELECT * FROM productos WHERE id = %s", (test_prod_id,))
    assert cursor.fetchone() is None

    cursor.close()
    conn.close()
