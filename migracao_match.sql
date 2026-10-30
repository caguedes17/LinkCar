-- LINKCAR - Migracao de suporte ao match de veiculos
-- Execute APENAS em uma copia do banco criado com a estrutura original,
-- ANTES das colunas e tabelas do match existirem.
-- NAO execute novamente sobre o banco da Carol, que ja foi atualizado no DB Browser.
-- Antes de executar, faca backup do banco.

PRAGMA foreign_keys = ON;
BEGIN TRANSACTION;

ALTER TABLE veiculos ADD COLUMN carroceria TEXT;
ALTER TABLE veiculos ADD COLUMN cor TEXT;
ALTER TABLE veiculos ADD COLUMN motor TEXT;
ALTER TABLE veiculos ADD COLUMN espaco_interno TEXT;
ALTER TABLE veiculos ADD COLUMN estilo_design TEXT;

CREATE TABLE IF NOT EXISTS recursos_tecnologia (
    id_recurso INTEGER PRIMARY KEY AUTOINCREMENT,
    nome_recurso TEXT NOT NULL UNIQUE
);

CREATE TABLE IF NOT EXISTS veiculo_recursos (
    id_veiculo INTEGER NOT NULL,
    id_recurso INTEGER NOT NULL,
    PRIMARY KEY (id_veiculo, id_recurso),
    FOREIGN KEY (id_veiculo) REFERENCES veiculos(id_veiculo),
    FOREIGN KEY (id_recurso) REFERENCES recursos_tecnologia(id_recurso)
);

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

COMMIT;
