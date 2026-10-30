from veiculos import cadastrar_veiculo, conectar


# Mostra opções numeradas para o anunciante
def escolher_opcao(pergunta, opcoes):
    print(f"\n{pergunta}")

    for numero, opcao in enumerate(opcoes, start=1):
        print(f"{numero} - {opcao}")

    while True:
        resposta = input("Escolha o número: ").strip()

        if resposta.isdigit():
            numero = int(resposta)

            if 1 <= numero <= len(opcoes):
                return opcoes[numero - 1]

        print("Opção inválida. Tente novamente.")


# Busca os recursos tecnológicos cadastrados no banco
def selecionar_recursos():
    conexao = conectar()

    try:
        cursor = conexao.cursor()

        cursor.execute("""
            SELECT id_recurso, nome_recurso
            FROM recursos_tecnologia
            ORDER BY nome_recurso
        """)

        recursos = cursor.fetchall()

    finally:
        conexao.close()

    print("\n===== RECURSOS TECNOLÓGICOS =====")

    for id_recurso, nome in recursos:
        print(f"{id_recurso} - {nome}")

    print("\nDigite os IDs dos recursos do veículo.")
    print("Separe por vírgula. Exemplo: 1, 3, 5")
    print("Pressione Enter se não quiser selecionar nenhum.")

    resposta = input("Recursos: ").strip()

    if not resposta:
        return []

    ids = [item.strip() for item in resposta.split(",")]

    if any(not item.isdigit() for item in ids):
        raise ValueError("Digite apenas IDs separados por vírgula.")

    selecionados = [int(item) for item in ids]

    if len(selecionados) != len(set(selecionados)):
        raise ValueError("Não repita o mesmo recurso.")

    ids_validos = {linha[0] for linha in recursos}

    if any(id_recurso not in ids_validos
           for id_recurso in selecionados):
        raise ValueError("Um dos recursos selecionados não existe.")

    return selecionados


# Cadastro interativo
def main():
    print("===== LINKCAR =====")
    print("CADASTRO DE VEÍCULOS\n")

    # Temporário: anunciante utilizado nos testes
    id_usuario = 2

    dados = {
        "marca": input("Marca: ").strip().title(),
        "modelo": input("Modelo: ").strip().title(),
        "ano": input("Ano: ").strip(),
        "preco": input("Preço (exemplo: 27000): ").strip(),
        "quilometragem": input("Quilometragem: ").strip(),

        "carroceria": escolher_opcao(
            "Tipo de carroceria:",
            [
                "Hatch",
                "Sedã",
                "SUV",
                "Picape",
                "Perua",
                "Minivan",
                "Cupê",
                "Conversível",
                "Utilitário"
            ]
        ),

        "cor": escolher_opcao(
            "Cor do veículo:",
            [
                "Branco",
                "Preto",
                "Prata",
                "Cinza",
                "Vermelho",
                "Azul",
                "Verde",
                "Amarelo",
                "Marrom",
                "Bege",
                "Outra"
            ]
        ),

        "motor": input(
            "\nMotor (exemplo: 1.0, 1.6, 2.0 ou Elétrico): "
        ).strip(),

        "combustivel": escolher_opcao(
            "Combustível:",
            [
                "Flex",
                "Gasolina",
                "Etanol",
                "Diesel",
                "Híbrido",
                "Elétrico"
            ]
        ),

        "cambio": escolher_opcao(
            "Tipo de câmbio:",
            [
                "Manual",
                "Automático",
                "CVT",
                "Automatizado"
            ]
        ),

        "espaco_interno": escolher_opcao(
            "Espaço interno:",
            [
                "Compacto",
                "Médio",
                "Amplo"
            ]
        ),

        "estilo_design": escolher_opcao(
            "Estilo e design:",
            [
                "Moderno",
                "Esportivo",
                "Clássico",
                "Robusto",
                "Luxuoso"
            ]
        ),

        "descricao": input(
            "\nDescrição do veículo: "
        ).strip()
    }

    dados["recursos"] = selecionar_recursos()

    id_veiculo = cadastrar_veiculo(id_usuario, dados)

    print("\n================================")
    print("VEÍCULO CADASTRADO COM SUCESSO!")
    print("Código do anúncio:", id_veiculo)
    print("================================")


if __name__ == "__main__":
    try:
        main()

    except Exception as erro:
        print("\nErro ao cadastrar veículo:", erro)
