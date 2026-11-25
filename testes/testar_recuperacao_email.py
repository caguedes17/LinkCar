
import traceback
from recuperacao_senha import enviar_recuperacao

print("=== LINKCAR | TESTE DE RECUPERACAO ===")

email = input("E-mail cadastrado: ").strip()

try:
    mensagem = enviar_recuperacao(email)
    print("\n" + mensagem)
    print("Verifique tambem a pasta de spam.")

except Exception as erro:
    print("\nNao foi possivel concluir o envio.")
    print("Tipo do erro:", type(erro).__name__)
    traceback.print_exc()
