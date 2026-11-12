-- LINKCAR | Estrutura SQLite com VARCHAR(n)
-- ATENCAO: SQLite nao aplica limite de comprimento do VARCHAR(n) automaticamente.
-- Este script cria a estrutura; nao inclui dados de usuarios nem outros registros.

CREATE TABLE favoritos (
    id_usuario INTEGER NOT NULL,
    id_veiculo INTEGER NOT NULL,
    data_favorito VARCHAR(19) NOT NULL DEFAULT CURRENT_TIMESTAMP,

    PRIMARY KEY (id_usuario, id_veiculo),

    FOREIGN KEY (id_usuario)
        REFERENCES usuarios(id_usuario),

    FOREIGN KEY (id_veiculo)
        REFERENCES veiculos(id_veiculo)
);

CREATE TABLE funcao_permissoes (
    id_funcao INTEGER NOT NULL,
    id_permissao INTEGER NOT NULL,

    PRIMARY KEY (id_funcao, id_permissao),

    FOREIGN KEY (id_funcao)
        REFERENCES funcoes(id_funcao),

    FOREIGN KEY (id_permissao)
        REFERENCES permissoes(id_permissao)
);

CREATE TABLE funcoes (
    id_funcao INTEGER PRIMARY KEY AUTOINCREMENT,
    nome_funcao VARCHAR(80) NOT NULL UNIQUE,
    descricao VARCHAR(2000)
);

CREATE TABLE permissoes (
    id_permissao INTEGER PRIMARY KEY AUTOINCREMENT,
    nome_permissao VARCHAR(100) NOT NULL UNIQUE,
    descricao VARCHAR(2000)
);

CREATE TABLE recursos_tecnologia (
    id_recurso INTEGER PRIMARY KEY AUTOINCREMENT,
    nome_recurso VARCHAR(150) NOT NULL UNIQUE
);

CREATE TABLE tokens_recuperacao (
    id_token INTEGER PRIMARY KEY AUTOINCREMENT,
    id_usuario INTEGER NOT NULL,
    token_hash VARCHAR(64) NOT NULL UNIQUE,
    data_expiracao VARCHAR(19) NOT NULL,
    utilizado INTEGER NOT NULL DEFAULT 0,
    data_criacao VARCHAR(19) NOT NULL DEFAULT CURRENT_TIMESTAMP,

    FOREIGN KEY (id_usuario)
        REFERENCES usuarios(id_usuario)
);

CREATE TABLE usuario_funcoes (
    id_usuario INTEGER NOT NULL,
    id_funcao INTEGER NOT NULL,

    PRIMARY KEY (id_usuario, id_funcao),

    FOREIGN KEY (id_usuario)
        REFERENCES usuarios(id_usuario),

    FOREIGN KEY (id_funcao)
        REFERENCES funcoes(id_funcao)
);

CREATE TABLE usuarios (
    id_usuario INTEGER PRIMARY KEY AUTOINCREMENT,
    nome VARCHAR(150) NOT NULL,
    email VARCHAR(254) NOT NULL UNIQUE,
    senha_hash VARCHAR(512) NOT NULL,
    data_criacao VARCHAR(19) NOT NULL DEFAULT CURRENT_TIMESTAMP,
    ativo INTEGER NOT NULL DEFAULT 1
);

CREATE TABLE veiculo_recursos (
    id_veiculo INTEGER NOT NULL,
    id_recurso INTEGER NOT NULL,

    PRIMARY KEY (id_veiculo, id_recurso),

    FOREIGN KEY (id_veiculo)
        REFERENCES veiculos(id_veiculo),

    FOREIGN KEY (id_recurso)
        REFERENCES recursos_tecnologia(id_recurso)
);

CREATE TABLE veiculos (
    id_veiculo INTEGER PRIMARY KEY AUTOINCREMENT,
    id_anunciante INTEGER NOT NULL,
    marca VARCHAR(100) NOT NULL,
    modelo VARCHAR(120) NOT NULL,
    ano INTEGER NOT NULL,
    preco REAL NOT NULL,
    quilometragem INTEGER,
    combustivel VARCHAR(50),
    cambio VARCHAR(50),
    descricao VARCHAR(2000),
    data_cadastro VARCHAR(19) NOT NULL DEFAULT CURRENT_TIMESTAMP,
    ativo INTEGER NOT NULL DEFAULT 1, carroceria VARCHAR(80), cor VARCHAR(80), motor VARCHAR(100), espaco_interno VARCHAR(100), estilo_design VARCHAR(100),

    FOREIGN KEY (id_anunciante)
        REFERENCES usuarios(id_usuario)
);

