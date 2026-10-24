import pymysql
from backend.conexion import obtener_conexion

def registrar_empleado(codigo, nombres, apellidos):
    codigo = codigo.strip().upper()
    nombres = nombres.strip()
    apellidos = apellidos.strip()

    if not codigo or not nombres or not apellidos:
        return False, "Todos los campos son obligatorios."

    conexion =  obtener_conexion()

    try:
        with conexion.cursor() as cursor:
            cursor.execute(
                """
                INSERT INTO empleados (codigo, nombres, apellidos)
                VALUES (%s, %s, %s)
                """,
                (codigo, nombres, apellidos)
            )
        conexion.commit()
        return True, "Empleado registrado correctamente."

    except pymysql.err.IntegrityError:
        conexion.rollback()
        return False, "El codigo del empleado ya existe. Por favor, use un codigo diferente."

    except Exception as error:
        conexion.rollback()
        print("Error al registrar empleado:", error)
        return False ,"No se pudo registrar el empleado."
    finally:
        conexion.close()

def listar_empleados():
    conexion = obtener_conexion()

    try: 
        with conexion.cursor() as cursor: 
            cursor.execute(
                """
                SELECT id, codigo, nombres, apellidos, estado FROM empleados
                ORDER BY id DESC
                """
            )
            return cursor.fetchall()
    finally:
        conexion.close()

def cambiar_estado_empleado(empleado_id, nuevo_estado):
    if nuevo_estado not in ("activo", "inactivo"):
        return False, "Estado no válido."

    conexion = obtener_conexion()

    try: 
        with conexion.cursor() as cursor:
            cursor.execute(
                """UPDATE empleados 
                SET estado = %s
                WHERE id = %s
            """,
            (nuevo_estado, empleado_id)
            )

            if cursor.rowcount == 0:
                cursor.execute(
                    "SELECT id FROM empleados WHERE id = %s",
                    (empleado_id)
                )

                if cursor.fetchone() is None:
                    return False, "No se encontró el empleado."
        conexion.commit()
        return True, "Estado actualizado correctamente."
    
    except Exception as error:
        conexion.rollback()
        print("Error al cambiar estado", error)
        return False, "No se pudo actualizar el estado."

    finally:
        conexion.close()