package br.com.cana.api.dto;

import java.math.BigDecimal;
import java.time.OffsetDateTime;
import java.util.List;

public record OrderResponse(
    Integer id,
    String cliente_telefone,
    String cliente_nome,
    String status,
    String forma_pagamento,
    String origem,
    BigDecimal valor_total,
    OffsetDateTime criado_em,
    List<OrderLineResponse> itens
) {
    public record OrderLineResponse(
        Integer produto_id,
        String produto,
        BigDecimal quantidade,
        String unidade_medida,
        BigDecimal preco_unitario,
        BigDecimal subtotal
    ) {}
}
