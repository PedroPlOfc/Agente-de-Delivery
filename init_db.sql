-- Remove tabelas antigas se existirem
DROP TABLE IF EXISTS itens_pedido CASCADE;
DROP TABLE IF EXISTS pedidos CASCADE;
DROP TABLE IF EXISTS estoque CASCADE;
DROP TABLE IF EXISTS produtos CASCADE;
DROP TABLE IF EXISTS categorias CASCADE;

-- 1. Categorias
CREATE TABLE categorias (
    id SERIAL PRIMARY KEY,
    nome VARCHAR(100) NOT NULL UNIQUE,
    descricao TEXT,
    criado_em TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- 2. Produtos
CREATE TABLE produtos (
    id SERIAL PRIMARY KEY,
    codigo_barras VARCHAR(20) UNIQUE NOT NULL,
    nome VARCHAR(150) NOT NULL,
    categoria_id INT NOT NULL REFERENCES categorias(id) ON DELETE RESTRICT,
    preco_venda NUMERIC(10, 2) NOT NULL CHECK (preco_venda >= 0),
    unidade_medida VARCHAR(10) NOT NULL DEFAULT 'UN',
    ativo BOOLEAN NOT NULL DEFAULT TRUE,
    criado_em TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- 3. Estoque
CREATE TABLE estoque (
    id SERIAL PRIMARY KEY,
    produto_id INT NOT NULL UNIQUE REFERENCES produtos(id) ON DELETE CASCADE,
    quantidade_disponivel NUMERIC(10, 3) NOT NULL DEFAULT 0.000,
    atualizado_em TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- 4. Pedidos
CREATE TABLE pedidos (
    id SERIAL PRIMARY KEY,
    cliente_telefone VARCHAR(20) NOT NULL,
    cliente_nome VARCHAR(100),
    status VARCHAR(30) NOT NULL DEFAULT 'PENDENTE',
    forma_pagamento VARCHAR(50),
    valor_total NUMERIC(10, 2) NOT NULL DEFAULT 0.00,
    origem VARCHAR(20) NOT NULL DEFAULT 'WHATSAPP',
    criado_em TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- 5. Itens do Pedido
CREATE TABLE itens_pedido (
    id SERIAL PRIMARY KEY,
    pedido_id INT NOT NULL REFERENCES pedidos(id) ON DELETE CASCADE,
    produto_id INT NOT NULL REFERENCES produtos(id) ON DELETE RESTRICT,
    quantidade NUMERIC(10, 3) NOT NULL CHECK (quantidade > 0),
    preco_unitario NUMERIC(10, 2) NOT NULL,
    subtotal NUMERIC(10, 2) NOT NULL
);

-- Carga inicial de dados de teste (Sacolão da Economia)
INSERT INTO categorias (id, nome, descricao) VALUES
(1, 'Hortifruti', 'Frutas e legumes'),
(2, 'Mercearia', 'Grãos e cereais'),
(3, 'Açougue', 'Carnes e aves'),
(4, 'Laticínios', 'Queijos e leites');

INSERT INTO produtos (id, codigo_barras, nome, categoria_id, preco_venda, unidade_medida) VALUES
(1, '7891000100011', 'Banana Prata', 1, 5.99, 'KG'),
(2, '7891000100028', 'Maçã Fuji', 1, 8.49, 'KG'),
(3, '7891000200018', 'Arroz Tio João 1kg', 2, 6.50, 'UN'),
(4, '7891000200025', 'Feijão Carioca 1kg', 2, 7.90, 'UN'),
(5, '7891000400029', 'Queijo Coalho Betânia', 4, 42.00, 'KG');

INSERT INTO estoque (produto_id, quantidade_disponivel) VALUES
(1, 150.000), (2, 80.000), (3, 500.000), (4, 350.000), (5, 25.000);