
from banco import conectar
from permissoes import exigir_permissao


def adicionar_favorito(id_usuario, id_veiculo):
    exigir_permissao(id_usuario, "gerenciar_favoritos")

    conexao = conectar()

    try:
        usuario = conexao.execute("""
            SELECT 1 FROM usuarios
            WHERE id_usuario = ? AND ativo = 1
        """, (id_usuario,)).fetchone()

        if usuario is None:
            raise ValueError("Usuário inexistente ou desativado.")

        veiculo = conexao.execute("""
            SELECT 1 FROM veiculos
            WHERE id_veiculo = ? AND ativo = 1
        """, (id_veiculo,)).fetchone()

        if veiculo is None:
            raise ValueError("Veículo inexistente ou inativo.")

        existente = conexao.execute("""
            SELECT 1 FROM favoritos
            WHERE id_usuario = ? AND id_veiculo = ?
        """, (id_usuario, id_veiculo)).fetchone()

        if existente:
            return False, "Este veículo já está nos seus favoritos."

        conexao.execute("""
            INSERT INTO favoritos (id_usuario, id_veiculo)
            VALUES (?, ?)
        """, (id_usuario, id_veiculo))

        conexao.commit()
        return True, "Veículo adicionado aos favoritos!"

    except Exception:
        conexao.rollback()
        raise

    finally:
        conexao.close()

def listar_favoritos(id_usuario):
    exigir_permissao(id_usuario, "gerenciar_favoritos")

    conexao = conectar()

    try:
        cursor = conexao.execute("""
            SELECT
                v.id_veiculo,
                v.marca,
                v.modelo,
                v.preco,
                f.data_favorito
            FROM favoritos f
            JOIN veiculos v
                ON f.id_veiculo = v.id_veiculo
            JOIN usuarios u
                ON f.id_usuario = u.id_usuario
            WHERE f.id_usuario = ?
              AND u.ativo = 1
              AND v.ativo = 1
            ORDER BY f.data_favorito DESC
        """, (id_usuario,))

        return cursor.fetchall()

    finally:
        conexao.close()

def remover_favorito(id_usuario, id_veiculo):
    exigir_permissao(id_usuario, "gerenciar_favoritos")

    conexao = conectar()

    try:
        cursor = conexao.execute("""
            DELETE FROM favoritos
            WHERE id_usuario = ?
              AND id_veiculo = ?
        """, (id_usuario, id_veiculo))

        if cursor.rowcount == 0:
            return False, "Veículo não encontrado nos favoritos."

        conexao.commit()
        return True, "Veículo removido dos favoritos!"

    except Exception:
        conexao.rollback()
        raise

    finally:
        conexao.close()
