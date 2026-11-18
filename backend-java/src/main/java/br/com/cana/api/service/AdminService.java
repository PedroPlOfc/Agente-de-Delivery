package br.com.cana.api.service;

import br.com.cana.api.dto.AdminProductRequest;
import br.com.cana.api.dto.AdminProductResponse;
import br.com.cana.api.entity.*;
import br.com.cana.api.repository.*;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;
import java.math.BigDecimal;
import java.math.RoundingMode;
import java.util.*;

@Service
public class AdminService {
    private static final BigDecimal ZERO = BigDecimal.ZERO.setScale(3);
    private final ProductRepository products;
    private final CategoryRepository categories;
    private final StockRepository stocks;
    private final StockMovementRepository movements;
    private final OrderRepository orders;

    public AdminService(ProductRepository products, CategoryRepository categories, StockRepository stocks,
                        StockMovementRepository movements, OrderRepository orders) {
        this.products = products;
        this.categories = categories;
        this.stocks = stocks;
        this.movements = movements;
        this.orders = orders;
    }

    @Transactional(readOnly = true)
    public Map<String, Object> dashboard() {
        List<ProductEntity> active = products.listarAtivos();
        long lowStock = active.stream().filter(p -> quantity(p).compareTo(p.getEstoqueMinimo()) <= 0).count();
        List<OrderEntity> allOrders = orders.findAll();
        long pending = allOrders.stream().filter(o -> "PENDENTE".equals(o.getStatus())).count();
        BigDecimal sales = allOrders.stream()
                .filter(o -> Set.of("CONFIRMADO", "EM_PREPARACAO", "SAIU_PARA_ENTREGA", "CONCLUIDO").contains(o.getStatus()))
                .map(OrderEntity::getValorTotal).filter(Objects::nonNull)
                .reduce(BigDecimal.ZERO, BigDecimal::add);
        return Map.of(
                "total_produtos", active.size(),
                "estoque_baixo", lowStock,
                "pedidos_pendentes", pending,
                "pedidos_total", allOrders.size(),
                "vendas_confirmadas", sales.setScale(2, RoundingMode.HALF_UP)
        );
    }

    @Transactional(readOnly = true)
    public List<AdminProductResponse> listarProdutos(String query) {
        String term = query == null ? "" : query.trim().toLowerCase(Locale.ROOT);
        return products.listarAtivos().stream()
                .filter(p -> term.isBlank() || p.getNome().toLowerCase(Locale.ROOT).contains(term)
                        || p.getCategoria().getNome().toLowerCase(Locale.ROOT).contains(term)
                        || p.getCodigoBarras().toLowerCase(Locale.ROOT).contains(term))
                .map(this::productResponse).toList();
    }

    @Transactional
    public AdminProductResponse criarProduto(AdminProductRequest request, String username) {
        validarProduto(request);
        String barcode = request.codigo_barras() == null || request.codigo_barras().isBlank()
                ? "CANA" + UUID.randomUUID().toString().replace("-", "").substring(0, 12).toUpperCase(Locale.ROOT)
                : request.codigo_barras().trim();
        if (products.findAll().stream().anyMatch(p -> p.getCodigoBarras().equalsIgnoreCase(barcode))) {
            throw new IllegalArgumentException("Já existe um produto com este código de barras.");
        }
        CategoryEntity category = obterCategoria(request.categoria());
        BigDecimal minimum = amountOrDefault(request.estoque_minimo(), BigDecimal.valueOf(5));
        ProductEntity product = products.save(new ProductEntity(barcode, request.nome().trim(), category,
                request.preco_venda(), normalizeUnit(request.unidade_medida()), minimum));
        BigDecimal initial = amountOrDefault(request.quantidade_inicial(), BigDecimal.ZERO).setScale(3, RoundingMode.HALF_UP);
        stocks.save(new StockEntity(product, initial));
        if (initial.signum() > 0) {
            movements.save(new StockMovementEntity(product, "INVENTARIO_INICIAL", initial, ZERO, initial,
                    "Saldo inicial do cadastro do produto", username));
        }
        return productResponse(product);
    }

    @Transactional
    public AdminProductResponse atualizarProduto(Integer id, AdminProductRequest request) {
        validarProduto(request);
        ProductEntity product = products.buscarAtivoPorId(id)
                .orElseThrow(() -> new ResourceNotFoundException("Produto não encontrado."));
        String barcode = request.codigo_barras() == null || request.codigo_barras().isBlank()
                ? product.getCodigoBarras() : request.codigo_barras().trim();
        boolean duplicate = products.findAll().stream()
                .anyMatch(p -> !p.getId().equals(id) && p.getCodigoBarras().equalsIgnoreCase(barcode));
        if (duplicate) throw new IllegalArgumentException("Já existe outro produto com este código de barras.");
        CategoryEntity category = obterCategoria(request.categoria());
        product.atualizar(barcode, request.nome().trim(), category, request.preco_venda(),
                normalizeUnit(request.unidade_medida()), amountOrDefault(request.estoque_minimo(), product.getEstoqueMinimo()));
        return productResponse(product);
    }

    @Transactional
    public Map<String, Object> movimentarEstoque(Integer productId, String type, BigDecimal quantity,
                                                  String reason, String username) {
        ProductEntity product = products.buscarAtivoPorId(productId)
                .orElseThrow(() -> new ResourceNotFoundException("Produto não encontrado."));
        return movimentar(product, type, quantity, reason, username);
    }

    private Map<String, Object> movimentar(ProductEntity product, String rawType, BigDecimal quantity,
                                           String reason, String username) {
        String type = rawType == null ? "" : rawType.trim().toUpperCase(Locale.ROOT);
        if (!Set.of("ENTRADA", "SAIDA", "AJUSTE").contains(type)) {
            throw new IllegalArgumentException("Tipo inválido. Use ENTRADA, SAIDA ou AJUSTE.");
        }
        if (quantity == null || quantity.signum() < 0 || (!type.equals("AJUSTE") && quantity.signum() == 0)) {
            throw new IllegalArgumentException("Informe uma quantidade válida maior que zero (AJUSTE aceita zero).");
        }
        BigDecimal normalizedQuantity = quantity.setScale(3, RoundingMode.HALF_UP);
        if (!type.equals("AJUSTE") && normalizedQuantity.signum() == 0) {
            throw new IllegalArgumentException("A quantidade precisa ser de pelo menos 0,001.");
        }
        if (reason == null || reason.isBlank()) throw new IllegalArgumentException("Informe o motivo da movimentação.");
        StockEntity stock = stocks.findByProdutoIdForUpdate(product.getId())
                .orElseGet(() -> stocks.save(new StockEntity(product, BigDecimal.ZERO)));
        BigDecimal before = stock.getQuantidadeDisponivel();
        BigDecimal after;
        if (type.equals("ENTRADA")) after = before.add(normalizedQuantity);
        else if (type.equals("SAIDA")) {
            after = before.subtract(normalizedQuantity);
            if (after.signum() < 0) throw new IllegalArgumentException("Estoque insuficiente. Saldo atual: " + before + ".");
        } else after = normalizedQuantity;
        after = after.setScale(3, RoundingMode.HALF_UP);
        stock.atualizarQuantidade(after);
        stocks.save(stock);
        StockMovementEntity movement = movements.save(new StockMovementEntity(product, type,
                normalizedQuantity, before, after, reason.trim(), username));
        return movementResponse(movement);
    }

    @Transactional(readOnly = true)
    public List<Map<String, Object>> historicoEstoque() {
        return movements.findTop100ByOrderByCriadoEmDesc().stream().map(this::movementResponse).toList();
    }

    @Transactional(readOnly = true)
    public List<Map<String, Object>> listarPedidos() {
        return orders.findTop100ByOrderByCriadoEmDesc().stream().map(this::orderResponse).toList();
    }

    @Transactional
    public Map<String, Object> atualizarStatusPedido(Integer id, String requestedStatus, String username) {
        String status = requestedStatus == null ? "" : requestedStatus.trim().toUpperCase(Locale.ROOT);
        Set<String> valid = Set.of("PENDENTE", "CONFIRMADO", "EM_PREPARACAO", "SAIU_PARA_ENTREGA", "CONCLUIDO", "CANCELADO");
        if (!valid.contains(status)) throw new IllegalArgumentException("Status de pedido inválido.");
        OrderEntity order = orders.findById(id).orElseThrow(() -> new ResourceNotFoundException("Pedido não encontrado."));

        if (Set.of("EM_PREPARACAO", "SAIU_PARA_ENTREGA", "CONCLUIDO").contains(status) && !order.isEstoqueBaixado()) {
            throw new IllegalArgumentException("Confirme o pedido antes de avançar o andamento; a confirmação registra a baixa do estoque.");
        }
        if (order.isEstoqueBaixado() && status.equals("PENDENTE")) {
            throw new IllegalArgumentException("Um pedido confirmado não pode voltar para PENDENTE. Cancele-o para estornar o estoque.");
        }
        if (status.equals("CONFIRMADO") && !order.isEstoqueBaixado()) {
            for (OrderItemEntity line : order.getItens()) {
                ProductEntity product = line.getProduto();
                StockEntity stock = stocks.findByProdutoIdForUpdate(product.getId())
                        .orElseThrow(() -> new IllegalArgumentException("Produto sem registro de estoque: " + product.getNome()));
                BigDecimal before = stock.getQuantidadeDisponivel();
                BigDecimal after = before.subtract(line.getQuantidade());
                if (after.signum() < 0) {
                    throw new IllegalArgumentException("Estoque insuficiente para confirmar o pedido. Produto: " + product.getNome()
                            + ". Disponível: " + before + ", solicitado: " + line.getQuantidade() + ".");
                }
                stock.atualizarQuantidade(after);
                movements.save(new StockMovementEntity(product, "SAIDA", line.getQuantidade(), before, after,
                        "Baixa automática da confirmação do pedido #" + order.getId(), username));
            }
            order.setEstoqueBaixado(true);
        } else if (status.equals("CANCELADO") && order.isEstoqueBaixado()) {
            for (OrderItemEntity line : order.getItens()) {
                ProductEntity product = line.getProduto();
                StockEntity stock = stocks.findByProdutoIdForUpdate(product.getId())
                        .orElseThrow(() -> new IllegalArgumentException("Produto sem registro de estoque: " + product.getNome()));
                BigDecimal before = stock.getQuantidadeDisponivel();
                BigDecimal after = before.add(line.getQuantidade());
                stock.atualizarQuantidade(after);
                movements.save(new StockMovementEntity(product, "ENTRADA", line.getQuantidade(), before, after,
                        "Estorno automático do pedido cancelado #" + order.getId(), username));
            }
            order.setEstoqueBaixado(false);
        }
        order.setStatus(status);
        return orderResponse(order);
    }

    private CategoryEntity obterCategoria(String name) {
        if (name == null || name.isBlank()) throw new IllegalArgumentException("Informe a categoria do produto.");
        return categories.findByNomeIgnoreCase(name.trim())
                .orElseGet(() -> categories.save(new CategoryEntity(name.trim(), "Categoria cadastrada pelo CANA Admin")));
    }

    private void validarProduto(AdminProductRequest request) {
        if (request == null || request.nome() == null || request.nome().isBlank()) throw new IllegalArgumentException("Informe o nome do produto.");
        if (request.preco_venda() == null || request.preco_venda().signum() < 0) throw new IllegalArgumentException("Informe um preço válido.");
        if (request.unidade_medida() == null || request.unidade_medida().isBlank() || request.unidade_medida().length() > 10)
            throw new IllegalArgumentException("Informe uma unidade de medida válida (até 10 caracteres).");
        if (request.estoque_minimo() != null && request.estoque_minimo().signum() < 0) throw new IllegalArgumentException("O estoque mínimo não pode ser negativo.");
        if (request.quantidade_inicial() != null && request.quantidade_inicial().signum() < 0) throw new IllegalArgumentException("O estoque inicial não pode ser negativo.");
        if (request.codigo_barras() != null && request.codigo_barras().length() > 20) throw new IllegalArgumentException("O código de barras pode ter no máximo 20 caracteres.");
    }

    private BigDecimal quantity(ProductEntity product) {
        return stocks.findByProduto_Id(product.getId()).map(StockEntity::getQuantidadeDisponivel).orElse(BigDecimal.ZERO);
    }

    private AdminProductResponse productResponse(ProductEntity p) {
        return new AdminProductResponse(p.getId(), p.getCodigoBarras(), p.getNome(), p.getCategoria().getNome(),
                p.getPrecoVenda(), p.getUnidadeMedida(), quantity(p), p.getEstoqueMinimo());
    }

    private Map<String, Object> movementResponse(StockMovementEntity m) {
        Map<String, Object> result = new LinkedHashMap<>();
        result.put("id", m.getId());
        result.put("produto_id", m.getProduto().getId());
        result.put("produto", m.getProduto().getNome());
        result.put("tipo", m.getTipo());
        result.put("quantidade", m.getQuantidade());
        result.put("saldo_anterior", m.getSaldoAnterior());
        result.put("saldo_posterior", m.getSaldoPosterior());
        result.put("motivo", m.getMotivo());
        result.put("usuario", m.getUsuario());
        result.put("criado_em", m.getCriadoEm());
        return result;
    }

    private Map<String, Object> orderResponse(OrderEntity o) {
        List<Map<String, Object>> lines = o.getItens().stream().map(line -> {
            Map<String, Object> item = new LinkedHashMap<>();
            item.put("produto", line.getProduto().getNome());
            item.put("quantidade", line.getQuantidade());
            item.put("unidade_medida", line.getProduto().getUnidadeMedida());
            item.put("subtotal", line.getSubtotal());
            return item;
        }).toList();
        Map<String, Object> result = new LinkedHashMap<>();
        result.put("id", o.getId());
        result.put("cliente_nome", o.getClienteNome() == null ? "Cliente" : o.getClienteNome());
        result.put("cliente_telefone", o.getClienteTelefone());
        result.put("status", o.getStatus());
        result.put("forma_pagamento", o.getFormaPagamento() == null ? "A definir" : o.getFormaPagamento());
        result.put("origem", o.getOrigem());
        result.put("valor_total", o.getValorTotal());
        result.put("criado_em", o.getCriadoEm());
        result.put("estoque_baixado", o.isEstoqueBaixado());
        result.put("itens", lines);
        return result;
    }

    private BigDecimal amountOrDefault(BigDecimal value, BigDecimal fallback) {
        return value == null ? fallback : value;
    }

    private String normalizeUnit(String value) {
        return value.trim().toUpperCase(Locale.ROOT);
    }
}
