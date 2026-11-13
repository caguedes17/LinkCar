from flask import Flask, render_template, request
from recuperacao_senha import redefinir_senha, validar_token
app = Flask(__name__)
@app.route("/redefinir-senha", methods=["GET", "POST"])
def pagina_redefinir_senha():
    if request.method == "GET":
        token = request.args.get("token", "")
        if validar_token(token) is None:
            return "Link inválido ou expirado.", 400
        return render_template("redefinir_senha.html", token=token)
    token = request.form.get("token", "")
    senha = request.form.get("senha", "")
    confirmar = request.form.get("confirmar", "")
    if senha != confirmar:
        return "As senhas não coincidem.", 400
    sucesso, mensagem = redefinir_senha(token, senha)
    return mensagem, (200 if sucesso else 400)