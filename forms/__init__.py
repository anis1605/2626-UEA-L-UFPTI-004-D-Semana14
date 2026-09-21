"""
Paquete forms para la organización modular de formularios del Proyecto Integrador.
Contiene las clases de formularios para cada módulo de la aplicación web:
- LoginForm: Autenticación de usuarios
- RegistroUsuarioForm: Registro de nuevos usuarios
- ProductoForm: Módulo de Productos
- ClienteForm: Módulo de Clientes
- ProveedorForm: Módulo de Proveedores
- FacturacionForm: Módulo de Facturación
"""

from .login_form import LoginForm
from .usuario_form import RegistroUsuarioForm
from .producto_form import ProductoForm
from .cliente_form import ClienteForm
from .proveedor_form import ProveedorForm
from .facturacion_form import FacturacionForm

__all__ = [
    'LoginForm',
    'RegistroUsuarioForm',
    'ProductoForm',
    'ClienteForm',
    'ProveedorForm',
    'FacturacionForm'
]
