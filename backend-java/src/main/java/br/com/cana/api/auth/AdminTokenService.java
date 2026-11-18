package br.com.cana.api.auth;

import br.com.cana.api.entity.AdminUserEntity;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.stereotype.Component;
import javax.crypto.Mac;
import javax.crypto.spec.SecretKeySpec;
import java.nio.charset.StandardCharsets;
import java.security.MessageDigest;
import java.time.Instant;
import java.util.Base64;

@Component
public class AdminTokenService {
    private static final long TOKEN_LIFETIME_SECONDS = 8 * 60 * 60;
    private final byte[] secret;

    public AdminTokenService(@Value("${cana.security.admin-token-secret}") String secret) {
        if (secret == null || secret.length() < 32) {
            throw new IllegalStateException("ADMIN_TOKEN_SECRET precisa ter pelo menos 32 caracteres.");
        }
        this.secret = secret.getBytes(StandardCharsets.UTF_8);
    }

    public String issue(AdminUserEntity user) {
        long expiry = Instant.now().getEpochSecond() + TOKEN_LIFETIME_SECONDS;
        String body = user.getUsername() + ":" + user.getPapel() + ":" + expiry;
        String payload = Base64.getUrlEncoder().withoutPadding()
                .encodeToString(body.getBytes(StandardCharsets.UTF_8));
        return payload + "." + sign(payload);
    }

    public Claims verify(String token) {
        try {
            String[] parts = token.split("\\.", -1);
            if (parts.length != 2 || !MessageDigest.isEqual(
                    sign(parts[0]).getBytes(StandardCharsets.UTF_8),
                    parts[1].getBytes(StandardCharsets.UTF_8))) return null;
            String body = new String(Base64.getUrlDecoder().decode(parts[0]), StandardCharsets.UTF_8);
            String[] values = body.split(":", -1);
            if (values.length != 3) return null;
            long expiry = Long.parseLong(values[2]);
            if (expiry <= Instant.now().getEpochSecond()) return null;
            return new Claims(values[0], values[1], expiry);
        } catch (RuntimeException ex) {
            return null;
        }
    }

    private String sign(String payload) {
        try {
            Mac mac = Mac.getInstance("HmacSHA256");
            mac.init(new SecretKeySpec(secret, "HmacSHA256"));
            return Base64.getUrlEncoder().withoutPadding().encodeToString(
                    mac.doFinal(payload.getBytes(StandardCharsets.UTF_8)));
        } catch (Exception ex) {
            throw new IllegalStateException("Não foi possível assinar o token administrativo.", ex);
        }
    }

    public record Claims(String username, String role, long expiresAt) {}
}
