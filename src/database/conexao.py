# conexao.py
import os
import urllib.parse
import pyodbc
import streamlit as st
from sqlalchemy import create_engine

_SQL_SECRETS = {}
try:
    # se houver seção [sql], usa ela;
    _SQL_SECRETS = st.secrets["sql"] if "sql" in st.secrets else dict(st.secrets)
except Exception:
    # carrega .env (opcional) e usa os.getenv
    try:
        from dotenv import load_dotenv
        load_dotenv()
    except Exception:
        pass

def _get(name: str, default: str | None = None) -> str | None:
    if _SQL_SECRETS:
        if name in _SQL_SECRETS:
            return _SQL_SECRETS.get(name, default)
        flat = f"SQL_{name}"
        if flat in _SQL_SECRETS:
            return _SQL_SECRETS.get(flat, default)
    return os.getenv(f"SQL_{name}", default)

SERVER     = _get("SERVER")
DB         = _get("DB")
USER       = _get("USER")
PASSWORD   = _get("PASSWORD")
DRIVER     = _get("DRIVER", "ODBC Driver 18 for SQL Server")
ENCRYPT    = _get("ENCRYPT", "no")
TRUST_CERT = _get("TRUST_CERT", "no")

AUTH = f"UID={USER};PWD={PASSWORD};" if USER and PASSWORD else "Trusted_Connection=yes;"

## Usar para cursor.execute, commit, etc.
def abrir_conexao_sql_server():
    return pyodbc.connect(
        f"DRIVER={{{DRIVER.strip()}}};"
        f"SERVER={SERVER};"
        f"DATABASE={DB};"
        f"{AUTH}"
        f"Encrypt={ENCRYPT};TrustServerCertificate={TRUST_CERT};"
    )

## Usar para pd.read_sql, suporte para pd
def abrir_engine_sql_server():
    conn_str = (
        f"DRIVER={{{DRIVER.strip()}}};"
        f"SERVER={SERVER};"
        f"DATABASE={DB};"
        f"{AUTH}"
        f"Encrypt={ENCRYPT};TrustServerCertificate={TRUST_CERT};"
    )
    params = urllib.parse.quote_plus(conn_str)
    return create_engine(f"mssql+pyodbc:///?odbc_connect={params}", fast_executemany=True)