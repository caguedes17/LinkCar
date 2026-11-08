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
         if resposta.isdigit() and 1 <= int(resposta) <= len(opcoes):
             return opcoes[int(resposta) - 1]
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
        print("Informe um valor positivo, exemplo: 100000")

def escolher_recursos():
    conexao = conectar()
    try:
        linhas = conexao.execute("""
            SELECT nome_recurso FROM recursos_tecnologia
            ORDER BY nome_recurso
        """).fetchall()
    finally:
        conexao.close()

    nomes = [linha[0] for linha in linhas]
    print("\nRECURSOS TECNOLÓGICOS")
    print("0 - Nenhuma preferência")
    for numero, nome in enumerate(nomes, 1):
        print(f"{numero} - {nome}")

    while True:
        resposta = input("IDs separados por vírgula: ").strip()
        if resposta in ("", "0"):
            return []
        partes = [p.strip() for p in resposta.split(",")]
        if all(p.isdigit() for p in partes):
            ids = [int(p) for p in partes]
            if len(ids) == len(set(ids)) and all(
                1 <= n <= len(nomes) for n in ids
            ):
                return [nomes[n - 1] for n in ids]
        print("Seleção inválida. Tente novamente.")

def main():
    print("===== LINKCAR | ENCONTRE SEU CARRO IDEAL =====")
    preferencias = {
        "preco": escolher_preco(),
        "carroceria": escolher("Carroceria:", [
             "Hatch", "Sedã", "SUV", "Picape", "Perua",
             "Minivan", "Cupê", "Conversível", "Utilitário"
        ]),
        "combustivel": escolher("Combustível:", [
            "Flex", "Gasolina", "Etanol", "Diesel", "Híbrido", "Elétrico"
        ]),
        "motor": escolher("Motor:", [
            "1.0", "1.3", "1.4", "1.5", "1.6", "1.8", "2.0", "Elétrico"
        ]),
        "cor": escolher("Cor:", [
            "Branco", "Preto", "Prata", "Cinza", "Vermelho",
            "Azul", "Verde", "Amarelo", "Marrom", "Bege", "Outra"
        ]),
        "marca": escolher("Marca:", [
             "Fiat", "Honda", "Toyota", "Volkswagen", "Chevrolet",
             "Hyundai", "Renault", "Nissan", "Jeep", "Ford", "BYD"
        ]),
        "espaco_interno": escolher("Espaço interno:", [
            "Compacto", "Médio", "Amplo"
         ]),
         "estilo_design": escolher("Estilo e design:", [
             "Moderno", "Esportivo", "Clássico", "Robusto", "Luxuoso"
         ]),
         "recursos": escolher_recursos()
    }

    resultados = gerar_ranking(preferencias)
    print("\n===== SEUS MATCHES =====")
    if not resultados:
        print("Nenhum veículo corresponde ao orçamento/filtros.")
        return
    for posicao, carro in enumerate(resultados, 1):
        print(
             f'{posicao}º - {carro["marca"]} {carro["modelo"]} | '
             f'R$ {carro["preco"]:.2f} | {carro["porcentagem"]}% match'
        )

if __name__ == "__main__":
    try:
        main()
    except Exception as erro:
            print("Erro:", erro)

    