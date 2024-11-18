import streamlit as st
from datetime import datetime, timedelta
from database.config import get_session
from database.crud import DatabaseManager
from database.models import Funcionario, Atestado
from sqlalchemy import func

def app():
    st.title('Gerenciar Atestados')
    
    # Inicializar conexão com banco de dados
    session = next(get_session())
    db = DatabaseManager(session)
    
    # Lista empresas do banco de dados
    empresas = db.listar_empresas()
    empresa_options = {empresa.nome: empresa.id for empresa in empresas}
    
    empresa_selecionada = st.selectbox('Selecione a Empresa', options=list(empresa_options.keys()))
    
    if empresa_selecionada:
        empresa_id = empresa_options[empresa_selecionada]
        funcionarios = db.listar_funcionarios_por_empresa(empresa_id)
        
        if funcionarios:
            st.markdown("## Registrar Atestado")
            with st.form("registrar_atestado"):
                funcionario_selecionado = st.selectbox(
                    'Selecione o Funcionário',
                    options=[f.nome for f in funcionarios],
                    key="atestado_funcionario"
                )
                
                col1, col2 = st.columns(2)
                with col1:
                    data_inicio_atestado = st.date_input(
                        'Data de Início do Atestado', 
                        value=datetime.today(),
                        key="atestado_inicio"
                    )
                with col2:
                    dias_atestado = st.number_input(
                        'Duração do Atestado (em dias)', 
                        min_value=1,
                        max_value=30,
                        value=1,
                        key="atestado_dias"
                    )
                
                submit_atestado = st.form_submit_button("Registrar Atestado")
                
                if submit_atestado:
                    funcionario = next((f for f in funcionarios if f.nome == funcionario_selecionado), None)
                    if funcionario:
                        atestado_ativo = session.query(Atestado).filter(
                            Atestado.funcionario_id == funcionario.id,
                            Atestado.ativo == True
                        ).first()

                        if atestado_ativo:
                            st.error(f'{funcionario_selecionado} já está em atestado.')
                        else:
                            data_fim_atestado = data_inicio_atestado + timedelta(days=dias_atestado - 1)
                            
                            try:
                                novo_atestado = Atestado(
                                    funcionario_id=funcionario.id,
                                    data_inicio=data_inicio_atestado,
                                    data_fim=data_fim_atestado,
                                    dias=dias_atestado,
                                    ativo=True,
                                    created_at=datetime.now()
                                )
                                
                                session.add(novo_atestado)
                                session.commit()
                                st.success(f'Atestado registrado com sucesso!')
                                st.experimental_rerun()
                                
                            except Exception as e:
                                session.rollback()
                                st.error(f"Erro ao registrar atestado: {str(e)}")

            st.markdown("## Funcionários em Atestado")
            funcionarios_em_atestado = session.query(Atestado).filter(Atestado.ativo == True).all()
            
            if funcionarios_em_atestado:
                for atestado in funcionarios_em_atestado:
                    funcionario = session.query(Funcionario).get(atestado.funcionario_id)
                    if funcionario:
                        with st.container():
                            col1, col2, col3 = st.columns([2, 2, 1])
                            with col1:
                                st.markdown(f"**{funcionario.nome}**")
                            with col2:
                                st.write(f"{atestado.data_inicio} a {atestado.data_fim}")
                            with col3:
                                if st.button('Retornar ao Trabalho', key=f'retorno_{funcionario.id}'):
                                    atestado.ativo = False
                                    session.commit()
                                    st.success(f'{funcionario.nome} retornou ao trabalho')
                                    st.experimental_rerun()
                        st.markdown("---")
            else:
                st.info("Não há funcionários em atestado no momento.")
        else:
            st.warning('Não há funcionários cadastrados para esta empresa.')
    else:
        st.warning('Selecione uma empresa para gerenciar atestados.') 