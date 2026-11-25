-- LINKCAR | Estrutura oficial para INSTALACAO NOVA
-- Compatível com o esquema do linkcar.db enviado.
-- ATENCAO: DROP TABLE IF EXISTS APAGA TODOS OS DADOS se executado em banco existente.
-- Execute SOMENTE em banco novo/de teste; nunca no linkcar.db atual.
-- NAO execute no banco atual com dados de usuarios/anuncios.
-- Os dados de referencia ficam no arquivo dados_iniciais.sql.
-- SQLite nao limita o tamanho de VARCHAR(n) automaticamente.

PRAGMA foreign_keys = ON;
BEGIN TRANSACTION;

-- Remover primeiro tabelas dependentes (filhas), depois as tabelas principais.
DROP TABLE IF EXISTS fotos_veiculos;
DROP TABLE IF EXISTS favoritos;
DROP TABLE IF EXISTS veiculo_recursos;
DROP TABLE IF EXISTS tokens_recuperacao;
DROP TABLE IF EXISTS usuario_funcoes;
DROP TABLE IF EXISTS funcao_permissoes;
DROP TABLE IF EXISTS veiculos;
DROP TABLE IF EXISTS recursos_tecnologia;
DROP TABLE IF EXISTS permissoes;
DROP TABLE IF EXISTS funcoes;
DROP TABLE IF EXISTS usuarios;

-- Tabela: usuarios
CREATE TABLE usuarios (
    id_usuario INTEGER PRIMARY KEY AUTOINCREMENT,
    nome VARCHAR(120) NOT NULL,
    email VARCHAR(254) NOT NULL UNIQUE,
    senha_hash VARCHAR(255) NOT NULL,
    data_criacao VARCHAR(32) NOT NULL DEFAULT CURRENT_TIMESTAMP,
    ativo INTEGER NOT NULL DEFAULT 1
);

-- Tabela: funcoes
CREATE TABLE funcoes (
    id_funcao INTEGER PRIMARY KEY AUTOINCREMENT,
    nome_funcao VARCHAR(80) NOT NULL UNIQUE,
    descricao VARCHAR(2000)
);

-- Tabela: permissoes
CREATE TABLE permissoes (
    id_permissao INTEGER PRIMARY KEY AUTOINCREMENT,
    nome_permissao VARCHAR(80) NOT NULL UNIQUE,
    descricao VARCHAR(2000)
);

-- Tabela: recursos_tecnologia
CREATE TABLE recursos_tecnologia (
    id_recurso INTEGER PRIMARY KEY AUTOINCREMENT,
    nome_recurso VARCHAR(120) NOT NULL UNIQUE
);

-- Tabela: veiculos
CREATE TABLE veiculos (
    id_veiculo INTEGER PRIMARY KEY AUTOINCREMENT,
    id_anunciante INTEGER NOT NULL,
    marca VARCHAR(80) NOT NULL,
    modelo VARCHAR(120) NOT NULL,
    ano INTEGER NOT NULL,
    preco REAL NOT NULL,
    quilometragem INTEGER,
    combustivel VARCHAR(40),
    cambio VARCHAR(40),
    descricao VARCHAR(2000),
    data_cadastro VARCHAR(32) NOT NULL DEFAULT CURRENT_TIMESTAMP,
    ativo INTEGER NOT NULL DEFAULT 1,
    carroceria VARCHAR(40),
    cor VARCHAR(40),
    motor VARCHAR(40),
    espaco_interno VARCHAR(40),
    estilo_design VARCHAR(40),

    FOREIGN KEY (id_anunciante)
        REFERENCES usuarios(id_usuario)
);

-- Tabela: usuario_funcoes
CREATE TABLE usuario_funcoes (
    id_usuario INTEGER NOT NULL,
    id_funcao INTEGER NOT NULL,

    PRIMARY KEY (id_usuario, id_funcao),

    FOREIGN KEY (id_usuario)
        REFERENCES usuarios(id_usuario),

    FOREIGN KEY (id_funcao)
        REFERENCES funcoes(id_funcao)
);

-- Tabela: funcao_permissoes
CREATE TABLE funcao_permissoes (
    id_funcao INTEGER NOT NULL,
    id_permissao INTEGER NOT NULL,

    PRIMARY KEY (id_funcao, id_permissao),

    FOREIGN KEY (id_funcao)
        REFERENCES funcoes(id_funcao),

    FOREIGN KEY (id_permissao)
        REFERENCES permissoes(id_permissao)
);

-- Tabela: veiculo_recursos
CREATE TABLE veiculo_recursos (
    id_veiculo INTEGER NOT NULL,
    id_recurso INTEGER NOT NULL,

    PRIMARY KEY (id_veiculo, id_recurso),

    FOREIGN KEY (id_veiculo)
        REFERENCES veiculos(id_veiculo),

    FOREIGN KEY (id_recurso)
        REFERENCES recursos_tecnologia(id_recurso)
);

-- Tabela: favoritos
CREATE TABLE favoritos (
    id_usuario INTEGER NOT NULL,
    id_veiculo INTEGER NOT NULL,
    data_favorito VARCHAR(32) NOT NULL DEFAULT CURRENT_TIMESTAMP,

    PRIMARY KEY (id_usuario, id_veiculo),

    FOREIGN KEY (id_usuario)
        REFERENCES usuarios(id_usuario),

    FOREIGN KEY (id_veiculo)
        REFERENCES veiculos(id_veiculo)
);

-- Tabela: fotos_veiculos (uma foto principal por veiculo)
-- O banco guarda apenas o caminho; o arquivo fica em static/uploads/.
CREATE TABLE fotos_veiculos (
    id_foto INTEGER PRIMARY KEY AUTOINCREMENT,
    id_veiculo INTEGER NOT NULL UNIQUE,
    caminho_arquivo VARCHAR(255) NOT NULL,
    data_upload DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,

    FOREIGN KEY (id_veiculo)
        REFERENCES veiculos(id_veiculo)
        ON DELETE CASCADE
);

-- Tabela: tokens_recuperacao
CREATE TABLE tokens_recuperacao (
    id_token INTEGER PRIMARY KEY AUTOINCREMENT,
    id_usuario INTEGER NOT NULL,
    token_hash VARCHAR(255) NOT NULL UNIQUE,
    data_expiracao VARCHAR(32) NOT NULL,
    utilizado INTEGER NOT NULL DEFAULT 0,
    data_criacao VARCHAR(32) NOT NULL DEFAULT CURRENT_TIMESTAMP,

    FOREIGN KEY (id_usuario)
        REFERENCES usuarios(id_usuario)
);

COMMIT;
