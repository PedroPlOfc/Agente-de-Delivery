package br.com.cana.api.entity;

import jakarta.persistence.*;
import java.time.OffsetDateTime;

@Entity
@Table(name = "admin_users")
public class AdminUserEntity {
    @Id @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;
    @Column(nullable = false, unique = true, length = 60)
    private String username;
    @Column(nullable = false, length = 120)
    private String nome;
    @Column(nullable = false, length = 20)
    private String papel;
    @Column(name = "password_hash", nullable = false, length = 255)
    private String passwordHash;
    @Column(nullable = false)
    private boolean ativo = true;
    @Column(name = "criado_em", nullable = false)
    private OffsetDateTime criadoEm = OffsetDateTime.now();

    protected AdminUserEntity() {}

    public AdminUserEntity(String username, String nome, String papel, String passwordHash) {
        this.username = username;
        this.nome = nome;
        this.papel = papel;
        this.passwordHash = passwordHash;
        this.ativo = true;
        this.criadoEm = OffsetDateTime.now();
    }

    public Long getId() { return id; }
    public String getUsername() { return username; }
    public String getNome() { return nome; }
    public String getPapel() { return papel; }
    public String getPasswordHash() { return passwordHash; }
    public boolean isAtivo() { return ativo; }
}
