"""
services/user_service.py

Camada de "serviço" (regras de negócio), que fica entre a interface
(main.py) e o banco de dados (database/). Isso mantém a interface
gráfica simples e facilita testes e futuras trocas de tecnologia.
"""

import re

from database.connection import get_session
from database.models import User
from authentication.auth import hash_password


REGEX_EMAIL = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")


class EmailInvalidoError(Exception):
    pass


class EmailJaCadastradoError(Exception):
    pass


class DadosInvalidosError(Exception):
    pass


def email_ja_existe(email: str) -> bool:
    """Verifica se já existe um usuário cadastrado com esse e-mail."""
    session = get_session()
    try:
        return session.query(User).filter(User.email == email.lower().strip()).first() is not None
    finally:
        session.close()


def cadastrar_usuario(full_name: str, email: str, senha: str, face_encoding: list) -> User:
    """
    Cadastra um novo usuário no banco de dados.

    Faz as seguintes validações antes de salvar:
      - Nome, e-mail e senha não podem estar vazios.
      - E-mail deve ter um formato válido.
      - E-mail não pode já estar cadastrado (evita duplicidade).
      - face_encoding deve ter sido capturado com sucesso.

    Levanta exceções específicas em caso de erro, para que a interface
    gráfica possa exibir mensagens claras ao usuário.
    """
    full_name = (full_name or "").strip()
    email = (email or "").strip().lower()

    if not full_name or not email or not senha:
        raise DadosInvalidosError("Nome, e-mail e senha são obrigatórios.")

    if not REGEX_EMAIL.match(email):
        raise EmailInvalidoError("O e-mail informado não é válido.")

    if face_encoding is None:
        raise DadosInvalidosError(
            "É necessário realizar o cadastro facial antes de finalizar."
        )

    session = get_session()
    try:
        if session.query(User).filter(User.email == email).first():
            raise EmailJaCadastradoError("Este e-mail já está cadastrado.")

        senha_hash = hash_password(senha)

        novo_usuario = User(
            full_name=full_name,
            email=email,
            password_hash=senha_hash,
        )
        novo_usuario.set_face_encoding(face_encoding)

        session.add(novo_usuario)
        session.commit()
        session.refresh(novo_usuario)
        return novo_usuario
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()


def listar_usuarios():
    """Retorna todos os usuários cadastrados (útil para telas de listagem)."""
    session = get_session()
    try:
        return session.query(User).all()
    finally:
        session.close()


def contar_usuarios() -> int:
    """Retorna a quantidade de usuários cadastrados."""
    session = get_session()
    try:
        return session.query(User).count()
    finally:
        session.close()
