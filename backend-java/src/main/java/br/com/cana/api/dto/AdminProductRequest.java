package br.com.cana.api.dto;

import java.math.BigDecimal;

public record AdminProductRequest(
        String codigo_barras,
        String nome,
        String categoria,
        BigDecimal preco_venda,
        String unidade_medida,
        BigDecimal estoque_minimo,
        BigDecimal quantidade_inicial
) {}
