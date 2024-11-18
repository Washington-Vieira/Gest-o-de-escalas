import streamlit as st
from pages import cadastro_empresa, cadastro_funcionario, gerar_escala, gerar_escala_folguista
from pages.gerenciar_ferias import app as gerenciar_ferias
from data_manager import carregar_empresas

st.set_page_config(page_title="Gerador de Escala", layout="wide")

# Carregar o CSS externo
def load_css(file_name):
    with open(file_name) as f:
        st.markdown(f'<style>{f.read()}</style>', unsafe_allow_html=True)

load_css('styles/main.css')

# Inicializar st.session_state.empresas
if 'empresas' not in st.session_state:
    st.session_state.empresas = carregar_empresas()

# Definir ícones para cada página
PAGES = {
    "🏢 Cadastro de Empresa": cadastro_empresa,
    "👤 Cadastro de Funcionário": cadastro_funcionario,
    "🚨 Gerenciar Afastamentos": gerenciar_ferias,
    "📅 Gerar Escala": gerar_escala,
    "📊 Gerar Escala Folguista": gerar_escala_folguista
}

# Mover o título da navegação para cima
st.sidebar.title('🧭 Navegação')
st.sidebar.markdown('---')

# Criar botões de navegação
for name, page_func in PAGES.items():
    if st.sidebar.button(name):
        st.session_state.page = name

# Exibir a página selecionada
if 'page' not in st.session_state:
    st.session_state.page = "🏢 Cadastro de Empresa"

# Chamar a função app() da página selecionada
PAGES[st.session_state.page]()

# Adicionar informações no rodapé
st.sidebar.text('Versão 0.5.7')
