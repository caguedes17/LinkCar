from veiculos import excluir_veiculo, listar_meus_veiculos
def main():
    print("===== LINKCAR =====")
    print("DESATIVAR MEU ANUNCIO\n")
    # Somente para teste local. Descubra o ID no SQLite.
    id_usuario = int(input("ID do anunciante de teste: "))
    veiculos = listar_meus_veiculos(id_usuario)
    if not veiculos:
        print("Nenhum anuncio ativo encontrado.")
        return
    for carro in veiculos:
        print(
            f"ID: {carro[0]} | {carro[1]} {carro[2]} "
            f"| Ano: {carro[3]} | R$ {carro[4]:.2f}"
        )
    resposta = input("\nID do anuncio a desativar: ")
    if not resposta.strip().isdigit():
        print("ID invalido. Nenhuma alteracao realizada.")
        return
    id_veiculo = int(resposta)
    anuncio = next(
        (v for v in veiculos if v[0] == id_veiculo),
        None
    )
    if anuncio is None:
        print("Esse anuncio nao pertence a sua lista ativa.")
        return
    print(f"\nAnuncio: {anuncio[1]} {anuncio[2]}")
    print("Os dados continuarao no banco de dados.")
    confirmar = input("Digite EXCLUIR para confirmar: ")
    if confirmar.strip() != "EXCLUIR":
        print("Operacao cancelada.")
        return
    excluir_veiculo(id_usuario, id_veiculo)
    print("Anuncio desativado com sucesso!")
if __name__ == "__main__":
    try:
        main()
    except (ValueError, PermissionError) as erro:
        print("Erro:", erro)
    except Exception as erro:
        print("Erro inesperado:", erro)
