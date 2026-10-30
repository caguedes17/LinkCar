
import sqlite3
import hashlib
import secrets
import getpass


def gerar_hash(senha):
    salt = secrets.token_bytes(16)

    hash_senha = hashlib.scrypt(
        senha.encode("utf-8"),
        salt=salt,
        n=2**14,
        r=8,
        p=1
    )

    return salt.hex() + ":" + hash_senha.hex()

def cadastrar_usuario(nome, email, senha, perfil):

    nome = nome.strip()
    email = email.strip().lower()

    if not nome or not email or not senha:
        return False, "Todos os campos são obrigatórios."

    if "@" not in email or "." not in email.split("@")[-1]:
        return False, "E-mail inválido."

    if len(senha) < 8:
        return False, "A senha precisa ter pelo menos 8 caracteres."

    perfis_permitidos = {
        "usuario": "Usuario",
        "anunciante": "Anunciante"
    }

    if perfil not in perfis_permitidos:
        return False, "Perfil inválido."

    funcao = perfis_permitidos[perfil]

    senha_hash = gerar_hash(senha)

    conexao = sqlite3.connect("linkcar.db")
    conexao.execute("PRAGMA foreign_keys = ON")

    try:
        cursor = conexao.cursor()

        cursor.execute("""
            INSERT INTO usuarios (nome, email, senha_hash)
            VALUES (?, ?, ?)
        """, (nome, email, senha_hash))

        id_usuario = cursor.lastrowid

        cursor.execute("""
            INSERT INTO usuario_funcoes (id_usuario, id_funcao)
            SELECT ?, id_funcao
            FROM funcoes
            WHERE nome_funcao = ?
        """, (id_usuario, funcao))

        if cursor.rowcount != 1:
            raise ValueError("Função não encontrada no banco.")

        conexao.commit()

        return True, "Cadastro realizado com sucesso!"

    except sqlite3.IntegrityError:
        conexao.rollback()
        return False, "Este e-mail já está cadastrado."

    except ValueError as erro:
        conexao.rollback()
        return False, str(erro)

    finally:
        conexao.close()

if __name__ == "__main__":

    print("\n========== LINKCAR ==========")
    print("       CADASTRO DE USUÁRIO")
    print("=============================")

    nome = input("Digite e sobrenome: ").strip()
    email = input("Digite seu e-mail: ").strip()

    senha = getpass.getpass("Crie sua senha: ")
    confirmar_senha = getpass.getpass("Confirme sua senha: ")

    if senha != confirmar_senha:
        print("\nErro: as senhas não são iguais.")

    else:
        print("\nEscolha o tipo de perfil:")
        print("1 - Usuário")
        print("2 - Anunciante")

        opcao = input("Opção: ").strip()

        perfis = {
            "1": "usuario",
            "2": "anunciante"
        }

        perfil = perfis.get(opcao)

        if perfil is None:
            print("\nErro: opção inválida.")

        else:
            sucesso, mensagem = cadastrar_usuario(
                nome, email, senha, perfil
            )

            print("\n" + mensagem)
