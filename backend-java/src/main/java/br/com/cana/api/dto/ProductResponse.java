package br.com.cana.api.dto;

import java.math.BigDecimal;

public record ProductResponse(
    Integer id,
    String codigo_barras,
    String nome,
    String categoria,
    BigDecimal preco_venda,
    String unidade_medida,
    BigDecimal quantidade_disponivel
) {}
