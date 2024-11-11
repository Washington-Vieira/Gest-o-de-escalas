import streamlit as st
from datetime import datetime, timedelta
from database.config import get_session
from database.crud import DatabaseManager
from database.models import Funcionario, Ferias, Atestado
from exportar_relatorio_ferias import adicionar_botao_exportacao_ferias
from exportar_relatorio_atestados import exportar_relatorio_atestados
import pandas as pd

def app():
    st.title('Gerenciar Férias e Atestados')
    
    # Inicializar conexão com banco de dados
    session = next(get_session())
    db = DatabaseManager(session)
    
    # Lista empresas do banco de dados
    empresas = db.listar_empresas()
    empresa_options = {empresa.nome: empresa.id for empresa in empresas}
    
    empresa_selecionada = st.selectbox('Selecione a Empresa', options=list(empresa_options.keys()))
    
    if empresa_selecionada:
        empresa_id = empresa_options[empresa_selecionada]
        
        # Buscar funcionários e folguistas da empresa
        funcionarios = db.listar_funcionarios_por_empresa(empresa_id)
        
        if funcionarios:
            tab1, tab2 = st.tabs(["Férias", "Atestados"])
            
            with tab1:
                st.markdown("## Registrar Férias")
                with st.form("registrar_ferias"):
                    funcionario_selecionado = st.selectbox(
                        'Selecione o Funcionário ou Folguista',
                        options=[f.nome for f in funcionarios]
                    )
                    
                    col1, col2 = st.columns(2)
                    with col1:
                        data_inicio_ferias = st.date_input('Data de Início das Férias', value=datetime.today())
                    with col2:
                        duracao_ferias = st.number_input('Duração das Férias (em dias)', min_value=1, max_value=30, value=30)
                    
                    submit_button = st.form_submit_button("Registrar Férias")
                    
                    if submit_button:
                        funcionario = next((f for f in funcionarios if f.nome == funcionario_selecionado), None)
                        if funcionario:
                            # Verificar se já existe um registro de férias ativo
                            ferias_ativa = session.query(Ferias).filter(
                                Ferias.funcionario_id == funcionario.id,
                                Ferias.ativa == True
                            ).first()
                            
                            if ferias_ativa:
                                st.error(f'{funcionario_selecionado} já está em férias de {ferias_ativa.data_inicio} a {ferias_ativa.data_fim}.')
                            else:
                                data_fim_ferias = data_inicio_ferias + timedelta(days=duracao_ferias)
                                
                                # Criar novo registro de férias
                                novas_ferias = Ferias(
                                    funcionario_id=funcionario.id,
                                    data_inicio=data_inicio_ferias,
                                    data_fim=data_fim_ferias,
                                    ativa=True
                                )
                                
                                # Atualizar status do funcionário
                                db.atualizar_status_ferias(funcionario.id, True)
                                
                                # Salvar no banco de dados
                                session.add(novas_ferias)
                                session.commit()
                                
                                st.success(f'Férias registradas para {funcionario_selecionado} de {data_inicio_ferias} a {data_fim_ferias}')
                                st.rerun()

                st.markdown("## Funcionários e Folguistas em Férias")
                funcionarios_em_ferias = session.query(Ferias).filter(Ferias.ativa == True).all()
                
                # Usar um conjunto para evitar duplicações
                funcionarios_exibidos = set()
                
                if funcionarios_em_ferias:
                    for ferias in funcionarios_em_ferias:
                        funcionario = session.query(Funcionario).get(ferias.funcionario_id)
                        if funcionario and funcionario.nome not in funcionarios_exibidos:
                            funcionarios_exibidos.add(funcionario.nome)
                            with st.container():
                                col1, col2, col3 = st.columns([2, 2, 1])
                                with col1:
                                    st.markdown(f"**{funcionario.nome}**")
                                with col2:
                                    st.write(f"{ferias.data_inicio} a {ferias.data_fim}")
                                with col3:
                                    if st.button('Retornar ao Trabalho', key=f'retorno_{funcionario.id}'):
                                        # Encerrar férias ativas
                                        ferias.ativa = False
                                        session.commit()
                                        
                                        st.success(f'{funcionario.nome} retornou ao trabalho')
                                        st.rerun()
                            st.markdown("---")
                else:
                    st.info("Não há funcionários ou folguistas em férias no momento.")

                st.markdown("## Histórico de Férias")
                adicionar_botao_exportacao_ferias(session, empresa_selecionada)

            with tab2:
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
                            value=1,
                            key="atestado_dias"
                        )
                    
                    motivo = st.text_area(
                        "Motivo do Atestado",
                        help="Descreva o motivo do atestado"
                    )
                    
                    submit_atestado = st.form_submit_button("Registrar Atestado")
                    
                    if submit_atestado:
                        funcionario = next((f for f in funcionarios if f.nome == funcionario_selecionado), None)
                        if funcionario:
                            # Verificar se já existe um registro de atestado ativo
                            atestado_ativo = session.query(Atestado).filter(
                                Atestado.funcionario_id == funcionario.id,
                                Atestado.ativo == True
                            ).first()

                            if atestado_ativo:
                                st.error(f'{funcionario_selecionado} já possui um atestado ativo de {atestado_ativo.data_inicio} a {atestado_ativo.data_fim}.')
                            else:
                                data_fim_atestado = data_inicio_atestado + timedelta(days=dias_atestado)
                                
                                novo_atestado = Atestado(
                                    funcionario_id=funcionario.id,
                                    data_inicio=data_inicio_atestado,
                                    data_fim=data_fim_atestado,
                                    motivo=motivo,
                                    dias=dias_atestado,
                                    ativo=True
                                )
                                
                                session.add(novo_atestado)
                                session.commit()
                                
                                st.success(f'Atestado registrado para {funcionario_selecionado} de {data_inicio_atestado} a {data_fim_atestado}')
                                st.rerun()
                                # Atualizar a escala de trabalho
                                atualizar_escala(funcionario.id, data_inicio_atestado, data_fim_atestado, "Atestado")

                st.markdown("## Atestados Ativos")
                atestados_ativos = session.query(Atestado).filter(
                    Atestado.ativo == True,
                    Atestado.funcionario_id.in_([f.id for f in funcionarios])
                ).all()
                
                if atestados_ativos:
                    for atestado in atestados_ativos:
                        funcionario = next((f for f in funcionarios if f.id == atestado.funcionario_id), None)
                        if funcionario:
                            with st.container():
                                col1, col2, col3, col4 = st.columns([2, 2, 2, 1])
                                with col1:
                                    st.markdown(f"**{funcionario.nome}**")
                                with col2:
                                    st.write(f"{atestado.data_inicio} a {atestado.data_fim}")
                                with col3:
                                    st.write(f"Motivo: {atestado.motivo}")
                                with col4:
                                    if st.button('Encerrar', key=f'encerrar_atestado_{atestado.id}'):
                                        atestado.ativo = False
                                        session.commit()
                                        st.success(f'Atestado encerrado')
                                        st.rerun()
                            st.markdown("---")
                else:
                    st.info("Não há atestados ativos no momento.")

                st.markdown("## Histórico de Atestados")
                if st.button("Exportar Relatório de Atestados"):
                    try:
                        excel_file = exportar_relatorio_atestados(session, empresa_selecionada)
                        st.download_button(
                            label="Baixar Relatório de Atestados",
                            data=excel_file,
                            file_name=f"relatorio_atestados_{empresa_selecionada}_{datetime.now().strftime('%B_%Y')}.xlsx",
                            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                        )
                    except Exception as e:
                        st.error(f"Erro ao gerar relatório: {str(e)}")
        else:
            st.warning('Não há funcionários cadastrados para esta empresa.')
    else:
        st.warning('Selecione uma empresa para gerenciar férias.')

def atualizar_escala(funcionario_id, data_inicio, data_fim, tipo):
    """Atualiza a escala de trabalho com os dias de férias ou atestado."""
    if 'escala_folguistas' in st.session_state:
        df = st.session_state.escala_folguistas
        for dia in pd.date_range(start=data_inicio, end=data_fim):
            dia_str = f'Dia {dia.day}'
            if dia_str in df.columns:
                index = df[df['Folguista'].str.contains(funcionario_id)].index
                if not index.empty:
                    df.at[index[0], dia_str] = tipo
        st.session_state.escala_folguistas = df
