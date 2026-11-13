
import os
import sqlite3
import tempfile
from unittest.mock import patch

import banco
import permissoes
import veiculos


def conectar_teste(caminho):
    conexao = sqlite3.connect(caminho)
    conexao.execute("PRAGMA foreign_keys = ON")
    return conexao


def testar_crud():
    with tempfile.TemporaryDirectory() as pasta:
        caminho = os.path.join(pasta, "teste_linkcar.db")

        origem = banco.conectar()
        destino = conectar_teste(caminho)

        try:
            origem.backup(destino)
        finally:
            origem.close()
            destino.close()

        def conexao_temporaria():
            return conectar_teste(caminho)

        with (
            patch.object(veiculos, "conectar", conexao_temporaria),
            patch.object(permissoes, "conectar", conexao_temporaria)
        ):
            conexao = conexao_temporaria()

            try:
                anunciantes = conexao.execute("""
                    SELECT DISTINCT u.id_usuario
                    FROM usuarios u
                    JOIN usuario_funcoes uf
                      ON uf.id_usuario = u.id_usuario
                    JOIN funcoes f
                      ON f.id_funcao = uf.id_funcao
                    WHERE u.ativo = 1
                      AND f.nome_funcao = 'Anunciante'
                    ORDER BY u.id_usuario
                    LIMIT 2
                """).fetchall()
            finally:
                conexao.close()

            if not anunciantes:
                print("[ERRO] Nenhum anunciante ativo.")
                return

            dono = anunciantes[0][0]

            dados = {
                "marca": "Honda",
                "modelo": "Civic Teste",
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
                "descricao": "Veiculo de teste",
                "recursos": []
            }

            id_veiculo = veiculos.cadastrar_veiculo(
                dono, dados
            )
            print("[OK] Veiculo criado na copia temporaria")

            dados_editados = dados.copy()
            dados_editados["preco"] = 79000
            dados_editados["cor"] = "Branco"

            veiculos.editar_veiculo(
                dono, id_veiculo, dados_editados
            )

            conexao = conexao_temporaria()

            try:
                resultado = conexao.execute("""
                    SELECT preco, cor
                    FROM veiculos
                    WHERE id_veiculo = ?
                """, (id_veiculo,)).fetchone()

                assert resultado == (79000, "Branco")

                print("[OK] Edicao realizada pelo proprietario")

                if len(anunciantes) >= 2:
                    outro = anunciantes[1][0]

                    try:
                        veiculos.editar_veiculo(
                            outro,
                            id_veiculo,
                            dados_editados
                        )
                    except PermissionError:
                        print(
                            "[OK] Edicao de outro anunciante bloqueada"
                        )
                    else:
                        raise AssertionError(
                            "FALHA: outro anunciante editou o veiculo"
                        )
                else:
                    print(
                        "[PENDENTE] Teste de outro anunciante: "
                        "necessarios 2 anunciantes ativos"
                    )

                veiculos.excluir_veiculo(
                    dono, id_veiculo
                )

                ativo = conexao.execute("""
                    SELECT ativo
                    FROM veiculos
                    WHERE id_veiculo = ?
                """, (id_veiculo,)).fetchone()

                assert ativo == (0,)

                print("[OK] Exclusao logica realizada")

                quantidade = conexao.execute("""
                    SELECT COUNT(*)
                    FROM veiculos
                    WHERE id_veiculo = ?
                """, (id_veiculo,)).fetchone()[0]

                assert quantidade == 1

                print("[OK] Registro preservado no SQLite")

            finally:
                conexao.close()

    print("[OK] Banco original preservado")


if __name__ == "__main__":
    testar_crud()
