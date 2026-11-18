package br.com.cana.api.dto;

import java.math.BigDecimal;

public record StockMovementRequest(String tipo, BigDecimal quantidade, String motivo) {}
