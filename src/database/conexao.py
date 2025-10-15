import os
import pyodbc
from sqlalchemy import create_engine
import urllib.parse
from dotenv import load_dotenv
import streamlit as st

try:
    import streamlit as st
    _S = st.secrets
    _SQL = _S["sql"] if "sql" in _S else _S
except Exception:
    _SQL = {}

# pega valor de secrets (preferência) ou env var como fallback
def _get(name, default=None):
    return (
        _SQL.get(name) or
        _SQL.get(f"SQL_{name}") or
        os.getenv(f"SQL_{name}", default)
    )

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