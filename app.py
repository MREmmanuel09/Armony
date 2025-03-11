from flask import Flask, render_template, request, redirect, url_for, session
import mysql.connector
from werkzeug.security import generate_password_hash, check_password_hash
import os

app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY', 'your_secret_key')

db_config = {
    'host': os.environ.get('DB_HOST', ''),
    'user': os.environ.get('DB_USER', ''),
    'password': os.environ.get('DB_PASSWORD', ''),
    'database': os.environ.get('DB_NAME', '')
}

def conectar_db():
    try:
        db = mysql.connector.connect(**db_config)
        return db
    except mysql.connector.Error as err:
        print(f"Error al conectar a la base de datos: {err}")
        return None

# Funciones para interactuar con la base de datos (CRUD)

def get_categorias():
    db = conectar_db()
    if db is None:
        return []
    cursor = db.cursor(dictionary=True)
    try:
        cursor.execute("SELECT * FROM categorias")
        categorias = cursor.fetchall()
        return categorias
    except mysql.connector.Error as err:
        print(f"Error al obtener categorías: {err}")
        return []
    finally:
        cursor.close()
        db.close()

def agregar_categoria(nombre_categoria):
    db = conectar_db()
    if db is None:
        raise Exception("No se pudo conectar a la base de datos")
    cursor = db.cursor()
    try:
        sql = "INSERT INTO categorias (nombre_categoria) VALUES (%s)"
        cursor.execute(sql, (nombre_categoria,))
        db.commit()
    except mysql.connector.Error as err:
        db.rollback()
        print(f"Error al agregar categoría: {err}")
        raise err
    finally:
        cursor.close()
        db.close()

def get_categoria_por_id(categoria_id):
    db = conectar_db()
    if db is None:
        return None
    cursor = db.cursor(dictionary=True)
    try:
        sql = "SELECT * FROM categorias WHERE categoria_id = %s"
        cursor.execute(sql, (categoria_id,))
        categoria = cursor.fetchone()
        return categoria
    except mysql.connector.Error as err:
        print(f"Error al obtener categoría por ID: {err}")
        return None
    finally:
        cursor.close()
        db.close()

def actualizar_categoria(categoria_id, nombre_categoria):
    db = conectar_db()
    if db is None:
        raise Exception("No se pudo conectar a la base de datos")
    cursor = db.cursor()
    try:
        sql = "UPDATE categorias SET nombre_categoria = %s WHERE categoria_id = %s"
        cursor.execute(sql, (nombre_categoria, categoria_id))
        db.commit()
    except mysql.connector.Error as err:
        db.rollback()
        print(f"Error al actualizar categoría: {err}")
        raise err
    finally:
        cursor.close()
        db.close()

def eliminar_categoria(categoria_id):
    db = conectar_db()
    if db is None:
        raise Exception("No se pudo conectar a la base de datos")
    cursor = db.cursor()
    try:
        # Verificar si existen productos asociados a esta categoría
        cursor.execute("SELECT COUNT(*) FROM productos WHERE categoria_id = %s", (categoria_id,))
        productos_count = cursor.fetchone()[0]
        if productos_count > 0:
            raise Exception("No se puede eliminar la categoría porque tiene productos asociados.")

        sql = "DELETE FROM categorias WHERE categoria_id = %s"
        cursor.execute(sql, (categoria_id,))
        db.commit()
    except mysql.connector.Error as err:
        db.rollback()
        print(f"Error al eliminar categoría: {err}")
        raise err
    finally:
        cursor.close()
        db.close()


def get_proveedores():
    db = conectar_db()
    if db is None:
        return []
    cursor = db.cursor(dictionary=True)
    try:
        cursor.execute("SELECT * FROM proveedores")
        proveedores = cursor.fetchall()
        return proveedores
    except mysql.connector.Error as err:
        print(f"Error al obtener proveedores: {err}")
        return []
    finally:
        cursor.close()
        db.close()

def agregar_proveedor(nombre_proveedor, contacto_info):
    db = conectar_db()
    if db is None:
        raise Exception("No se pudo conectar a la base de datos")
    cursor = db.cursor()
    try:
        sql = "INSERT INTO proveedores (nombre_proveedor, contacto_info) VALUES (%s, %s)"
        cursor.execute(sql, (nombre_proveedor, contacto_info))
        db.commit()
    except mysql.connector.Error as err:
        db.rollback()
        print(f"Error al agregar proveedor: {err}")
        raise err
    finally:
        cursor.close()
        db.close()

def get_proveedor_por_id(proveedor_id):
    db = conectar_db()
    if db is None:
        return None
    cursor = db.cursor(dictionary=True)
    try:
        sql = "SELECT * FROM proveedores WHERE proveedor_id = %s"
        cursor.execute(sql, (proveedor_id,))
        proveedor = cursor.fetchone()
        return proveedor
    except mysql.connector.Error as err:
        print(f"Error al obtener proveedor por ID: {err}")
        return None
    finally:
        cursor.close()
        db.close()

def actualizar_proveedor(proveedor_id, nombre_proveedor, contacto_info):
    db = conectar_db()
    if db is None:
        raise Exception("No se pudo conectar a la base de datos")
    cursor = db.cursor()
    try:
        sql = "UPDATE proveedores SET nombre_proveedor = %s, contacto_info = %s WHERE proveedor_id = %s"
        cursor.execute(sql, (nombre_proveedor, contacto_info, proveedor_id))
        db.commit()
    except mysql.connector.Error as err:
        db.rollback()
        print(f"Error al actualizar proveedor: {err}")
        raise err
    finally:
        cursor.close()
        db.close()

def eliminar_proveedor(proveedor_id):
    db = conectar_db()
    if db is None:
        raise Exception("No se pudo conectar a la base de datos")
    cursor = db.cursor()
    try:
        sql = "DELETE FROM proveedores WHERE proveedor_id = %s"
        cursor.execute(sql, (proveedor_id,))
        db.commit()
    except mysql.connector.Error as err:
        db.rollback()
        print(f"Error al eliminar proveedor: {err}")
        raise err
    finally:
        cursor.close()
        db.close()


def get_productos_inventario():
    db = conectar_db()
    if db is None:
        return []
    cursor = db.cursor(dictionary=True)
    try:
        query = """
        SELECT
            p.producto_id,
            p.nombre_producto,
            c.nombre_categoria,
            prov.nombre_proveedor,
            p.marca,
            p.precio_venta,
            i.cantidad_stock
        FROM productos p
        JOIN categorias c ON p.categoria_id = c.categoria_id
        JOIN inventario i ON p.producto_id = i.producto_id
        LEFT JOIN proveedores prov ON p.proveedor_id = prov.proveedor_id
        """
        cursor.execute(query)
        productos_inventario = cursor.fetchall()
        return productos_inventario
    except mysql.connector.Error as err:
        print(f"Error al obtener productos del inventario: {err}")
        return []
    finally:
        cursor.close()
        db.close()

def agregar_producto(producto_data):
    db = conectar_db()
    if db is None:
        raise Exception("No se pudo conectar a la base de datos")
    cursor = db.cursor()

    try:
        sql_producto = """
        INSERT INTO productos (categoria_id, proveedor_id, nombre_producto, descripcion, marca, unidad, precio_compra, precio_venta, nivel_minimo_stock, codigo_barras_sku, imagen_producto_url)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """
        values_producto = (
            producto_data['categoria_id'],
            producto_data['proveedor_id'],
            producto_data['nombre_producto'],
            producto_data['descripcion'],
            producto_data['marca'],
            producto_data['unidad'],
            producto_data['precio_compra'],
            producto_data['precio_venta'],
            producto_data['nivel_minimo_stock'],
            producto_data['codigo_barras_sku'],
            producto_data['imagen_producto_url']
        )
        cursor.execute(sql_producto, values_producto)
        producto_id = cursor.lastrowid

        sql_inventario = "INSERT INTO inventario (producto_id, cantidad_stock, fecha_expiracion, notas) VALUES (%s, %s, %s, %s)"
        values_inventario = (
            producto_id,
            producto_data['cantidad_stock'],
            producto_data['fecha_expiracion'],
            producto_data['notas']
        )
        cursor.execute(sql_inventario, values_inventario)

        db.commit()
    except mysql.connector.Error as err:
        db.rollback()
        print(f"Error al agregar producto: {err}")
        raise err
    finally:
        cursor.close()
        db.close()

def get_producto_por_id(producto_id):
    db = conectar_db()
    if db is None:
        return None
    cursor = db.cursor(dictionary=True)
    try:
        query = """
        SELECT
            p.*,
            i.cantidad_stock,
            i.fecha_expiracion,
            i.notas
        FROM productos p
        JOIN inventario i ON p.producto_id = i.producto_id
        WHERE p.producto_id = %s
        """
        cursor.execute(query, (producto_id,))
        producto = cursor.fetchone()
        return producto
    except mysql.connector.Error as err:
        print(f"Error al obtener producto por ID: {err}")
        return None
    finally:
        cursor.close()
        db.close()

def actualizar_producto(producto_id, producto_data):
    db = conectar_db()
    if db is None:
        raise Exception("No se pudo conectar a la base de datos")
    cursor = db.cursor()

    try:
        sql_producto = """
        UPDATE productos SET
            categoria_id = %s,
            proveedor_id = %s,
            nombre_producto = %s,
            descripcion = %s,
            marca = %s,
            unidad = %s,
            precio_compra = %s,
            precio_venta = %s,
            nivel_minimo_stock = %s,
            codigo_barras_sku = %s,
            imagen_producto_url = %s
        WHERE producto_id = %s
        """
        values_producto = (
            producto_data['categoria_id'],
            producto_data['proveedor_id'],
            producto_data['nombre_producto'],
            producto_data['descripcion'],
            producto_data['marca'],
            producto_data['unidad'],
            producto_data['precio_compra'],
            producto_data['precio_venta'],
            producto_data['nivel_minimo_stock'],
            producto_data['codigo_barras_sku'],
            producto_data['imagen_producto_url'],
            producto_id
        )
        cursor.execute(sql_producto, values_producto)

        sql_inventario = """
        UPDATE inventario SET
            cantidad_stock = %s,
            fecha_expiracion = %s,
            notas = %s
        WHERE producto_id = %s
        """
        values_inventario = (
            producto_data['cantidad_stock'],
            producto_data['fecha_expiracion'],
            producto_data['notas'],
            producto_id
        )
        cursor.execute(sql_inventario, values_inventario)
        db.commit()
    except mysql.connector.Error as err:
        db.rollback()
        print(f"Error al actualizar producto: {err}")
        raise err
    finally:
        cursor.close()
        db.close()


def eliminar_producto(producto_id):
    db = conectar_db()
    if db is None:
        raise Exception("No se pudo conectar a la base de datos")
    cursor = db.cursor()
    try:
        # Primero eliminar de inventario por la llave foranea
        sql_inventario = "DELETE FROM inventario WHERE producto_id = %s"
        cursor.execute(sql_inventario, (producto_id,))

        sql_producto = "DELETE FROM productos WHERE producto_id = %s"
        cursor.execute(sql_producto, (producto_id,))
        db.commit()
    except mysql.connector.Error as err:
        db.rollback()
        print(f"Error al eliminar producto: {err}")
        raise err
    finally:
        cursor.close()
        db.close()


# Rutas de la aplicación


@app.route('/')
def inicio():
    return render_template('index.html')

@app.route('/registro', methods=['GET', 'POST'])
def registro():
    if request.method == 'POST':
        nombre = request.form['nombre']
        correo_electronico = request.form['correo_electronico']
        contrasena_plana = request.form['contrasena']
        contrasena_hash = generate_password_hash(contrasena_plana)

        db = conectar_db()
        if db is None:
            return "Error al conectar a la base de datos para registro."
        cursor = db.cursor()
        try:
            sql = "INSERT INTO usuarios (nombre, correo_electronico, contrasena) VALUES (%s, %s, %s)"
            cursor.execute(sql, (nombre, correo_electronico, contrasena_hash))
            db.commit()
            return redirect(url_for('login'))
        except mysql.connector.Error as err:
            db.rollback()
            return f"Error al registrar usuario: {err}"
        finally:
            cursor.close()
            db.close()

    return render_template('registro.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    mensaje_error = None
    if request.method == 'POST':
        correo_electronico = request.form['correo_electronico']
        contrasena_plana = request.form['contrasena']

        db = conectar_db()
        if db is None:
            mensaje_error = "Error al conectar a la base de datos para login."
            return render_template('login.html', mensaje_error=mensaje_error)
        cursor = db.cursor(dictionary=True)
        try:
            sql = "SELECT * FROM usuarios WHERE correo_electronico = %s"
            cursor.execute(sql, (correo_electronico,))
            user = cursor.fetchone()

            if user and check_password_hash(user['contrasena'], contrasena_plana):
                session['usuario_id'] = user['id']
                session['nombre'] = user['nombre']  # Almacenar el nombre del usuario en la sesión
                session['rol'] = user['rol']
                if session['rol'] == 'admin':
                    return redirect(url_for('admin_inventario'))
                else:
                    return redirect(url_for('index'))
            else:
                mensaje_error = 'Credenciales incorrectas. Inténtalo de nuevo.'

        except mysql.connector.Error as err:
            mensaje_error = f"Error al iniciar sesión: {err}"
        finally:
            cursor.close()
            db.close()

    return render_template('login.html', mensaje_error=mensaje_error)

@app.route('/admin/inventario', methods=['GET', 'POST'])
def admin_inventario():
    if 'usuario_id' in session and session['rol'] == 'admin':
        mensaje_producto = None
        mensaje_categoria = None
        mensaje_proveedor = None
        mensaje_producto_error = None
        mensaje_categoria_error = None
        mensaje_proveedor_error = None

        if request.method == 'POST':
            if 'add_product' in request.form:
                producto_data = {
                    'nombre_producto': request.form['product_name'],
                    'descripcion': request.form['description'],
                    'categoria_id': int(request.form['category']),
                    'proveedor_id': int(request.form['supplier']),
                    'marca': request.form['brand'],
                    'unidad': request.form['unit'],
                    'precio_compra': float(request.form['purchase_price']),
                    'precio_venta': float(request.form['selling_price']),
                    'nivel_minimo_stock': int(request.form['minimum_stock_level']),
                    'codigo_barras_sku': request.form['barcode_sku'],
                    'imagen_producto_url': request.form['product_image_url'],
                    'cantidad_stock': int(request.form['stock_quantity']),
                    'fecha_expiracion': request.form['expiration_date'],
                    'notas': request.form['notes']
                }
                try:
                    agregar_producto(producto_data)
                    mensaje_producto = "Producto agregado exitosamente!"
                except Exception as err:
                    mensaje_producto_error = f"Error al agregar producto: {err}"
            elif 'add_category' in request.form:
                nombre_categoria = request.form['nombre_categoria']
                try:
                    agregar_categoria(nombre_categoria)
                    mensaje_categoria = "Categoría agregada exitosamente!"
                except Exception as err:
                    mensaje_categoria_error = f"Error al agregar categoría: {err}"
            elif 'add_supplier' in request.form:
                nombre_proveedor = request.form['nombre_proveedor']
                contacto_info = request.form['contacto_info']
                try:
                    agregar_proveedor(nombre_proveedor, contacto_info)
                    mensaje_proveedor = "Proveedor agregado exitosamente!"
                except Exception as err:
                    mensaje_proveedor_error = f"Error al agregar proveedor: {err}"


        categorias = get_categorias()
        proveedores = get_proveedores()
        productos_inventario = get_productos_inventario()
        return render_template('admin_inventario.html',
                                   categorias=categorias,
                                   proveedores=proveedores,
                                   productos_inventario=productos_inventario,
                                   mensaje_producto=mensaje_producto,
                                   mensaje_categoria=mensaje_categoria,
                                   mensaje_proveedor=mensaje_proveedor,
                                   mensaje_producto_error=mensaje_producto_error,
                                   mensaje_categoria_error=mensaje_categoria_error,
                                   mensaje_proveedor_error=mensaje_proveedor_error)
    else:
        return redirect(url_for('login'))

@app.route('/agendar_cita', methods=['POST'])
def agendar_cita():
    if request.method == 'POST':
        nombre = request.form['nombre']
        email = request.form['email']
        telefono = request.form['telefono']
        fecha = request.form['fecha']
        hora = request.form['hora']
        servicio = request.form['servicio']
        mensaje = request.form['mensaje']

        # Aquí puedes agregar la lógica para guardar la cita en la base de datos
        # Por ejemplo:
        db = conectar_db()
        if db is None:
            return "Error al conectar a la base de datos para agendar cita."
        cursor = db.cursor()
        try:
            sql = """
            INSERT INTO citas (nombre, email, telefono, fecha, hora, servicio, mensaje)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
            """
            cursor.execute(sql, (nombre, email, telefono, fecha, hora, servicio, mensaje))
            db.commit()
            return redirect(url_for('index', mensaje="Cita agendada exitosamente!"))
        except mysql.connector.Error as err:
            db.rollback()
            return f"Error al agendar cita: {err}"
        finally:
            cursor.close()
            db.close()

    return redirect(url_for('index'))

# Rutas para Editar

@app.route('/admin/inventario/editar_producto/<int:id>', methods=['GET', 'POST'])
def editar_producto(id):
    if 'usuario_id' in session and session['rol'] == 'admin':
        producto = get_producto_por_id(id)
        categorias = get_categorias()
        proveedores = get_proveedores()
        mensaje_producto = None
        mensaje_producto_error = None

        if request.method == 'POST':
            producto_data = {
                    'nombre_producto': request.form['product_name'],
                    'descripcion': request.form['description'],
                    'categoria_id': int(request.form['category']),
                    'proveedor_id': int(request.form['supplier']),
                    'marca': request.form['brand'],
                    'unidad': request.form['unit'],
                    'precio_compra': float(request.form['purchase_price']),
                    'precio_venta': float(request.form['selling_price']),
                    'nivel_minimo_stock': int(request.form['minimum_stock_level']),
                    'codigo_barras_sku': request.form['barcode_sku'],
                    'imagen_producto_url': request.form['product_image_url'],
                    'cantidad_stock': int(request.form['stock_quantity']),
                    'fecha_expiracion': request.form['expiration_date'],
                    'notas': request.form['notes']
                }
            try:
                actualizar_producto(id, producto_data)
                mensaje_producto = "Producto actualizado exitosamente!"
            except Exception as err:
                mensaje_producto_error = f"Error al actualizar producto: {err}"
            return render_template('editar_producto.html', producto=producto, categorias=categorias, proveedores=proveedores, mensaje_producto=mensaje_producto, mensaje_producto_error=mensaje_producto_error)


        return render_template('editar_producto.html', producto=producto, categorias=categorias, proveedores=proveedores, mensaje_producto=mensaje_producto, mensaje_producto_error=mensaje_producto_error)
    else:
        return redirect(url_for('login'))

@app.route('/admin/inventario/editar_categoria/<int:id>', methods=['GET', 'POST'])
def editar_categoria(id):
    if 'usuario_id' in session and session['rol'] == 'admin':
        categoria = get_categoria_por_id(id)
        mensaje_categoria = None
        mensaje_categoria_error = None

        if request.method == 'POST':
            nombre_categoria = request.form['nombre_categoria']
            try:
                actualizar_categoria(id, nombre_categoria)
                mensaje_categoria = "Categoría actualizada exitosamente!"
            except Exception as err:
                mensaje_categoria_error = f"Error al actualizar categoría: {err}"
            return render_template('editar_categoria.html', categoria=categoria, mensaje_categoria=mensaje_categoria, mensaje_categoria_error=mensaje_categoria_error)

        return render_template('editar_categoria.html', categoria=categoria, mensaje_categoria=mensaje_categoria, mensaje_categoria_error=mensaje_categoria_error)
    else:
        return redirect(url_for('login'))

@app.route('/admin/inventario/editar_proveedor/<int:id>', methods=['GET', 'POST'])
def editar_proveedor(id):
    if 'usuario_id' in session and session['rol'] == 'admin':
        proveedor = get_proveedor_por_id(id)
        mensaje_proveedor = None
        mensaje_proveedor_error = None

        if request.method == 'POST':
            nombre_proveedor = request.form['nombre_proveedor']
            contacto_info = request.form['contacto_info']
            try:
                actualizar_proveedor(id, nombre_proveedor, contacto_info)
                mensaje_proveedor = "Proveedor actualizado exitosamente!"
            except Exception as err:
                mensaje_proveedor_error = f"Error al actualizar proveedor: {err}"
            return render_template('editar_proveedor.html', proveedor=proveedor, mensaje_proveedor=mensaje_proveedor, mensaje_proveedor_error=mensaje_proveedor_error)

        return render_template('editar_proveedor.html', proveedor=proveedor, mensaje_proveedor=mensaje_proveedor, mensaje_proveedor_error=mensaje_proveedor_error)
    else:
        return redirect(url_for('login'))


# Rutas para Eliminar

@app.route('/admin/inventario/eliminar_producto/<int:id>', methods=['POST'])
def eliminar_producto_route(id):
    if 'usuario_id' in session and session['rol'] == 'admin':
        try:
            eliminar_producto(id)
            return redirect(url_for('admin_inventario', mensaje_producto="Producto eliminado exitosamente!"))
        except Exception as e:
            return redirect(url_for('admin_inventario', mensaje_producto_error=f"Error al eliminar producto: {e}"))
    else:
        return redirect(url_for('login'))

@app.route('/admin/inventario/eliminar_categoria/<int:id>', methods=['POST'])
def eliminar_categoria_route(id):
    if 'usuario_id' in session and session['rol'] == 'admin':
        try:
            eliminar_categoria(id)
            return redirect(url_for('admin_inventario', mensaje_categoria="Categoría eliminada exitosamente!"))
        except Exception as e:
            mensaje_error = str(e) # Captura el mensaje de la excepción
            return redirect(url_for('admin_inventario', mensaje_categoria_error=f"Error al eliminar categoría: {mensaje_error}")) # Pasa el mensaje de error
    else:
        return redirect(url_for('login'))

@app.route('/admin/inventario/eliminar_proveedor/<int:id>', methods=['POST'])
def eliminar_proveedor_route(id):
    if 'usuario_id' in session and session['rol'] == 'admin':
        try:
            eliminar_proveedor(id)
            return redirect(url_for('admin_inventario', mensaje_proveedor="Proveedor eliminado exitosamente!"))
        except Exception as e:
            return redirect(url_for('admin_inventario', mensaje_proveedor_error=f"Error al eliminar proveedor: {e}"))
    else:
        return redirect(url_for('login'))


@app.route('/main')
def index():
    if 'usuario_id' in session:
        return render_template('index.html', usuario_id=session['usuario_id'])
    else:
        return redirect(url_for('login'))

@app.route('/usuario')
def pagina_usuario():
    if 'usuario_id' in session:
        return render_template('pagina_usuario.html', usuario_id=session['usuario_id'])
    else:
        return redirect(url_for('login'))


@app.route('/logout')
def logout():
    session.pop('usuario_id', None)
    session.pop('rol', None)
    return redirect(url_for('inicio'))


