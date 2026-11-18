package br.com.cana.api.auth;

import br.com.cana.api.entity.AdminUserEntity;
import org.junit.jupiter.api.Test;
import static org.junit.jupiter.api.Assertions.*;

class AdminTokenServiceTest {
    @Test
    void issuesVerifiableTokenAndRejectsTampering() {
        AdminTokenService service = new AdminTokenService("test-secret-that-is-long-enough-for-hmac-signing");
        AdminUserEntity user = new AdminUserEntity("nicolas", "Nicolas", "ADMIN", "hash");
        String token = service.issue(user);
        AdminTokenService.Claims claims = service.verify(token);
        assertNotNull(claims);
        assertEquals("nicolas", claims.username());
        assertEquals("ADMIN", claims.role());
        assertNull(service.verify(token + "x"));
    }
}
