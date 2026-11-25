
from unittest.mock import patch

import match


def executar_testes():
    veiculo = {
        "id_veiculo": 1,
        "marca": "Honda",
        "modelo": "Civic",
        "ano": 2020,
        "preco": 85000,
        "carroceria": "Sedã",
        "combustivel": "Flex",
        "motor": "2.0",
        "cor": "Preto",
        "espaco_interno": "Amplo",
        "estilo_design": "Moderno",
        "recursos": ["Bluetooth", "Câmera de ré"]
    }

    preferencias = {
        "preco": 100000,
        "carroceria": "Sedã",
        "combustivel": "Flex",
        "motor": "2.0",
        "cor": "Preto",
        "marca": "Honda",
        "espaco_interno": "Amplo",
        "estilo_design": "Moderno",
        "recursos": ["Bluetooth", "Câmera de ré"]
    }

    assert sum(match.PESOS.values()) == 100
    print("[OK] Pesos totalizam 100")

    resultado = match.calcular_compatibilidade(
        veiculo, preferencias
    )

    assert resultado == 100
    print("[OK] Compatibilidade de 100%")

    acima_orcamento = preferencias.copy()
    acima_orcamento["preco"] = 50000

    resultado = match.calcular_compatibilidade(
        veiculo, acima_orcamento
    )

    assert resultado is None
    print("[OK] Orcamento respeitado")

    sem_preferencia = {
        "marca": "Qualquer",
        "cor": "Preto"
    }

    resultado = match.calcular_compatibilidade(
        veiculo, sem_preferencia
    )

    assert resultado == 100
    print("[OK] Opcao Qualquer ignorada")

    recursos_parciais = {
        "recursos": ["Bluetooth", "GPS"]
    }

    resultado = match.calcular_compatibilidade(
        veiculo, recursos_parciais
    )

    assert resultado == 50
    print("[OK] Compatibilidade parcial de recursos")

    outro = veiculo.copy()
    outro["id_veiculo"] = 2
    outro["marca"] = "Toyota"
    outro["modelo"] = "Corolla"
    outro["preco"] = 90000
    outro["cor"] = "Branco"

    with patch.object(
        match,
        "buscar_veiculos_disponiveis",
        return_value=[outro, veiculo]
    ):
        ranking = match.gerar_ranking(preferencias)

    assert len(ranking) == 2
    assert ranking[0]["id_veiculo"] == 1
    assert ranking[0]["porcentagem"] == 100
    assert ranking[1]["porcentagem"] < 100

    print("[OK] Ranking ordenado corretamente")

    explicacao = match.explicar_compatibilidade(
        outro, preferencias
    )

    assert explicacao["atendidos"]
    assert explicacao["nao_atendidos"]

    print("[OK] Explicacao do match funcionando")

    try:
        match.calcular_compatibilidade(
            veiculo, {"preco": -100}
        )
    except ValueError:
        print("[OK] Preco negativo bloqueado")
    else:
        raise AssertionError(
            "FALHA: preco negativo aceito"
        )

    print("\n=== TESTES DO MATCH CONCLUIDOS ===")


if __name__ == "__main__":
    executar_testes()
