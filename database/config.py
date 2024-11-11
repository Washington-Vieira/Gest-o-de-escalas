from sqlmodel import create_engine, Session, text
import os
from dotenv import load_dotenv
import logging
from urllib.parse import quote_plus

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Carrega as variáveis do arquivo .env
load_dotenv()

def validate_env_vars():
    """
    Valida se todas as variáveis de ambiente necessárias estão definidas
    """
    required_vars = ['DB_USER', 'DB_PASSWORD', 'DB_HOST', 'DB_PORT', 'DB_NAME']
    missing_vars = [var for var in required_vars if not os.getenv(var)]
    
    if missing_vars:
        raise EnvironmentError(
            f"Variáveis de ambiente faltando: {', '.join(missing_vars)}"
        )

# Validar variáveis de ambiente
validate_env_vars()

# Obtém as variáveis de ambiente
DB_USER = os.getenv("DB_USER")
DB_PASSWORD = quote_plus(os.getenv("DB_PASSWORD"))  # Codifica caracteres especiais na senha
DB_HOST = os.getenv("DB_HOST")
DB_PORT = os.getenv("DB_PORT")
DB_NAME = os.getenv("DB_NAME")

# Constrói a URL de conexão
DATABASE_URL = f"postgresql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"

try:
    # Cria o engine com configurações básicas
    engine = create_engine(
        DATABASE_URL,
        echo=False,
        pool_pre_ping=True,
        pool_size=5,
        max_overflow=10,
        connect_args={
            "connect_timeout": 30,
            "application_name": "escala_app"
        }
    )
    logger.info("Engine do banco de dados criado com sucesso")
    
    # Testa a conexão imediatamente
    with engine.connect() as conn:
        conn.execute(text("SELECT 1"))
        logger.info("Conexão de teste realizada com sucesso")
        
except Exception as e:
    logger.error(f"Erro ao criar/testar engine do banco de dados: {str(e)}")
    raise

def get_session():
    """
    Gerador de sessões do banco de dados.
    """
    try:
        with Session(engine) as session:
            yield session
    except Exception as e:
        logger.error(f"Erro na sessão do banco de dados: {str(e)}")
        raise
    finally:
        session.close() 