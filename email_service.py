import os
import smtplib
import ssl
from email.message import EmailMessage
def enviar_email(destinatario, assunto, mensagem):
    servidor = os.environ["SMTP_HOST"]
    porta = int(os.environ.get("SMTP_PORT", "587"))
    usuario = os.environ["SMTP_USER"]
    senha = os.environ["SMTP_PASSWORD"]
    remetente = os.environ.get("SMTP_FROM", usuario)
    email = EmailMessage()
    email["From"] = remetente
    email["To"] = destinatario
    email["Subject"] = assunto
    email.set_content(mensagem)
    contexto = ssl.create_default_context()
    if porta == 465:
        with smtplib.SMTP_SSL(
            servidor, porta, context=contexto, timeout=15
        ) as smtp:
            smtp.login(usuario, senha)
            smtp.send_message(email)
    else:
        with smtplib.SMTP(servidor, porta, timeout=15) as smtp:
            smtp.ehlo()
            smtp.starttls(context=contexto)
            smtp.ehlo()
            smtp.login(usuario, senha)
            smtp.send_message(email)
    return True