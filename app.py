import math
import os
from contextlib import closing
from pathlib import Path
from dotenv import load_dotenv
from flask import Flask, jsonify, render_template, request, session
from banco import conectar
from login import autenticar_usuario
from match import PESOS, gerar_ranking
from permissoes import verificar_permissao
from recuperacao_senha import redefinir_senha, validar_token
load_dotenv(Path(__file__).with_name(".env"))
app = Flask(__name__)
chave_sessao = os.getenv("FLASK_SECRET_KEY")
if not chave_sessao:
    raise RuntimeError("Configure FLASK_SECRET_KEY no arquivo .env.")
app.config["SECRET_KEY"] = chave_sessao
def verificar_acesso_api(permissao):
    id_usuario = session.get("id_usuario")
    if id_usuario is None:
        return jsonify(erro="Faça login."), 401
    with closing(conectar()) as conexao:
        usuario_ativo = conexao.execute(
            "SELECT 1 FROM usuarios WHERE id_usuario = ? AND ativo = 1",
            (id_usuario,)
        ).fetchone()
    if usuario_ativo is None:
        session.clear()
        return jsonify(erro="Faça login."), 401
    if not verificar_permissao(id_usuario, permissao):
        return jsonify(erro="Acesso negado."), 403
    return None

def validar_preferencias_api(dados):
    if not isinstance(dados, dict) or set(dados) - set(PESOS):
        return None
    preferencias = {}
    for campo, valor in dados.items():
        if campo == "recursos":
            if not isinstance(valor, list) or any(
                not isinstance(recurso, str) for recurso in valor
            ):
                return None
            preferencias[campo] = [
                recurso.strip() for recurso in valor if recurso.strip()
            ]
        elif campo == "preco":
            if isinstance(valor, bool):
                return None
            try:
                preco = float(valor)
            except (TypeError, ValueError, OverflowError):
                return None
            if not math.isfinite(preco) or preco < 0:
                return None
            preferencias[campo] = preco
        elif not isinstance(valor, str):
            return None
        elif valor.strip().casefold() not in ("", "qualquer"):
            preferencias[campo] = valor.strip()
    return preferencias

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
@app.post("/api/login")
def api_login():
    dados = request.get_json(silent=True)
    if not isinstance(dados, dict):
        return jsonify(erro="Envie um objeto JSON."), 400
    email = dados.get("email")
    senha = dados.get("senha")
    if not isinstance(email, str) or not isinstance(senha, str):
        return jsonify(erro="Informe e-mail e senha."), 400
    session.clear()
    sucesso, usuario = autenticar_usuario(email, senha)
    if not sucesso:
        return jsonify(erro="E-mail ou senha inválidos."), 401
    session["id_usuario"] = usuario["id_usuario"]
    return jsonify(nome=usuario["nome"], perfil=usuario["perfil"])

@app.post("/api/logout")
def api_logout():
    session.clear()
    return jsonify(mensagem="Logout realizado com sucesso.")
@app.get("/api/admin/acesso")
def api_admin_acesso():
    erro = verificar_acesso_api("gerenciar_usuarios")
    if erro is not None:
        return erro
    return jsonify(acesso=True)
@app.post("/api/match")
def api_match():
    erro = verificar_acesso_api("consultar_veiculos")
    if erro is not None:
        return erro
    preferencias = validar_preferencias_api(request.get_json(silent=True))
    if preferencias is None:
        return jsonify(erro="Confira os critérios informados."), 400
    return jsonify(resultados=gerar_ranking(preferencias))