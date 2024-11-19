import streamlit as st
import pandas as pd
from datetime import datetime, date
import calendar
from database.config import get_session
from database.crud import DatabaseManager
from exportar_escalas import exportar_escalas_para_excel, adicionar_botao_exportacao
from database.models import Ferias, Atestado
from utils import transformar_escala_folguistas_para_dataframe
from escala_generator import gerar_escala_folguistas

def app():
    st.title('Geração de Escala - Folguistas')
    
    # Inicializa conexão com banco de dados
    session = next(get_session())
    db = DatabaseManager(session)
    
    # Lista empresas do banco de dados
    empresas = db.listar_empresas()
    empresa_options = {empresa.nome: empresa.id for empresa in empresas}
    
    empresa_selecionada = st.selectbox('Selecione a Empresa', options=list(empresa_options.keys()))
    
    # Definir o primeiro dia do mês atual automaticamente
    hoje = datetime.today()
    data_inicio = date(hoje.year, hoje.month, 1)  # Primeiro dia do mês
    
    # Mostrar a data de forma informativa
    #st.info(f'Escala será gerada para o mês de {data_inicio.strftime("%B/%Y")}')
    
    data_inicio_str = data_inicio.strftime('%Y-%m-%d')
    
    # Chave única para o estado da escala (mantendo o mesmo formato do gerar_escala.py)
    escala_key = f"escala_folguistas_{empresa_selecionada}_{data_inicio_str}"
    
    if empresa_selecionada:
        empresa_id = empresa_options[empresa_selecionada]
        folguistas = db.listar_folguistas_por_empresa(empresa_id)
        
        if folguistas:
            # Se não existir escala salva ou usuário solicitar regeneração
            if escala_key not in st.session_state or st.button("Gerar Nova Escala"):
                folguistas_info = {}
                afastamentos_info = {}
                
                for folguista in folguistas:
                    nome = f"{folguista.nome} ({folguista.familia_letras})"
                    folguistas_info[nome] = {
                        'horario': folguista.horario_turno,
                        'turno': folguista.turno
                    }
                    
                    # Verificar férias ativas
                    ferias_ativa = session.query(Ferias).filter(
                        Ferias.funcionario_id == folguista.id,
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
                        Atestado.funcionario_id == folguista.id,
                        Atestado.ativo == True
                    ).first()
                    
                    if atestado_ativo:
                        afastamentos_info[nome] = {
                            'tipo': 'Atestado',
                            'data_inicio': atestado_ativo.data_inicio,
                            'data_fim': atestado_ativo.data_fim
                        }

                escala_folguistas = gerar_escala_folguistas(
                    folguistas_info, 
                    data_inicio_str,
                    afastamentos_info
                )
                
                # Transformar a escala em DataFrame
                df_escala = transformar_escala_folguistas_para_dataframe(escala_folguistas, data_inicio)
                
                # Salvar na session_state
                st.session_state[escala_key] = df_escala
            
            # Usar a escala salva
            df_escala = st.session_state[escala_key]
            
            st.write("Edite a escala dos folguistas:")
            df_escala_editado = st.data_editor(
                df_escala,
                key=f"editor_folguistas_{escala_key}",
                disabled=["Folguista"],
                hide_index=True,
            )
            
            # Botão para salvar alterações
            if st.button('Salvar Alterações'):
                st.session_state[escala_key] = df_escala_editado
                st.success('Alterações na escala dos folguistas salvas com sucesso!')
            
            # Atualizar df_escala na session_state
            st.session_state[escala_key] = df_escala_editado
            
            # Criar DataFrame vazio para a escala principal (já que é só folguistas)
            df_escala_principal = pd.DataFrame()
            
            adicionar_botao_exportacao(
                df_escala_final=df_escala_principal,  # DataFrame vazio para escala principal
                df_folguistas=df_escala_editado,      # DataFrame dos folguistas
                empresa_nome=empresa_selecionada      # Nome da empresa
            )
            
            # st.write("Visualização final da escala dos folguistas:")
            # st.dataframe(st.session_state[escala_key], hide_index=True)
            
        else:
            st.warning('Não há folguistas cadastrados para esta empresa.')
    else:
        st.warning('Selecione uma empresa para gerar a escala.')