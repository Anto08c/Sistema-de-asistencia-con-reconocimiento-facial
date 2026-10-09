
from empleados import registrar_empleado, listar_empleados

print("=== REGISTRO DE EMPLEADOS ===")

codigo = input("Código del empleado: ")
nombres = input("Nombres: ")
apellidos = input("Apellidos: ")

correcto, mensaje = registrar_empleado(
    codigo,
    nombres,
    apellidos
)

print(mensaje)

print("\n=== LISTA DE EMPLEADOS ===")

for empleado in listar_empleados():
    print(
        empleado["id"],
        empleado["codigo"],
        empleado["nombres"],
        empleado["apellidos"],
        empleado["estado"]
    )