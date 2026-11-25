from veiculos import validar_dados

veiculo = {
    "marca": "Honda",
    "modelo": "Civic",
    "ano": 2022,
    "preco": 120000,
    "quilometragem": 35000,
    "combustivel": "Flex",
    "cambio": "Automático"
}

try:
    resultado = validar_dados(veiculo)
    print("Dados do veículo válidos!")

except ValueError as erro:
    print("Erro:", erro)
