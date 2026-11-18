package br.com.cana.api.entity;

import jakarta.persistence.*;
import java.math.BigDecimal;
import java.time.OffsetDateTime;

@Entity
@Table(name = "movimentacoes_estoque")
public class StockMovementEntity {
    @Id @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;
    @ManyToOne(fetch = FetchType.LAZY, optional = false)
    @JoinColumn(name = "produto_id", nullable = false)
    private ProductEntity produto;
    @Column(nullable = false, length = 30)
    private String tipo;
    @Column(nullable = false, precision = 10, scale = 3)
    private BigDecimal quantidade;
    @Column(name = "saldo_anterior", nullable = false, precision = 10, scale = 3)
    private BigDecimal saldoAnterior;
    @Column(name = "saldo_posterior", nullable = false, precision = 10, scale = 3)
    private BigDecimal saldoPosterior;
    @Column(nullable = false, length = 255)
    private String motivo;
    @Column(nullable = false, length = 60)
    private String usuario;
    @Column(name = "criado_em", nullable = false)
    private OffsetDateTime criadoEm = OffsetDateTime.now();

    protected StockMovementEntity() {}

    public StockMovementEntity(ProductEntity produto, String tipo, BigDecimal quantidade,
                               BigDecimal saldoAnterior, BigDecimal saldoPosterior,
                               String motivo, String usuario) {
        this.produto = produto;
        this.tipo = tipo;
        this.quantidade = quantidade;
        this.saldoAnterior = saldoAnterior;
        this.saldoPosterior = saldoPosterior;
        this.motivo = motivo;
        this.usuario = usuario;
        this.criadoEm = OffsetDateTime.now();
    }

    public Long getId() { return id; }
    public ProductEntity getProduto() { return produto; }
    public String getTipo() { return tipo; }
    public BigDecimal getQuantidade() { return quantidade; }
    public BigDecimal getSaldoAnterior() { return saldoAnterior; }
    public BigDecimal getSaldoPosterior() { return saldoPosterior; }
    public String getMotivo() { return motivo; }
    public String getUsuario() { return usuario; }
    public OffsetDateTime getCriadoEm() { return criadoEm; }
}
