"""
authentication/auth.py

Responsável por todo o tratamento seguro de senhas.

Usamos bcrypt, que:
  - Gera um "salt" aleatório automaticamente para cada senha, então duas
    senhas iguais produzem hashes diferentes.
  - É propositalmente lento, dificultando ataques de força bruta.
  - É o padrão de mercado recomendado para hash de senhas.

IMPORTANTE: a senha em texto puro NUNCA é armazenada ou logada em
nenhum lugar do sistema.
"""

import bcrypt


def hash_password(plain_password: str) -> str:
    """
    Gera o hash bcrypt de uma senha em texto puro.

    Args:
        plain_password: a senha digitada pelo usuário.

    Returns:
        str: hash da senha, pronto para ser salvo no banco de dados.
    """
    if not plain_password or len(plain_password) < 6:
        raise ValueError("A senha deve ter pelo menos 6 caracteres.")

    senha_bytes = plain_password.encode("utf-8")
    salt = bcrypt.gensalt()
    hashed = bcrypt.hashpw(senha_bytes, salt)
    return hashed.decode("utf-8")


def verify_password(plain_password: str, password_hash: str) -> bool:
    """
    Verifica se a senha em texto puro corresponde ao hash armazenado.

    Args:
        plain_password: senha digitada no momento do login/verificação.
        password_hash: hash salvo no banco de dados.

    Returns:
        bool: True se a senha for válida, False caso contrário.
    """
    try:
        return bcrypt.checkpw(
            plain_password.encode("utf-8"),
            password_hash.encode("utf-8"),
        )
    except (ValueError, TypeError):
        # Hash inválido/corrompido — trata como senha incorreta.
        return False
