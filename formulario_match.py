
from match import gerar_ranking
from banco import conectar


def escolher(pergunta, opcoes):
    print(f"\n{pergunta}")
    print("0 - Qualquer")

    for numero, opcao in enumerate(opcoes, 1):
        print(f"{numero} - {opcao}")

    while True:
        resposta = input("Escolha: ").strip()

        if resposta in ("", "0"):
            return None

        if resposta.isdigit():
            numero = int(resposta)

            if 1 <= numero <= len(opcoes):
                return opcoes[numero - 1]

        print("Opção inválida. Tente novamente.")


def escolher_preco():
    while True:
        resposta = input("\nPreço máximo (R$): ").strip()

        if not resposta:
            return None

        try:
            preco = float(resposta.replace(",", "."))

            if 0 < preco < float("inf"):
                return preco
        except ValueError:
            pass

        print("Digite um preço válido. Exemplo: 100000")


def escolher_recursos():
    conexao = conectar()

    try:
        recursos = conexao.execute("""
            SELECT nome_recurso
            FROM recursos_tecnologia
            ORDER BY nome_recurso
        """).fetchall()
    finally:
        conexao.close()

    nomes = [linha[0] for linha in recursos]

    if not nomes:
        return []

    print("\nRECURSOS TECNOLÓGICOS")
    print("0 - Nenhuma preferência")

    for numero, nome in enumerate(nomes, 1):
        print(f"{numero} - {nome}")

    while True:
        resposta = input(
            "\nDigite os números separados por vírgula: "
        ).strip()

        if resposta in ("", "0"):
            return []

        partes = [item.strip() for item in resposta.split(",")]

        if all(item.isdigit() for item in partes):
            numeros = [int(item) for item in partes]

            if all(1 <= n <= len(nomes) for n in numeros):
                return [nomes[n - 1] for n in dict.fromkeys(numeros)]

        print("Seleção inválida. Tente novamente.")


def main():
    print("===== LINKCAR =====")
    print("ENCONTRE SEU CARRO IDEAL")

    preferencias = {
        "preco": escolher_preco(),
        "carroceria": escolher(
            "Carroceria:",
            ["Hatch", "Sedã", "SUV", "Picape", "Perua",
             "Minivan", "Cupê", "Conversível", "Utilitário"]
        ),
        "combustivel": escolher(
            "Combustível:",
            ["Flex", "Gasolina", "Etanol", "Diesel",
             "Híbrido", "Elétrico"]
        ),
        "motor": escolher(
            "Motor:",
            ["1.0", "1.3", "1.4", "1.5", "1.6",
             "1.8", "2.0", "Elétrico"]
        ),
        "cor": escolher(
            "Cor:",
            ["Branco", "Preto", "Prata", "Cinza",
             "Vermelho", "Azul", "Verde", "Amarelo",
             "Marrom", "Bege", "Outra"]
        ),
        "marca": escolher(
            "Marca:",
            ["Fiat", "Honda", "Toyota", "Volkswagen",
             "Chevrolet", "Hyundai", "Renault",
             "Nissan", "Jeep", "Ford", "BYD"]
        ),
        "espaco_interno": escolher(
            "Espaço interno:",
            ["Compacto", "Médio", "Amplo"]
        ),
        "estilo_design": escolher(
            "Estilo e design:",
            ["Moderno", "Esportivo", "Clássico",
             "Robusto", "Luxuoso"]
        ),
        "recursos": escolher_recursos()
    }

    resultados = gerar_ranking(preferencias)

    print("\n===== SEUS MATCHES =====")

    if not resultados:
        print("Nenhum veículo encontrado com os filtros escolhidos.")
        return

    for posicao, veiculo in enumerate(resultados, 1):
        preco = f'{veiculo["preco"]:,.2f}'
        preco = preco.replace(",", "X").replace(".", ",").replace("X", ".")

        print(
            f'{posicao}º - {veiculo["marca"]} {veiculo["modelo"]} | '
            f'R$ {preco} | '
            f'{veiculo["porcentagem"]}% match'
        )


if __name__ == "__main__":
    main()
