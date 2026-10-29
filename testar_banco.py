import sqlite3


conexao = sqlite3.connect("linkcar.db")


conexao.execute("PRAGMA foreign_keys = ON")


cursor = conexao.cursor()

cursor.execute("""
    SELECT name
    FROM sqlite_master
    WHERE type = 'table'
    AND name NOT LIKE 'sqlite_%'
    ORDER BY name
""")

tabelas = cursor.fetchall()

print("Conexão realizada com sucesso!")
print("\nTabelas encontradas:")

for tabela in tabelas:
    print("-", tabela[0])

conexao.close()
