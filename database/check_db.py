from config import engine
from sqlmodel import text
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def check_database():
    try:
        with engine.connect() as connection:
            # Verifica a conexão
            result = connection.execute(text("SELECT version();"))
            version = result.scalar()
            logger.info(f"Conectado ao PostgreSQL versão: {version}")
            
            # Lista todas as tabelas
            result = connection.execute(text("""
                SELECT table_schema, table_name 
                FROM information_schema.tables 
                WHERE table_schema = 'public'
                ORDER BY table_schema, table_name;
            """))
            
            tables = result.fetchall()
            if tables:
                logger.info("Tabelas encontradas:")
                for schema, table in tables:
                    logger.info(f"- {schema}.{table}")
            else:
                logger.warning("Nenhuma tabela encontrada no schema 'public'")
            
            # Verifica permissões do usuário
            result = connection.execute(text("""
                SELECT current_user, current_database();
            """))
            user, database = result.fetchone()
            logger.info(f"Usuário atual: {user}")
            logger.info(f"Banco de dados atual: {database}")
            
    except Exception as e:
        logger.error(f"Erro ao verificar banco de dados: {str(e)}")
        raise

if __name__ == "__main__":
    check_database() 