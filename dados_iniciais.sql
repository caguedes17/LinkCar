-- LINKCAR | Dados iniciais para INSTALACAO NOVA
-- Execute APOS LinkCar_estrutura_revisada.sql.
-- Nenhum usuario, senha, token, favorito ou veiculo pessoal esta incluido.
-- Nao execute no banco atual; use uma copia nova.
PRAGMA foreign_keys = ON;
BEGIN TRANSACTION;

-- funcoes: 3 registros
INSERT OR IGNORE INTO funcoes (id_funcao, nome_funcao, descricao) VALUES
    (1, 'Administrador', 'Gerenciamento geral do sistema'),
    (2, 'Anunciante', 'Gerenciamento dos próprios anúncios'),
    (3, 'Usuario', 'Consulta e pesquisa de veículos');

-- permissoes: 8 registros
INSERT OR IGNORE INTO permissoes (id_permissao, nome_permissao, descricao) VALUES
    (1, 'gerenciar_usuarios', 'Cadastrar, consultar, alterar e desativar usuários'),
    (2, 'gerenciar_funcoes', 'Criar e administrar funções do sistema'),
    (3, 'gerenciar_permissoes', 'Administrar as permissões de acesso'),
    (4, 'cadastrar_veiculos', 'Cadastrar novos veículos'),
    (5, 'editar_veiculos', 'Alterar informações dos veículos'),
    (6, 'excluir_veiculos', 'Excluir veículos cadastrados'),
    (7, 'consultar_veiculos', 'Consultar e pesquisar veículos'),
    (8, 'gerenciar_favoritos', 'Adicionar e remover veículos dos favoritos');

-- recursos_tecnologia: 40 registros
INSERT OR IGNORE INTO recursos_tecnologia (id_recurso, nome_recurso) VALUES
    (1, 'Ar-condicionado'),
    (2, 'Direção elétrica'),
    (3, 'Bluetooth'),
    (4, 'Central multimídia'),
    (5, 'Câmera de ré'),
    (6, 'Sensor de estacionamento'),
    (7, 'GPS integrado'),
    (8, 'Carregador por indução'),
    (9, 'Chave presencial'),
    (10, 'Piloto automático'),
    (11, 'Assistente de estacionamento'),
    (12, 'Alerta de ponto cego'),
    (13, 'Frenagem automática de emergência'),
    (14, 'Android Auto'),
    (15, 'Apple CarPlay'),
    (16, 'Câmera 360 graus'),
    (17, 'Sensor de estacionamento dianteiro'),
    (18, 'Piloto automático adaptativo'),
    (19, 'Alerta de saída de faixa'),
    (20, 'Assistente de permanência em faixa'),
    (21, 'Alerta de colisão frontal'),
    (22, 'Detector de fadiga do motorista'),
    (23, 'Monitoramento da pressão dos pneus'),
    (24, 'Controle eletrônico de estabilidade'),
    (25, 'Controle de tração'),
    (26, 'Assistente de partida em rampa'),
    (27, 'Airbags laterais'),
    (28, 'Fixação ISOFIX'),
    (29, 'Faróis de LED'),
    (30, 'Acendimento automático dos faróis'),
    (31, 'Sensor de chuva'),
    (32, 'Painel de instrumentos digital'),
    (33, 'Entradas USB-C'),
    (34, 'Internet Wi-Fi integrada'),
    (35, 'Sistema de som premium'),
    (36, 'Ar-condicionado digital'),
    (37, 'Bancos com ajuste elétrico'),
    (38, 'Bancos aquecidos'),
    (39, 'Teto solar'),
    (40, 'Partida por botão');

-- Atribuicao RBAC pelo NOME, independente dos IDs locais.
INSERT OR IGNORE INTO funcao_permissoes (id_funcao, id_permissao)
SELECT f.id_funcao, p.id_permissao
FROM funcoes AS f CROSS JOIN permissoes AS p
WHERE f.nome_funcao = 'Administrador';

INSERT OR IGNORE INTO funcao_permissoes (id_funcao, id_permissao)
SELECT f.id_funcao, p.id_permissao
FROM funcoes AS f CROSS JOIN permissoes AS p
WHERE f.nome_funcao = 'Anunciante'
  AND p.nome_permissao IN (
    'cadastrar_veiculos', 'consultar_veiculos',
    'editar_veiculos', 'excluir_veiculos'
  );

INSERT OR IGNORE INTO funcao_permissoes (id_funcao, id_permissao)
SELECT f.id_funcao, p.id_permissao
FROM funcoes AS f CROSS JOIN permissoes AS p
WHERE f.nome_funcao = 'Usuario'
  AND p.nome_permissao IN ('consultar_veiculos', 'gerenciar_favoritos');

COMMIT;
