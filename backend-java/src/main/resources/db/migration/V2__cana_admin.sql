-- CANA Admin: migration non-destructive. Never drops existing business data.
ALTER TABLE produtos
    ADD COLUMN IF NOT EXISTS estoque_minimo NUMERIC(10, 3) NOT NULL DEFAULT 5.000;

ALTER TABLE pedidos
    ADD COLUMN IF NOT EXISTS estoque_baixado BOOLEAN NOT NULL DEFAULT FALSE;

CREATE TABLE IF NOT EXISTS admin_users (
    id BIGSERIAL PRIMARY KEY,
    username VARCHAR(60) NOT NULL UNIQUE,
    nome VARCHAR(120) NOT NULL,
    papel VARCHAR(20) NOT NULL CHECK (papel IN ('ADMIN', 'STAFF')),
    password_hash VARCHAR(255) NOT NULL,
    ativo BOOLEAN NOT NULL DEFAULT TRUE,
    criado_em TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS movimentacoes_estoque (
    id BIGSERIAL PRIMARY KEY,
    produto_id INTEGER NOT NULL REFERENCES produtos(id) ON DELETE RESTRICT,
    tipo VARCHAR(30) NOT NULL CHECK (tipo IN ('ENTRADA', 'SAIDA', 'AJUSTE', 'INVENTARIO_INICIAL')),
    quantidade NUMERIC(10, 3) NOT NULL CHECK (quantidade >= 0),
    saldo_anterior NUMERIC(10, 3) NOT NULL,
    saldo_posterior NUMERIC(10, 3) NOT NULL,
    motivo VARCHAR(255) NOT NULL,
    usuario VARCHAR(60) NOT NULL,
    criado_em TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_movimentacoes_estoque_criado
    ON movimentacoes_estoque (criado_em DESC);
CREATE INDEX IF NOT EXISTS idx_movimentacoes_estoque_produto
    ON movimentacoes_estoque (produto_id, criado_em DESC);

INSERT INTO categorias (nome, descricao) VALUES
    ('Padaria', 'Pães e produtos de padaria'),
    ('Bebidas', 'Água e bebidas'),
    ('Limpeza', 'Produtos de limpeza doméstica')
ON CONFLICT (nome) DO NOTHING;

-- Mantém os cinco produtos iniciais da V1 e completa o catálogo até 30 ativos.
-- Os preços e quantidades iniciais são valores demonstrativos e devem ser revisados no painel.
WITH seed(codigo_barras, nome, categoria_nome, preco_venda, unidade_medida, quantidade, minimo) AS (
    VALUES
    ('CANA0006', 'Tomate', 'Hortifruti', 7.99::NUMERIC, 'KG', 35.000::NUMERIC, 8.000::NUMERIC),
    ('CANA0007', 'Batata Inglesa', 'Hortifruti', 5.49::NUMERIC, 'KG', 45.000::NUMERIC, 10.000::NUMERIC),
    ('CANA0008', 'Cebola', 'Hortifruti', 4.99::NUMERIC, 'KG', 30.000::NUMERIC, 8.000::NUMERIC),
    ('CANA0009', 'Cenoura', 'Hortifruti', 5.99::NUMERIC, 'KG', 25.000::NUMERIC, 8.000::NUMERIC),
    ('CANA0010', 'Laranja Pera', 'Hortifruti', 4.49::NUMERIC, 'KG', 40.000::NUMERIC, 10.000::NUMERIC),
    ('CANA0011', 'Mamão Papaya', 'Hortifruti', 7.49::NUMERIC, 'KG', 18.000::NUMERIC, 5.000::NUMERIC),
    ('CANA0012', 'Melancia', 'Hortifruti', 3.49::NUMERIC, 'KG', 60.000::NUMERIC, 10.000::NUMERIC),
    ('CANA0013', 'Alface Crespa', 'Hortifruti', 3.50::NUMERIC, 'UN', 20.000::NUMERIC, 5.000::NUMERIC),
    ('CANA0014', 'Alho', 'Hortifruti', 29.90::NUMERIC, 'KG', 8.000::NUMERIC, 2.000::NUMERIC),
    ('CANA0015', 'Limão Tahiti', 'Hortifruti', 4.99::NUMERIC, 'KG', 20.000::NUMERIC, 5.000::NUMERIC),
    ('CANA0016', 'Óleo de Soja 900ml', 'Mercearia', 7.49::NUMERIC, 'UN', 48.000::NUMERIC, 10.000::NUMERIC),
    ('CANA0017', 'Açúcar Refinado 1kg', 'Mercearia', 4.79::NUMERIC, 'UN', 60.000::NUMERIC, 12.000::NUMERIC),
    ('CANA0018', 'Café em Pó 250g', 'Mercearia', 13.90::NUMERIC, 'UN', 40.000::NUMERIC, 10.000::NUMERIC),
    ('CANA0019', 'Macarrão Espaguete 500g', 'Mercearia', 4.29::NUMERIC, 'UN', 55.000::NUMERIC, 12.000::NUMERIC),
    ('CANA0020', 'Farinha de Mandioca 1kg', 'Mercearia', 7.90::NUMERIC, 'UN', 28.000::NUMERIC, 8.000::NUMERIC),
    ('CANA0021', 'Sal Refinado 1kg', 'Mercearia', 2.99::NUMERIC, 'UN', 40.000::NUMERIC, 10.000::NUMERIC),
    ('CANA0022', 'Leite Integral 1L', 'Laticínios', 5.49::NUMERIC, 'UN', 72.000::NUMERIC, 15.000::NUMERIC),
    ('CANA0023', 'Manteiga 200g', 'Laticínios', 10.90::NUMERIC, 'UN', 24.000::NUMERIC, 6.000::NUMERIC),
    ('CANA0024', 'Ovos Brancos (Dúzia)', 'Laticínios', 12.90::NUMERIC, 'UN', 30.000::NUMERIC, 8.000::NUMERIC),
    ('CANA0025', 'Peito de Frango', 'Açougue', 17.90::NUMERIC, 'KG', 25.000::NUMERIC, 6.000::NUMERIC),
    ('CANA0026', 'Carne Moída', 'Açougue', 29.90::NUMERIC, 'KG', 18.000::NUMERIC, 5.000::NUMERIC),
    ('CANA0027', 'Sardinha em Lata', 'Mercearia', 6.49::NUMERIC, 'UN', 36.000::NUMERIC, 8.000::NUMERIC),
    ('CANA0028', 'Pão de Forma', 'Padaria', 8.90::NUMERIC, 'UN', 20.000::NUMERIC, 5.000::NUMERIC),
    ('CANA0029', 'Água Mineral 1,5L', 'Bebidas', 3.49::NUMERIC, 'UN', 48.000::NUMERIC, 10.000::NUMERIC),
    ('CANA0030', 'Detergente Neutro 500ml', 'Limpeza', 2.79::NUMERIC, 'UN', 40.000::NUMERIC, 10.000::NUMERIC)
), slots AS (
    SELECT GREATEST(0, 30 - COUNT(*))::INTEGER AS vagas FROM produtos WHERE ativo = TRUE
), elegiveis AS (
    SELECT seed.* FROM seed
    WHERE NOT EXISTS (SELECT 1 FROM produtos p WHERE p.codigo_barras = seed.codigo_barras)
    ORDER BY seed.nome
    LIMIT (SELECT vagas FROM slots)
), inseridos AS (
    INSERT INTO produtos (codigo_barras, nome, categoria_id, preco_venda, unidade_medida, estoque_minimo)
    SELECT e.codigo_barras, e.nome, c.id, e.preco_venda, e.unidade_medida, e.minimo
    FROM elegiveis e JOIN categorias c ON c.nome = e.categoria_nome
    ON CONFLICT (codigo_barras) DO NOTHING
    RETURNING id, codigo_barras
), produtos_seed AS (
    -- Data-modifying CTE rows are consumed through RETURNING; the UNION also includes products
    -- that already existed before this migration and may need their stock row created.
    SELECT p.id, p.codigo_barras
    FROM produtos p JOIN seed s ON s.codigo_barras = p.codigo_barras
    UNION
    SELECT i.id, i.codigo_barras FROM inseridos i
)
INSERT INTO estoque (produto_id, quantidade_disponivel)
SELECT ps.id, s.quantidade
FROM produtos_seed ps
JOIN seed s ON s.codigo_barras = ps.codigo_barras
ON CONFLICT (produto_id) DO NOTHING;

-- Registra os saldos de abertura dos produtos de demonstração apenas uma vez.
INSERT INTO movimentacoes_estoque
    (produto_id, tipo, quantidade, saldo_anterior, saldo_posterior, motivo, usuario)
SELECT p.id, 'INVENTARIO_INICIAL', e.quantidade_disponivel, 0, e.quantidade_disponivel,
       'Carga inicial do catálogo de demonstração', 'sistema'
FROM produtos p
JOIN estoque e ON e.produto_id = p.id
WHERE (p.codigo_barras LIKE 'CANA%' OR p.codigo_barras IN ('7891000100011','7891000100028','7891000200018','7891000200025','7891000400029'))
  AND NOT EXISTS (
      SELECT 1 FROM movimentacoes_estoque m
      WHERE m.produto_id = p.id AND m.tipo = 'INVENTARIO_INICIAL'
  );

SELECT setval(pg_get_serial_sequence('produtos', 'id'), COALESCE((SELECT MAX(id) FROM produtos), 1), true);
SELECT setval(pg_get_serial_sequence('estoque', 'id'), COALESCE((SELECT MAX(id) FROM estoque), 1), true);
