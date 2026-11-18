package br.com.cana.api.controller;

import br.com.cana.api.dto.ProductResponse;
import br.com.cana.api.service.ProductService;
import org.springframework.web.bind.annotation.*;
import java.math.BigDecimal;
import java.util.List;

@RestController
@RequestMapping("/api/products")
public class ProductController {
    private final ProductService service;
    public ProductController(ProductService service) { this.service = service; }

    @GetMapping
    public List<ProductResponse> buscar(@RequestParam(defaultValue = "") String query) {
        return service.buscar(query);
    }

    @GetMapping("/barcode/{barcode}")
    public ProductResponse barcode(@PathVariable String barcode) { return service.buscarPorCodigo(barcode); }

    @GetMapping("/{id}")
    public ProductResponse porId(@PathVariable Integer id) { return service.buscarPorId(id); }

    @GetMapping("/{id}/stock")
    public java.util.Map<String, Object> estoque(@PathVariable Integer id) {
        BigDecimal quantity = service.consultarEstoque(id);
        return java.util.Map.of("produto_id", id, "quantidade_disponivel", quantity);
    }
}
