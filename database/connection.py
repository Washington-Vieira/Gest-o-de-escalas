from sqlalchemy import create_engine, text
from dotenv import load_dotenv
import os

def test_connection():
    try:
        load_dotenv()
        
        # Obtém as variáveis de ambiente
        host = os.getenv('DB_HOST', 'localhost')
        port = int(os.getenv('DB_PORT', '5432'))
        database = os.getenv('DB_NAME')
        user = os.getenv('DB_USER')
        password = os.getenv('DB_PASSWORD')
        
        # Monta a URL de conexão explicitamente sem SSL
        DATABASE_URL = f"postgresql://{user}:{password}@{host}:{port}/{database}?sslmode=disable"
        
        # Cria o engine com timeout mais longo
        engine = create_engine(
            DATABASE_URL,
            connect_args={
                'connect_timeout': 30,
                'application_name': 'escala_app'
            }
        )
        
        # Testa a conexão
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
            print("Conexão estabelecida com sucesso!")
        return True
    except Exception as e:
        print(f"Erro na conexão: {str(e)}")
        return False

def init_db():
    # Código de inicialização do banco de dados aqui
    pass 