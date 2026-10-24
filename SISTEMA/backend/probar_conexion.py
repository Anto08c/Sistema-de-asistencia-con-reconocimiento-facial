from backend.conexion import obtener_conexion

try:
    conexion = obtener_conexion()

    print("¡Conexión a MySQL exitosa!")

    with conexion.cursor() as cursor:
        cursor.execute("SHOW TABLES")
        tablas = cursor.fetchall()

        print("Tablas encontradas:")
        for tabla in tablas:
            print(tabla)

    conexion.close()

except Exception as error:
    print("Error al conectar con MySQL:")
    print(error)
