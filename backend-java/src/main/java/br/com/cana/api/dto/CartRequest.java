package br.com.cana.api.dto;

import jakarta.validation.constraints.NotNull;
import java.util.List;
import java.util.Map;

public record CartRequest(@NotNull List<Map<String, Object>> itens) {}
