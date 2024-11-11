import sys
from pathlib import Path

# Adiciona o diretório raiz do projeto ao PYTHONPATH
root_dir = Path(__file__).parent.parent
sys.path.append(str(root_dir))

from database.connection import init_db, test_connection

if __name__ == "__main__":
    if test_connection():
        init_db() 