package br.com.cana.api.config;

import jakarta.servlet.FilterChain;
import jakarta.servlet.ServletException;
import jakarta.servlet.http.HttpServletRequest;
import jakarta.servlet.http.HttpServletResponse;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.stereotype.Component;
import org.springframework.web.filter.OncePerRequestFilter;
import java.io.IOException;
import java.nio.charset.StandardCharsets;
import java.security.MessageDigest;

@Component
public class InternalTokenFilter extends OncePerRequestFilter {
    @Value("${cana.security.internal-token:}")
    private String configuredToken;

    @Override
    protected boolean shouldNotFilter(HttpServletRequest request) {
        return !request.getRequestURI().startsWith("/api/") || request.getRequestURI().equals("/api/health");
    }

    @Override
    protected void doFilterInternal(HttpServletRequest request, HttpServletResponse response, FilterChain chain)
            throws ServletException, IOException {
        // Em desenvolvimento local o token pode ficar vazio. Em produção, configure-o obrigatoriamente.
        if (configuredToken == null || configuredToken.isBlank()) {
            chain.doFilter(request, response);
            return;
        }

        String received = request.getHeader("X-Internal-Token");
        boolean valid = received != null && MessageDigest.isEqual(
                configuredToken.getBytes(StandardCharsets.UTF_8), received.getBytes(StandardCharsets.UTF_8));
        if (!valid) {
            response.setStatus(HttpServletResponse.SC_UNAUTHORIZED);
            response.setContentType("application/json");
            response.getWriter().write("{\"detail\":\"Token interno inválido ou ausente\"}");
            return;
        }
        chain.doFilter(request, response);
    }
}
