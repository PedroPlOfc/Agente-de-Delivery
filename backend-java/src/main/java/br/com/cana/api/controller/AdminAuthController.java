package br.com.cana.api.controller;

import br.com.cana.api.auth.AdminAuthenticationService;
import br.com.cana.api.dto.AdminLoginRequest;
import org.springframework.http.HttpStatus;
import org.springframework.web.bind.annotation.*;
import java.util.Map;

@RestController
@RequestMapping("/api/admin/auth")
public class AdminAuthController {
    private final AdminAuthenticationService authentication;
    public AdminAuthController(AdminAuthenticationService authentication) { this.authentication = authentication; }

    @PostMapping("/login")
    @ResponseStatus(HttpStatus.OK)
    public Map<String, Object> login(@RequestBody AdminLoginRequest request) {
        return authentication.login(request.username(), request.password());
    }
}
