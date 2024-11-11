from config import engine
from sqlmodel import Session, text
import logging
import sys

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def test_connection():
    try:
        # Tenta criar uma conexão
        with engine.connect() as connection:
            # Testa a conexão com uma query simples
            result = connection.execute(text("SELECT version();"))
            version = result.scalar()
            logger.info(f"Conexão estabelecida com sucesso!")
            logger.info(f"Versão do PostgreSQL: {version}")
            return True
            
    except Exception as e:
        logger.error(f"Erro ao conectar com o banco de dados: {str(e)}")
        logger.error("Detalhes da conexão:")
        logger.error(f"Host: {engine.url.host}")
        logger.error(f"Port: {engine.url.port}")
        logger.error(f"Database: {engine.url.database}")
        logger.error(f"Username: {engine.url.username}")
        return False

if __name__ == "__main__":
    success = test_connection()
    if not success:
        sys.exit(1) 