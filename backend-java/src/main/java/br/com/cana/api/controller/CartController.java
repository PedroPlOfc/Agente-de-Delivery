package br.com.cana.api.controller;

import br.com.cana.api.dto.CartRequest;
import br.com.cana.api.service.CartService;
import jakarta.validation.Valid;
import org.springframework.web.bind.annotation.*;
import java.util.List;
import java.util.Map;

@RestController
@RequestMapping("/api/carts")
public class CartController {
    private final CartService service;
    public CartController(CartService service) { this.service = service; }

    @GetMapping("/{phone}")
    public Map<String, Object> carregar(@PathVariable String phone) {
        return Map.of("telefone", phone, "itens", service.carregar(phone));
    }

    @PutMapping("/{phone}")
    public Map<String, Object> salvar(@PathVariable String phone, @Valid @RequestBody CartRequest request) {
        List<Map<String, Object>> items = service.salvar(phone, request.itens());
        return Map.of("telefone", phone, "itens", items);
    }

    @DeleteMapping("/{phone}")
    public Map<String, String> limpar(@PathVariable String phone) {
        service.limpar(phone);
        return Map.of("status", "deleted");
    }
}
