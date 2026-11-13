
import os
import sqlite3
import tempfile
from unittest.mock import patch

import banco
import permissoes
import veiculos


def testar_cadastro():
    with tempfile.TemporaryDirectory() as pasta:
        caminho = os.path.join(pasta, "teste_linkcar.db")

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

        with patch.object(
            veiculos, "conectar", conectar_teste
        ), patch.object(
            permissoes, "conectar", conectar_teste
        ):
            conexao = conectar_teste()

            try:
                anunciante = conexao.execute("""
                    SELECT u.id_usuario
                    FROM usuarios u
                    JOIN usuario_funcoes uf
                      ON uf.id_usuario = u.id_usuario
                    JOIN funcoes f
                      ON f.id_funcao = uf.id_funcao
                    WHERE u.ativo = 1
                      AND f.nome_funcao = 'Anunciante'
                    LIMIT 1
                """).fetchone()
            finally:
                conexao.close()

            if anunciante is None:
                print("Nenhum anunciante ativo encontrado.")
                return

            id_usuario = anunciante[0]

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
                id_usuario, dados
            )

            conexao = conectar_teste()

            try:
                resultado = conexao.execute("""
                    SELECT marca, modelo, ativo
                    FROM veiculos
                    WHERE id_veiculo = ?
                """, (id_veiculo,)).fetchone()
            finally:
                conexao.close()

            assert resultado == (
                "Honda", "Civic Teste", 1
            ), "Falha ao verificar o cadastro."

            print("[OK] Permissao de cadastro")
            print("[OK] Veiculo cadastrado")
            print("[OK] Dados gravados no SQLite")
            print("[OK] Veiculo ativo")

    print("[OK] Banco original preservado")


if __name__ == "__main__":
    testar_cadastro()
