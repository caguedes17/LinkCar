
import os
import sqlite3
import tempfile
from unittest.mock import patch

import banco
import match


def executar_testes():
    with tempfile.TemporaryDirectory() as pasta:
        caminho = os.path.join(
            pasta, "teste_filtros_match.db"
        )

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
            match, "conectar", conectar_teste
        ):
            conexao = conectar_teste()

            try:
                registro = conexao.execute("""
                    SELECT
                        v.id_veiculo,
                        v.id_anunciante
                    FROM veiculos v
                    JOIN usuarios u
                      ON u.id_usuario = v.id_anunciante
                    WHERE v.ativo = 1
                      AND u.ativo = 1
                    ORDER BY v.id_veiculo
                    LIMIT 1
                """).fetchone()

                if registro is None:
                    print(
                        "[PENDENTE] Nenhum veiculo "
                        "de anunciante ativo encontrado."
                    )
                    return

                id_veiculo, id_anunciante = registro

                disponiveis = (
                    match.buscar_veiculos_disponiveis()
                )

                assert any(
                    v["id_veiculo"] == id_veiculo
                    for v in disponiveis
                )

                print("[OK] Veiculo ativo encontrado")

                conexao.execute("""
                    UPDATE veiculos
                    SET ativo = 0
                    WHERE id_veiculo = ?
                """, (id_veiculo,))
                conexao.commit()

                disponiveis = (
                    match.buscar_veiculos_disponiveis()
                )

                assert all(
                    v["id_veiculo"] != id_veiculo
                    for v in disponiveis
                )

                print(
                    "[OK] Veiculo inativo "
                    "excluido do Match"
                )

                conexao.execute("""
                    UPDATE veiculos
                    SET ativo = 1
                    WHERE id_veiculo = ?
                """, (id_veiculo,))

                conexao.execute("""
                    UPDATE usuarios
                    SET ativo = 0
                    WHERE id_usuario = ?
                """, (id_anunciante,))
                conexao.commit()

                disponiveis = (
                    match.buscar_veiculos_disponiveis()
                )

                assert all(
                    v["id_veiculo"] != id_veiculo
                    for v in disponiveis
                )

                print(
                    "[OK] Anunciante inativo "
                    "bloqueado no Match"
                )

                ranking = match.gerar_ranking({})

                assert all(
                    v["id_veiculo"] != id_veiculo
                    for v in ranking
                )

                print(
                    "[OK] Ranking respeita "
                    "os filtros de seguranca"
                )

                violacoes = conexao.execute(
                    "PRAGMA foreign_key_check"
                ).fetchall()

                assert not violacoes

                print(
                    "[OK] Integridade SQLite preservada"
                )

            finally:
                conexao.close()

    print("[OK] Banco original preservado")
    print("=== TESTES DOS FILTROS CONCLUIDOS ===")


if __name__ == "__main__":
    executar_testes()
