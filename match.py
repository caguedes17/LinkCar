
import math
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


def normalizar(valor):
    if valor is None:
        return ""
    return str(valor).strip().casefold()


def sem_preferencia(valor):
    return normalizar(valor) in ("", "qualquer")


def validar_preferencias(preferencias):
    if not isinstance(preferencias, dict):
        raise ValueError("Preferencias invalidas.")

    preco = preferencias.get("preco")

    if not sem_preferencia(preco):
        try:
            valor = float(preco)
        except (ValueError, TypeError, OverflowError):
            raise ValueError("Preco maximo invalido.")

        if not math.isfinite(valor) or valor <= 0:
            raise ValueError("Preco maximo invalido.")

    recursos = preferencias.get("recursos", [])

    if recursos is not None and not isinstance(recursos, list):
        raise ValueError("Recursos devem ser uma lista.")

    return True


def buscar_veiculos_disponiveis():
    conexao = conectar()
    conexao.row_factory = sqlite3.Row

    try:
        veiculos = conexao.execute("""
            SELECT v.*
            FROM veiculos v
            JOIN usuarios u
                ON u.id_usuario = v.id_anunciante
            WHERE v.ativo = 1
              AND u.ativo = 1
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

            veiculo["recursos"] = [
                recurso[0] for recurso in recursos
            ]

            resultados.append(veiculo)

        return resultados

    finally:
        conexao.close()


def calcular_compatibilidade(veiculo, preferencias):
    validar_preferencias(preferencias)

    pontos = 0
    total = 0

    for criterio, peso in PESOS.items():
        if criterio in ("preco", "recursos"):
            continue

        desejado = preferencias.get(criterio)

        if sem_preferencia(desejado):
            continue

        total += peso

        if normalizar(veiculo.get(criterio)) == normalizar(desejado):
            pontos += peso

    preco_maximo = preferencias.get("preco")

    if not sem_preferencia(preco_maximo):
        preco_veiculo = float(veiculo["preco"])

        if not math.isfinite(preco_veiculo):
            return None

        if preco_veiculo > float(preco_maximo):
            return None

        total += PESOS["preco"]
        pontos += PESOS["preco"]

    desejados = {
        normalizar(recurso)
        for recurso in preferencias.get("recursos", []) or []
        if not sem_preferencia(recurso)
    }

    if desejados:
        disponiveis = {
            normalizar(recurso)
            for recurso in veiculo.get("recursos", []) or []
        }

        total += PESOS["recursos"]

        pontos += PESOS["recursos"] * (
            len(desejados & disponiveis) / len(desejados)
        )

    if total == 0:
        return 0

    return round(pontos / total * 100)


def explicar_compatibilidade(veiculo, preferencias):
    validar_preferencias(preferencias)

    atendidos = []
    nao_atendidos = []

    nomes = {
        "carroceria": "Carroceria",
        "combustivel": "Combustivel",
        "motor": "Motor",
        "cor": "Cor",
        "marca": "Marca",
        "espaco_interno": "Espaco interno",
        "estilo_design": "Estilo e design"
    }

    preco_maximo = preferencias.get("preco")

    if not sem_preferencia(preco_maximo):
        if float(veiculo["preco"]) <= float(preco_maximo):
            atendidos.append("Preco dentro do orcamento")
        else:
            nao_atendidos.append("Preco acima do orcamento")

    for criterio, nome in nomes.items():
        desejado = preferencias.get(criterio)

        if sem_preferencia(desejado):
            continue

        atual = veiculo.get(criterio)

        if normalizar(atual) == normalizar(desejado):
            atendidos.append(f"{nome}: {atual}")
        else:
            nao_atendidos.append(
                f"{nome}: desejado {desejado}, "
                f"veiculo {atual or 'nao informado'}"
            )

    disponiveis = {
        normalizar(recurso)
        for recurso in veiculo.get("recursos", []) or []
    }

    for recurso in preferencias.get("recursos", []) or []:
        if sem_preferencia(recurso):
            continue

        if normalizar(recurso) in disponiveis:
            atendidos.append(f"Possui {recurso}")
        else:
            nao_atendidos.append(f"Nao possui {recurso}")

    return {
        "atendidos": atendidos,
        "nao_atendidos": nao_atendidos
    }


def gerar_ranking(preferencias):
    validar_preferencias(preferencias)

    resultados = []

    for veiculo in buscar_veiculos_disponiveis():
        porcentagem = calcular_compatibilidade(
            veiculo, preferencias
        )

        if porcentagem is None:
            continue

        explicacao = explicar_compatibilidade(
            veiculo, preferencias
        )

        resultados.append({
            "id_veiculo": veiculo["id_veiculo"],
            "marca": veiculo["marca"],
            "modelo": veiculo["modelo"],
            "preco": veiculo["preco"],
            "porcentagem": porcentagem,
            "atendidos": explicacao["atendidos"],
            "nao_atendidos": explicacao["nao_atendidos"]
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
        "motor": "Qualquer",
        "cor": "Preto",
        "marca": "Honda",
        "espaco_interno": "Qualquer",
        "estilo_design": "Qualquer",
        "recursos": [
            "Bluetooth",
            "Câmera de ré",
            "Central multimídia"
        ]
    }

    try:
        resultados = gerar_ranking(preferencias)

        print("\n===== LINKCAR MATCH =====")
        print("Veiculos encontrados:", len(resultados))

        for veiculo in resultados:
            print(
                f'{veiculo["marca"]} {veiculo["modelo"]} | '
                f'R$ {veiculo["preco"]:.2f} | '
                f'{veiculo["porcentagem"]}% match'
            )

        if not resultados:
            print("Nenhum veiculo encontrado.")

    except (ValueError, TypeError, sqlite3.Error) as erro:
        print("Erro ao gerar ranking:", erro)
