
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


def calcular_compatibilidade(veiculo, preferencias, detalhar=False):
    pontos = 0
    total = 0
    detalhes = []

    for criterio, peso in PESOS.items():
        if criterio in ("preco", "recursos"):
            continue
        desejado = preferencias.get(criterio)
        if not normalizar(desejado):
            continue

        total += peso
        atual = veiculo.get(criterio)
         if not normalizar(atual):
            status = "não informado"
        elif normalizar(atual) == normalizar(desejado):
            pontos += peso
            status = "atende"
        else:
            status = "não atende"

        detalhes.append({
             "criterio": criterio,
              "desejado": desejado,
              "encontrado": atual,
              "status": status
            })
        
    preco_maximo = preferencias.get("preco")
    if preco_maximo not in (None, ""):
         teto = float(preco_maximo)
         if teto <= 0 or teto == float("inf"):
             raise ValueError("Preço máximo inválido")
         if float(veiculo["preco"]) > teto:
             return None
         total += PESOS["preco"]
         pontos += PESOS["preco"]
         detalhes.append({
             "criterio": "preco",
             "desejado": teto,
             "encontrado": veiculo["preco"],
             "status": "atende"
        })

    desejados = {
        normalizar(r): r for r in preferencias.get("recursos", [])
         if normalizar(r)
    }
     if desejados:
        disponiveis = {
            normalizar(r) for r in veiculo.get("recursos", [])
        }
        atendidos = [r for chave, r in desejados.items()
                     if chave in disponiveis]
        faltantes = [r for chave, r in desejados.items()
                     if chave not in disponiveis]
        total += PESOS["recursos"]
        pontos += PESOS["recursos"] * len(atendidos) / len(desejados)
        detalhes.append({
            "criterio": "recursos",
            "atendidos": atendidos,
            "faltantes": faltantes,
            "status": "atende" if not faltantes else "parcial"
                     if atendidos else "não atende"
        })
    
    porcentagem = round(pontos / total * 100) if total else 0
    if detalhar:
        return {"porcentagem": porcentagem, "detalhes": detalhes}
    return porcentagem
    
