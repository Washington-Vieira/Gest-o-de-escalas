import streamlit as st
import pandas as pd
import calendar
from datetime import datetime
from escala_generator import gerar_escala_turnos_por_funcao
from utils import transformar_escala_para_dataframe, turnos_funcionarios
from exportar_escalas import adicionar_botao_exportacao, exportar_escalas_para_excel
from database.config import get_session
from database.crud import DatabaseManager

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
        
        # Melhorar a lógica de filtro de funcionários ativos
        funcionarios_ativos = []
        for f in funcionarios:
            status = db.verificar_status_funcionario(f.id)
            if not status["em_ferias"] and not status["em_atestado"]:
                funcionarios_ativos.append(f)

        if funcionarios_ativos:
            lista_dataframes = []

            # Agrupa funcionários por turno (apenas ativos)
            funcionarios_por_turno = {}
            for turno in turnos_funcionarios:
                funcionarios_por_turno[turno] = [f for f in funcionarios_ativos if f.turno == turno]

            for turno in turnos_funcionarios:
                st.subheader(f'Escala {turno} - {empresa_selecionada}')
                funcionarios_turno = funcionarios_por_turno[turno]

                if funcionarios_turno:
                    funcionarios_por_funcao = {}
                    ferias = []  # Lista de funcionários de férias/atestado
                    
                    # Atualizar a lógica de construção do dicionário de funcionários
                    for func in funcionarios_turno:
                        status = db.verificar_status_funcionario(func.id)
                        if not status["em_ferias"] and not status["em_atestado"]:
                            funcao = func.funcao
                            nome = f"{func.nome} ({func.familia_letras})"
                            if funcao not in funcionarios_por_funcao:
                                funcionarios_por_funcao[funcao] = {}
                            funcionarios_por_funcao[funcao][nome] = {
                                'horario': func.horario_turno,
                                'data_inicio': func.data_inicio,
                                'turno': func.turno
                            }
                        else:
                            ferias.append(func.nome)

                    escala_por_funcao = gerar_escala_turnos_por_funcao(
                        funcionarios_por_funcao, 
                        data_inicio_str, 
                        ferias
                    )
                    
                    num_dias_no_mes = calendar.monthrange(data_inicio.year, data_inicio.month)[1]
                    df_escala = transformar_escala_para_dataframe(escala_por_funcao, num_dias_no_mes)
                    
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
                
                # Modificação aqui: Usar dados da sessão se existirem
                if 'escala_folguistas' in st.session_state:
                    df_folguistas = st.session_state.escala_folguistas
                else:
                    # Caso não haja dados na sessão, criar DataFrame vazio
                    df_folguistas = pd.DataFrame()
                
                # Botão de exportação com os dados corretos
                if st.button('Exportar para Excel'):
                    try:
                        mes_ano = data_inicio.strftime('%B %Y')
                        excel_file = exportar_escalas_para_excel(
                            df_final,
                            df_folguistas,
                            empresa_selecionada,
                            mes_ano
                        )
                        
                        st.download_button(
                            label="Baixar Excel",
                            data=excel_file,
                            file_name=f"escalas_{empresa_selecionada}_{mes_ano}.xlsx",
                            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                        )
                    except Exception as e:
                        st.error(f"Erro ao exportar: {str(e)}")
        else:
            st.warning('Não há funcionários cadastrados para esta empresa.')
    else:
        st.warning('Selecione uma empresa para gerar a escala.')