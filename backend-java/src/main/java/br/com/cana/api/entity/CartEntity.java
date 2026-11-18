package br.com.cana.api.entity;

import jakarta.persistence.*;
import java.time.OffsetDateTime;

@Entity
@Table(name = "carrinhos")
public class CartEntity {
    @Id
    @Column(length = 40)
    private String telefone;

    @Column(name = "itens_json", nullable = false, columnDefinition = "text")
    private String itensJson;

    @Column(name = "atualizado_em", nullable = false)
    private OffsetDateTime atualizadoEm;

    protected CartEntity() {}

    public CartEntity(String telefone, String itensJson) {
        this.telefone = telefone;
        this.itensJson = itensJson;
        this.atualizadoEm = OffsetDateTime.now();
    }

    public String getTelefone() { return telefone; }
    public String getItensJson() { return itensJson; }
    public void setItensJson(String itensJson) { this.itensJson = itensJson; this.atualizadoEm = OffsetDateTime.now(); }
}
