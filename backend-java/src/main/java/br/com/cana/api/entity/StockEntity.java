package br.com.cana.api.entity;

import jakarta.persistence.*;
import java.math.BigDecimal;
import java.time.OffsetDateTime;

@Entity
@Table(name = "estoque")
public class StockEntity {
    @Id @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Integer id;

    @OneToOne(fetch = FetchType.LAZY, optional = false)
    @JoinColumn(name = "produto_id", nullable = false, unique = true)
    private ProductEntity produto;

    @Column(name = "quantidade_disponivel", nullable = false, precision = 10, scale = 3)
    private BigDecimal quantidadeDisponivel = BigDecimal.ZERO;

    @Column(name = "atualizado_em")
    private OffsetDateTime atualizadoEm;

    protected StockEntity() {}

    public StockEntity(ProductEntity produto, BigDecimal quantidadeDisponivel) {
        this.produto = produto;
        this.quantidadeDisponivel = quantidadeDisponivel == null ? BigDecimal.ZERO : quantidadeDisponivel;
        this.atualizadoEm = OffsetDateTime.now();
    }

    public void atualizarQuantidade(BigDecimal quantidade) {
        this.quantidadeDisponivel = quantidade;
        this.atualizadoEm = OffsetDateTime.now();
    }

    public BigDecimal getQuantidadeDisponivel() { return quantidadeDisponivel; }
}
