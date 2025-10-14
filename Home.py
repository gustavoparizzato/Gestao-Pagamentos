import streamlit as st
import os
from datetime import datetime, timedelta, timezone
from src.database.autenticacao import autenticar, esta_autenticado, usuario_atual
from src.menu.menu import menu_navegacao_sidebar

st.set_page_config(page_title="Home", page_icon="🏠", layout="wide")

menu_navegacao_sidebar()

# CSS para ocultar a sidebar e bloquear o botão de expansão quando não estiver autenticado
hide_sidebar_style = """
    <style>
        /* Oculta a sidebar completamente */
        section[data-testid="stSidebar"] {
            display: none !important;
        }
    </style>
"""

# Verificar se o usuário está autenticado
if not esta_autenticado():
    # Se não estiver autenticado, aplicar o CSS para ocultar a sidebar
    st.markdown(hide_sidebar_style, unsafe_allow_html=True)

st.markdown("<h1 style='text-align:center;'>🔍 Sistema de Gestão Orçamentária</h1>", unsafe_allow_html=True)
st.markdown("---")

if not esta_autenticado():

    col_esq, col_meio, col_dir = st.columns([2,5,2.1])

    with col_meio:
        with st.form("form_login", clear_on_submit=False):
            st.markdown("### 🔐 Login")
            email = st.text_input("E-mail", autocomplete="username")
            senha = st.text_input("Senha", type="password", autocomplete="current-password")
            entrar = st.form_submit_button("Entrar", type="primary")

    if entrar:
        ok, erro = autenticar((email or "").strip().lower(), senha or "")
        if ok:
            st.success("Login realizado!")
            st.rerun()
        else:
            st.error(erro)

else:
    u = usuario_atual()
    perfil = u["perfil"]

    st.success(f"Bem-vindo, **{u['nome']}**!")
    st.markdown("#### Acesse as funcionalidades pelo menu lateral")
    # st.caption(f"E-mail: {u['email']} • Login: {u['momento_login']}")

    st.markdown("---")
    st.markdown(f"**Usuário:** {u['nome']} ({perfil})")

    if st.sidebar.button("🚪 Desconectar", key="btn_sair", use_container_width=True):
        st.session_state.pop("usuario_autenticado", None)
        st.switch_page("Home.py")