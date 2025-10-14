import streamlit as st
from src.database.autenticacao import usuario_atual

#Constrói o menu lateral de navegação com controle de acesso
def menu_navegacao_sidebar():

    u = usuario_atual()
    perfil = u.get("perfil", "").lower() if u else ""

    if st.sidebar.button("🏠 Home", key="btn_home", use_container_width=True, type="primary"):
        st.switch_page("Home.py")

    if st.sidebar.button("🧾 Cheques", key="btn_visao", use_container_width=True, type="primary"):
        st.switch_page("pages/1_Cheques.py")

    if st.sidebar.button("⚙️ Configurações", key="btn_config", use_container_width=True, type="primary"):
        st.switch_page("pages/2_Configurações.py")

    st.sidebar.markdown("---")

    # --- Rodapé com dados do usuário ---
    if u:
        st.sidebar.caption(f"👤 {u['nome']} ({u['perfil']})")