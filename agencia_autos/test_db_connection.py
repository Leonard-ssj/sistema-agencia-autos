import psycopg2
from dotenv import load_dotenv
import os

# Cargar variables de entorno
load_dotenv()

# Obtener credenciales
DB_NAME = os.getenv('DB_NAME', 'agencia_autos')
DB_USER = os.getenv('DB_USER', 'autos_user')
DB_PASS = os.getenv('DB_PASS', 'autos_pass')
DB_HOST = os.getenv('DB_HOST', '127.0.0.1')
DB_PORT = os.getenv('DB_PORT', '5432')

print("=" * 60)
print("PRUEBA DE CONEXIÓN A POSTGRESQL")
print("=" * 60)
print(f"\nCredenciales:")
print(f"  Host: {DB_HOST}")
print(f"  Port: {DB_PORT}")
print(f"  Database: {DB_NAME}")
print(f"  User: {DB_USER}")
print(f"  Password: {'*' * len(DB_PASS)}")
print()

try:
    print("Intentando conectar...")
    conn = psycopg2.connect(
        dbname=DB_NAME,
        user=DB_USER,
        password=DB_PASS,
        host=DB_HOST,
        port=DB_PORT
    )
    
    print("CONEXION EXITOSA")
    
    # Probar una consulta simple
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM vehiculo;")
    count = cursor.fetchone()[0]
    print(f"Consulta exitosa: {count} vehiculos en la base de datos")
    
    cursor.execute("SELECT COUNT(*) FROM venta;")
    count = cursor.fetchone()[0]
    print(f"Consulta exitosa: {count} ventas en la base de datos")
    
    cursor.close()
    conn.close()
    
    print("\n" + "=" * 60)
    print("TODO ESTÁ FUNCIONANDO CORRECTAMENTE")
    print("=" * 60)
    
except psycopg2.OperationalError as e:
    print("ERROR DE CONEXION:")
    print(f"   {str(e)}")
    print("\nPosibles soluciones:")
    print("  1. Verificar que PostgreSQL esté corriendo")
    print("  2. Verificar las credenciales en el archivo .env")
    print("  3. Verificar que la base de datos 'agencia_autos' exista")
    print("  4. Verificar que el usuario 'autos_user' tenga permisos")
    
except Exception as e:
    print(f"ERROR INESPERADO: {str(e)}")
