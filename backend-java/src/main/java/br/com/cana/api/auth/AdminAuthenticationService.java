package br.com.cana.api.auth;

import br.com.cana.api.entity.AdminUserEntity;
import br.com.cana.api.repository.AdminUserRepository;
import org.springframework.http.HttpStatus;
import org.springframework.stereotype.Service;
import org.springframework.web.server.ResponseStatusException;
import java.util.Map;

@Service
public class AdminAuthenticationService {
    private final AdminUserRepository users;
    private final PasswordHasher passwords;
    private final AdminTokenService tokens;

    public AdminAuthenticationService(AdminUserRepository users, PasswordHasher passwords, AdminTokenService tokens) {
        this.users = users;
        this.passwords = passwords;
        this.tokens = tokens;
    }

    public Map<String, Object> login(String username, String password) {
        if (username == null || password == null) throw invalidLogin();
        AdminUserEntity user = users.findByUsernameIgnoreCase(username.trim())
                .filter(AdminUserEntity::isAtivo)
                .filter(u -> passwords.matches(password, u.getPasswordHash()))
                .orElseThrow(this::invalidLogin);
        return Map.of(
                "token", tokens.issue(user),
                "expires_in", 28_800,
                "user", Map.of("username", user.getUsername(), "nome", user.getNome(), "papel", user.getPapel())
        );
    }

    private ResponseStatusException invalidLogin() {
        return new ResponseStatusException(HttpStatus.UNAUTHORIZED, "Usuário ou senha incorretos.");
    }
}
