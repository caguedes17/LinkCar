
import sqlite3
import hashlib
import secrets
import getpass


def verificar_senha(senha_digitada, senha_armazenada):
    try:
        salt_hex, hash_original = senha_armazenada.split(":")
        
        salt = bytes.fromhex(salt_hex)

        novo_hash = hashlib.scrypt(
            senha_digitada.encode("utf-8"),
            salt=salt,
            n=2**14,
            r=8,
            p=1
        )

        return secrets.compare_digest(
            novo_hash.hex(),
            hash_original
        )

    except (ValueError, TypeError):
        return False


def autenticar_usuario(email, senha):
    email = email.strip().lower()

    conexao = sqlite3.connect("linkcar.db")
    conexao.execute("PRAGMA foreign_keys = ON")

    try:
        cursor = conexao.cursor()

        cursor.execute("""
            SELECT 
                usuarios.id_usuario,
                usuarios.nome,
                usuarios.senha_hash,
                usuarios.ativo,
                funcoes.nome_funcao
            FROM usuarios
            INNER JOIN usuario_funcoes
                ON usuarios.id_usuario = usuario_funcoes.id_usuario
            INNER JOIN funcoes
                ON usuario_funcoes.id_funcao = funcoes.id_funcao
            WHERE usuarios.email = ?
        """, (email,))

        resultado = cursor.fetchone()

        if resultado is None:
            return False, "E-mail ou senha incorretos."

        id_usuario, nome, senha_hash, ativo, perfil = resultado

        if not verificar_senha(senha, senha_hash):
            return False, "E-mail ou senha incorretos."

        if ativo != 1:
            return False, "Esta conta está desativada."

        return True, {
            "id_usuario": id_usuario,
            "nome": nome,
            "perfil": perfil
        }

    finally:
        conexao.close()


if __name__ == "__main__":

    print("\n========== LINKCAR ==========")
    print("          LOGIN")
    print("=============================")

    email = input("Digite seu e-mail: ").strip()
    senha = getpass.getpass("Digite sua senha: ")

    sucesso, resultado = autenticar_usuario(email, senha)

    if sucesso:
        print("\nLogin realizado com sucesso!")
        print("Bem-vindo,", resultado["nome"])
        print("Perfil:", resultado["perfil"])
    else:
        print("\n" + resultado)
