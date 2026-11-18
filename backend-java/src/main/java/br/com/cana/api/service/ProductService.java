package br.com.cana.api.service;

import br.com.cana.api.dto.ProductResponse;
import br.com.cana.api.entity.ProductEntity;
import br.com.cana.api.repository.ProductRepository;
import br.com.cana.api.repository.StockRepository;
import org.springframework.stereotype.Service;
import java.math.BigDecimal;
import java.util.List;

@Service
public class ProductService {
    private final ProductRepository products;
    private final StockRepository stocks;

    public ProductService(ProductRepository products, StockRepository stocks) {
        this.products = products;
        this.stocks = stocks;
    }

    public List<ProductResponse> buscar(String termo) {
        String query = termo == null ? "" : termo.trim();
        if (query.isEmpty()) return List.of();
        return products.buscarPorNome(query).stream().map(this::toResponse).toList();
    }

    public ProductResponse buscarPorCodigo(String codigo) {
        return products.buscarPorCodigo(codigo)
                .map(this::toResponse)
                .orElseThrow(() -> new ResourceNotFoundException("Produto não encontrado para o código informado."));
    }

    public ProductResponse buscarPorId(Integer id) {
        return products.buscarAtivoPorId(id)
                .map(this::toResponse)
                .orElseThrow(() -> new ResourceNotFoundException("Produto não encontrado."));
    }

    public BigDecimal consultarEstoque(Integer id) {
        buscarPorId(id); // valida se o produto existe e está ativo
        return stocks.findByProduto_Id(id)
                .map(s -> s.getQuantidadeDisponivel())
                .orElse(BigDecimal.ZERO);
    }

    private ProductResponse toResponse(ProductEntity p) {
        BigDecimal quantity = stocks.findByProduto_Id(p.getId())
                .map(s -> s.getQuantidadeDisponivel())
                .orElse(BigDecimal.ZERO);
        return new ProductResponse(
                p.getId(), p.getCodigoBarras(), p.getNome(), p.getCategoria().getNome(),
                p.getPrecoVenda(), p.getUnidadeMedida(), quantity);
    }
}
