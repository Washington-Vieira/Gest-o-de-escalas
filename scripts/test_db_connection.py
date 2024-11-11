import sys
from pathlib import Path
import psycopg2
from dotenv import load_dotenv
import os

# Adiciona o diretório raiz ao PYTHONPATH
root_dir = Path(__file__).parent.parent
sys.path.append(str(root_dir))

def test_direct_connection():
    """Testa conexão direta com psycopg2"""
    load_dotenv()
    
    try:
        print("\nTestando conexão direta com psycopg2:")
        conn = psycopg2.connect(
            dbname=os.getenv('DB_NAME'),
            user=os.getenv('DB_USER'),
            password=os.getenv('DB_PASSWORD'),
            host=os.getenv('DB_HOST'),
            port=os.getenv('DB_PORT'),
            connect_timeout=30
        )
        
        cur = conn.cursor()
        cur.execute('SELECT 1')
        print("Conexão direta bem sucedida!")
        
        cur.close()
        conn.close()
        return True
    except Exception as e:
        print(f"Erro na conexão direta: {str(e)}")
        return False

def test_sqlalchemy_connection():
    """Testa conexão com SQLAlchemy"""
    try:
        print("\nTestando conexão com SQLAlchemy:")
        from models.database import test_connection
        return test_connection()
    except Exception as e:
        print(f"Erro na conexão SQLAlchemy: {str(e)}")
        return False

if __name__ == "__main__":
    print("Iniciando testes de conexão...")
    direct = test_direct_connection()
    alchemy = test_sqlalchemy_connection()
    
    if direct and alchemy:
        print("\nTodos os testes de conexão foram bem sucedidos!")
    else:
        print("\nHouve falhas nos testes de conexão!") 