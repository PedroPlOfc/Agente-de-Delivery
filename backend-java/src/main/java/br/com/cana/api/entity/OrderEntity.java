package br.com.cana.api.entity;

import jakarta.persistence.*;
import java.math.BigDecimal;
import java.time.OffsetDateTime;
import java.util.ArrayList;
import java.util.List;

@Entity
@Table(name = "pedidos")
public class OrderEntity {
    @Id @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Integer id;

    @Column(name = "cliente_telefone", nullable = false, length = 20)
    private String clienteTelefone;

    @Column(name = "cliente_nome", length = 100)
    private String clienteNome;

    @Column(nullable = false, length = 30)
    private String status = "PENDENTE";

    @Column(name = "forma_pagamento", length = 50)
    private String formaPagamento;

    @Column(name = "valor_total", nullable = false, precision = 10, scale = 2)
    private BigDecimal valorTotal = BigDecimal.ZERO;

    @Column(nullable = false, length = 20)
    private String origem = "WHATSAPP";

    @Column(name = "criado_em")
    private OffsetDateTime criadoEm = OffsetDateTime.now();

    @Column(name = "estoque_baixado", nullable = false)
    private boolean estoqueBaixado = false;

    @OneToMany(mappedBy = "pedido", cascade = CascadeType.ALL, orphanRemoval = true)
    private List<OrderItemEntity> itens = new ArrayList<>();

    protected OrderEntity() {}

    public OrderEntity(String telefone, String nome, String pagamento, String origem) {
        this.clienteTelefone = telefone;
        this.clienteNome = nome;
        this.formaPagamento = pagamento;
        this.origem = origem;
    }

    public void adicionarItem(OrderItemEntity item) {
        itens.add(item);
        item.setPedido(this);
        valorTotal = valorTotal.add(item.getSubtotal());
    }

    public Integer getId() { return id; }
    public String getClienteTelefone() { return clienteTelefone; }
    public String getClienteNome() { return clienteNome; }
    public String getStatus() { return status; }
    public String getFormaPagamento() { return formaPagamento; }
    public BigDecimal getValorTotal() { return valorTotal; }
    public String getOrigem() { return origem; }
    public OffsetDateTime getCriadoEm() { return criadoEm; }
    public List<OrderItemEntity> getItens() { return itens; }
    public boolean isEstoqueBaixado() { return estoqueBaixado; }
    public void setStatus(String status) { this.status = status; }
    public void setEstoqueBaixado(boolean estoqueBaixado) { this.estoqueBaixado = estoqueBaixado; }
}
