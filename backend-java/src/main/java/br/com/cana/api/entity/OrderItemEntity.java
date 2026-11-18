package br.com.cana.api.entity;

import jakarta.persistence.*;
import java.math.BigDecimal;
import java.math.RoundingMode;
import java.text.Normalizer;
import java.util.Locale;

@Entity
@Table(name = "itens_pedido")
public class OrderItemEntity {
    @Id @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Integer id;

    @ManyToOne(fetch = FetchType.LAZY, optional = false)
    @JoinColumn(name = "pedido_id", nullable = false)
    private OrderEntity pedido;

    @ManyToOne(fetch = FetchType.LAZY, optional = false)
    @JoinColumn(name = "produto_id", nullable = false)
    private ProductEntity produto;

    @Column(nullable = false, precision = 10, scale = 3)
    private BigDecimal quantidade;

    @Column(name = "preco_unitario", nullable = false, precision = 10, scale = 2)
    private BigDecimal precoUnitario;

    @Column(nullable = false, precision = 10, scale = 2)
    private BigDecimal subtotal;

    protected OrderItemEntity() {}

    public OrderItemEntity(ProductEntity produto, BigDecimal quantidadeSolicitada, String unidadeMedida) {
        if (quantidadeSolicitada == null || quantidadeSolicitada.signum() <= 0) {
            throw new IllegalArgumentException("A quantidade solicitada deve ser maior que zero.");
        }
        this.produto = produto;
        this.precoUnitario = produto.getPrecoVenda();

        if (ehValorMonetario(unidadeMedida)) {
            // Para pedidos por valor (ex.: R$ 10 de queijo), o valor informado vira o subtotal.
            this.subtotal = quantidadeSolicitada.setScale(2, RoundingMode.HALF_UP);
            if (this.subtotal.signum() <= 0 || this.precoUnitario.signum() <= 0) {
                throw new IllegalArgumentException("Valor solicitado e preço do produto devem ser maiores que zero.");
            }
            this.quantidade = this.subtotal.divide(this.precoUnitario, 3, RoundingMode.HALF_UP);
            if (this.quantidade.signum() <= 0) {
                throw new IllegalArgumentException("O valor solicitado é menor que a menor quantidade comercializável.");
            }
        } else {
            this.quantidade = converterParaUnidadeDoCatalogo(
                    quantidadeSolicitada, unidadeMedida, produto.getUnidadeMedida());
            this.subtotal = this.precoUnitario.multiply(this.quantidade).setScale(2, RoundingMode.HALF_UP);
        }
    }

    private static boolean ehValorMonetario(String unidade) {
        String normalizada = normalizarUnidade(unidade);
        return normalizada.equals("REAL") || normalizada.equals("REAIS") || normalizada.equals("R$");
    }

    private static BigDecimal converterParaUnidadeDoCatalogo(
            BigDecimal quantidade, String unidadeSolicitada, String unidadeCatalogo) {
        String solicitada = normalizarUnidade(unidadeSolicitada);
        String catalogo = normalizarUnidade(unidadeCatalogo);

        if (solicitada.isBlank() || solicitada.equals(catalogo)) return quantidade;
        if (solicitada.equals("G") && catalogo.equals("KG")) {
            return quantidade.divide(BigDecimal.valueOf(1000), 3, RoundingMode.HALF_UP);
        }
        if (solicitada.equals("ML") && catalogo.equals("L")) {
            return quantidade.divide(BigDecimal.valueOf(1000), 3, RoundingMode.HALF_UP);
        }
        // Em catálogo, um pacote/unidade pode ser cadastrado como unidade de venda (UN).
        if (solicitada.equals("PCT") && catalogo.equals("UN")) return quantidade;

        throw new IllegalArgumentException(
                "A unidade solicitada (" + unidadeSolicitada + ") não é compatível com a unidade do produto ("
                        + unidadeCatalogo + ").");
    }

    private static String normalizarUnidade(String unidade) {
        if (unidade == null) return "";
        String texto = Normalizer.normalize(unidade.trim(), Normalizer.Form.NFD)
                .replaceAll("\\p{M}", "")
                .toUpperCase(Locale.ROOT);
        return switch (texto) {
            case "UNIDADE", "UNIDADES" -> "UN";
            case "GRAMA", "GRAMAS" -> "G";
            case "QUILO", "QUILOS", "KILO", "KILOS" -> "KG";
            case "LITRO", "LITROS" -> "L";
            case "MILILITRO", "MILILITROS" -> "ML";
            case "PACOTE", "PACOTES" -> "PCT";
            default -> texto;
        };
    }

    public void setPedido(OrderEntity pedido) { this.pedido = pedido; }
    public BigDecimal getSubtotal() { return subtotal; }
    public ProductEntity getProduto() { return produto; }
    public BigDecimal getQuantidade() { return quantidade; }
    public BigDecimal getPrecoUnitario() { return precoUnitario; }
}
