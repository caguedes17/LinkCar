
import math
import os
import sqlite3
from veiculos import cadastrar_veiculo, excluir_veiculo
from contextlib import closing
from pathlib import Path
from veiculos import buscar_veiculo_para_edicao, editar_veiculo

from dotenv import load_dotenv
from flask import Flask, jsonify, render_template, request, session

from banco import conectar
from login import autenticar_usuario
from match import PESOS, buscar_veiculos_disponiveis, gerar_ranking
from permissoes import verificar_permissao
from recuperacao_senha import (
    redefinir_senha,
    validar_token,
    enviar_recuperacao,
)

# Carrega o .env da pasta do projeto, antes de ler qualquer variável
load_dotenv(Path(__file__).with_name(".env"))

app = Flask(__name__)

chave_sessao = os.getenv("FLASK_SECRET_KEY")
if not chave_sessao:
    raise RuntimeError("Configure FLASK_SECRET_KEY no arquivo .env.")
app.config["SECRET_KEY"] = chave_sessao


# ==========================================
# FUNÇÕES AUXILIARES
# ==========================================

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


# ==========================================
# PÁGINAS
# ==========================================

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


# ==========================================
# API: LOGIN E LOGOUT
# ==========================================

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


# ==========================================
# API: ADMIN E MATCH
# ==========================================

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

@app.post("/api/recuperar-senha")
def api_recuperar_senha():
    dados = request.get_json(silent=True)
    if not isinstance(dados, dict):
        return jsonify(erro="Envie um objeto JSON."), 400
    email = dados.get("email")
    if not isinstance(email, str) or not (1 <= len(email.strip()) <= 254):
        return jsonify(erro="Informe um e-mail valido."), 400
    try:
        enviar_recuperacao(email)
    except Exception:
        app.logger.exception("Falha na recuperacao de senha")
        return jsonify(erro="Servico temporariamente indisponivel."), 503
    return jsonify(mensagem=(
        "Se o e-mail estiver cadastrado, "
        "as instrucoes serao enviadas."
    )), 200
@app.get("/api/veiculos")
def api_listar_veiculos():
    erro = verificar_acesso_api("consultar_veiculos")

    if erro is not None:
        return erro

    veiculos = buscar_veiculos_disponiveis()

    return jsonify(veiculos=veiculos)

@app.post("/api/veiculos")
def api_cadastrar_veiculo():
    erro = verificar_acesso_api("cadastrar_veiculos")
    if erro is not None:
        return erro
    dados = request.get_json(silent=True)
    if not isinstance(dados, dict):
        return jsonify(erro="Envie os dados do veículo em JSON."), 400
    campos_texto = (
        "marca", "modelo", "combustivel", "cambio", "carroceria",
        "cor", "motor", "espaco_interno", "estilo_design", "descricao",
    )
    for campo in campos_texto:
        if campo in dados and not isinstance(dados[campo], str):
            return jsonify(erro=f"O campo {campo} deve ser texto."), 400
    for campo in ("ano", "quilometragem"):
        if type(dados.get(campo)) is not int:
            return jsonify(erro=f"O campo {campo} deve ser um inteiro."), 400
    if type(dados.get("preco")) not in (int, float):
        return jsonify(erro="O preço deve ser um número."), 400
    try:
        id_veiculo = cadastrar_veiculo(session["id_usuario"], dados)
    except PermissionError:
        return jsonify(erro="Acesso negado."), 403
    except ValueError as erro:
        return jsonify(erro=str(erro)), 400
    except OverflowError:
        return jsonify(erro="Valor numérico fora do limite aceito."), 400
    except sqlite3.IntegrityError:
        return jsonify(erro="Confira os dados e os IDs dos recursos."), 400
    return jsonify(id_veiculo=id_veiculo), 201

@app.patch("/api/veiculos/<int:id_veiculo>")
def api_editar_veiculo(id_veiculo):
    erro = verificar_acesso_api("editar_veiculos")
    if erro is not None:
        return erro
    alteracoes = request.get_json(silent=True)
    if not isinstance(alteracoes, dict) or not alteracoes:
        return jsonify(erro="Informe os dados que deseja alterar."), 400
    campos_editaveis = {
        "marca", "modelo", "ano", "preco", "quilometragem",
        "combustivel", "cambio", "descricao", "carroceria",
        "cor", "motor", "espaco_interno", "estilo_design", "recursos"
    }
    if set(alteracoes) - campos_editaveis:
        return jsonify(erro="Existem campos nao permitidos."), 400
    try:
        dados = buscar_veiculo_para_edicao(
            session["id_usuario"], id_veiculo
        )
        dados.update(alteracoes)
        editar_veiculo(session["id_usuario"], id_veiculo, dados)
    except PermissionError:
        return jsonify(erro="Acesso negado."), 403
    except ValueError as erro:
        return jsonify(erro=str(erro)), 400
    except (TypeError, OverflowError):
        return jsonify(erro="Dados invalidos."), 400
    except sqlite3.IntegrityError:
        return jsonify(erro="Confira os recursos informados."), 400
    return jsonify(
        mensagem="Veículo atualizado com sucesso!",
        id_veiculo=id_veiculo
    ), 200
@app.delete("/api/veiculos/<int:id_veiculo>")
def api_excluir_veiculo(id_veiculo):
    erro = verificar_acesso_api("excluir_veiculos")

    if erro is not None:
        return erro

    try:
        excluir_veiculo(
            session["id_usuario"],
            id_veiculo
        )

    except PermissionError:
        return jsonify(erro="Acesso negado."), 403

    except ValueError as erro:
        return jsonify(erro=str(erro)), 404

    return jsonify(
        mensagem="Veículo desativado com sucesso!",
        id_veiculo=id_veiculo
    ), 200