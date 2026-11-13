
import os
import sqlite3
import tempfile
from unittest.mock import patch

import banco
import cadastro
import favoritos
import permissoes
import veiculos


def executar_testes():
    with tempfile.TemporaryDirectory() as pasta:
        caminho = os.path.join(pasta, "teste_favoritos.db")

        origem = banco.conectar()
        destino = sqlite3.connect(caminho)

        try:
            origem.backup(destino)
        finally:
            origem.close()
            destino.close()

        def conectar_teste():
            conexao = sqlite3.connect(caminho)
            conexao.execute("PRAGMA foreign_keys = ON")
            return conexao

        with (
            patch.object(cadastro, "conectar", conectar_teste),
            patch.object(favoritos, "conectar", conectar_teste),
            patch.object(veiculos, "conectar", conectar_teste),
            patch.object(permissoes, "conectar", conectar_teste)
        ):
            senha = "SenhaTeste@123"

            sucesso, mensagem = cadastro.cadastrar_usuario(
                "Anunciante Teste",
                "anunciante.fav@exemplo.com",
                senha,
                "anunciante"
            )
            assert sucesso, mensagem

            sucesso, mensagem = cadastro.cadastrar_usuario(
                "Usuario Teste",
                "usuario.fav@exemplo.com",
                senha,
                "usuario"
            )
            assert sucesso, mensagem

            conexao = conectar_teste()

            try:
                anunciante = conexao.execute("""
                    SELECT id_usuario FROM usuarios
                    WHERE email = ?
                """, ("anunciante.fav@exemplo.com",)).fetchone()[0]

                usuario = conexao.execute("""
                    SELECT id_usuario FROM usuarios
                    WHERE email = ?
                """, ("usuario.fav@exemplo.com",)).fetchone()[0]
            finally:
                conexao.close()

            dados = {
                "marca": "Honda",
                "modelo": "Civic Teste Favoritos",
                "ano": 2020,
                "preco": 85000,
                "quilometragem": 45000,
                "combustivel": "Flex",
                "cambio": "Automatico",
                "carroceria": "Sedan",
                "cor": "Preto",
                "motor": "2.0",
                "espaco_interno": "Amplo",
                "estilo_design": "Moderno",
                "descricao": "Teste de favoritos",
                "recursos": []
            }

            id_veiculo = veiculos.cadastrar_veiculo(
                anunciante, dados
            )

            sucesso, _ = favoritos.adicionar_favorito(
                usuario, id_veiculo
            )
            assert sucesso
            print("[OK] Favorito adicionado")

            sucesso, _ = favoritos.adicionar_favorito(
                usuario, id_veiculo
            )
            assert not sucesso
            print("[OK] Favorito duplicado bloqueado")

            lista = favoritos.listar_favoritos(usuario)

            assert any(
                item[0] == id_veiculo for item in lista
            )
            print("[OK] Listagem de favoritos")

            sucesso, _ = favoritos.remover_favorito(
                usuario, id_veiculo
            )
            assert sucesso
            print("[OK] Favorito removido")

            lista = favoritos.listar_favoritos(usuario)

            assert not any(
                item[0] == id_veiculo for item in lista
            )
            print("[OK] Remocao confirmada")

            sucesso, _ = favoritos.remover_favorito(
                usuario, id_veiculo
            )
            assert not sucesso
            print("[OK] Remocao duplicada bloqueada")

            try:
                favoritos.adicionar_favorito(
                    anunciante, id_veiculo
                )
            except PermissionError:
                print("[OK] Anunciante sem permissao bloqueado")
            else:
                raise AssertionError(
                    "FALHA: anunciante gerenciou favoritos"
                )

            veiculos.excluir_veiculo(
                anunciante, id_veiculo
            )

            try:
                favoritos.adicionar_favorito(
                    usuario, id_veiculo
                )
            except ValueError:
                print("[OK] Veiculo inativo bloqueado")
            else:
                raise AssertionError(
                    "FALHA: veiculo inativo foi favoritado"
                )

            conexao = conectar_teste()

            try:
                violacoes = conexao.execute(
                    "PRAGMA foreign_key_check"
                ).fetchall()

                assert not violacoes
                print("[OK] Integridade SQLite preservada")
            finally:
                conexao.close()

    print("[OK] Banco original preservado")
    print("=== TESTES DE FAVORITOS CONCLUIDOS ===")


if __name__ == "__main__":
    executar_testes()
