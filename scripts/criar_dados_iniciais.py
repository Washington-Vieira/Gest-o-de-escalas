import sys
from pathlib import Path

# Adiciona o diretório raiz ao PYTHONPATH
root_dir = Path(__file__).parent.parent
sys.path.append(str(root_dir))

from models import SessionLocal, create_tables
from models.database import test_connection
from models.models import Empresa, Funcionario

def criar_dados_iniciais():
    try:
        print("Testando conexão...")
        if not test_connection():
            print("Falha no teste de conexão!")
            return
            
        print("Criando tabelas...")
        if not create_tables():
            print("Falha ao criar tabelas!")
            return
        
        print("Iniciando criação dos dados...")
        db = SessionLocal()
        
        try:
            # Criar empresa
            print("Criando empresa...")
            empresa = Empresa(
                nome="Empresa Teste",
                cnpj="12345678901234"
            )
            db.add(empresa)
            db.commit()
            
            # Criar funcionário
            print("Criando funcionário...")
            funcionario = Funcionario(
                nome="Funcionário Teste",
                matricula="12345",
                empresa_id=empresa.id
            )
            db.add(funcionario)
            db.commit()
            
            print("Dados iniciais criados com sucesso!")
            
        except Exception as e:
            print(f"Erro ao criar dados: {str(e)}")
            db.rollback()
        finally:
            db.close()
            
    except Exception as e:
        print(f"Erro ao criar dados iniciais: {str(e)}")

if __name__ == "__main__":
    criar_dados_iniciais() 