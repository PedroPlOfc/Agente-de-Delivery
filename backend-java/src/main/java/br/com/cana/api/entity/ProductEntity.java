package br.com.cana.api.entity;

import jakarta.persistence.*;
import java.math.BigDecimal;
import java.time.OffsetDateTime;

@Entity
@Table(name = "produtos")
public class ProductEntity {
    @Id @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Integer id;

    @Column(name = "codigo_barras", nullable = false, unique = true, length = 20)
    private String codigoBarras;

    @Column(nullable = false, length = 150)
    private String nome;

    @ManyToOne(fetch = FetchType.LAZY, optional = false)
    @JoinColumn(name = "categoria_id", nullable = false)
    private CategoryEntity categoria;

    @Column(name = "preco_venda", nullable = false, precision = 10, scale = 2)
    private BigDecimal precoVenda;

    @Column(name = "unidade_medida", nullable = false, length = 10)
    private String unidadeMedida = "UN";

    @Column(name = "estoque_minimo", nullable = false, precision = 10, scale = 3)
    private BigDecimal estoqueMinimo = BigDecimal.valueOf(5);

    @Column(nullable = false)
    private boolean ativo = true;

    @Column(name = "criado_em")
    private OffsetDateTime criadoEm;

    protected ProductEntity() {}

    public ProductEntity(String codigoBarras, String nome, CategoryEntity categoria,
                         BigDecimal precoVenda, String unidadeMedida, BigDecimal estoqueMinimo) {
        this.codigoBarras = codigoBarras;
        this.nome = nome;
        this.categoria = categoria;
        this.precoVenda = precoVenda;
        this.unidadeMedida = unidadeMedida;
        this.estoqueMinimo = estoqueMinimo == null ? BigDecimal.valueOf(5) : estoqueMinimo;
        this.ativo = true;
    }

    public void atualizar(String codigoBarras, String nome, CategoryEntity categoria,
                          BigDecimal precoVenda, String unidadeMedida, BigDecimal estoqueMinimo) {
        this.codigoBarras = codigoBarras;
        this.nome = nome;
        this.categoria = categoria;
        this.precoVenda = precoVenda;
        this.unidadeMedida = unidadeMedida;
        this.estoqueMinimo = estoqueMinimo;
    }

    public Integer getId() { return id; }
    public String getCodigoBarras() { return codigoBarras; }
    public String getNome() { return nome; }
    public CategoryEntity getCategoria() { return categoria; }
    public BigDecimal getPrecoVenda() { return precoVenda; }
    public String getUnidadeMedida() { return unidadeMedida; }
    public boolean isAtivo() { return ativo; }
    public BigDecimal getEstoqueMinimo() { return estoqueMinimo; }
}
