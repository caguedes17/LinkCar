
import os
import sqlite3
import tempfile
from unittest.mock import patch

import banco
import cadastro
import login


def testar_usuario_inativo():
    with tempfile.TemporaryDirectory() as pasta:
        caminho_teste = os.path.join(
            pasta, "linkcar_teste.db"
        )

        origem = banco.conectar()

        try:
            destino = sqlite3.connect(caminho_teste)
            try:
                origem.backup(destino)
            finally:
                destino.close()
        finally:
            origem.close()

        def conectar_teste():
            conexao = sqlite3.connect(caminho_teste)
            conexao.execute("PRAGMA foreign_keys = ON")
            return conexao

        with (
            patch.object(cadastro, "conectar", conectar_teste),
            patch.object(login, "conectar", conectar_teste)
        ):
            email = "teste.inativo@exemplo.com"
            senha = "SenhaTeste@123"

            sucesso, mensagem = cadastro.cadastrar_usuario(
                "Usuario Teste Inativo",
                email,
                senha,
                "usuario"
            )

            assert sucesso, mensagem

            autorizado, _ = login.autenticar_usuario(
                email, senha
            )

            assert autorizado, (
                "Falha: usuário ativo não conseguiu entrar."
            )

            conexao = conectar_teste()

            try:
                conexao.execute("""
                    UPDATE usuarios
                    SET ativo = 0
                    WHERE email = ?
                """, (email,))
                conexao.commit()
            finally:
                conexao.close()

            autorizado, mensagem = login.autenticar_usuario(
                email, senha
            )

            assert not autorizado, (
                "FALHA DE SEGURANÇA: conta desativada "
                "conseguiu fazer login."
            )

            print("Cadastro de teste: OK")
            print("Login com conta ativa: OK")
            print("Bloqueio de conta desativada: OK")
            print("Mensagem:", mensagem)

    print("Banco original preservado.")


if __name__ == "__main__":
    testar_usuario_inativo()
