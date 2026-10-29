-- LINK CAR - Estrutura inicial do banco de dados
-- Execute este arquivo em um banco SQLite vazio.
-- No DB Browser: Arquivo > Importar > Banco de dados a partir de arquivo SQL
-- ou abra o arquivo no Editor SQL e clique em Executar.

PRAGMA foreign_keys = ON;
BEGIN TRANSACTION;

-- 1. Usuarios
DROP TABLE IF EXISTS usuarios;
CREATE TABLE usuarios (
    id_usuario INTEGER PRIMARY KEY AUTOINCREMENT,
    nome TEXT NOT NULL,
    email TEXT NOT NULL UNIQUE,
    senha_hash TEXT NOT NULL,
    data_criacao TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
    ativo INTEGER NOT NULL DEFAULT 1
);

-- 2. Funcoes (papeis do RBAC)
DROP TABLE IF EXISTS funcoes;
CREATE TABLE funcoes (
    id_funcao INTEGER PRIMARY KEY AUTOINCREMENT,
    nome_funcao TEXT NOT NULL UNIQUE,
    descricao TEXT
);

-- 3. Permissoes
CREATE TABLE IF NOT EXISTS permissoes (
    id_permissao INTEGER PRIMARY KEY AUTOINCREMENT,
    nome_permissao TEXT NOT NULL UNIQUE,
    descricao TEXT
);

-- 4. Relacionamento entre usuarios e funcoes
DROP TABLE IF EXISTS usuario_funcoes;
CREATE TABLE usuario_funcoes (
    id_usuario INTEGER NOT NULL,
    id_funcao INTEGER NOT NULL,
    PRIMARY KEY (id_usuario, id_funcao),
    FOREIGN KEY (id_usuario) REFERENCES usuarios(id_usuario),
    FOREIGN KEY (id_funcao) REFERENCES funcoes(id_funcao)
);

-- 5. Relacionamento entre funcoes e permissoes
DROP TABLE IF EXISTS funcao_permissoes;
CREATE TABLE funcao_permissoes (
    id_funcao INTEGER NOT NULL,
    id_permissao INTEGER NOT NULL,
    PRIMARY KEY (id_funcao, id_permissao),
    FOREIGN KEY (id_funcao) REFERENCES funcoes(id_funcao),
    FOREIGN KEY (id_permissao) REFERENCES permissoes(id_permissao)
);

-- 6. Veiculos
DROP TABLE IF EXISTS veiculos;
CREATE TABLE veiculos (
    id_veiculo INTEGER PRIMARY KEY AUTOINCREMENT,
    id_anunciante INTEGER NOT NULL,
    marca TEXT NOT NULL,
    modelo TEXT NOT NULL,
    ano INTEGER NOT NULL,
    preco REAL NOT NULL,
    quilometragem INTEGER,
    combustivel TEXT,
    cambio TEXT,
    descricao TEXT,
    data_cadastro TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
    ativo INTEGER NOT NULL DEFAULT 1,
    FOREIGN KEY (id_anunciante) REFERENCES usuarios(id_usuario)
);

-- Dados iniciais: funcoes
INSERT OR IGNORE INTO funcoes (nome_funcao, descricao) VALUES
('Administrador', 'Gerenciamento geral do sistema'),
('Anunciante', 'Gerenciamento dos proprios anuncios'),
('Usuario', 'Consulta e pesquisa de veiculos');

-- Dados iniciais: permissoes
INSERT OR IGNORE INTO permissoes (nome_permissao, descricao) VALUES
('gerenciar_usuarios', 'Cadastrar, consultar, alterar e desativar usuarios'),
('gerenciar_funcoes', 'Criar e administrar funcoes do sistema'),
('gerenciar_permissoes', 'Administrar as permissoes de acesso'),
('cadastrar_veiculos', 'Cadastrar novos veiculos'),
('editar_veiculos', 'Alterar informacoes dos veiculos'),
('excluir_veiculos', 'Excluir veiculos cadastrados'),
('consultar_veiculos', 'Consultar e pesquisar veiculos'),
('gerenciar_favoritos', 'Adicionar e remover veiculos dos favoritos');

-- Administrador recebe todas as permissoes
INSERT OR IGNORE INTO funcao_permissoes (id_funcao, id_permissao)
SELECT f.id_funcao, p.id_permissao
FROM funcoes AS f
CROSS JOIN permissoes AS p
WHERE f.nome_funcao = 'Administrador';

-- Anunciante recebe permissoes relacionadas aos seus anuncios
INSERT OR IGNORE INTO funcao_permissoes (id_funcao, id_permissao)
SELECT f.id_funcao, p.id_permissao
FROM funcoes AS f
CROSS JOIN permissoes AS p
WHERE f.nome_funcao = 'Anunciante'
  AND p.nome_permissao IN (
      'cadastrar_veiculos',
      'editar_veiculos',
      'excluir_veiculos',
      'consultar_veiculos'
  );

-- Usuario pode consultar veiculos e gerenciar favoritos
INSERT OR IGNORE INTO funcao_permissoes (id_funcao, id_permissao)
SELECT f.id_funcao, p.id_permissao
FROM funcoes AS f
CROSS JOIN permissoes AS p
WHERE f.nome_funcao = 'Usuario'
  AND p.nome_permissao IN (
      'consultar_veiculos',
      'gerenciar_favoritos'
  );

COMMIT;