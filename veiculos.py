
import sqlite3
from permissoes import exigir_permissao, consultar_perfil


def conectar():
    conexao = sqlite3.connect("linkcar.db")
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
        "cambio"
    ]

    for campo in campos_obrigatorios:
        if not dados.get(campo):
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

    if preco <= 0:
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
                descricao
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            id_usuario,
            dados["marca"],
            dados["modelo"],
            int(dados["ano"]),
            float(dados["preco"]),
            int(dados["quilometragem"]),
            dados["combustivel"],
            dados["cambio"],
            dados.get("descricao", "")
        ))

        conexao.commit()

        return cursor.lastrowid

    except Exception:
        conexao.rollback()
        raise

    finally:
        conexao.close()
