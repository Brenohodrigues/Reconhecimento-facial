"""
database/models.py

Define as tabelas do banco de dados usando o ORM do SQLAlchemy.

Como usamos um ORM, este arquivo NÃO precisa mudar quando trocarmos de
SQLite para PostgreSQL (ou outro banco relacional suportado pelo
SQLAlchemy) — a definição das tabelas é independente do banco físico.
"""

import json
from datetime import datetime

from sqlalchemy import Column, Integer, String, Text, DateTime
from database.connection import Base


class User(Base):
    """
    Representa um usuário cadastrado no sistema.

    Campos:
        id             - identificador único (chave primária)
        full_name      - nome completo do usuário
        email          - e-mail (único, usado como identificador de login)
        password_hash  - hash bcrypt da senha (NUNCA a senha em texto puro)
        face_encoding  - vetor de 128 posições (embedding facial) gerado
                         pela biblioteca face_recognition, serializado
                         como JSON (string) para ser salvo em uma coluna
                         de texto.
        created_at     - data/hora do cadastro
    """

    __tablename__ = "users"

    id = Column(Integer, primary_key=True, autoincrement=True)
    full_name = Column(String(150), nullable=False)
    email = Column(String(150), nullable=False, unique=True, index=True)
    password_hash = Column(String(200), nullable=False)
    face_encoding = Column(Text, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    # -- Métodos auxiliares para converter o embedding facial (lista de
    #    floats) de/para o formato de texto armazenado no banco. -------

    def set_face_encoding(self, encoding_list):
        """Recebe uma lista/array de floats e salva como JSON (texto)."""
        self.face_encoding = json.dumps(list(encoding_list))

    def get_face_encoding(self):
        """Retorna o embedding facial como lista de floats."""
        return json.loads(self.face_encoding)

    def __repr__(self):
        return f"<User id={self.id} email={self.email}>"
