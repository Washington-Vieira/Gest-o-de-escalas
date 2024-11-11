import psycopg2
from dotenv import load_dotenv
import os

load_dotenv()

print("Testando conexão com credenciais:")
print(f"Host: {os.getenv('DB_HOST')}")
print(f"User: {os.getenv('DB_USER')}")
print(f"DB: {os.getenv('DB_NAME')}")

try:
    conn = psycopg2.connect(
        host=os.getenv('DB_HOST'),
        database=os.getenv('DB_NAME'),
        user=os.getenv('DB_USER'),
        password=os.getenv('DB_PASSWORD'),
        port=os.getenv('DB_PORT')
    )
    print("Conexão bem sucedida!")
    conn.close()
except Exception as e:
    print(f"Erro na conexão: {str(e)}") 