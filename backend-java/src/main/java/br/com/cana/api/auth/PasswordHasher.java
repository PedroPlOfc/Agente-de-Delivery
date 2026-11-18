package br.com.cana.api.auth;

import org.springframework.stereotype.Component;
import javax.crypto.SecretKeyFactory;
import javax.crypto.spec.PBEKeySpec;
import java.security.MessageDigest;
import java.security.SecureRandom;
import java.util.Base64;

@Component
public class PasswordHasher {
    private static final int ITERATIONS = 160_000;
    private static final int KEY_BITS = 256;
    private final SecureRandom random = new SecureRandom();

    public String hash(String password) {
        byte[] salt = new byte[16];
        random.nextBytes(salt);
        byte[] derived = derive(password, salt, ITERATIONS);
        return "pbkdf2$" + ITERATIONS + "$" + Base64.getEncoder().withoutPadding().encodeToString(salt)
                + "$" + Base64.getEncoder().withoutPadding().encodeToString(derived);
    }

    public boolean matches(String password, String encoded) {
        try {
            String[] parts = encoded.split("\\$", -1);
            if (parts.length != 4 || !parts[0].equals("pbkdf2")) return false;
            int iterations = Integer.parseInt(parts[1]);
            if (iterations < 100_000 || iterations > 1_000_000) return false;
            byte[] salt = Base64.getDecoder().decode(parts[2]);
            byte[] expected = Base64.getDecoder().decode(parts[3]);
            return MessageDigest.isEqual(expected, derive(password, salt, iterations));
        } catch (RuntimeException ex) {
            return false;
        }
    }

    private byte[] derive(String password, byte[] salt, int iterations) {
        PBEKeySpec spec = new PBEKeySpec(password.toCharArray(), salt, iterations, KEY_BITS);
        try {
            return SecretKeyFactory.getInstance("PBKDF2WithHmacSHA256").generateSecret(spec).getEncoded();
        } catch (Exception ex) {
            throw new IllegalStateException("Não foi possível processar a senha.", ex);
        } finally {
            spec.clearPassword();
        }
    }
}
