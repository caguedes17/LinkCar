
import os
import sqlite3
import tempfile
import uuid
from unittest.mock import patch

import banco
import cadastro
import permissoes
import veiculos


def executar_testes():
    with tempfile.TemporaryDirectory() as pasta:
        caminho = os.path.join(pasta, "teste_seguranca.db")

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
            patch.object(veiculos, "conectar", conectar_teste),
            patch.object(permissoes, "conectar", conectar_teste)
        ):
            identificador = uuid.uuid4().hex[:12]

            contas = [
                ("Anunciante Teste 1", "anunciante"),
                ("Anunciante Teste 2", "anunciante"),
                ("Usuario Teste", "usuario")
            ]

            ids = []

            for indice, (nome, perfil) in enumerate(contas):
                email = f"teste{indice}_{identificador}@example.com"

                sucesso, mensagem = cadastro.cadastrar_usuario(
                    nome,
                    email,
                    "SenhaTeste@123",
                    perfil
                )

                assert sucesso, mensagem

                conexao = conectar_teste()
                try:
                    resultado = conexao.execute("""
                        SELECT id_usuario
                        FROM usuarios
                        WHERE email = ?
                    """, (email,)).fetchone()

                    assert resultado is not None
                    ids.append(resultado[0])
                finally:
                    conexao.close()

            dono, outro, usuario_comum = ids

            dados = {
                "marca": "Honda",
                "modelo": "Civic Teste RBAC",
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
                "descricao": "Teste de seguranca",
                "recursos": []
            }

            id_veiculo = veiculos.cadastrar_veiculo(
                dono, dados
            )

            print("[OK] Anunciante cadastrou veiculo")

            dados_editados = dados.copy()
            dados_editados["preco"] = 79000

            veiculos.editar_veiculo(
                dono, id_veiculo, dados_editados
            )

            print("[OK] Proprietario editou veiculo")

            try:
                veiculos.editar_veiculo(
                    outro, id_veiculo, dados_editados
                )
            except PermissionError:
                print("[OK] Edicao por terceiro bloqueada")
            else:
                raise AssertionError(
                    "FALHA: outro anunciante conseguiu editar"
                )

            try:
                veiculos.excluir_veiculo(
                    outro, id_veiculo
                )
            except PermissionError:
                print("[OK] Exclusao por terceiro bloqueada")
            else:
                raise AssertionError(
                    "FALHA: outro anunciante conseguiu excluir"
                )

            try:
                veiculos.cadastrar_veiculo(
                    usuario_comum, dados
                )
            except PermissionError:
                print("[OK] Cadastro por usuario comum bloqueado")
            else:
                raise AssertionError(
                    "FALHA: usuario comum conseguiu cadastrar"
                )

            conexao = conectar_teste()
            try:
                resultado = conexao.execute("""
                    SELECT preco, ativo, id_anunciante
                    FROM veiculos
                    WHERE id_veiculo = ?
                """, (id_veiculo,)).fetchone()

                assert resultado == (79000, 1, dono)

                print("[OK] Tentativas negadas nao alteraram o anuncio")
            finally:
                conexao.close()

            veiculos.excluir_veiculo(dono, id_veiculo)

            conexao = conectar_teste()
            try:
                resultado = conexao.execute("""
                    SELECT ativo
                    FROM veiculos
                    WHERE id_veiculo = ?
                """, (id_veiculo,)).fetchone()

                assert resultado == (0,)

                print("[OK] Exclusao logica pelo proprietario")

                violacoes = conexao.execute(
                    "PRAGMA foreign_key_check"
                ).fetchall()

                assert not violacoes

                print("[OK] Integridade SQLite preservada")
            finally:
                conexao.close()

    print("[OK] Banco original preservado")
    print("=== TESTES DE SEGURANCA CONCLUIDOS ===")


if __name__ == "__main__":
    executar_testes()
