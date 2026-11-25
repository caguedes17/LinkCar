"""LinkCar: foto principal por veículo, integrada sem alterar app.py.

Dependência: Pillow. Instalação: python -m pip install Pillow
A tabela fotos_veiculos deve existir no linkcar.db (ver LEIA-ME_UPLOAD.txt).
"""
from contextlib import closing
from io import BytesIO
from pathlib import Path
import secrets
import sqlite3

from flask import Blueprint, current_app, jsonify, request, session, url_for
from PIL import Image, ImageOps, UnidentifiedImageError

from banco import conectar
from permissoes import verificar_permissao

fotos_veiculos_bp = Blueprint('fotos_veiculos', __name__)
LIMITE_BYTES = 5 * 1024 * 1024  # 5 MB por foto original
EXTENSOES = {'.jpg', '.jpeg', '.png', '.webp'}
PASTA_RELATIVA = Path('uploads') / 'veiculos'


def _usuario():
    uid = session.get('id_usuario')
    if type(uid) is not int:
        return None
    with closing(conectar()) as con:
        existe = con.execute('SELECT 1 FROM usuarios WHERE id_usuario=? AND ativo=1', (uid,)).fetchone()
    return uid if existe else None


def _pode_editar(con, id_usuario, id_veiculo):
    """Anunciante só pode modificar imagem de veículo ativo de sua propriedade."""
    if not verificar_permissao(id_usuario, 'editar_veiculos'):
        return False
    return bool(con.execute(
        'SELECT 1 FROM veiculos WHERE id_veiculo=? AND id_anunciante=? AND ativo=1',
        (id_veiculo, id_usuario)
    ).fetchone())


def _arquivo_local(caminho):
    """Só admite caminhos criados pelo módulo dentro de static/uploads/veiculos."""
    if not isinstance(caminho, str):
        return None
    parte = Path(caminho.replace('\\', '/'))
    if (len(parte.parts) != 3 or parte.parts[0:2] != ('uploads', 'veiculos')
            or not parte.name.startswith('veiculo-') or parte.suffix != '.jpg'):
        return None
    return Path(current_app.static_folder) / parte


def _imagem_jpeg(arquivo):
    if not arquivo or not arquivo.filename:
        raise ValueError('Selecione uma imagem JPG, PNG ou WebP.')
    if Path(arquivo.filename).suffix.lower() not in EXTENSOES:
        raise ValueError('Formato inválido. Use JPG, PNG ou WebP.')
    conteudo = arquivo.stream.read(LIMITE_BYTES + 1)
    if len(conteudo) > LIMITE_BYTES:
        raise OverflowError('A foto deve ter até 5 MB.')
    if not conteudo:
        raise ValueError('O arquivo está vazio.')
    try:
        with Image.open(BytesIO(conteudo)) as conferir:
            if conferir.format not in ('JPEG', 'PNG', 'WEBP'):
                raise ValueError('O conteúdo não é uma imagem JPG, PNG ou WebP.')
            if conferir.width * conferir.height > 24_000_000:
                raise ValueError('Imagem grande demais. Limite de 24 megapixels.')
            conferir.verify()
        with Image.open(BytesIO(conteudo)) as original:
            imagem = ImageOps.exif_transpose(original)
            if imagem.mode in ('RGBA', 'LA') or 'transparency' in imagem.info:
                fundo = Image.new('RGB', imagem.size, 'white')
                rgba = imagem.convert('RGBA')
                fundo.paste(rgba, mask=rgba.getchannel('A'))
                imagem = fundo
            else:
                imagem = imagem.convert('RGB')
            imagem.thumbnail((1600, 1200), Image.Resampling.LANCZOS)
            saída = BytesIO()
            imagem.save(saída, format='JPEG', quality=86, optimize=True)
            return saída.getvalue()
    except (UnidentifiedImageError, OSError, Image.DecompressionBombError, ValueError) as exc:
        raise ValueError('O arquivo não é uma imagem válida ou está danificado.') from exc


@fotos_veiculos_bp.get('/api/fotos-veiculos')
def listar_fotos():
    uid = _usuario()
    if uid is None:
        return jsonify(erro='Faça login.'), 401
    if not verificar_permissao(uid, 'consultar_veiculos'):
        return jsonify(erro='Acesso negado.'), 403
    with closing(conectar()) as con:
        rows = con.execute("""
            SELECT f.id_veiculo, f.caminho_arquivo
            FROM fotos_veiculos f
            JOIN veiculos v ON v.id_veiculo = f.id_veiculo
            JOIN usuarios u ON u.id_usuario = v.id_anunciante
            WHERE v.ativo=1 AND u.ativo=1
        """).fetchall()
    fotos = {str(idv): url_for('static', filename=caminho) for idv, caminho in rows}
    return jsonify(fotos=fotos)


@fotos_veiculos_bp.post('/api/veiculos/<int:id_veiculo>/foto')
def enviar_foto(id_veiculo):
    uid = _usuario()
    if uid is None:
        return jsonify(erro='Faça login.'), 401
    with closing(conectar()) as con:
        if not _pode_editar(con, uid, id_veiculo):
            return jsonify(erro='Você não pode alterar fotos deste anúncio.'), 403
    try:
        if request.content_length is not None and request.content_length > LIMITE_BYTES + 256 * 1024:
            return jsonify(erro='A foto deve ter até 5 MB.'), 413
        imagem = _imagem_jpeg(request.files.get('foto'))
    except OverflowError as exc:
        return jsonify(erro=str(exc)), 413
    except ValueError as exc:
        return jsonify(erro=str(exc)), 400

    pasta = Path(current_app.static_folder) / PASTA_RELATIVA
    pasta.mkdir(parents=True, exist_ok=True)
    nome = f'veiculo-{id_veiculo}-{secrets.token_hex(10)}.jpg'
    destino = pasta / nome
    destino.write_bytes(imagem)
    caminho = (PASTA_RELATIVA / nome).as_posix()
    anterior = None
    novo = True
    try:
        with closing(conectar()) as con:
            if not _pode_editar(con, uid, id_veiculo):
                destino.unlink(missing_ok=True)
                return jsonify(erro='Acesso negado.'), 403
            row = con.execute('SELECT caminho_arquivo FROM fotos_veiculos WHERE id_veiculo=?', (id_veiculo,)).fetchone()
            if row:
                novo = False
                anterior = row[0]
            con.execute("""
                INSERT INTO fotos_veiculos (id_veiculo, caminho_arquivo)
                VALUES (?, ?)
                ON CONFLICT(id_veiculo) DO UPDATE SET
                    caminho_arquivo=excluded.caminho_arquivo,
                    data_upload=CURRENT_TIMESTAMP
            """, (id_veiculo, caminho))
            con.commit()
    except (sqlite3.Error, OSError):
        destino.unlink(missing_ok=True)
        current_app.logger.exception('Falha ao salvar foto do veículo %d', id_veiculo)
        return jsonify(erro='Não foi possível salvar a foto no banco.'), 500

    antigo = _arquivo_local(anterior)
    if antigo and antigo != destino:
        antigo.unlink(missing_ok=True)
    return jsonify(mensagem='Foto salva com sucesso!', id_veiculo=id_veiculo,
                   foto_url=url_for('static', filename=caminho)), (201 if novo else 200)


@fotos_veiculos_bp.delete('/api/veiculos/<int:id_veiculo>/foto')
def remover_foto(id_veiculo):
    uid = _usuario()
    if uid is None:
        return jsonify(erro='Faça login.'), 401
    with closing(conectar()) as con:
        if not _pode_editar(con, uid, id_veiculo):
            return jsonify(erro='Acesso negado.'), 403
        row = con.execute('SELECT caminho_arquivo FROM fotos_veiculos WHERE id_veiculo=?', (id_veiculo,)).fetchone()
        if not row:
            return jsonify(erro='Este veículo não possui foto enviada.'), 404
        con.execute('DELETE FROM fotos_veiculos WHERE id_veiculo=?', (id_veiculo,))
        con.commit()
    arquivo = _arquivo_local(row[0])
    if arquivo:
        arquivo.unlink(missing_ok=True)
    return jsonify(mensagem='Foto removida com sucesso!'), 200
