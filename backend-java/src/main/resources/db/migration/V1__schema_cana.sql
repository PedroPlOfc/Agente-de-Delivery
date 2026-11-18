-- Migração não destrutiva: cria apenas objetos ausentes e preserva dados existentes.
CREATE TABLE IF NOT EXISTS categorias (
    id SERIAL PRIMARY KEY,
    nome VARCHAR(100) NOT NULL UNIQUE,
    descricao TEXT,
    criado_em TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS produtos (
    id SERIAL PRIMARY KEY,
    codigo_barras VARCHAR(20) UNIQUE NOT NULL,
    nome VARCHAR(150) NOT NULL,
    categoria_id INTEGER NOT NULL REFERENCES categorias(id) ON DELETE RESTRICT,
    preco_venda NUMERIC(10, 2) NOT NULL CHECK (preco_venda >= 0),
    unidade_medida VARCHAR(10) NOT NULL DEFAULT 'UN',
    ativo BOOLEAN NOT NULL DEFAULT TRUE,
    criado_em TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS estoque (
    id SERIAL PRIMARY KEY,
    produto_id INTEGER NOT NULL UNIQUE REFERENCES produtos(id) ON DELETE CASCADE,
    quantidade_disponivel NUMERIC(10, 3) NOT NULL DEFAULT 0.000,
    atualizado_em TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS pedidos (
    id SERIAL PRIMARY KEY,
    cliente_telefone VARCHAR(20) NOT NULL,
    cliente_nome VARCHAR(100),
    status VARCHAR(30) NOT NULL DEFAULT 'PENDENTE',
    forma_pagamento VARCHAR(50),
    valor_total NUMERIC(10, 2) NOT NULL DEFAULT 0.00,
    origem VARCHAR(20) NOT NULL DEFAULT 'WHATSAPP',
    criado_em TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS itens_pedido (
    id SERIAL PRIMARY KEY,
    pedido_id INTEGER NOT NULL REFERENCES pedidos(id) ON DELETE CASCADE,
    produto_id INTEGER NOT NULL REFERENCES produtos(id) ON DELETE RESTRICT,
    quantidade NUMERIC(10, 3) NOT NULL CHECK (quantidade > 0),
    preco_unitario NUMERIC(10, 2) NOT NULL,
    subtotal NUMERIC(10, 2) NOT NULL
);

-- Persistência definitiva dos carrinhos sob responsabilidade do serviço Java.
CREATE TABLE IF NOT EXISTS carrinhos (
    telefone VARCHAR(40) PRIMARY KEY,
    itens_json TEXT NOT NULL DEFAULT '[]',
    atualizado_em TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_produtos_nome_lower ON produtos (LOWER(nome));
CREATE INDEX IF NOT EXISTS idx_pedidos_cliente_telefone ON pedidos (cliente_telefone);

INSERT INTO categorias (nome, descricao) VALUES
    ('Hortifruti', 'Frutas e legumes'),
    ('Mercearia', 'Grãos e cereais'),
    ('Açougue', 'Carnes e aves'),
    ('Laticínios', 'Queijos e leites')
ON CONFLICT (nome) DO NOTHING;

INSERT INTO produtos (codigo_barras, nome, categoria_id, preco_venda, unidade_medida)
SELECT seed.codigo_barras, seed.nome, c.id, seed.preco_venda, seed.unidade_medida
FROM (VALUES
    ('7891000100011', 'Banana Prata', 'Hortifruti', 5.99::NUMERIC, 'KG'),
    ('7891000100028', 'Maçã Fuji', 'Hortifruti', 8.49::NUMERIC, 'KG'),
    ('7891000200018', 'Arroz Tio João 1kg', 'Mercearia', 6.50::NUMERIC, 'UN'),
    ('7891000200025', 'Feijão Carioca 1kg', 'Mercearia', 7.90::NUMERIC, 'UN'),
    ('7891000400029', 'Queijo Coalho Betânia', 'Laticínios', 42.00::NUMERIC, 'KG')
) AS seed(codigo_barras, nome, categoria_nome, preco_venda, unidade_medida)
JOIN categorias c ON c.nome = seed.categoria_nome
ON CONFLICT (codigo_barras) DO NOTHING;

INSERT INTO estoque (produto_id, quantidade_disponivel)
SELECT p.id, seed.quantidade
FROM (VALUES
    ('7891000100011', 150.000::NUMERIC),
    ('7891000100028', 80.000::NUMERIC),
    ('7891000200018', 500.000::NUMERIC),
    ('7891000200025', 350.000::NUMERIC),
    ('7891000400029', 25.000::NUMERIC)
) AS seed(codigo_barras, quantidade)
JOIN produtos p ON p.codigo_barras = seed.codigo_barras
ON CONFLICT (produto_id) DO NOTHING;

-- Ajusta sequências quando o banco recebeu IDs explícitos na carga inicial.
SELECT setval(pg_get_serial_sequence('categorias', 'id'), COALESCE((SELECT MAX(id) FROM categorias), 1), true);
SELECT setval(pg_get_serial_sequence('produtos', 'id'), COALESCE((SELECT MAX(id) FROM produtos), 1), true);
SELECT setval(pg_get_serial_sequence('estoque', 'id'), COALESCE((SELECT MAX(id) FROM estoque), 1), true);
