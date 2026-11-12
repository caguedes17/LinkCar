import hashlib
import secrets
import sqlite3
from datetime import datetime, timedelta, timezone

from banco import conectar


def solicitar_recuperacao(email):
    email = email.strip().lower()
    mensagem = "Se o e-mail estiver cadastrado, as instruções serão enviadas."

    conexao = conectar()

    try:
        usuario = conexao.execute("""
            SELECT id_usuario
            FROM usuarios
            WHERE email = ? AND ativo = 1
        """, (email,)).fetchone()

        if usuario is None:
            return None, mensagem

        id_usuario = usuario[0]

        token = secrets.token_urlsafe(32)

        token_hash = hashlib.sha256(
            token.encode("utf-8")
        ).hexdigest()

        expiracao = (
            datetime.now(timezone.utc) + timedelta(minutes=10)
        ).strftime("%Y-%m-%d %H:%M:%S")

        conexao.execute("""
            UPDATE tokens_recuperacao
            SET utilizado = 1
            WHERE id_usuario = ? AND utilizado = 0
        """, (id_usuario,))

        conexao.execute("""
            INSERT INTO tokens_recuperacao (
                id_usuario,
                token_hash,
                data_expiracao
            )
            VALUES (?, ?, ?)
        """, (id_usuario, token_hash, expiracao))

        conexao.commit()

        return token, mensagem

    except sqlite3.Error:
        conexao.rollback()
        raise

    finally:
        conexao.close()

def validar_token(token):
    if not isinstance(token, str) or not token:
        return None

    token_hash = hashlib.sha256(
        token.encode("utf-8")
    ).hexdigest()

    conexao = conectar()

    try:
        resultado = conexao.execute("""
            SELECT t.id_usuario, t.data_expiracao
            FROM tokens_recuperacao t
            JOIN usuarios u
                ON u.id_usuario = t.id_usuario
            WHERE t.token_hash = ?
              AND t.utilizado = 0
              AND u.ativo = 1
        """, (token_hash,)).fetchone()

        if resultado is None:
            return None

        id_usuario, expiracao = resultado

        data_expiracao = datetime.strptime(
            expiracao, "%Y-%m-%d %H:%M:%S"
        ).replace(tzinfo=timezone.utc)

        if datetime.now(timezone.utc) >= data_expiracao:
            return None

        return id_usuario

    finally:
        conexao.close()

from cadastro import gerar_hash


def redefinir_senha(token, nova_senha):
    if not isinstance(nova_senha, str) or len(nova_senha) < 8:
        return False, "A senha deve ter pelo menos 8 caracteres."

    if not isinstance(token, str) or not token:
        return False, "Token inválido ou expirado."

    token_hash = hashlib.sha256(
        token.encode("utf-8")
    ).hexdigest()

    conexao = conectar()

    try:
        conexao.execute("BEGIN IMMEDIATE")

        resultado = conexao.execute("""
            SELECT t.id_token, t.id_usuario, t.data_expiracao
            FROM tokens_recuperacao t
            JOIN usuarios u ON u.id_usuario = t.id_usuario
            WHERE t.token_hash = ?
              AND t.utilizado = 0
              AND u.ativo = 1
        """, (token_hash,)).fetchone()

        if resultado is None:
            conexao.rollback()
            return False, "Token inválido ou expirado."

        id_token, id_usuario, expiracao = resultado

        data_expiracao = datetime.strptime(
            expiracao, "%Y-%m-%d %H:%M:%S"
        ).replace(tzinfo=timezone.utc)

        if datetime.now(timezone.utc) >= data_expiracao:
            conexao.rollback()
            return False, "Token inválido ou expirado."

        senha_hash = gerar_hash(nova_senha)

        conexao.execute("""
            UPDATE usuarios
            SET senha_hash = ?
            WHERE id_usuario = ? AND ativo = 1
        """, (senha_hash, id_usuario))

        conexao.execute("""
            UPDATE tokens_recuperacao
            SET utilizado = 1
            WHERE id_usuario = ? AND utilizado = 0
        """, (id_usuario,))

        conexao.commit()

        return True, "Senha redefinida com sucesso!"

    except Exception:
        conexao.rollback()
        raise

    finally:
        conexao.close()

import os
from urllib.parse import urlencode
from email_service import enviar_email

def enviar_recuperacao(email):
    email = email.strip().lower()
    mensagem_padrao = (
        "Se o e-mail estiver cadastrado, "
        "as instruções serão enviadas."
    )
    token, _ = solicitar_recuperacao(email)
    if token is None:
        return mensagem_padrao
    url_base = os.getenv("APP_BASE_URL", "").rstrip("/")
    if not url_base.startswith(("http://", "https://")):
        raise ValueError("Configure APP_BASE_URL no arquivo .env.")
    parametros = urlencode({"token": token})
    link = f"{url_base}/redefinir-senha?{parametros}"
    assunto = "LinkCar - Recuperação de senha"
    mensagem = f"""Olá!
Recebemos uma solicitação de recuperação
 de senha para sua conta LinkCar.
Acesse o link abaixo para criar uma nova senha:
{link}
Este link é válido por 10 minutos e só
pode ser utilizado uma vez.
Se você não solicitou a recuperação,
ignore esta mensagem.
Equipe LinkCar
"""
    enviar_email(email, assunto, mensagem)
    return mensagem_padrao