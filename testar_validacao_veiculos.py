
from veiculos import validar_dados

dados = {
    "marca": "Honda",
    "modelo": "Civic",
    "ano": 2020,
    "preco": 85000,
    "quilometragem": 45000,
    "combustivel": "Flex",
    "cambio": "Automatico",
    "carroceria": "Sedan",
    "cor": "Preto",
    "motor": "2.0",
    "espaco_interno": "Amplo",
    "estilo_design": "Moderno"
}

print("=== TESTES DE VALIDACAO LINKCAR ===")

testes = [
    ("Dados validos", {}, True),
    ("Preco negativo", {"preco": -100}, False),
    ("Ano invalido", {"ano": 1800}, False),
    ("Quilometragem negativa", {"quilometragem": -10}, False),
    ("Marca vazia", {"marca": ""}, False)
]

for nome, alteracoes, esperado in testes:
    dados_teste = dados.copy()
    dados_teste.update(alteracoes)

    try:
        validar_dados(dados_teste)
        resultado = True
    except ValueError:
        resultado = False

    if resultado == esperado:
        print(f"[OK] {nome}")
    else:
        print(f"[FALHOU] {nome}")
