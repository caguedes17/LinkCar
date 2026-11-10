-- SQLITE: VARCHAR(n) tem afinidade TEXT e nao limita automaticamente n caracteres.
-- LINKCAR | ESTRUTURA COMPLETA PARA NOVAS INSTALACOES
-- Inclui tabelas iniciais e os campos / recursos do match.
-- CRIAR um banco SQLite NOVO e VAZIO para executar este script.
-- NAO executar no linkcar.db atual que ja possui usuarios e veiculos.
-- NAO contem DROP TABLE, ALTER TABLE nem transacao BEGIN/COMMIT.
-- Nao substitui uma migracao de um banco antigo existente.

-- Execute este arquivo em um banco SQLite vazio.
-- No DB Browser: Arquivo > Importar > Banco de dados a partir de arquivo SQL
-- ou abra o arquivo no Editor SQL e clique em Executar.

PRAGMA foreign_keys = ON;

-- 1. Usuarios
CREATE TABLE IF NOT EXISTS usuarios (
    id_usuario INTEGER PRIMARY KEY AUTOINCREMENT,
    nome VARCHAR(120) NOT NULL,
    email VARCHAR(254) NOT NULL UNIQUE,
    senha_hash VARCHAR(255) NOT NULL,
    data_criacao VARCHAR(32) NOT NULL DEFAULT CURRENT_TIMESTAMP,
    ativo INTEGER NOT NULL DEFAULT 1
);

-- 2. Funcoes (papeis do RBAC)
CREATE TABLE IF NOT EXISTS funcoes (
    id_funcao INTEGER PRIMARY KEY AUTOINCREMENT,
    nome_funcao VARCHAR(80) NOT NULL UNIQUE,
    descricao VARCHAR(2000)
);

-- 3. Permissoes
CREATE TABLE IF NOT EXISTS permissoes (
    id_permissao INTEGER PRIMARY KEY AUTOINCREMENT,
    nome_permissao VARCHAR(80) NOT NULL UNIQUE,
    descricao VARCHAR(2000)
);

-- 4. Relacionamento entre usuarios e funcoes
CREATE TABLE IF NOT EXISTS usuario_funcoes (
    id_usuario INTEGER NOT NULL,
    id_funcao INTEGER NOT NULL,
    PRIMARY KEY (id_usuario, id_funcao),
    FOREIGN KEY (id_usuario) REFERENCES usuarios(id_usuario),
    FOREIGN KEY (id_funcao) REFERENCES funcoes(id_funcao)
);

-- 5. Relacionamento entre funcoes e permissoes
CREATE TABLE IF NOT EXISTS funcao_permissoes (
    id_funcao INTEGER NOT NULL,
    id_permissao INTEGER NOT NULL,
    PRIMARY KEY (id_funcao, id_permissao),
    FOREIGN KEY (id_funcao) REFERENCES funcoes(id_funcao),
    FOREIGN KEY (id_permissao) REFERENCES permissoes(id_permissao)
);

-- 6. Veiculos
CREATE TABLE IF NOT EXISTS veiculos (
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
    FOREIGN KEY (id_anunciante) REFERENCES usuarios(id_usuario)
);

-- 7 . Favoritos
CREATE TABLE IF NOT EXISTS favoritos (
    id_usuario INTEGER NOT NULL,
    id_veiculo INTEGER NOT NULL,
    data_favorito VARCHAR(32) NOT NULL DEFAULT CURRENT_TIMESTAMP,

    PRIMARY KEY (id_usuario, id_veiculo),

    FOREIGN KEY (id_usuario)
        REFERENCES usuarios(id_usuario),

    FOREIGN KEY (id_veiculo)
        REFERENCES veiculos(id_veiculo)
);

-- 8 . Token de recuperação de senha
CREATE TABLE IF NOT EXISTS tokens_recuperacao (
    id_token INTEGER PRIMARY KEY AUTOINCREMENT,
    id_usuario INTEGER NOT NULL,
    token_hash VARCHAR(255) NOT NULL UNIQUE,
    data_expiracao VARCHAR(32) NOT NULL,
    utilizado INTEGER NOT NULL DEFAULT 0,
    data_criacao VARCHAR(32) NOT NULL DEFAULT CURRENT_TIMESTAMP,

    FOREIGN KEY (id_usuario)
        REFERENCES usuarios(id_usuario)
);

-- 9 e 10. Recursos do match (relacionamento N:N com veiculos)
CREATE TABLE IF NOT EXISTS recursos_tecnologia (
    id_recurso INTEGER PRIMARY KEY AUTOINCREMENT,
    nome_recurso VARCHAR(120) NOT NULL UNIQUE
);

CREATE TABLE IF NOT EXISTS veiculo_recursos (
    id_veiculo INTEGER NOT NULL,
    id_recurso INTEGER NOT NULL,
    PRIMARY KEY (id_veiculo, id_recurso),
    FOREIGN KEY (id_veiculo) REFERENCES veiculos(id_veiculo),
    FOREIGN KEY (id_recurso) REFERENCES recursos_tecnologia(id_recurso)
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

-- Catalogo de recursos tecnologicos (40 opcoes)
INSERT OR IGNORE INTO recursos_tecnologia (nome_recurso) VALUES
('Ar-condicionado'),
('Direção elétrica'),
('Bluetooth'),
('Central multimídia'),
('Câmera de ré'),
('Sensor de estacionamento'),
('GPS integrado'),
('Carregador por indução'),
('Chave presencial'),
('Piloto automático'),
('Assistente de estacionamento'),
('Alerta de ponto cego'),
('Frenagem automática de emergência'),
('Android Auto'),
('Apple CarPlay'),
('Câmera 360 graus'),
('Sensor de estacionamento dianteiro'),
('Piloto automático adaptativo'),
('Alerta de saída de faixa'),
('Assistente de permanência em faixa'),
('Alerta de colisão frontal'),
('Detector de fadiga do motorista'),
('Monitoramento da pressão dos pneus'),
('Controle eletrônico de estabilidade'),
('Controle de tração'),
('Assistente de partida em rampa'),
('Airbags laterais'),
('Fixação ISOFIX'),
('Faróis de LED'),
('Acendimento automático dos faróis'),
('Sensor de chuva'),
('Painel de instrumentos digital'),
('Entradas USB-C'),
('Internet Wi-Fi integrada'),
('Sistema de som premium'),
('Ar-condicionado digital'),
('Bancos com ajuste elétrico'),
('Bancos aquecidos'),
('Teto solar'),
('Partida por botão');
