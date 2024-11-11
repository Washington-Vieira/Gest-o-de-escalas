from sqlmodel import SQLModel, create_engine, Session
from config import engine
from models import Empresa, Funcionario, Ferias, Atestado
import logging
from sqlalchemy import text

logger = logging.getLogger(__name__)

def init_db():
    try:
        logger.info("Iniciando processo de criação do banco de dados...")
        
        # Dropa todas as tabelas existentes e recria
        SQLModel.metadata.drop_all(engine)
        
        SQLModel.metadata.create_all(engine)
        
        logger.info("Banco de dados criado com sucesso!")
        
        # Verifica as tabelas criadas
        with engine.connect() as connection:
            result = connection.execute(text("""
                SELECT table_name 
                FROM information_schema.tables 
                WHERE table_schema = 'public'
            """))
            tables = [row[0] for row in result]
            logger.info(f"Tabelas criadas: {', '.join(tables)}")

        # Verifica se podemos conectar e fazer operações básicas
        with Session(engine) as session:
            # Tenta criar uma empresa de teste
            empresa_teste = Empresa(nome="Empresa Teste")
            session.add(empresa_teste)
            session.commit()
            session.refresh(empresa_teste)
            
            logger.info(f"Teste de inserção realizado com sucesso. ID da empresa teste: {empresa_teste.id}")
            
            # Remove a empresa de teste
            session.delete(empresa_teste)
            session.commit()
            
    except Exception as e:
        logger.error(f"Erro ao criar tabelas: {str(e)}")
        raise

if __name__ == "__main__":
    init_db() 