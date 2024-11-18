import streamlit as st
import pandas as pd
import calendar
from datetime import datetime, date
from escala_generator import gerar_escala_turnos_por_funcao
from utils import transformar_escala_para_dataframe, turnos_funcionarios
from exportar_escalas import adicionar_botao_exportacao, exportar_escalas_para_excel
from database.config import get_session
from database.crud import DatabaseManager
from database.models import Ferias, Atestado

def obter_afastamentos(session, funcionarios):
    """Obtém todos os afastamentos (férias e atestados) ativos"""
    afastamentos_info = {}
    
    for funcionario in funcionarios:
        nome = f"{funcionario.nome} ({funcionario.familia_letras})"
        
        # Verifica férias ativas
        ferias = session.query(Ferias).filter(
            Ferias.funcionario_id == funcionario.id,
            Ferias.ativa == True
        ).first()
        
        if ferias:
            afastamentos_info[nome] = {
                'data_inicio': ferias.data_inicio,
                'data_fim': ferias.data_fim
            }
            continue  # Se tem férias, não precisa verificar atestado
            
        # Verifica atestados ativos
        atestado = session.query(Atestado).filter(
            Atestado.funcionario_id == funcionario.id,
            Atestado.ativo == True
        ).first()
        
        if atestado:
            afastamentos_info[nome] = {
                'data_inicio': atestado.data_inicio,
                'data_fim': atestado.data_fim
            }
    
    return afastamentos_info

def app():
    st.title('Geração de Escala')
    
    # Inicializa conexão com banco de dados
    session = next(get_session())
    db = DatabaseManager(session)
    
    # Lista empresas do banco de dados
    empresas = db.listar_empresas()
    empresa_options = {empresa.nome: empresa.id for empresa in empresas}
    
    empresa_selecionada = st.selectbox('Selecione a Empresa', options=list(empresa_options.keys()))
    data_inicio = st.date_input('Data de Início da Escala', value=datetime.today())
    data_inicio_str = data_inicio.strftime('%Y-%m-%d')

    if empresa_selecionada:
        empresa_id = empresa_options[empresa_selecionada]
        funcionarios = db.listar_funcionarios_por_empresa(empresa_id)
        
        if funcionarios:
            lista_dataframes = []

            # Agrupa funcionários por turno (usar todos, não apenas ativos)
            funcionarios_por_turno = {}
            for turno in turnos_funcionarios:
                funcionarios_por_turno[turno] = [f for f in funcionarios if f.turno == turno]

            for turno in turnos_funcionarios:
                st.subheader(f'Escala {turno} - {empresa_selecionada}')
                funcionarios_turno = funcionarios_por_turno[turno]

                if funcionarios_turno:
                    funcionarios_por_funcao = {}
                    afastamentos_info = obter_afastamentos(session, funcionarios_turno)
                    
                    # Atualizar a lógica de construção do dicionário de funcionários
                    for func in funcionarios_turno:
                        status = db.verificar_status_funcionario(func.id)
                        funcao = func.funcao
                        nome = f"{func.nome} ({func.familia_letras})"
                        
                        if funcao not in funcionarios_por_funcao:
                            funcionarios_por_funcao[funcao] = {}
                            
                        funcionarios_por_funcao[funcao][nome] = {
                            'horario': func.horario_turno,
                            'data_inicio': func.data_inicio,
                            'turno': func.turno
                        }
                        
                        # Verificar férias ativas
                        ferias_ativa = session.query(Ferias).filter(
                            Ferias.funcionario_id == func.id,
                            Ferias.ativa == True
                        ).first()
                        
                        if ferias_ativa:
                            afastamentos_info[nome] = {
                                'tipo': 'Férias',
                                'data_inicio': ferias_ativa.data_inicio,
                                'data_fim': ferias_ativa.data_fim
                            }
                        
                        # Verificar atestados ativos
                        atestado_ativo = session.query(Atestado).filter(
                            Atestado.funcionario_id == func.id,
                            Atestado.ativo == True
                        ).first()
                        
                        if atestado_ativo:
                            afastamentos_info[nome] = {
                                'tipo': 'Atestado',
                                'data_inicio': atestado_ativo.data_inicio,
                                'data_fim': atestado_ativo.data_fim
                            }

                    escala_por_funcao = gerar_escala_turnos_por_funcao(
                        funcionarios_por_funcao, 
                        data_inicio_str,
                        afastamentos_info
                    )
                    
                    num_dias_no_mes = calendar.monthrange(data_inicio.year, data_inicio.month)[1]
                    df_escala = transformar_escala_para_dataframe(escala_por_funcao, num_dias_no_mes)
                    
                    # Armazena o DataFrame na sessão para acesso posterior
                    st.session_state.df_escala = df_escala
                    
                    st.write(f"Edite a escala do {turno}:")
                    df_escala_editado = st.data_editor(
                        df_escala,
                        key=f"editor_{turno}",
                        disabled=["Funcionário"],
                        hide_index=True,
                    )
                    
                    if st.button(f'Salvar Alterações - {turno}'):
                        # Aqui você pode adicionar lógica para salvar as alterações no banco
                        st.success(f'Alterações na escala do {turno} salvas com sucesso!')
                    
                    lista_dataframes.append(df_escala_editado)

            if lista_dataframes:
                df_final = pd.concat(lista_dataframes, ignore_index=True)
                st.subheader('Escala Final')
                
                st.write("Visualização da escala final:")
                st.dataframe(df_final, hide_index=True)
                
                # Buscar escala de folguistas usando a mesma data
                primeiro_dia_mes = date(data_inicio.year, data_inicio.month, 1)
                data_inicio_str = primeiro_dia_mes.strftime('%Y-%m-%d')
                escala_key = f"escala_folguistas_{empresa_selecionada}_{data_inicio_str}"
                
                # Buscar escala de folguistas da session_state
                df_folguistas = st.session_state.get(escala_key, pd.DataFrame())
                
                # Gerar Excel e mostrar botão de download direto
                try:
                    mes_ano = primeiro_dia_mes.strftime('%B %Y')
                    excel_file = exportar_escalas_para_excel(
                        df_final,            # Escala principal
                        df_folguistas,       # Escala de folguistas
                        empresa_selecionada,
                        mes_ano
                    )
                    
                    st.download_button(
                        label="📥 Exportar Escala para Excel",
                        data=excel_file,
                        file_name=f"escalas_{empresa_selecionada}_{mes_ano}.xlsx",
                        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                        use_container_width=True
                    )
                except Exception as e:
                    st.error(f"Erro ao gerar arquivo Excel: {str(e)}")
        else:
            st.warning('Não há funcionários cadastrados para esta empresa.')
    else:
        st.warning('Selecione uma empresa para gerar a escala.')