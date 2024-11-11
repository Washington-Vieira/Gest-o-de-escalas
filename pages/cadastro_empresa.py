import streamlit as st
from database.config import get_session
from database.models import Empresa
from database.crud import DatabaseManager

def app():
    st.title('Cadastro de Empresas')
    
    session = next(get_session())
    db = DatabaseManager(session)
    
    nome_empresa = st.text_input('Nome da Empresa')
    
    if st.button('Cadastrar Empresa'):
        if nome_empresa:
            empresa_existente = db.obter_empresa_por_nome(nome_empresa)
            
            if not empresa_existente:
                nova_empresa = Empresa(nome=nome_empresa)
                db.criar_empresa(nova_empresa)
                st.success(f'Empresa {nome_empresa} cadastrada com sucesso!')
            else:
                st.error('Esta empresa já está cadastrada.')
        else:
            st.error('Por favor, insira um nome para a empresa.')

    # Lista de empresas cadastradas
    st.subheader("Empresas Cadastradas")
    empresas = db.listar_empresas()
    for empresa in empresas:
        col1, col2 = st.columns([3, 1])
        with col1:
            st.write(f"- {empresa.nome}")
        with col2:
            if st.button(f'Excluir {empresa.nome}'):
                # Alerta de confirmação
                if st.session_state.get(f'confirmar_exclusao_{empresa.id}', False):
                    db.session.delete(empresa)  # Exclui a empresa
                    db.session.commit()  # Confirma a exclusão
                    st.success(f'Empresa {empresa.nome} excluída com sucesso!')
                    st.session_state[f'confirmar_exclusao_{empresa.id}'] = False  # Resetar estado
                else:
                    st.session_state[f'confirmar_exclusao_{empresa.id}'] = True
                    st.warning(f'Você tem certeza que deseja excluir a empresa {empresa.nome}? Clique novamente para confirmar.')
