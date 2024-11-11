from sqlalchemy import create_engine, text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from dotenv import load_dotenv
import os

# Carrega as variáveis de ambiente
load_dotenv()

# Debug: imprime as variáveis (sem a senha)
print("Configurações de conexão:")
print(f"HOST: {os.getenv('DB_HOST')}")
print(f"PORT: {os.getenv('DB_PORT')}")
print(f"DB: {os.getenv('DB_NAME')}")
print(f"USER: {os.getenv('DB_USER')}")

# Configuração da conexão usando os parâmetros que funcionaram com psycopg2
DATABASE_URL = (
    f"postgresql+psycopg2://{os.getenv('DB_USER')}:{os.getenv('DB_PASSWORD')}"
    f"@{os.getenv('DB_HOST')}:{os.getenv('DB_PORT')}/{os.getenv('DB_NAME')}"
)

# Criar engine com configurações mais simples
engine = create_engine(
    DATABASE_URL,
    echo=True,
    pool_pre_ping=True,
    connect_args={
        'connect_timeout': 30,
        'client_encoding': 'utf8',
        'options': '-c timezone=UTC'
    }
)

# Criar sessão
SessionLocal = sessionmaker(
    bind=engine,
    autocommit=False,
    autoflush=False,
    expire_on_commit=False
)

# Base para os modelos
Base = declarative_base()

def test_connection():
    """Função para testar a conexão"""
    try:
        db = SessionLocal()
        db.execute(text('SELECT 1'))
        print("Conexão teste bem sucedida!")
        db.close()
        return True
    except Exception as e:
        print(f"Erro ao testar conexão: {str(e)}")
        return False

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close() 