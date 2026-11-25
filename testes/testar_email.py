from email_service import enviar_email
def main():
    destinatario = input(
        "Digite o e-mail que receberá o teste: "
    ).strip()
    if not destinatario:
        print("Informe um destinatário válido.")
        return
    assunto = "LinkCar - Teste de envio"
    mensagem = """
Olá!
Este é um e-mail de teste do LinkCar.
Se você recebeu esta mensagem, o serviço
de envio de e-mails está funcionando.
Equipe LinkCar
"""
    try:
        enviar_email(destinatario, assunto, mensagem)
        print("E-mail enviado com sucesso!")
    except Exception as erro:
        print("Falha no envio:", type(erro).__name__)
if __name__ == "__main__":
    main()