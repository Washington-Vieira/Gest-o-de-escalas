import streamlit as st
from datetime import datetime, time
from database.config import get_session
from database.models import Funcionario
from database.crud import DatabaseManager
from utils import funcoes_familias, turnos_funcionarios

def app():
    st.title('Cadastro de Funcionários')
    
    session = next(get_session())
    db = DatabaseManager(session)
    
    # Lista de empresas para seleção
    empresas = db.listar_empresas()
    empresa_options = {empresa.nome: empresa.id for empresa in empresas}
    
    empresa_selecionada = st.selectbox('Selecione a Empresa', options=list(empresa_options.keys()))
    nome_funcionario = st.text_input('Nome do Funcionário')
    
    # Adicionando "Folguista" à lista de funções
    funcoes_familias['Folguista'] = 'CP'  # Adiciona a função "Folguista" com uma família de letras padrão
    funcao_funcionario = st.selectbox('Selecione a Função', options=list(funcoes_familias.keys()))
    
    # Inicializa as variáveis de horário e turno
    horario_turno = ""
    turno_funcionario = ""

    # Se "Folguista" for selecionado, preenche automaticamente os campos
    if funcao_funcionario == 'Folguista':
        horario_turno = "Variável"
        turno_funcionario = "Variável"
        st.write("Os campos de horário e turno foram preenchidos automaticamente como 'Variável'.")
    else:
        # Se não for folguista, permite a seleção de turno
        turno_funcionario = st.selectbox('Selecione o Turno', options=turnos_funcionarios)

        # Exibe os campos de hora de início e fim do turno
        hora_inicio = st.time_input('Hora de Início do Turno', value=time(6, 0))
        hora_fim = st.time_input('Hora de Fim do Turno', value=time(14, 0))

    familia_letras = funcoes_familias[funcao_funcionario]
    data_inicio = st.date_input('Data de Início', value=datetime.today())

    if st.button('Cadastrar Funcionário'):
        if all([nome_funcionario, funcao_funcionario, empresa_selecionada]):
            # Se não for folguista, formata o horário do turno
            if funcao_funcionario != 'Folguista':
                horario_turno = f"{hora_inicio.strftime('%H:%M')} as {hora_fim.strftime('%H:%M')}"
            
            novo_funcionario = Funcionario(
                nome=nome_funcionario,
                funcao=funcao_funcionario,
                familia_letras=familia_letras,
                horario_turno=horario_turno,
                data_inicio=data_inicio,
                turno=turno_funcionario,
                empresa_id=empresa_options[empresa_selecionada],
                em_ferias=False,
                is_folguista=(funcao_funcionario == 'Folguista')  # Define is_folguista como True se for folguista
            )
            
            db.criar_funcionario(novo_funcionario)
            st.success(f'Funcionário {nome_funcionario} cadastrado com sucesso!')
        else:
            st.error('Por favor, preencha todos os campos.')

    # Lista de funcionários da empresa selecionada
    if empresa_selecionada:
        st.subheader(f"Funcionários de {empresa_selecionada}")
        funcionarios = db.listar_funcionarios_por_empresa(empresa_options[empresa_selecionada])
        for func in funcionarios:
            col1, col2 = st.columns([3, 1])
            with col1:
                st.write(f"- {func.nome} ({func.funcao})")
            with col2:
                if st.button(f'Excluir {func.nome}'):
                    # Alerta de confirmação
                    if st.session_state.get(f'confirmar_exclusao_{func.id}', False):
                        db.session.delete(func)  # Exclui o funcionário
                        db.session.commit()  # Confirma a exclusão
                        st.success(f'Funcionário {func.nome} excluído com sucesso!')
                        st.session_state[f'confirmar_exclusao_{func.id}'] = False  # Resetar estado
                    else:
                        st.session_state[f'confirmar_exclusao_{func.id}'] = True
                        st.warning(f'Você tem certeza que deseja excluir o funcionário {func.nome}? Clique novamente para confirmar.')

# Chame a função app() para executar a aplicação
if __name__ == "__main__":
    app()
