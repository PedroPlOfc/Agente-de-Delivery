package br.com.cana.api.config;

import br.com.cana.api.auth.AdminTokenService;
import br.com.cana.api.entity.AdminUserEntity;
import br.com.cana.api.repository.AdminUserRepository;
import jakarta.servlet.FilterChain;
import jakarta.servlet.ServletException;
import jakarta.servlet.http.HttpServletRequest;
import jakarta.servlet.http.HttpServletResponse;
import org.springframework.stereotype.Component;
import org.springframework.web.filter.OncePerRequestFilter;
import java.io.IOException;

@Component
public class AdminTokenFilter extends OncePerRequestFilter {
    public static final String USER_ATTRIBUTE = "canaAdminUser";
    private final AdminTokenService tokens;
    private final AdminUserRepository users;

    public AdminTokenFilter(AdminTokenService tokens, AdminUserRepository users) {
        this.tokens = tokens;
        this.users = users;
    }

    @Override
    protected boolean shouldNotFilter(HttpServletRequest request) {
        String uri = request.getRequestURI();
        return !uri.startsWith("/api/admin/") || uri.equals("/api/admin/auth/login");
    }

    @Override
    protected void doFilterInternal(HttpServletRequest request, HttpServletResponse response, FilterChain chain)
            throws ServletException, IOException {
        String authorization = request.getHeader("Authorization");
        if (authorization == null || !authorization.startsWith("Bearer ")) {
            unauthorized(response);
            return;
        }
        AdminTokenService.Claims claims = tokens.verify(authorization.substring(7).trim());
        if (claims == null) {
            unauthorized(response);
            return;
        }
        AdminUserEntity user = users.findByUsernameIgnoreCase(claims.username()).orElse(null);
        if (user == null || !user.isAtivo() || !user.getPapel().equals(claims.role())) {
            unauthorized(response);
            return;
        }
        request.setAttribute(USER_ATTRIBUTE, user);
        chain.doFilter(request, response);
    }

    private void unauthorized(HttpServletResponse response) throws IOException {
        response.setStatus(HttpServletResponse.SC_UNAUTHORIZED);
        response.setContentType("application/json");
        response.setCharacterEncoding("UTF-8");
        response.getWriter().write("{\"detail\":\"Sessão administrativa inválida ou expirada. Entre novamente.\"}");
    }
}
