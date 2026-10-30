
from veiculos import (
    conectar,
    editar_veiculo,
    listar_meus_veiculos,
    buscar_veiculo_para_edicao
)

def perguntar(campo, valor_atual):
    if valor_atual is None:
        valor_atual = ""

    resposta = input(
        f"{campo} [{valor_atual}]: "
    ).strip()

    if resposta == "":
        return valor_atual

    return resposta



def escolher_opcao(campo, valor_atual, opcoes):
    print(f"\n{campo}")
    print(f"Atual: {valor_atual or 'Nao informado'}")

    for numero, opcao in enumerate(opcoes, 1):
        print(f"{numero} - {opcao}")

    while True:
        resposta = input(
            "Escolha um numero ou Enter para manter: "
        ).strip()

        if resposta == "":
            return valor_atual or ""

        if resposta.isdigit():
            numero = int(resposta)

            if 1 <= numero <= len(opcoes):
                return opcoes[numero - 1]

        print("Opcao invalida. Tente novamente.")



def editar_recursos(recursos_atuais):
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

    print("\n===== RECURSOS TECNOLOGICOS =====")

    for id_recurso, nome in recursos:
        marcado = "*" if id_recurso in recursos_atuais else " "
        print(f"[{marcado}] {id_recurso} - {nome}")

    print("\n* = Recurso ja cadastrado no veiculo")
    print("Enter = manter os recursos atuais")
    print("0 = remover todos os recursos")
    print("IDs separados por virgula = nova selecao")

    ids_validos = {
        linha[0] for linha in recursos
    }

    while True:
        resposta = input("\nRecursos: ").strip()

        if resposta == "":
            return recursos_atuais

        if resposta == "0":
            return []

        partes = [
            item.strip()
            for item in resposta.split(",")
        ]

        if all(item.isdigit() for item in partes):
            selecionados = [
                int(item) for item in partes
            ]

            sem_repetidos = (
                len(selecionados) == len(set(selecionados))
            )

            todos_validos = all(
                recurso in ids_validos
                for recurso in selecionados
            )

            if sem_repetidos and todos_validos:
                return selecionados

        print("Selecao invalida. Tente novamente.")



def main():

    id_usuario = 2

    print("===== LINKCAR =====")
    print("EDITAR MEUS VEICULOS\n")

    veiculos = listar_meus_veiculos(id_usuario)

    if not veiculos:
        print("Voce nao possui veiculos cadastrados.")
        return

    print("===== MEUS ANUNCIOS =====")

    for carro in veiculos:
        print("----------------------------")
        print("ID:", carro[0])
        print("Veiculo:", carro[1], carro[2])
        print("Ano:", carro[3])
        print("Preco: R$", carro[4])

    print("----------------------------")

    id_veiculo = int(
        input("\nDigite o ID do veiculo para editar: ")
    )

    dados = buscar_veiculo_para_edicao(
        id_usuario,
        id_veiculo
    )

    print("\n===== EDITAR INFORMACOES =====")
    print("Pressione Enter para manter o valor atual.\n")


    campos = [
        "marca",
        "modelo",
        "ano",
        "preco",
        "quilometragem",
        "motor",
        "descricao"
    ]

    for campo in campos:
        dados[campo] = perguntar(
            campo.replace("_", " ").title(),
            dados.get(campo)
        )


    opcoes = {
        "carroceria": [
            "Hatch",
            "Sedã",
            "SUV",
            "Picape",
            "Perua",
            "Minivan",
            "Cupê",
            "Conversível",
            "Utilitário"
        ],

        "cor": [
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
        ],

        "combustivel": [
            "Flex",
            "Gasolina",
            "Etanol",
            "Diesel",
            "Híbrido",
            "Elétrico"
        ],

        "cambio": [
            "Manual",
            "Automático",
            "CVT",
            "Automatizado"
        ],

        "espaco_interno": [
            "Compacto",
            "Médio",
            "Amplo"
        ],

        "estilo_design": [
            "Moderno",
            "Esportivo",
            "Clássico",
            "Robusto",
            "Luxuoso"
        ]
    }

    for campo, alternativas in opcoes.items():
        dados[campo] = escolher_opcao(
            campo.replace("_", " ").title(),
            dados.get(campo),
            alternativas
        )

    dados["recursos"] = editar_recursos(
        dados["recursos"]
    )


    print("\n===== CONFIRMAR ALTERACOES =====")

    confirmar = input(
        "Deseja salvar as alteracoes? (S/N): "
    ).strip().lower()

    if confirmar != "s":
        print("\nEdicao cancelada.")
        return

    editar_veiculo(
        id_usuario,
        id_veiculo,
        dados
    )

    print("\n================================")
    print("VEICULO ATUALIZADO COM SUCESSO!")
    print("================================")



if __name__ == "__main__":
    try:
        main()

    except (ValueError, PermissionError) as erro:
        print("\nErro:", erro)

    except Exception as erro:
        print("\nErro inesperado:", erro)
