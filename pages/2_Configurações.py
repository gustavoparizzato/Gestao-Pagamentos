import streamlit as st
import pandas as pd
from datetime import datetime
from src.database.persistir_dados_bd import cadastrar_usuario, atualizar_usuario, gerar_hash_senha
from src.database.recuperar_dados_bd import carregar_usuarios, carregar_usuario_id, email_existe
from src.database.autenticacao import exigir_login, usuario_atual
from src.menu.menu import menu_navegacao_sidebar

st.title("Configurações")

exigir_login(["admin", "analista", "viewer"])
u = usuario_atual() or {}
perfil = u.get("perfil") or ""

menu_navegacao_sidebar()

opcoes = ["Atualizar Meus Dados"]
if perfil == "admin":
    opcoes.extend(["Listar Usuários", "Cadastrar Usuário"])
if perfil == "analista":
    opcoes.append("Listar Usuários")

modo = st.radio("**Ações**", opcoes, key="settings_mode", horizontal= True)

st.markdown("---")

# Listar todos os usuários cadastrados
if modo == "Listar Usuários":
    st.subheader("👥 Usuários")

    usuarios_df = carregar_usuarios()
    if usuarios_df is None or usuarios_df.empty:
        st.info("Nenhum usuário encontrado.")
        st.stop()

    # Cabeçalho
    cols_head = st.columns([1, 2, 3, 1.5, 1, 2])
    with cols_head[0]: st.markdown("**ID**")
    with cols_head[1]: st.markdown("**Nome**")
    with cols_head[2]: st.markdown("**E-mail**")
    with cols_head[3]: st.markdown("**Perfil**")
    with cols_head[4]: st.markdown("**Ativo**")
    with cols_head[5]: st.markdown("**Ações**")

    # Para cada usuário, mostramos a linha e um botão de editar
    for _, row in usuarios_df.iterrows():
        uid = row["idUsuario"]

        # estado de edição por linha
        edit_key = f"editing_{uid}"
        if edit_key not in st.session_state:
            st.session_state[edit_key] = False

        if not st.session_state[edit_key]:
            # Modo visualização
            col = st.columns([1, 2, 3, 1.5, 1, 2])
            with col[0]: st.write(uid)
            with col[1]: st.write(row["nome"])
            with col[2]: st.write(row["email"])
            with col[3]: st.write(row["perfil"])
            with col[4]: st.write("✅" if bool(row["ativo"]) else "❌")
            if perfil == "admin": # somente admin pode editar dados de usuários
                with col[5]:
                    if st.button("✏️ Editar", key=f"btn_edit_{uid}", type="primary"):
                        st.session_state[edit_key] = True
                        st.rerun()

        else:
            with st.form(f"form_edit_{uid}", clear_on_submit=False):
                col = st.columns([1, 2, 3, 1.5, 1, 2])
                with col[0]:
                    st.write(uid)
                with col[1]:
                    novo_nome = st.text_input(" ", value=str(row["nome"]), key=f"nome_{uid}", label_visibility="collapsed")
                with col[2]:
                    novo_email = st.text_input(" ", value=str(row["email"]), key=f"email_{uid}", label_visibility="collapsed")
                with col[3]:
                    perfis = ["admin", "analista", "viewer"]
                    try:
                        idx = perfis.index(str(row["perfil"]))
                    except ValueError:
                        idx = 0
                    novo_perfil = st.selectbox(" ", perfis, index=idx, key=f"perfil_{uid}", label_visibility="collapsed")
                with col[4]:
                    novo_ativo = st.toggle(" ", value=bool(row["ativo"]), key=f"ativo_{uid}", label_visibility="collapsed")
                with col[5]:
                    b1, b2 = st.columns(2)
                    with b1:
                        salvar = st.form_submit_button("💾 Salvar")
                    with b2:
                        cancelar = st.form_submit_button("↩️ Cancelar")

                if cancelar:
                    st.session_state[edit_key] = False
                    st.rerun()

                if salvar:
                    novo_nome = (novo_nome or "").strip()
                    novo_email = (novo_email or "").strip().lower()

                    if not novo_nome or not novo_email:
                        st.error("Nome e e-mail são obrigatórios.")
                        st.stop()
                    if novo_email != str(row["email"]).lower():
                        if email_existe(novo_email):
                            st.error("E-mail já cadastrado para outro usuário.")
                            st.stop()

                    try:
                        ok = atualizar_usuario(uid, nome=novo_nome, email=novo_email, perfil=novo_perfil, ativo=bool(novo_ativo), senha_hash=None)  # não altera senha aqui
                        if ok:
                            st.success(f"Usuário {uid} atualizado com sucesso!")
                            st.session_state[edit_key] = False
                            st.rerun()
                        else:
                            st.error("Não foi possível atualizar o usuário.")
                    except Exception as e:
                        st.error(str(e))

    st.markdown("---")
    with st.expander("📋 Visualizar tabela completa (somente leitura)"):
        st.dataframe(
            usuarios_df[
                [
                    "idUsuario", "nome", "email", "perfil", "ativo", "criado_em", "ultima_modificacao", "ultimo_login"]
                ],
                hide_index=True,
                column_config={
                    "idUsuario": st.column_config.TextColumn("ID"),
                    "nome": st.column_config.TextColumn("Nome"),
                    "email": st.column_config.TextColumn("E-mail"),
                    "perfil": st.column_config.SelectboxColumn("Perfil", options=["admin", "analista", "viewer"]),
                    "ativo": st.column_config.CheckboxColumn("Ativo"),
                    "criado_em": st.column_config.DatetimeColumn("Criado em", format="DD/MM/YYYY HH:mm:ss"),
                    "ultima_modificacao": st.column_config.DatetimeColumn("Última Modificação", format="DD/MM/YYYY HH:mm:ss"),
                    "ultimo_login": st.column_config.DatetimeColumn("Último Login", format="DD/MM/YYYY HH:mm:ss"),
                }
            )

# Cadastrar um novo usuário
elif modo == "Cadastrar Usuário":
    st.subheader("➕ Cadastrar Usuário")

    with st.form("form_cadastro", clear_on_submit=True):
        col1, col2 = st.columns([2, 2])
        with col1:
            nome = st.text_input("Nome *")
            email = st.text_input("E-mail *")
            perfil = st.selectbox("Perfil *", ["admin", "analista", "viewer"])
        with col2:
            ativo = st.toggle("Ativo", value=True)
            senha = st.text_input("Senha *", type="password")
            confirma = st.text_input("Confirmar senha *", type="password")

        salvar = st.form_submit_button("💾 Cadastrar", type="primary")

    if salvar:
        if not nome or not email or not senha or not confirma:
            st.error("Preencha todos os campos obrigatórios (*).")
        elif senha != confirma:
            st.error("As senhas não conferem.")
        elif email_existe(email):
            st.error("E-mail já cadastrado.")
        else:
            try:
                cadastrar_usuario(nome, email, perfil, ativo, senha)
                st.success(f"Usuário **{nome}** cadastrado com sucesso!")
            except Exception as e:
                st.error(str(e))

# Atualizar os próprios dados de login
elif modo == "Atualizar Meus Dados":
    st.subheader("✏️ Atualizar Meus Dados")

    u = usuario_atual()
    if not u or "idUsuario" not in u:
        st.error("Usuário atual não encontrado.")
        st.stop()

    user = carregar_usuario_id(u["idUsuario"])
    if not user:
        st.error("Usuário atual não encontrado.")
        st.stop()

    with st.form("form_update_dados"):
        col1, col2 = st.columns([2, 2])
        with col1:
            nome = st.text_input("Nome", value=user[1])
            email = st.text_input("E-mail", value=user[2])
            perfil = st.selectbox("Perfil", ["admin", "analista", "viewer"], index=["admin","analista","viewer"].index(user[3]))
        with col2:
            ativo = st.toggle("Ativo", value=bool(user[4]))

        st.markdown("**Trocar senha (opcional)**")
        colp1, colp2 = st.columns(2)
        with colp1:
            nova_senha = st.text_input("Nova senha", type="password")
        with colp2:
            conf_senha = st.text_input("Confirmar nova senha", type="password")

        salvar = st.form_submit_button("💾 Salvar alterações", type="primary")

    if salvar:
        if (nova_senha or conf_senha) and nova_senha != conf_senha:
            st.error("As senhas não conferem.")
            st.stop()
        else:
            senha_hash = gerar_hash_senha(nova_senha) if nova_senha else None

        ok = atualizar_usuario(user[0], nome=nome.strip(), email=email.strip(), perfil=perfil, ativo=ativo, senha_hash=senha_hash)
        if ok:
            st.success("Dados atualizados!")
            st.rerun()
        else:
            st.error("Não foi possível atualizar.")