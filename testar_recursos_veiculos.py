
import os
import sqlite3
import tempfile
from unittest.mock import patch

import banco
import permissoes
import veiculos


def executar_testes():
    with tempfile.TemporaryDirectory() as pasta:
        caminho = os.path.join(pasta, "teste_recursos.db")

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
            patch.object(veiculos, "conectar", conectar_teste),
            patch.object(permissoes, "conectar", conectar_teste)
        ):
            conexao = conectar_teste()

            try:
                anunciante = conexao.execute("""
                    SELECT u.id_usuario
                    FROM usuarios u
                    JOIN usuario_funcoes uf
                      ON u.id_usuario = uf.id_usuario
                    JOIN funcoes f
                      ON uf.id_funcao = f.id_funcao
                    WHERE u.ativo = 1
                      AND f.nome_funcao = 'Anunciante'
                    LIMIT 1
                """).fetchone()

                recurso = conexao.execute("""
                    SELECT id_recurso
                    FROM recursos_tecnologia
                    ORDER BY id_recurso
                    LIMIT 1
                """).fetchone()

                maior_recurso = conexao.execute("""
                    SELECT COALESCE(MAX(id_recurso), 0)
                    FROM recursos_tecnologia
                """).fetchone()[0]

            finally:
                conexao.close()

            if anunciante is None:
                print("[PENDENTE] Nenhum anunciante ativo.")
                return

            if recurso is None:
                print("[PENDENTE] Nenhum recurso cadastrado.")
                return

            id_usuario = anunciante[0]
            id_recurso = recurso[0]
            recurso_inexistente = maior_recurso + 1000

            dados = {
                "marca": "Honda",
                "modelo": "Civic Teste Recursos",
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
                "descricao": "Teste de integridade",
                "recursos": [id_recurso]
            }

            id_veiculo = veiculos.cadastrar_veiculo(
                id_usuario, dados
            )

            conexao = conectar_teste()

            try:
                quantidade = conexao.execute("""
                    SELECT COUNT(*)
                    FROM veiculo_recursos
                    WHERE id_veiculo = ?
                      AND id_recurso = ?
                """, (id_veiculo, id_recurso)).fetchone()[0]

                assert quantidade == 1
                print("[OK] Cadastro com recurso valido")

                quantidade_antes = conexao.execute("""
                    SELECT COUNT(*)
                    FROM veiculos
                """).fetchone()[0]

            finally:
                conexao.close()

            dados_duplicados = dados.copy()
            dados_duplicados["recursos"] = [
                id_recurso, id_recurso
            ]

            try:
                veiculos.cadastrar_veiculo(
                    id_usuario, dados_duplicados
                )
            except ValueError:
                print("[OK] Recursos duplicados bloqueados")
            else:
                raise AssertionError(
                    "FALHA: recursos duplicados aceitos"
                )

            dados_invalidos = dados.copy()
            dados_invalidos["recursos"] = [
                recurso_inexistente
            ]

            try:
                veiculos.cadastrar_veiculo(
                    id_usuario, dados_invalidos
                )
            except sqlite3.IntegrityError:
                print("[OK] Recurso inexistente bloqueado")
            else:
                raise AssertionError(
                    "FALHA: recurso inexistente aceito"
                )

            conexao = conectar_teste()

            try:
                quantidade_depois = conexao.execute("""
                    SELECT COUNT(*)
                    FROM veiculos
                """).fetchone()[0]

                assert quantidade_antes == quantidade_depois
                print("[OK] Rollback preservou o banco")

            finally:
                conexao.close()

            dados_editados = dados.copy()
            dados_editados["recursos"] = []

            veiculos.editar_veiculo(
                id_usuario,
                id_veiculo,
                dados_editados
            )

            conexao = conectar_teste()

            try:
                restantes = conexao.execute("""
                    SELECT COUNT(*)
                    FROM veiculo_recursos
                    WHERE id_veiculo = ?
                """, (id_veiculo,)).fetchone()[0]

                assert restantes == 0

                print("[OK] Edicao de recursos funcionando")

                violacoes = conexao.execute(
                    "PRAGMA foreign_key_check"
                ).fetchall()

                assert not violacoes

                print("[OK] Integridade das FK validada")

            finally:
                conexao.close()

    print("[OK] Banco original preservado")


if __name__ == "__main__":
    executar_testes()
