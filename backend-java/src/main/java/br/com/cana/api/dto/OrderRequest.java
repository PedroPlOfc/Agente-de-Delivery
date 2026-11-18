package br.com.cana.api.dto;

import jakarta.validation.Valid;
import jakarta.validation.constraints.NotBlank;
import jakarta.validation.constraints.NotEmpty;
import jakarta.validation.constraints.NotNull;
import jakarta.validation.constraints.Positive;
import java.math.BigDecimal;
import java.util.List;

public record OrderRequest(
    @NotBlank String cliente_telefone,
    String cliente_nome,
    String forma_pagamento,
    String origem,
    @NotEmpty List<@Valid OrderItemRequest> itens
) {
    public record OrderItemRequest(
        Integer produto_id,
        String produto,
        @NotNull @Positive BigDecimal quantidade,
        String unidade_medida
    ) {}
}
