"""
Aplicación Principal Flask - Sistema de Gestión de Ferretería
Proyecto Integrador U4 - Avance 14/16 (Semana 14)
Incorpora Autenticación Funcional con Flask-Login, Werkzeug y MySQL.
"""
import datetime
from flask import Flask, render_template, request, redirect, url_for, flash
from flask_wtf.csrf import CSRFProtect
from flask_login import (
    LoginManager,
    login_user,
    logout_user,
    login_required,
    current_user
)
from conexion import obtener_conexion, inicializar_base_datos
from models import Usuario
from forms import (
    LoginForm,
    RegistroUsuarioForm,
    ProductoForm,
    ClienteForm,
    ProveedorForm,
    FacturacionForm
)

app = Flask(__name__)

# Configuración de clave secreta para la gestión de sesiones y protección CSRF con Flask-WTF
app.config['SECRET_KEY'] = 'clave_secreta_super_segura_ferreteria_el_constructor_2026_semana14'
csrf = CSRFProtect(app)

# Configuración del gestor de sesiones Flask-Login
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'
login_manager.login_message = 'Debe iniciar sesión para acceder a las funciones administrativas del sistema.'
login_manager.login_message_category = 'warning'


@login_manager.user_loader
def load_user(user_id):
    """
    Recupera la instancia del usuario activo desde la base de datos MySQL por su ID.
    Requerido obligatoriamente por Flask-Login.
    """
    return Usuario.obtener_por_id(user_id)


# Información general del sistema (variables globales inyectadas a plantillas)
SISTEMA_INFO = {
    "empresa": "Ferretería El Tornillo Dorado",
    "desarrollador": "Clara Anahi Gonzalez Apolo",
    "asignatura": "Desarrollo de Aplicaciones Web",
    "periodo": "2026-2026",
    "sucursal_principal": "Terminal Terrestre de Puyo",
    "telefono_contacto": "+123 456 7890",
    "email_contacto": "ferreteriaelconstructor@ferreterias.com"
}

# Inicializar esquema relacional y tabla de usuarios en MySQL al iniciar la aplicación
inicializar_base_datos()


@app.context_processor
def inject_global_vars():
    """Inyecta la información general del sistema en todas las plantillas Jinja2."""
    return dict(sistema=SISTEMA_INFO)


# ==============================================================================
# MÓDULO DE AUTENTICACIÓN Y SESIONES (SEMANA 14)
# ==============================================================================

@app.route('/registro', methods=['GET', 'POST'])
def registro():
    """
    REGISTRO DE USUARIOS:
    Permite registrar nuevos usuarios en la base de datos MySQL almacenando
    sus contraseñas protegidas con hash seguro (Werkzeug scrypt).
    """
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))

    form = RegistroUsuarioForm()
    if form.validate_on_submit():
        nombre_usuario = form.usuario.data.strip()
        password_plano = form.password.data
        nombre_completo = form.nombre.data.strip()
        rol = form.rol.data

        try:
            Usuario.crear_usuario(
                usuario=nombre_usuario,
                password_plano=password_plano,
                nombre=nombre_completo,
                rol=rol
            )
            flash(
                f"¡Usuario '{nombre_usuario}' registrado exitosamente con contraseña segura! Ya puede iniciar sesión.",
                "success"
            )
            return redirect(url_for('login'))
        except Exception as e:
            flash(f"Error al registrar el usuario en MySQL: {e}", "danger")

    return render_template('registro.html', form=form)


@app.route('/login', methods=['GET', 'POST'])
def login():
    """
    INICIO DE SESIÓN:
    Valida credenciales ingresadas comparando el hash almacenado con check_password_hash.
    Inicia la sesión mediante login_user y redirige al dashboard o a la ruta solicitada.
    """
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))

    form = LoginForm()
    if form.validate_on_submit():
        nombre_usuario = form.usuario.data.strip()
        password_plano = form.password.data
        remember = form.remember_me.data

        usuario = Usuario.obtener_por_usuario(nombre_usuario)
        if usuario and usuario.verificar_password(password_plano):
            login_user(usuario, remember=remember)
            flash(f"¡Bienvenido(a) {usuario.nombre or usuario.usuario}! Ha iniciado sesión correctamente.", "success")
            next_page = request.args.get('next')
            if next_page and next_page.startswith('/'):
                return redirect(next_page)
            return redirect(url_for('dashboard'))
        else:
            flash("Nombre de usuario o contraseña incorrectos. Verifique sus credenciales.", "danger")

    return render_template('login.html', form=form)


@app.route('/logout')
@login_required
def logout():
    """
    CIERRE DE SESIÓN:
    Finaliza la sesión del usuario actual mediante logout_user() y redirige al login.
    """
    nombre = current_user.nombre or current_user.usuario
    logout_user()
    flash(f"Hasta pronto, {nombre}. Ha cerrado sesión de forma segura.", "info")
    return redirect(url_for('login'))


# ==============================================================================
# RUTA PRINCIPAL (PÚBLICA) Y DASHBOARD (PROTEGIDO)
# ==============================================================================

@app.route('/')
def index():
    """Página pública de bienvenida con resumen estadístico del negocio."""
    conn = obtener_conexion()
    cursor = conn.cursor(dictionary=True)

    cursor.execute('SELECT COUNT(*) AS total FROM productos')
    total_productos = cursor.fetchone()['total']

    cursor.execute('SELECT COUNT(*) AS total FROM clientes')
    total_clientes = cursor.fetchone()['total']

    cursor.execute('SELECT COUNT(*) AS total FROM proveedores')
    total_proveedores = cursor.fetchone()['total']

    cursor.execute('SELECT COUNT(*) AS total FROM facturas')
    total_facturas = cursor.fetchone()['total']

    cursor.close()
    conn.close()

    resumen = {
        "total_productos": total_productos,
        "total_clientes": total_clientes,
        "total_proveedores": total_proveedores,
        "total_facturas": total_facturas
    }
    return render_template('index.html', resumen=resumen)


@app.route('/dashboard')
@login_required
def dashboard():
    """
    PANEL DE CONTROL ADMINISTRATIVO (PROTEGIDO CON @login_required):
    Muestra estadísticas y accesos directos únicamente al personal autenticado.
    """
    conn = obtener_conexion()
    cursor = conn.cursor(dictionary=True)

    cursor.execute('SELECT COUNT(*) AS total FROM productos')
    total_productos = cursor.fetchone()['total']

    cursor.execute('SELECT COUNT(*) AS total FROM clientes')
    total_clientes = cursor.fetchone()['total']

    cursor.execute('SELECT COUNT(*) AS total FROM proveedores')
    total_proveedores = cursor.fetchone()['total']

    cursor.execute('SELECT COUNT(*) AS total FROM facturas')
    total_facturas = cursor.fetchone()['total']

    cursor.close()
    conn.close()

    resumen = {
        "total_productos": total_productos,
        "total_clientes": total_clientes,
        "total_proveedores": total_proveedores,
        "total_facturas": total_facturas
    }
    return render_template('dashboard.html', resumen=resumen)


# ==============================================================================
# MÓDULO DE PRODUCTOS (CRUD COMPLETO CON MYSQL Y PROTEGIDO CON @login_required)
# ==============================================================================

@app.route('/productos')
@login_required
def productos():
    """
    OPERACIÓN SELECT (LISTAR):
    Recupera los productos desde MySQL aplicando LEFT JOIN con la tabla proveedores
    para evidenciar relaciones entre tablas mediante Clave Foránea (FK).
    """
    conn = obtener_conexion()
    cursor = conn.cursor(dictionary=True)

    query = """
        SELECT p.id, p.nombre, p.categoria, p.unidad, p.stock, p.precio, p.proveedor_ruc,
               pr.empresa AS proveedor_empresa
        FROM productos p
        LEFT JOIN proveedores pr ON p.proveedor_ruc = pr.ruc
        ORDER BY p.id ASC
    """
    cursor.execute(query)
    productos_db = cursor.fetchall()

    cursor.close()
    conn.close()
    return render_template('productos.html', productos=productos_db)


@app.route('/productos/nuevo', methods=['GET', 'POST'])
@login_required
def nuevo_producto():
    """
    OPERACIÓN INSERT (AGREGAR):
    Valida los datos con Flask-WTF y realiza un INSERT parametrizado con marcadores %s.
    """
    conn = obtener_conexion()
    cursor = conn.cursor(dictionary=True)

    # Cargar lista de proveedores para el campo FK SelectField
    cursor.execute("SELECT ruc, empresa FROM proveedores WHERE activo = 1 ORDER BY empresa ASC")
    proveedores = cursor.fetchall()
    opciones_proveedores = [('', '-- Seleccione Proveedor --')] + [(p['ruc'], f"{p['empresa']} ({p['ruc']})") for p in proveedores]

    form = ProductoForm()
    form.proveedor_ruc.choices = opciones_proveedores

    if form.validate_on_submit():
        # Generar identificador autoincremental de formato PROD-XXX
        cursor.execute("SELECT id FROM productos ORDER BY id DESC LIMIT 1")
        ultimo = cursor.fetchone()
        if ultimo and ultimo['id'].startswith('PROD-'):
            try:
                num = int(ultimo['id'].split('-')[1]) + 1
            except ValueError:
                num = 1
        else:
            num = 1
        nuevo_id = f"PROD-{num:03d}"

        nombre = form.nombre.data.strip()
        categoria = form.categoria.data
        unidad = form.unidad.data
        stock = int(form.stock.data)
        precio = float(form.precio.data)
        proveedor_ruc = form.proveedor_ruc.data.strip() if form.proveedor_ruc.data else None

        insert_query = """
            INSERT INTO productos (id, nombre, categoria, unidad, stock, precio, proveedor_ruc)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
        """
        cursor.execute(insert_query, (nuevo_id, nombre, categoria, unidad, stock, precio, proveedor_ruc))
        conn.commit()

        cursor.close()
        conn.close()

        flash(f"Producto '{nombre}' agregado exitosamente con código {nuevo_id} en MySQL.", "success")
        return redirect(url_for('productos'))

    cursor.close()
    conn.close()
    return render_template('formulario_producto.html', form=form, titulo="Registrar Nuevo Producto", es_edicion=False)


@app.route('/productos/editar/<id>', methods=['GET', 'POST'])
@login_required
def editar_producto(id):
    """
    OPERACIÓN UPDATE (MODIFICAR):
    Recupera el registro seleccionado con WHERE id = %s, precarga los valores en el formulario
    Flask-WTF y ejecuta un UPDATE parametrizado con commit().
    """
    conn = obtener_conexion()
    cursor = conn.cursor(dictionary=True)

    cursor.execute("SELECT * FROM productos WHERE id = %s", (id,))
    producto = cursor.fetchone()

    if not producto:
        cursor.close()
        conn.close()
        flash(f"El producto con código '{id}' no fue encontrado en MySQL.", "danger")
        return redirect(url_for('productos'))

    cursor.execute("SELECT ruc, empresa FROM proveedores WHERE activo = 1 ORDER BY empresa ASC")
    proveedores = cursor.fetchall()
    opciones_proveedores = [('', '-- Sin Proveedor Asignado --')] + [(p['ruc'], f"{p['empresa']} ({p['ruc']})") for p in proveedores]

    form = ProductoForm(data=producto)
    form.proveedor_ruc.choices = opciones_proveedores

    if form.validate_on_submit():
        nombre = form.nombre.data.strip()
        categoria = form.categoria.data
        unidad = form.unidad.data
        stock = int(form.stock.data)
        precio = float(form.precio.data)
        proveedor_ruc = form.proveedor_ruc.data.strip() if form.proveedor_ruc.data else None

        update_query = """
            UPDATE productos 
            SET nombre = %s, categoria = %s, unidad = %s, stock = %s, precio = %s, proveedor_ruc = %s 
            WHERE id = %s
        """
        cursor.execute(update_query, (nombre, categoria, unidad, stock, precio, proveedor_ruc, id))
        conn.commit()

        cursor.close()
        conn.close()

        flash(f"Producto '{id}' modificado exitosamente en MySQL.", "success")
        return redirect(url_for('productos'))

    cursor.close()
    conn.close()
    return render_template('formulario_producto.html', form=form, titulo=f"Editar Producto ({producto['id']})", es_edicion=True)


@app.route('/productos/eliminar/<id>', methods=['POST'])
@login_required
def eliminar_producto(id):
    """
    OPERACIÓN DELETE (ELIMINAR):
    Elimina exclusivamente el registro seleccionado utilizando WHERE id = %s.
    """
    conn = obtener_conexion()
    cursor = conn.cursor(dictionary=True)

    cursor.execute("SELECT nombre FROM productos WHERE id = %s", (id,))
    producto = cursor.fetchone()

    if not producto:
        cursor.close()
        conn.close()
        flash(f"El producto con código '{id}' no existe en MySQL.", "warning")
        return redirect(url_for('productos'))

    cursor.execute("DELETE FROM productos WHERE id = %s", (id,))
    conn.commit()

    cursor.close()
    conn.close()

    flash(f"Producto '{producto['nombre']}' ({id}) eliminado permanentemente de MySQL.", "success")
    return redirect(url_for('productos'))


# ==============================================================================
# MÓDULO DE CLIENTES (PROTEGIDO CON @login_required)
# ==============================================================================

@app.route('/clientes')
@login_required
def clientes():
    conn = obtener_conexion()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM clientes ORDER BY nombre ASC")
    clientes_db = cursor.fetchall()
    cursor.close()
    conn.close()
    return render_template('clientes.html', clientes=clientes_db)


@app.route('/clientes/nuevo', methods=['GET', 'POST'])
@login_required
def nuevo_cliente():
    form = ClienteForm()
    if form.validate_on_submit():
        ruc = form.ruc.data.strip()
        nombre = form.nombre.data.strip()
        tipo = form.tipo.data
        telefono = form.telefono.data.strip()
        email = form.email.data.strip()
        direccion = form.direccion.data.strip()

        conn = obtener_conexion()
        cursor = conn.cursor(dictionary=True)

        cursor.execute("SELECT ruc FROM clientes WHERE ruc = %s", (ruc,))
        if cursor.fetchone():
            cursor.close()
            conn.close()
            flash(f"El cliente con RUC/Cédula '{ruc}' ya se encuentra registrado en MySQL.", "warning")
            return render_template('formulario_cliente.html', form=form, titulo="Registrar Nuevo Cliente", es_edicion=False)

        insert_query = """
            INSERT INTO clientes (ruc, nombre, tipo, telefono, email, direccion) 
            VALUES (%s, %s, %s, %s, %s, %s)
        """
        cursor.execute(insert_query, (ruc, nombre, tipo, telefono, email, direccion))
        conn.commit()
        cursor.close()
        conn.close()

        flash(f"Cliente '{nombre}' registrado correctamente en MySQL.", "success")
        return redirect(url_for('clientes'))

    return render_template('formulario_cliente.html', form=form, titulo="Registrar Nuevo Cliente", es_edicion=False)


@app.route('/clientes/editar/<ruc>', methods=['GET', 'POST'])
@login_required
def editar_cliente(ruc):
    conn = obtener_conexion()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM clientes WHERE ruc = %s", (ruc,))
    cliente = cursor.fetchone()

    if not cliente:
        cursor.close()
        conn.close()
        flash(f"El cliente con RUC '{ruc}' no fue encontrado en MySQL.", "danger")
        return redirect(url_for('clientes'))

    form = ClienteForm(data=cliente)

    if form.validate_on_submit():
        nombre = form.nombre.data.strip()
        tipo = form.tipo.data
        telefono = form.telefono.data.strip()
        email = form.email.data.strip()
        direccion = form.direccion.data.strip()

        update_query = """
            UPDATE clientes 
            SET nombre = %s, tipo = %s, telefono = %s, email = %s, direccion = %s 
            WHERE ruc = %s
        """
        cursor.execute(update_query, (nombre, tipo, telefono, email, direccion, ruc))
        conn.commit()
        cursor.close()
        conn.close()

        flash(f"Cliente '{nombre}' actualizado correctamente en MySQL.", "success")
        return redirect(url_for('clientes'))

    cursor.close()
    conn.close()
    return render_template('formulario_cliente.html', form=form, titulo=f"Editar Cliente ({cliente['nombre']})", es_edicion=True)


@app.route('/clientes/eliminar/<ruc>', methods=['POST'])
@login_required
def eliminar_cliente(ruc):
    conn = obtener_conexion()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("DELETE FROM clientes WHERE ruc = %s", (ruc,))
    conn.commit()
    cursor.close()
    conn.close()

    flash(f"Cliente con RUC '{ruc}' eliminado correctamente de MySQL.", "success")
    return redirect(url_for('clientes'))


# ==============================================================================
# MÓDULO DE PROVEEDORES (PROTEGIDO CON @login_required)
# ==============================================================================

@app.route('/proveedores')
@login_required
def proveedores():
    conn = obtener_conexion()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM proveedores ORDER BY empresa ASC")
    proveedores_db = cursor.fetchall()
    cursor.close()
    conn.close()
    return render_template('proveedores.html', proveedores=proveedores_db)


@app.route('/proveedores/nuevo', methods=['GET', 'POST'])
@login_required
def nuevo_proveedor():
    form = ProveedorForm()
    if form.validate_on_submit():
        ruc = form.ruc.data.strip()
        empresa = form.empresa.data.strip()
        categoria = form.categoria.data
        contacto = form.contacto.data.strip()
        telefono = form.telefono.data.strip()
        ciudad = form.ciudad.data.strip()
        activo = 1 if form.activo.data else 0

        conn = obtener_conexion()
        cursor = conn.cursor(dictionary=True)

        cursor.execute("SELECT ruc FROM proveedores WHERE ruc = %s", (ruc,))
        if cursor.fetchone():
            cursor.close()
            conn.close()
            flash(f"El proveedor con RUC '{ruc}' ya se encuentra registrado en MySQL.", "warning")
            return render_template('formulario_proveedor.html', form=form, titulo="Registrar Nuevo Proveedor", es_edicion=False)

        insert_query = """
            INSERT INTO proveedores (ruc, empresa, categoria, contacto, telefono, ciudad, activo) 
            VALUES (%s, %s, %s, %s, %s, %s, %s)
        """
        cursor.execute(insert_query, (ruc, empresa, categoria, contacto, telefono, ciudad, activo))
        conn.commit()
        cursor.close()
        conn.close()

        flash(f"Proveedor '{empresa}' registrado correctamente en MySQL.", "success")
        return redirect(url_for('proveedores'))

    return render_template('formulario_proveedor.html', form=form, titulo="Registrar Nuevo Proveedor", es_edicion=False)


@app.route('/proveedores/editar/<ruc>', methods=['GET', 'POST'])
@login_required
def editar_proveedor(ruc):
    conn = obtener_conexion()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM proveedores WHERE ruc = %s", (ruc,))
    proveedor = cursor.fetchone()

    if not proveedor:
        cursor.close()
        conn.close()
        flash(f"El proveedor con RUC '{ruc}' no fue encontrado en MySQL.", "danger")
        return redirect(url_for('proveedores'))

    form = ProveedorForm(data=proveedor)

    if form.validate_on_submit():
        empresa = form.empresa.data.strip()
        categoria = form.categoria.data
        contacto = form.contacto.data.strip()
        telefono = form.telefono.data.strip()
        ciudad = form.ciudad.data.strip()
        activo = 1 if form.activo.data else 0

        update_query = """
            UPDATE proveedores 
            SET empresa = %s, categoria = %s, contacto = %s, telefono = %s, ciudad = %s, activo = %s 
            WHERE ruc = %s
        """
        cursor.execute(update_query, (empresa, categoria, contacto, telefono, ciudad, activo, ruc))
        conn.commit()
        cursor.close()
        conn.close()

        flash(f"Proveedor '{empresa}' actualizado correctamente en MySQL.", "success")
        return redirect(url_for('proveedores'))

    cursor.close()
    conn.close()
    return render_template('formulario_proveedor.html', form=form, titulo=f"Editar Proveedor ({proveedor['empresa']})", es_edicion=True)


@app.route('/proveedores/eliminar/<ruc>', methods=['POST'])
@login_required
def eliminar_proveedor(ruc):
    conn = obtener_conexion()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("DELETE FROM proveedores WHERE ruc = %s", (ruc,))
    conn.commit()
    cursor.close()
    conn.close()

    flash(f"Proveedor con RUC '{ruc}' eliminado correctamente de MySQL.", "success")
    return redirect(url_for('proveedores'))


# ==============================================================================
# MÓDULO DE FACTURACIÓN (PROTEGIDO CON @login_required)
# ==============================================================================

@app.route('/facturacion')
@login_required
def facturacion():
    conn = obtener_conexion()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM facturas ORDER BY fecha DESC")
    facturas_db = cursor.fetchall()
    cursor.close()
    conn.close()
    return render_template('facturacion.html', facturas=facturas_db)


@app.route('/facturacion/nueva', methods=['GET', 'POST'])
@login_required
def nueva_factura():
    form = FacturacionForm()
    if form.validate_on_submit():
        conn = obtener_conexion()
        cursor = conn.cursor(dictionary=True)

        cursor.execute("SELECT numero FROM facturas ORDER BY numero DESC LIMIT 1")
        ultimo = cursor.fetchone()
        if ultimo and ultimo['numero'].startswith('FAC-'):
            try:
                num = int(ultimo['numero'].split('-')[1]) + 1
            except ValueError:
                num = 100
        else:
            num = 100
        nuevo_numero = f"FAC-{num:05d}"

        subtotal = float(form.subtotal.data)
        iva = round(subtotal * 0.15, 2)
        total = round(subtotal + iva, 2)
        fecha_str = form.fecha.data.strftime('%Y-%m-%d') if hasattr(form.fecha.data, 'strftime') else str(form.fecha.data)
        cliente = form.cliente.data.strip()
        estado = form.estado.data

        insert_query = """
            INSERT INTO facturas (numero, fecha, cliente_nombre, subtotal, iva, total, estado) 
            VALUES (%s, %s, %s, %s, %s, %s, %s)
        """
        cursor.execute(insert_query, (nuevo_numero, fecha_str, cliente, subtotal, iva, total, estado))
        conn.commit()
        cursor.close()
        conn.close()

        flash(f"Factura '{nuevo_numero}' emitida exitosamente en MySQL.", "success")
        return redirect(url_for('facturacion'))

    if request.method == 'GET' and not form.fecha.data:
        form.fecha.data = datetime.date.today()

    return render_template('formulario_facturacion.html', form=form, titulo="Emitir Nueva Factura", es_edicion=False)


@app.route('/facturacion/editar/<numero>', methods=['GET', 'POST'])
@login_required
def editar_factura(numero):
    conn = obtener_conexion()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM facturas WHERE numero = %s", (numero,))
    factura = cursor.fetchone()

    if not factura:
        cursor.close()
        conn.close()
        flash(f"La factura con número '{numero}' no fue encontrada en MySQL.", "danger")
        return redirect(url_for('facturacion'))

    datos_form = dict(factura)
    datos_form['cliente'] = factura['cliente_nombre']
    if isinstance(datos_form.get('fecha'), str):
        try:
            datos_form['fecha'] = datetime.datetime.strptime(datos_form['fecha'], '%Y-%m-%d').date()
        except ValueError:
            pass

    form = FacturacionForm(data=datos_form)

    if form.validate_on_submit():
        subtotal = float(form.subtotal.data)
        iva = round(subtotal * 0.15, 2)
        total = round(subtotal + iva, 2)
        fecha_str = form.fecha.data.strftime('%Y-%m-%d') if hasattr(form.fecha.data, 'strftime') else str(form.fecha.data)
        cliente = form.cliente.data.strip()
        estado = form.estado.data

        update_query = """
            UPDATE facturas 
            SET fecha = %s, cliente_nombre = %s, subtotal = %s, iva = %s, total = %s, estado = %s 
            WHERE numero = %s
        """
        cursor.execute(update_query, (fecha_str, cliente, subtotal, iva, total, estado, numero))
        conn.commit()
        cursor.close()
        conn.close()

        flash(f"Factura '{numero}' actualizada correctamente en MySQL.", "success")
        return redirect(url_for('facturacion'))

    cursor.close()
    conn.close()
    return render_template('formulario_facturacion.html', form=form, titulo=f"Editar Factura ({factura['numero']})", es_edicion=True)


@app.route('/facturacion/eliminar/<numero>', methods=['POST'])
@login_required
def eliminar_factura(numero):
    conn = obtener_conexion()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("DELETE FROM facturas WHERE numero = %s", (numero,))
    conn.commit()
    cursor.close()
    conn.close()

    flash(f"Factura '{numero}' eliminada correctamente de MySQL.", "success")
    return redirect(url_for('facturacion'))


if __name__ == '__main__':
    app.run(debug=True, port=5000)
