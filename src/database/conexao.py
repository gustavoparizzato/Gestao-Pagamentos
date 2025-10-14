import os
import pyodbc
from sqlalchemy import create_engine
import urllib.parse
from dotenv import load_dotenv

load_dotenv()

SERVER     = os.getenv("SQL_SERVER")
DB = os.getenv("SQL_DB")
USER       = os.getenv("SQL_USER")
PASSWORD   = os.getenv("SQL_PASSWORD")
DRIVER     = os.getenv("SQL_DRIVER")
ENCRYPT    = os.getenv("SQL_ENCRYPT", "no")	
TRUST_CERT = os.getenv("SQL_TRUST_CERT", "no")

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