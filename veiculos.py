
import sqlite3
import math
from pathlib import Path

from permissoes import exigir_permissao, consultar_perfil


def conectar():
    caminho_banco = Path(__file__).resolve().parent / "linkcar.db"
    if not caminho_banco.is_file():
        raise FileNotFoundError("Banco linkcar.db nao encontrado na pasta LinkCar.")
    conexao = sqlite3.connect(caminho_banco)
    conexao.execute("PRAGMA foreign_keys = ON")
    return conexao


def verificar_usuario_ativo(id_usuario):
    conexao = conectar()

    try:
        cursor = conexao.cursor()

        cursor.execute("""
            SELECT ativo
            FROM usuarios
            WHERE id_usuario = ?
        """, (id_usuario,))

        resultado = cursor.fetchone()

        if resultado is None or resultado[0] != 1:
            raise PermissionError(
                "Usuario inexistente ou desativado."
            )

    finally:
        conexao.close()


def validar_dados(dados):
    campos_obrigatorios = [
        "marca",
        "modelo",
        "ano",
        "preco",
        "quilometragem",
        "combustivel",
        "cambio",
        "carroceria",
        "cor",
        "motor",
        "espaco_interno",
        "estilo_design",
    ]

    for campo in campos_obrigatorios:
        if dados.get(campo) is None or str(dados[campo]).strip() == "":
            raise ValueError(
                f"O campo {campo} é obrigatório."
            )

    try:
        ano = int(dados["ano"])
        preco = float(dados["preco"])
        quilometragem = int(dados["quilometragem"])

    except (ValueError, TypeError):
        raise ValueError(
            "Ano, preço e quilometragem devem ser numéricos."
        )

    if ano < 1900 or ano > 2100:
        raise ValueError("Ano do veículo inválido.")

    if not math.isfinite(preco) or preco <= 0:
        raise ValueError("O preço deve ser maior que zero.")

    if quilometragem < 0:
        raise ValueError("A quilometragem não pode ser negativa.")

    return True

def verificar_propriedade(id_usuario, id_veiculo):
    conexao = conectar()

    try:
        cursor = conexao.cursor()

        cursor.execute("""
            SELECT id_anunciante
            FROM veiculos
            WHERE id_veiculo = ?
              AND ativo = 1
        """, (id_veiculo,))

        resultado = cursor.fetchone()

        if resultado is None:
            raise ValueError("Veículo não encontrado.")

        perfil = consultar_perfil(id_usuario)

        if perfil != "Administrador":
            if resultado[0] != id_usuario:
                raise PermissionError(
                    "Você não pode alterar este veículo."
                )

        return True

    finally:
        conexao.close()
        
def cadastrar_veiculo(id_usuario, dados):
    verificar_usuario_ativo(id_usuario)

    exigir_permissao(id_usuario, "cadastrar_veiculos")

    validar_dados(dados)

    recursos = dados.get("recursos", [])

    if not isinstance(recursos, list):
        raise ValueError("Lista de recursos inválida.")

    if any(type(r) is not int or r <= 0 for r in recursos):
        raise ValueError("IDs dos recursos inválidos.")

    if len(recursos) != len(set(recursos)):
        raise ValueError("Existem recursos repetidos.")

    conexao = conectar()

    try:
        cursor = conexao.cursor()

        cursor.execute("""
            INSERT INTO veiculos (
                id_anunciante,
                marca,
                modelo,
                ano,
                preco,
                quilometragem,
                combustivel,
                cambio,
                descricao,
                carroceria,
                cor,
                motor,
                espaco_interno,
                estilo_design
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            id_usuario,
            dados["marca"],
            dados["modelo"],
            int(dados["ano"]),
            float(dados["preco"]),
            int(dados["quilometragem"]),
            dados["combustivel"],
            dados["cambio"],
            dados.get("descricao", ""),
            dados["carroceria"],
            dados["cor"],
            dados["motor"],
            dados["espaco_interno"],
            dados["estilo_design"]
        ))

        id_veiculo = cursor.lastrowid

        for id_recurso in recursos:
            cursor.execute("""
                INSERT INTO veiculo_recursos (
                    id_veiculo,
                    id_recurso
                )
                VALUES (?, ?)
            """, (id_veiculo, id_recurso))

        conexao.commit()

        return id_veiculo

    except Exception:
        conexao.rollback()
        raise

    finally:
        conexao.close()


def listar_meus_veiculos(id_usuario):
    verificar_usuario_ativo(id_usuario)
    exigir_permissao(id_usuario, "consultar_veiculos")

    conexao = conectar()

    try:
        cursor = conexao.cursor()

        cursor.execute("""
            SELECT
                id_veiculo,
                marca,
                modelo,
                ano,
                preco,
                quilometragem
            FROM veiculos
            WHERE id_anunciante = ?
            AND ativo = 1
            ORDER BY id_veiculo DESC
        """, (id_usuario,))

        return cursor.fetchall()
    finally:
        conexao.close()
    

def excluir_veiculo(id_usuario, id_veiculo):
    """Desativa um anuncio sem apagar o registro."""
    verificar_usuario_ativo(id_usuario)
    exigir_permissao(id_usuario, "excluir_veiculos")
    verificar_propriedade(id_usuario, id_veiculo)
    perfil = consultar_perfil(id_usuario)
    conexao = conectar()
    try:
        cursor = conexao.cursor()
        cursor.execute("""
            UPDATE veiculos
            SET ativo = 0
            WHERE id_veiculo = ?
              AND ativo = 1
              AND (
                  id_anunciante = ?
                  OR ? = 'Administrador'
              )
        """, (id_veiculo, id_usuario, perfil))
        if cursor.rowcount != 1:
            raise ValueError(
                "Anuncio inexistente ou acesso negado."
            )
        conexao.commit()
        return True
    except Exception:
        conexao.rollback()
        raise
    finally:
        conexao.close()
