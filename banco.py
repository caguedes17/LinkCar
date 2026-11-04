import sqlite3
from pathlib import Path

CAMINHO_BANCO = Path(__file__).resolve().parent / "linkcar.db"


def conectar():
    if not CAMINHO_BANCO.is_file():
        raise FileNotFoundError(
            "Banco linkcar.db não encontrado."
        )

    conexao = sqlite3.connect(CAMINHO_BANCO)
    conexao.execute("PRAGMA foreign_keys = ON")

    return conexao