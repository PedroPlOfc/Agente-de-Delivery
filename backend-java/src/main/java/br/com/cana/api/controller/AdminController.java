package br.com.cana.api.controller;

import br.com.cana.api.config.AdminTokenFilter;
import br.com.cana.api.dto.AdminProductRequest;
import br.com.cana.api.dto.AdminProductResponse;
import br.com.cana.api.dto.OrderStatusRequest;
import br.com.cana.api.dto.StockMovementRequest;
import br.com.cana.api.entity.AdminUserEntity;
import br.com.cana.api.service.AdminService;
import jakarta.servlet.http.HttpServletRequest;
import org.springframework.http.HttpStatus;
import org.springframework.web.bind.annotation.*;
import java.util.List;
import java.util.Map;

@RestController
@RequestMapping("/api/admin")
public class AdminController {
    private final AdminService service;
    public AdminController(AdminService service) { this.service = service; }

    @GetMapping("/dashboard")
    public Map<String, Object> dashboard() { return service.dashboard(); }

    @GetMapping("/products")
    public List<AdminProductResponse> products(@RequestParam(defaultValue = "") String query) {
        return service.listarProdutos(query);
    }

    @PostMapping("/products")
    @ResponseStatus(HttpStatus.CREATED)
    public AdminProductResponse createProduct(@RequestBody AdminProductRequest body, HttpServletRequest request) {
        AdminUserEntity user = currentUser(request);
        requireAdmin(user);
        return service.criarProduto(body, user.getUsername());
    }

    @PutMapping("/products/{id}")
    public AdminProductResponse updateProduct(@PathVariable Integer id, @RequestBody AdminProductRequest body,
                                              HttpServletRequest request) {
        requireAdmin(currentUser(request));
        return service.atualizarProduto(id, body);
    }

    @PostMapping("/products/{id}/stock-movements")
    public Map<String, Object> stockMovement(@PathVariable Integer id, @RequestBody StockMovementRequest body,
                                             HttpServletRequest request) {
        AdminUserEntity user = currentUser(request);
        return service.movimentarEstoque(id, body.tipo(), body.quantidade(), body.motivo(), user.getUsername());
    }

    @GetMapping("/stock-movements")
    public List<Map<String, Object>> stockMovements() { return service.historicoEstoque(); }

    @GetMapping("/orders")
    public List<Map<String, Object>> orders() { return service.listarPedidos(); }

    @PatchMapping("/orders/{id}/status")
    public Map<String, Object> updateOrderStatus(@PathVariable Integer id, @RequestBody OrderStatusRequest body,
                                                 HttpServletRequest request) {
        AdminUserEntity user = currentUser(request);
        return service.atualizarStatusPedido(id, body.status(), user.getUsername());
    }

    private AdminUserEntity currentUser(HttpServletRequest request) {
        Object user = request.getAttribute(AdminTokenFilter.USER_ATTRIBUTE);
        if (!(user instanceof AdminUserEntity admin)) {
            throw new org.springframework.web.server.ResponseStatusException(HttpStatus.UNAUTHORIZED, "Sessão administrativa inválida.");
        }
        return admin;
    }

    private void requireAdmin(AdminUserEntity user) {
        if (!"ADMIN".equals(user.getPapel())) {
            throw new org.springframework.web.server.ResponseStatusException(HttpStatus.FORBIDDEN,
                    "Somente o administrador pode cadastrar ou editar produtos.");
        }
    }
}
