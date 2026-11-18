package br.com.cana.api.auth;

import br.com.cana.api.entity.AdminUserEntity;
import br.com.cana.api.repository.AdminUserRepository;
import org.springframework.boot.CommandLineRunner;
import org.springframework.stereotype.Component;

@Component
public class AdminUserSeeder implements CommandLineRunner {
    private final AdminUserRepository users;
    private final PasswordHasher passwords;

    public AdminUserSeeder(AdminUserRepository users, PasswordHasher passwords) {
        this.users = users;
        this.passwords = passwords;
    }

    @Override
    public void run(String... args) {
        // Apenas estas duas contas iniciais são criadas. Não há endpoint público de cadastro.
        if (!users.existsByUsernameIgnoreCase("nicolas")) {
            users.save(new AdminUserEntity("nicolas", "Nicolas", "ADMIN", passwords.hash("123")));
        }
        if (!users.existsByUsernameIgnoreCase("pedro.lucas")) {
            users.save(new AdminUserEntity("pedro.lucas", "Pedro Lucas", "STAFF", passwords.hash("123")));
        }
    }
}
