package br.com.cana.api.service;

import br.com.cana.api.dto.OrderRequest;
import br.com.cana.api.dto.OrderResponse;
import br.com.cana.api.entity.OrderEntity;
import br.com.cana.api.entity.OrderItemEntity;
import br.com.cana.api.entity.ProductEntity;
import br.com.cana.api.repository.OrderRepository;
import br.com.cana.api.repository.ProductRepository;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;
import java.util.List;

@Service
public class OrderService {
    private final OrderRepository orders;
    private final ProductRepository products;

    public OrderService(OrderRepository orders, ProductRepository products) {
        this.orders = orders;
        this.products = products;
    }

    @Transactional
    public OrderResponse criar(OrderRequest request) {
        String phone = request.cliente_telefone().replaceAll("\\D", "");
        if (phone.isBlank()) throw new IllegalArgumentException("Telefone do cliente inválido.");
        OrderEntity order = new OrderEntity(
                phone, request.cliente_nome(), request.forma_pagamento(),
                request.origem() == null || request.origem().isBlank() ? "WHATSAPP" : request.origem());

        for (OrderRequest.OrderItemRequest line : request.itens()) {
            ProductEntity product = resolveProduct(line);
            order.adicionarItem(new OrderItemEntity(product, line.quantidade(), line.unidade_medida()));
        }
        return toResponse(orders.save(order));
    }

    private ProductEntity resolveProduct(OrderRequest.OrderItemRequest line) {
        if (line.produto_id() != null) {
            return products.buscarAtivoPorId(line.produto_id())
                    .orElseThrow(() -> new ResourceNotFoundException("Produto " + line.produto_id() + " não encontrado."));
        }
        if (line.produto() != null && !line.produto().isBlank()) {
            return products.buscarNomeExato(line.produto().trim())
                    .orElseThrow(() -> new ResourceNotFoundException("Produto não cadastrado: " + line.produto()));
        }
        throw new IllegalArgumentException("Cada item precisa informar produto_id ou produto.");
    }

    private OrderResponse toResponse(OrderEntity order) {
        List<OrderResponse.OrderLineResponse> lines = order.getItens().stream().map(line ->
                new OrderResponse.OrderLineResponse(
                        line.getProduto().getId(), line.getProduto().getNome(), line.getQuantidade(),
                        line.getProduto().getUnidadeMedida(), line.getPrecoUnitario(), line.getSubtotal())).toList();
        return new OrderResponse(order.getId(), order.getClienteTelefone(), order.getClienteNome(),
                order.getStatus(), order.getFormaPagamento(), order.getOrigem(), order.getValorTotal(),
                order.getCriadoEm(), lines);
    }
}
