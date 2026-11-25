"""Rotas de páginas e apoio ao frontend. Não substitui a API existente."""
from contextlib import closing
from flask import Blueprint, jsonify, redirect, render_template, request, session, url_for
from banco import conectar
from permissoes import verificar_permissao

frontend = Blueprint('frontend', __name__)


def usuario_atual():
    uid = session.get('id_usuario')
    if uid is None:
        return None
    with closing(conectar()) as db:
        row = db.execute('SELECT id_usuario, nome, email FROM usuarios WHERE id_usuario=? AND ativo=1', (uid,)).fetchone()
        if not row:
            session.clear()
            return None
        permissoes = [x[0] for x in db.execute('''
            SELECT DISTINCT p.nome_permissao FROM usuario_funcoes uf
            JOIN funcao_permissoes fp ON fp.id_funcao = uf.id_funcao
            JOIN permissoes p ON p.id_permissao=fp.id_permissao
            WHERE uf.id_usuario=?''', (uid,)).fetchall()]
        funcoes = [x[0] for x in db.execute('''
            SELECT f.nome_funcao FROM usuario_funcoes uf
            JOIN funcoes f ON f.id_funcao=uf.id_funcao
            WHERE uf.id_usuario=?''', (uid,)).fetchall()]
    return {'id_usuario':row[0], 'nome':row[1], 'email':row[2], 'permissoes':permissoes, 'perfis':funcoes}


def exige_sessao():
    if not usuario_atual():
        return redirect(url_for('frontend.login', proximo=request.path))
    return None


def exige_anunciante():
    erro = exige_sessao()
    if erro:
        return erro
    if not verificar_permissao(session['id_usuario'], 'cadastrar_veiculos'):
        return redirect(url_for('frontend.catalogo'))
    return None


@frontend.get('/')
def inicio():
    return render_template('index.html', pagina='inicio')


@frontend.get('/login')
def login():
    return render_template('login.html', pagina='login')


@frontend.get('/cadastro')
def cadastro():
    return render_template('cadastro.html', pagina='cadastro')


@frontend.get('/recuperar-senha')
def recuperar_senha():
    return render_template('recuperar_senha.html', pagina='recuperar')


@frontend.get('/catalogo')
def catalogo():
    erro = exige_sessao()
    return erro or render_template('catalogo.html', pagina='catalogo')


@frontend.get('/match')
def match():
    erro = exige_sessao()
    return erro or render_template('match.html', pagina='match')


@frontend.get('/favoritos')
def favoritos():
    erro = exige_sessao()
    return erro or render_template('favoritos.html', pagina='favoritos')


@frontend.get('/anunciante')
def anunciante():
    erro = exige_anunciante()
    return erro or render_template('anunciante.html', pagina='anunciante')


@frontend.get('/anunciante/novo')
def anunciante_novo():
    erro = exige_anunciante()
    return erro or render_template('veiculo_form.html', pagina='anunciante', modo='novo')


@frontend.get('/anunciante/editar/<int:id_veiculo>')
def anunciante_editar(id_veiculo):
    erro = exige_anunciante()
    return erro or render_template('veiculo_form.html', pagina='anunciante', modo='editar', id_veiculo=id_veiculo)


@frontend.get('/api/sessao')
def api_sessao():
    usuario = usuario_atual()
    if not usuario:
        return jsonify(autenticado=False), 401
    return jsonify(autenticado=True, usuario=usuario)


@frontend.get('/api/recursos')
def api_recursos():
    if not usuario_atual():
        return jsonify(erro='Faça login.'), 401
    with closing(conectar()) as db:
        dados = db.execute('SELECT id_recurso, nome_recurso FROM recursos_tecnologia ORDER BY nome_recurso').fetchall()
    return jsonify(recursos=[{'id_recurso': r[0], 'nome_recurso': r[1]} for r in dados])


@frontend.get('/api/anunciante/meus-veiculos')
def api_meus_veiculos():
    usuario = usuario_atual()
    if not usuario:
        return jsonify(erro='Faça login.'), 401
    if 'consultar_veiculos' not in usuario['permissoes'] or 'cadastrar_veiculos' not in usuario['permissoes']:
        return jsonify(erro='Acesso negado.'), 403
    with closing(conectar()) as db:
        db.row_factory = __import__('sqlite3').Row
        dados = db.execute('SELECT * FROM veiculos WHERE id_anunciante=? AND ativo=1 ORDER BY id_veiculo DESC', (usuario['id_usuario'],)).fetchall()
    return jsonify(veiculos=[dict(r) for r in dados])


@frontend.get('/api/anunciante/veiculo/<int:id_veiculo>')
def api_meu_veiculo(id_veiculo):
    usuario = usuario_atual()
    if not usuario:
        return jsonify(erro='Faça login.'), 401
    if 'editar_veiculos' not in usuario['permissoes']:
        return jsonify(erro='Acesso negado.'), 403
    import sqlite3
    with closing(conectar()) as db:
        db.row_factory = sqlite3.Row
        row = db.execute('SELECT * FROM veiculos WHERE id_veiculo=? AND id_anunciante=? AND ativo=1', (id_veiculo, usuario['id_usuario'])).fetchone()
        if not row:
            return jsonify(erro='Veículo não encontrado.'), 404
        recursos = db.execute('SELECT id_recurso FROM veiculo_recursos WHERE id_veiculo=?', (id_veiculo,)).fetchall()
    dados = dict(row)
    dados['recursos'] = [r[0] for r in recursos]
    return jsonify(veiculo=dados)
