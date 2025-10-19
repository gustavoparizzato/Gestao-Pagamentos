import bcrypt
from src.database.conexao import abrir_conexao_sql_server

def gerar_hash_senha(senha_plana: str) -> str:
    sal = bcrypt.gensalt(rounds=12)
    return bcrypt.hashpw(senha_plana.encode("utf-8"), sal).decode("utf-8")

def cadastrar_cheque(identificadorCheque: int, nomeCliente: str, valor: float, banco: str, dataVencimento: str, optPagamento: bool, dataPagamento: str, criado_por: str):
    conn = abrir_conexao_sql_server()
    cursor = conn.cursor()
    try:
        cursor.execute("INSERT INTO Cheques_Pagar (identificadorCheque, nomeCliente, valor, banco, dataVencimento, optPagamento, dataPagamento, criado_por) VALUES (?, ?, ?, ?, ?, ?, ?, ?)", (identificadorCheque, nomeCliente.strip(), valor, banco.strip(), dataVencimento, optPagamento, dataPagamento, criado_por))
        conn.commit()
        return True
    except Exception as e:
        raise
    finally:
        conn.close()

def atualizar_cheque(idCheque: int, *, identificadorCheque: int = None, nomeCliente: str = None, valor: float = None, banco: str = None, dataVencimento: str = None, optPagamento: bool = None, dataPagamento: str = None) -> bool:
    sets = []
    valores = []
    if identificadorCheque is not None:
        sets.append("identificadorCheque = ?"); valores.append(identificadorCheque)
    if nomeCliente is not None:
        sets.append("nomeCliente = ?"); valores.append(nomeCliente.strip())
    if valor is not None:
        sets.append("valor = ?"); valores.append(valor)
    if banco is not None:
        sets.append("banco = ?"); valores.append(banco.strip())
    if dataVencimento is not None:
        sets.append("dataVencimento = ?"); valores.append(dataVencimento)
    if optPagamento is not None:
        sets.append("optPagamento = ?"); valores.append(optPagamento)
    if dataPagamento is not None:
        sets.append("dataPagamento = ?"); valores.append(dataPagamento)
    
    if not sets:
        return False

    sql = f"UPDATE Cheques_Pagar SET {', '.join(sets)} WHERE idCheque = ?"
    valores.append(idCheque)
    conn = abrir_conexao_sql_server()
    cursor = conn.cursor()
    
    try:
        cursor.execute(sql, valores)
        conn.commit()
        return True
    except Exception as e:
        raise
    finally:
        cursor.close()
        conn.close()

# Insere novo usuário na tabela
def cadastrar_usuario(nome: str, email: str, perfil: str, ativo: bool, senha: str):
    conn = abrir_conexao_sql_server()
    cursor = conn.cursor()
    try:
        senha_hash = gerar_hash_senha(senha)
        cursor.execute("INSERT INTO Usuarios (nome, email, perfil, ativo, senha_hash) VALUES (?, ?, ?, ?, ?)", (nome.strip(), email.strip(), perfil, 1 if ativo else 0, senha_hash))
        conn.commit()
        return True
    except Exception as e:
        raise
    finally:
        conn.close()

# Atualizar dados de um usuário
def atualizar_usuario(user_id: int, *, nome: str = None, email: str = None, perfil: str = None, ativo: bool = None, senha_hash: str = None, ultimo_login: str = None) -> bool:
    sets = []
    valores = []
    if nome is not None:
        sets.append("nome = ?"); valores.append(nome.strip())
    if email is not None:
        sets.append("email = ?"); valores.append(email.strip().lower())
    if perfil is not None:
        sets.append("perfil = ?"); valores.append(perfil)
    if ativo is not None:
        sets.append("ativo = ?"); valores.append(1 if ativo else 0)
    if senha_hash is not None:
        sets.append("senha_hash = ?"); valores.append(senha_hash)
    if ultimo_login is not None:
        sets.append("ultimo_login = ?"); valores.append(ultimo_login)
    
    if not sets:
        return False

    sql = f"UPDATE Usuarios SET {', '.join(sets)} WHERE idUsuario = ?"
    valores.append(user_id)
    conn = abrir_conexao_sql_server()
    cursor = conn.cursor()
    
    try:
        cursor.execute(sql, valores)
        conn.commit()
        return True
    except Exception as e:
        raise
    finally:
        cursor.close()
        conn.close()