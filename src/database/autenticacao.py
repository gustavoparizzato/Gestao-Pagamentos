import streamlit as st
from datetime import datetime
import bcrypt
from src.database.recuperar_dados_bd import carregar_usuarios
from src.database.persistir_dados_bd import atualizar_usuario

def obter_usuario_por_email(email: str):
    # Busca usuário pelo e-mail carregando a tabela e filtrando em memória. 
    df = carregar_usuarios()
    if df is None or df.empty:
        return None
    linha = df.loc[df["email"].str.lower() == (email or "").strip().lower()]
    if linha.empty:
        return None
    r = linha.iloc[0]
    return {
        "idUsuario": int(r["idUsuario"]),
        "nome": r["nome"],
        "email": r["email"],
        "perfil": r["perfil"],
        "ativo": bool(r["ativo"]),
        "senha_hash": r.get("senha_hash"),
    }

def obter_usuario_por_id(id_usuario: int):
    # Busca usuário pelo id
    df = carregar_usuarios()
    if df is None or df.empty:
        return None
    linha = df.loc[df["idUsuario"].astype(int) == int(id_usuario)]
    if linha.empty:
        return None
    r = linha.iloc[0]
    return {
        "idUsuario": int(r["idUsuario"]),
        "nome": r["nome"],
        "email": r["email"],
        "perfil": r["perfil"],
        "ativo": bool(r["ativo"]),
        "senha_hash": r.get("senha_hash"),
    }

def verificar_senha(senha_plana: str, senha_hash_salvo: str) -> bool:
    if not senha_plana or not senha_hash_salvo:
        return False
    try:
        return bcrypt.checkpw(senha_plana.encode("utf-8"), senha_hash_salvo.encode("utf-8"))
    except Exception:
        return False

def autenticar(email: str, senha: str) -> tuple[bool, str | None]:
    usuario = obter_usuario_por_email(email)
    if not usuario:
        return False, "Usuário não encontrado."
    if not usuario.get("ativo", False):
        return False, "Usuário inativo."
    if not verificar_senha(senha, usuario.get("senha_hash")):
        return False, "Senha inválida."

    st.session_state["usuario_autenticado"] = {
        "idUsuario": usuario["idUsuario"],
        "nome": usuario["nome"],
        "email": usuario["email"],
        "perfil": usuario["perfil"],
        "ativo": bool(usuario["ativo"]),
        "momento_login": datetime.now().isoformat(timespec="seconds"),
    }

    atualizar_usuario(usuario["idUsuario"], ultimo_login=datetime.now().isoformat(timespec="seconds"))

    return True, None

def esta_autenticado() -> bool:
    u = st.session_state.get("usuario_autenticado")
    return bool(u and u.get("ativo", False))

def usuario_atual():
    return st.session_state.get("usuario_autenticado")

def exigir_login(perfis_permitidos: list[str] | None = None):
    if not esta_autenticado():
        st.error("É necessário estar autenticado para acessar esta página.")
        st.page_link("Home.py", label="**Clique aqui para fazer login**")
        st.stop()
    if perfis_permitidos:
        perfil = (usuario_atual() or {}).get("perfil")
        if perfil not in perfis_permitidos:
            st.error("Acesso negado para o seu perfil.")
            st.stop()