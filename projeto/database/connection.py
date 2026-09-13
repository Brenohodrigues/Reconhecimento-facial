"""
database/connection.py

Responsável por configurar a conexão com o banco de dados.

Este módulo é o ÚNICO lugar que precisa mudar caso você decida migrar
de SQLite para PostgreSQL (ou outro banco) no futuro. Basta alterar a
variável de ambiente DATABASE_URL — nenhum outro arquivo do projeto
precisa ser modificado, pois todo o resto usa o SQLAlchemy ORM de
forma independente do banco físico.

Exemplos de DATABASE_URL:
    SQLite (padrão):
        sqlite:///data/app.db

    PostgreSQL (exemplo futuro):
        postgresql+psycopg2://usuario:senha@localhost:5432/facial_db
"""

import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

# ---------------------------------------------------------------------------
# 1. Definição da URL do banco de dados
# ---------------------------------------------------------------------------
# Por padrão usamos SQLite, salvo em ./data/app.db.
# Para trocar de banco, defina a variável de ambiente DATABASE_URL antes
# de rodar o programa, por exemplo:
#   export DATABASE_URL="postgresql+psycopg2://user:pass@localhost/db"
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///data/app.db")

# Garante que a pasta "data" exista quando usamos SQLite localmente.
if DATABASE_URL.startswith("sqlite"):
    os.makedirs("data", exist_ok=True)

# ---------------------------------------------------------------------------
# 2. Criação do engine (conexão física com o banco)
# ---------------------------------------------------------------------------
# connect_args é necessário apenas para SQLite, para permitir uso do
# mesmo arquivo de banco em threads diferentes (a interface gráfica e o
# processamento da webcam podem rodar em threads distintas).
connect_args = {"check_same_thread": False} if DATABASE_URL.startswith("sqlite") else {}

engine = create_engine(DATABASE_URL, connect_args=connect_args, echo=False)

# ---------------------------------------------------------------------------
# 3. Sessão e Base declarativa
# ---------------------------------------------------------------------------
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()


def get_session():
    """
    Retorna uma nova sessão do banco de dados.
    Deve ser usada com cuidado: sempre feche a sessão (session.close())
    após o uso, ou utilize-a dentro de um bloco try/finally.
    """
    return SessionLocal()


def init_db():
    """
    Cria todas as tabelas definidas em models.py, caso ainda não existam.
    Deve ser chamada uma vez na inicialização da aplicação (ver main.py).
    """
    # Importação local para evitar import circular entre connection.py
    # e models.py.
    from database import models  # noqa: F401
    Base.metadata.create_all(bind=engine)
