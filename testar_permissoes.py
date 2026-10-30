from permissoes import (
    consultar_perfil,
    consultar_permissoes,
    verificar_permissao
)

id_usuario = int(input("Digite o ID do usuario: "))

perfil = consultar_perfil(id_usuario)
permissoes = consultar_permissoes(id_usuario)

print("\\n========== TESTE RBAC ==========")
print("Perfil:", perfil)

print("\\nPermissoes do usuario:")
for permissao in permissoes:
    print("-", permissao)

print("\\nTeste de permissao:")
acao = input("Digite uma permissao para testar: ")

if verificar_permissao(id_usuario, acao):
    print("Acesso permitido!")
else:
    print("Acesso negado!")
