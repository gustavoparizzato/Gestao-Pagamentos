from src.database.conexao import abrir_engine_sql_server
import pandas as pd
from sqlalchemy import text

# Carrega dados do banco de dados - Importação e Exportação
def carregar_cheques(data_ini, data_fim):
    engine = abrir_engine_sql_server()
    with engine.connect() as conn: ## usar .begin para casos de transação, .connect para apenas consultas simples
        return pd.read_sql(text(f"SELECT * FROM Cheques_Receber WHERE dataVencimento BETWEEN '{data_ini}' AND '{data_fim}'"), conn)

def carregar_cheques_filtros(data_ini, data_fim, identificador=None, nome=None):
    # Usamos limite superior exclusivo (data_fim + 1 dia) para pegar o dia todo
    sql = """
    SELECT idCheque, identificadorCheque, nomeCliente, valor, banco,
           dataVencimento, dataPagamento, criado_por, criado_em, ultima_modificacao
    FROM Cheques_Receber
    WHERE dataVencimento >= :data_ini
      AND dataVencimento < :data_fim_exclusivo
      {and_ident}
      {and_nome}
    """
    and_ident = "AND identificadorCheque = :identificador" if identificador is not None else ""
    and_nome  = "AND nomeCliente LIKE :nome" if nome else ""

    sql = sql.format(and_ident=and_ident, and_nome=and_nome)

    params = {
        "data_ini": pd.to_datetime(data_ini),
        "data_fim_exclusivo": pd.to_datetime(data_fim) + pd.Timedelta(days=1),
    }
    if identificador is not None:
        params["identificador"] = int(identificador)
    if nome:
        params["nome"] = f"%{nome}%"

    engine = abrir_engine_sql_server()
    with engine.connect() as conn:
        return pd.read_sql(text(sql), conn, params=params)

# Carrega todos os usuários
def carregar_usuarios():
    engine = abrir_engine_sql_server()
    with engine.connect() as conn:
        return pd.read_sql(text(f"SELECT * FROM Usuarios"), conn) 

# Carrega um usuário pelo ID
def carregar_usuario_id(user_id: int):
    engine = abrir_engine_sql_server()
    with engine.connect() as conn:
        return conn.execute(text("SELECT * FROM Usuarios WHERE idUsuario=:idUsuario"), {"idUsuario": user_id}).fetchone()
    
# Verifica se o e-mail já existe no banco de dados
def email_existe(email: str) -> bool:
    engine = abrir_engine_sql_server()
    with engine.connect() as conn:
        r = conn.execute(text("SELECT 1 FROM Usuarios WHERE LOWER(email)=LOWER(:e)"), {"e": email.strip()}).fetchone()
        return r is not None