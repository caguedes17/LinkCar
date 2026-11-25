from veiculos import listar_meus_veiculos

id_usuario = 2

try:
    veiculos = listar_meus_veiculos(id_usuario)

    print("===== MEUS ANÚNCIOS =====")

    if not veiculos:
        print("Nenhum veículo encontrado.")

    for carro in veiculos:
        print("------------------------")
        print("ID:", carro[0])
        print("Veículo:", carro[1], carro[2])
        print("Ano:", carro[3])
        print("Preço: R$", carro[4])
        print("Quilometragem:", carro[5], "km")

except Exception as erro:
    print("Erro:", erro)
