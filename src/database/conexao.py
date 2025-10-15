# conexao.py
import os
import urllib.parse
import pyodbc
from sqlalchemy import create_engine
import pymssql
import streamlit as st

_SQL_SECRETS = {}
try:
    _SQL_SECRETS = st.secrets["sql"] if "sql" in st.secrets else dict(st.secrets)
except Exception:
    try:
        from dotenv import load_dotenv
        load_dotenv()
    except Exception:
        pass

def _get(name, default=None):
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

# detecta se há driver ODBC do SQL Server no sistema
_ODBC_DRIVERS = set(pyodbc.drivers())
_USE_PYODBC = DRIVER in _ODBC_DRIVERS

AUTH = f"UID={USER};PWD={PASSWORD};" if USER and PASSWORD else "Trusted_Connection=yes;"

def _pyodbc_conn_str():
    return (
        f"DRIVER={{{DRIVER.strip()}}};"
        f"SERVER={SERVER};"
        f"DATABASE={DB};"
        f"{AUTH}"
        f"Encrypt={ENCRYPT};TrustServerCertificate={TRUST_CERT};"
    )

class _CursorQmarkWrapper:
    def __init__(self, cur):
        self._cur = cur
    def execute(self, sql, params=None):
        if params is not None:
            sql = sql.replace("?", "%s")
            return self._cur.execute(sql, params)
        return self._cur.execute(sql)
    def executemany(self, sql, seq_of_params):
        if seq_of_params is not None:
            sql = sql.replace("?", "%s")
            return self._cur.executemany(sql, seq_of_params)
        return self._cur.executemany(sql, seq_of_params)
    def __getattr__(self, name):
        return getattr(self._cur, name)

class _ConnQmarkWrapper:
    def __init__(self, conn):
        self._conn = conn
    def cursor(self, *a, **k):
        return _CursorQmarkWrapper(self._conn.cursor(*a, **k))
    def __getattr__(self, name):
        return getattr(self._conn, name)

# Usar para cursor.execute, commit, etc.
def abrir_conexao_sql_server():
    if _USE_PYODBC:
        return pyodbc.connect(_pyodbc_conn_str())
    host, port = (SERVER.split(",", 1) + [None])[:2]
    port = int(port) if port else 1433
    raw = pymssql.connect(server=host, port=port, user=USER, password=PASSWORD, database=DB, charset="utf8")
    return _ConnQmarkWrapper(raw) 

# Usar para pd.read_sql, suporte para pd
def abrir_engine_sql_server():
    if _USE_PYODBC:
        params = urllib.parse.quote_plus(_pyodbc_conn_str())
        return create_engine(f"mssql+pyodbc:///?odbc_connect={params}", fast_executemany=True)
    if SERVER and "," in SERVER:
        host, port = SERVER.split(",", 1)
        server_for_url = f"{host}:{port}"
    else:
        server_for_url = SERVER
    quoted_user = urllib.parse.quote_plus(USER or "")
    quoted_pwd  = urllib.parse.quote_plus(PASSWORD or "")
    url = f"mssql+pymssql://{quoted_user}:{quoted_pwd}@{server_for_url}/{DB}?charset=utf8"
    return create_engine(url)