
import sqlite3
from banco import conectar


PESOS = {
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


def buscar_veiculos_disponiveis():
    conexao = conectar()
    conexao.row_factory = sqlite3.Row

    try:
        veiculos = conexao.execute("""
            SELECT v.*
            FROM veiculos v
            JOIN usuarios u ON u.id_usuario = v.id_anunciante
            WHERE v.ativo = 1 AND u.ativo = 1
        """).fetchall()

        resultados = []

        for linha in veiculos:
            veiculo = dict(linha)

            recursos = conexao.execute("""
                SELECT r.nome_recurso
                FROM recursos_tecnologia r
                JOIN veiculo_recursos vr
                    ON vr.id_recurso = r.id_recurso
                WHERE vr.id_veiculo = ?
            """, (veiculo["id_veiculo"],)).fetchall()

            veiculo["recursos"] = [r[0] for r in recursos]
            resultados.append(veiculo)

        return resultados

    finally:
        conexao.close()


def normalizar(valor):
    return str(valor or "").strip().casefold()


def calcular_compatibilidade(veiculo, preferencias):
    pontos = 0
    total = 0

    for criterio, peso in PESOS.items():
        if criterio in ("preco", "recursos"):
            continue

        desejado = preferencias.get(criterio)

        if not normalizar(desejado):
            continue

        total += peso

        if normalizar(veiculo.get(criterio)) == normalizar(desejado):
            pontos += peso

    preco_maximo = preferencias.get("preco")

    if preco_maximo is not None and preco_maximo != "":
        if float(veiculo["preco"]) > float(preco_maximo):
            return None

        total += PESOS["preco"]
        pontos += PESOS["preco"]

    desejados = {
        normalizar(r)
        for r in preferencias.get("recursos", [])
        if normalizar(r)
    }

    if desejados:
        disponiveis = {
            normalizar(r)
            for r in veiculo.get("recursos", [])
        }

        total += PESOS["recursos"]
        pontos += PESOS["recursos"] * (
            len(desejados & disponiveis) / len(desejados)
        )

    if total == 0:
        return 0

    return round(pontos / total * 100)


def gerar_ranking(preferencias):
    resultados = []

    for veiculo in buscar_veiculos_disponiveis():
        porcentagem = calcular_compatibilidade(
            veiculo, preferencias
        )

        if porcentagem is None:
            continue

        resultados.append({
            "id_veiculo": veiculo["id_veiculo"],
            "marca": veiculo["marca"],
            "modelo": veiculo["modelo"],
            "preco": veiculo["preco"],
            "porcentagem": porcentagem
        })

    return sorted(
        resultados,
        key=lambda v: (-v["porcentagem"], v["preco"])
    )


if __name__ == "__main__":
    preferencias = {
        "preco": 100000,
        "carroceria": "Sedã",
        "combustivel": "Flex",
        "cor": "Preto",
        "marca": "Honda",
        "recursos": [
            "Bluetooth",
            "Câmera de ré",
            "Central multimídia"
        ]
    }

    resultados = gerar_ranking(preferencias)

    print("===== LINKCAR MATCH =====")
    print("Veículos encontrados:", len(resultados))

    for veiculo in resultados:
        print(
            f'{veiculo["marca"]} {veiculo["modelo"]} | '
            f'R$ {veiculo["preco"]:.2f} | '
            f'{veiculo["porcentagem"]}% match'
        )

    if not resultados:
        print("Nenhum veículo encontrado dentro do orçamento.")
