
import sqlite3
from banco import conectar


def buscar_veiculos_disponiveis():
    conexao = conectar()

    try:
        conexao.row_factory = sqlite3.Row
        cursor = conexao.cursor()

        cursor.execute("""
            SELECT *
            FROM veiculos
            WHERE ativo = 1
            ORDER BY id_veiculo DESC
        """)

        return [dict(linha) for linha in cursor.fetchall()]

    finally:
        conexao.close()


def calcular_compatibilidade(veiculo, preferencias):
    pesos = {
        "preco": 25,
        "carroceria": 15,
        "combustivel": 10,
        "motor": 10,
        "cor": 5,
        "marca": 10,
        "recursos": 10,
        "espaco_interno": 10,
        "estilo_design": 5
    }

    pontos = 0
    pontos_possiveis = 0

    for criterio, peso in pesos.items():
        if criterio in ("preco", "recursos"):
            continue

        preferencia = preferencias.get(criterio)

        if preferencia is None or str(preferencia).strip() == "":
            continue

        pontos_possiveis += peso
        valor_veiculo = veiculo.get(criterio)

        if (
            valor_veiculo is not None
            and str(valor_veiculo).strip().casefold()
            == str(preferencia).strip().casefold()
        ):
            pontos += peso

    preco_maximo = preferencias.get("preco")

    if preco_maximo is not None:
        pontos_possiveis += pesos["preco"]

        if float(veiculo["preco"]) <= float(preco_maximo):
            pontos += pesos["preco"]

    if pontos_possiveis == 0:
        return 0

    return round((pontos / pontos_possiveis) * 100)


if __name__ == "__main__":
    veiculos = buscar_veiculos_disponiveis()

    print("===== LINKCAR MATCH =====")
    print("Veículos disponíveis:", len(veiculos))

    preferencias = {
        "preco": 100000,
        "carroceria": "Sedã",
        "combustivel": "Flex",
        "cor": "Preto",
        "marca": "Honda"
    }

    resultados = []

    for veiculo in veiculos:
        porcentagem = calcular_compatibilidade(veiculo, preferencias)

        resultados.append({
            "id_veiculo": veiculo["id_veiculo"],
            "marca": veiculo["marca"],
            "modelo": veiculo["modelo"],
            "porcentagem": porcentagem
        })

    resultados.sort(
        key=lambda resultado: resultado["porcentagem"],
        reverse=True
    )

    print("\n===== RESULTADOS DO MATCH =====")

    for resultado in resultados:
        print(
            f'{resultado["marca"]} {resultado["modelo"]}: '
            f'{resultado["porcentagem"]}% de compatibilidade'
        )
