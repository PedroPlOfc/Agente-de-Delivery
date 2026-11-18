package br.com.cana.api.controller;

import br.com.cana.api.dto.OrderRequest;
import br.com.cana.api.dto.OrderResponse;
import br.com.cana.api.service.OrderService;
import jakarta.validation.Valid;
import org.springframework.http.HttpStatus;
import org.springframework.web.bind.annotation.*;

@RestController
@RequestMapping("/api/orders")
public class OrderController {
    private final OrderService service;
    public OrderController(OrderService service) { this.service = service; }

    @PostMapping
    @ResponseStatus(HttpStatus.CREATED)
    public OrderResponse criar(@Valid @RequestBody OrderRequest request) {
        return service.criar(request);
    }
}
