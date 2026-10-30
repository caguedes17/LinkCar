from veiculos import cadastrar_veiculo

print("===== LINKCAR =====")
print("CADASTRO DE VEÍCULOS\n")

id_usuario = 2

dados = {
    "marca": input("Marca: ").strip(),
    "modelo": input("Modelo: ").strip(),
    "ano": input("Ano: ").strip(),
    "preco": input("Preço (R$): ").strip(),
    "quilometragem": input("Quilometragem: ").strip(),
    "combustivel": input("Combustível: ").strip(),
    "cambio": input("Câmbio: ").strip(),
    "descricao": input("Descrição: ").strip()
}

try:
    id_veiculo = cadastrar_veiculo(id_usuario, dados)

    print("\nVeículo cadastrado com sucesso!")
    print("Código do anúncio:", id_veiculo)

except Exception as erro:
    print("\nErro ao cadastrar:", erro)
