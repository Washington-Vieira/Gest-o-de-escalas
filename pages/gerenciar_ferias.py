import streamlit as st
from datetime import datetime, timedelta
import pandas as pd
from database.config import get_session
from database.crud import DatabaseManager
from database.models import Funcionario, Ferias, Atestado
from sqlalchemy import func
import time
from io import BytesIO
from exportar_relatorio_ferias import exportar_relatorio_ferias
from exportar_relatorio_atestados import exportar_relatorio_atestados

def app():
    st.title('Gerenciamento de Afastamentos')
    
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
            # Criar três abas: Férias, Atestados e Afastados
            tab1, tab2, tab3 = st.tabs(["Registrar Férias", "Registrar Atestados", "Funcionários Afastados"])
            
            # Aba de Férias (seu código existente)
            with tab1:
                st.markdown("## Registrar Férias")
                with st.form("registrar_ferias"):
                    funcionario_selecionado = st.selectbox(
                        'Selecione o Funcionário',
                        options=[f.nome for f in funcionarios],
                        key="ferias_funcionario"
                    )
                    
                    col1, col2 = st.columns(2)
                    with col1:
                        data_inicio_ferias = st.date_input(
                            'Data de Início das Férias', 
                            value=datetime.today(),
                            key="ferias_inicio"
                        )
                    with col2:
                        dias_ferias = st.number_input(
                            'Duração das Férias (em dias)', 
                            min_value=1,
                            value=30,
                            key="ferias_dias"
                        )
                    
                    submit_ferias = st.form_submit_button("Registrar Férias")
                    
                    if submit_ferias:
                        funcionario = next((f for f in funcionarios if f.nome == funcionario_selecionado), None)
                        if funcionario:
                            ferias_ativa = session.query(Ferias).filter(
                                Ferias.funcionario_id == funcionario.id,
                                Ferias.ativa == True
                            ).first()

                            if ferias_ativa:
                                st.error(f'{funcionario_selecionado} já está em férias.')
                            else:
                                data_fim_ferias = data_inicio_ferias + timedelta(days=dias_ferias - 1)
                                
                                try:
                                    novas_ferias = Ferias(
                                        funcionario_id=funcionario.id,
                                        data_inicio=data_inicio_ferias,
                                        data_fim=data_fim_ferias,
                                        dias=dias_ferias,
                                        ativa=True,
                                        created_at=func.now()
                                    )
                                    
                                    session.add(novas_ferias)
                                    session.commit()
                                    st.success('Férias registradas com sucesso!')
                                    time.sleep(1)  # Pequena pausa para mostrar a mensagem
                                    st.empty()  # Limpa a mensagem
                                    
                                except Exception as e:
                                    session.rollback()
                                    st.error(f"Erro ao registrar férias: {str(e)}")

            # Nova Aba de Atestados
            with tab2:
                st.markdown("## Registrar Atestado")
                with st.form("registrar_atestado"):
                    funcionario_selecionado_atestado = st.selectbox(
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
                    
                    # Adicionando campo de motivo
                    motivo_atestado = st.text_area(
                        'Motivo do Atestado',
                        key="atestado_motivo",
                        height=100
                    )
                    
                    submit_atestado = st.form_submit_button("Registrar Atestado")
                    
                    if submit_atestado:
                        if not motivo_atestado.strip():  # Verifica se o motivo não está vazio
                            st.error("Por favor, informe o motivo do atestado.")
                        else:
                            funcionario = next((f for f in funcionarios if f.nome == funcionario_selecionado_atestado), None)
                            if funcionario:
                                atestado_ativo = session.query(Atestado).filter(
                                    Atestado.funcionario_id == funcionario.id,
                                    Atestado.ativo == True
                                ).first()

                                if atestado_ativo:
                                    st.error(f'{funcionario_selecionado_atestado} já está em atestado.')
                                else:
                                    data_fim_atestado = data_inicio_atestado + timedelta(days=dias_atestado - 1)
                                    
                                    try:
                                        novo_atestado = Atestado(
                                            funcionario_id=funcionario.id,
                                            data_inicio=data_inicio_atestado,
                                            data_fim=data_fim_atestado,
                                            dias=dias_atestado,
                                            motivo=motivo_atestado,  # Adicionando o motivo
                                            ativo=True,
                                            created_at=datetime.now()
                                        )
                                        
                                        session.add(novo_atestado)
                                        session.commit()
                                        st.success(f'Atestado registrado com sucesso!')
                                        time.sleep(1)
                                        st.empty()
                                        
                                    except Exception as e:
                                        session.rollback()
                                        st.error(f"Erro ao registrar atestado: {str(e)}")

            # Aba de Funcionários Afastados
            with tab3:
                # Botões de exportação no topo da aba
                col_export1, col_export2 = st.columns(2)
                
                with col_export1:
                    try:
                        excel_file = exportar_relatorio_ferias(session, empresa_selecionada)
                        st.download_button(
                            label="📥 Exportar Relatório de Férias",
                            data=excel_file,
                            file_name=f"relatorio_ferias_{empresa_selecionada}_{datetime.now().strftime('%B_%Y')}.xlsx",
                            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                            use_container_width=True
                        )
                    except Exception as e:
                        st.error(f"Erro ao gerar relatório de férias: {str(e)}")
                
                with col_export2:
                    try:
                        excel_file = exportar_relatorio_atestados(session, empresa_selecionada)
                        st.download_button(
                            label="📥 Exportar Relatório de Atestados",
                            data=excel_file,
                            file_name=f"relatorio_atestados_{empresa_selecionada}_{datetime.now().strftime('%B_%Y')}.xlsx",
                            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                            use_container_width=True
                        )
                    except Exception as e:
                        st.error(f"Erro ao gerar relatório de atestados: {str(e)}")

                # Resto do código existente da aba (listagem de funcionários afastados)
                st.markdown("---")
                col1, col2 = st.columns(2)
                
                with col1:
                    st.markdown("### Funcionários em Férias")
                    funcionarios_em_ferias = session.query(Ferias).filter(Ferias.ativa == True).all()
                    
                    if funcionarios_em_ferias:
                        for ferias in funcionarios_em_ferias:
                            funcionario = session.query(Funcionario).get(ferias.funcionario_id)
                            if funcionario:
                                with st.container():
                                    st.markdown(f"**{funcionario.nome}**")
                                    st.write(f"Férias: {ferias.data_inicio} a {ferias.data_fim}")
                                    if st.button('Retornar ao Trabalho', key=f'retorno_ferias_{funcionario.id}'):
                                        try:
                                            ferias.ativa = False
                                            session.commit()
                                            st.success(f'{funcionario.nome} retornou ao trabalho')
                                            time.sleep(1)  # Pequena pausa para mostrar a mensagem
                                            st.empty()  # Limpa a mensagem
                                        except Exception as e:
                                            st.error(f"Erro ao retornar do trabalho: {str(e)}")
                                st.markdown("---")
                    else:
                        st.info("Não há funcionários em férias no momento.")
                
                with col2:
                    st.markdown("### Funcionários em Atestado")
                    funcionarios_em_atestado = session.query(Atestado).filter(Atestado.ativo == True).all()
                    
                    if funcionarios_em_atestado:
                        for atestado in funcionarios_em_atestado:
                            funcionario = session.query(Funcionario).get(atestado.funcionario_id)
                            if funcionario:
                                with st.container():
                                    st.markdown(f"**{funcionario.nome}**")
                                    st.write(f"Atestado: {atestado.data_inicio} a {atestado.data_fim}")
                                    if st.button('Retornar ao Trabalho', key=f'retorno_atestado_{funcionario.id}'):
                                        try:
                                            atestado.ativo = False
                                            session.commit()
                                            st.success(f'{funcionario.nome} retornou ao trabalho')
                                            time.sleep(1)  # Pequena pausa para mostrar a mensagem
                                            st.empty()  # Limpa a mensagem
                                        except Exception as e:
                                            st.error(f"Erro ao retornar do trabalho: {str(e)}")
                                st.markdown("---")
                    else:
                        st.info("Não há funcionários em atestado no momento.")

        else:
            st.warning('Não há funcionários cadastrados para esta empresa.')
    else:
        st.warning('Selecione uma empresa para gerenciar afastamentos.')