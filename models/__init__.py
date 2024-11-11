from .database import Base, engine, SessionLocal, get_db
from .models import Empresa, Funcionario, Ferias, Escala

def create_tables():
    try:
        Base.metadata.create_all(bind=engine)
        print("Tabelas criadas com sucesso!")
        return True
    except Exception as e:
        print(f"Erro ao criar tabelas: {str(e)}")
        return False 