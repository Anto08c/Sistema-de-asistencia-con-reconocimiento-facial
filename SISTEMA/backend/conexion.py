import pymysql

def obtener_conexion():
    conexion = pymysql.connect(
        host="localhost",
        user="root",
        password="",
        database="bd_asistencias_ab",
        port=3306,
        charset="utf8mb4",
        cursorclass=pymysql.cursors.DictCursor
    )

    return conexion


