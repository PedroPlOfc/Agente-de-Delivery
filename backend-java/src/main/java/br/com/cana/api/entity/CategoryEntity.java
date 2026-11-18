package br.com.cana.api.entity;

import jakarta.persistence.*;

@Entity
@Table(name = "categorias")
public class CategoryEntity {
    @Id @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Integer id;

    @Column(nullable = false, unique = true, length = 100)
    private String nome;

    @Column(columnDefinition = "text")
    private String descricao;

    protected CategoryEntity() {}

    public CategoryEntity(String nome, String descricao) {
        this.nome = nome;
        this.descricao = descricao;
    }

    public Integer getId() { return id; }
    public String getNome() { return nome; }
}
