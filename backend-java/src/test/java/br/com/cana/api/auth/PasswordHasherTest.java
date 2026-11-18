package br.com.cana.api.auth;

import org.junit.jupiter.api.Test;
import static org.junit.jupiter.api.Assertions.*;

class PasswordHasherTest {
    private final PasswordHasher hasher = new PasswordHasher();

    @Test
    void hashesAndVerifiesPasswordWithoutStoringPlainText() {
        String encoded = hasher.hash("123");
        assertNotEquals("123", encoded);
        assertTrue(hasher.matches("123", encoded));
        assertFalse(hasher.matches("321", encoded));
    }
}
