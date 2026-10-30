from veiculos import cadastrar_veiculo

id_usuario = 2

veiculo = {
    "marca": "Honda",
    "modelo": "Civic",
    "ano": 2022,
    "preco": 120000,
    "quilometragem": 35000,
    "combustivel": "Flex",
    "cambio": "Automático",
    "descricao": "Veículo em ótimo estado de conservação."
}

try:
    id_veiculo = cadastrar_veiculo(id_usuario, veiculo)

    print("Veículo cadastrado com sucesso!")
    print("ID do veículo:", id_veiculo)

except Exception as erro:
    print("Não foi possível cadastrar:", erro)
