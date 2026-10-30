import sqlite3

def conectar():
    conexao = sqlite3.connect("linkcar.db")
    conexao.execute("PRAGMA foreign_keys = ON")
    return conexao

def consultar_perfil(id_usuario):
    conexao = conectar()
    try:
        cursor = conexao.cursor()
        cursor.execute("""
            SELECT funcoes.nome_funcao
            FROM usuario_funcoes
            INNER JOIN funcoes
                ON usuario_funcoes.id_funcao = funcoes.id_funcao
            WHERE usuario_funcoes.id_usuario = ?
        """, (id_usuario,))
        resultado = cursor.fetchone()
        if resultado is None:
            return None
        return resultado[0]
    finally:
        conexao.close()


def consultar_permissoes(id_usuario):
    conexao = conectar()
    try:
        cursor = conexao.cursor()
        cursor.execute("""
            SELECT DISTINCT permissoes.nome_permissao
            FROM usuario_funcoes
            INNER JOIN funcao_permissoes
                ON usuario_funcoes.id_funcao = funcao_permissoes.id_funcao
            INNER JOIN permissoes
                ON funcao_permissoes.id_permissao = permissoes.id_permissao
            WHERE usuario_funcoes.id_usuario = ?
        """, (id_usuario,))
        resultados = cursor.fetchall()
        return [linha[0] for linha in resultados]
    finally:
        conexao.close()

def verificar_permissao(id_usuario, permissao):
    permissoes_usuario = consultar_permissoes(id_usuario)
    return permissao in permissoes_usuario

def exigir_permissao(id_usuario, permissao):
    if not verificar_permissao(id_usuario, permissao):
        raise PermissionError(
             "Acesso negado: voce nao possui permissao para esta operacao."
        )
    return True
