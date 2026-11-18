package br.com.cana.api.service;

import br.com.cana.api.entity.CartEntity;
import br.com.cana.api.repository.CartRepository;
import com.fasterxml.jackson.core.type.TypeReference;
import com.fasterxml.jackson.databind.ObjectMapper;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;
import java.util.List;
import java.util.Map;

@Service
public class CartService {
    private static final TypeReference<List<Map<String, Object>>> CART_TYPE = new TypeReference<>() {};
    private final CartRepository carts;
    private final ObjectMapper mapper;

    public CartService(CartRepository carts, ObjectMapper mapper) {
        this.carts = carts;
        this.mapper = mapper;
    }

    @Transactional(readOnly = true)
    public List<Map<String, Object>> carregar(String phone) {
        return carts.findById(normalizePhone(phone))
                .map(cart -> deserialize(cart.getItensJson()))
                .orElseGet(List::of);
    }

    @Transactional
    public List<Map<String, Object>> salvar(String phone, List<Map<String, Object>> items) {
        String normalized = normalizePhone(phone);
        if (normalized.isBlank()) throw new IllegalArgumentException("Telefone inválido.");
        try {
            String json = mapper.writeValueAsString(items == null ? List.of() : items);
            CartEntity cart = carts.findById(normalized).orElseGet(() -> new CartEntity(normalized, "[]"));
            cart.setItensJson(json);
            carts.save(cart);
            return items == null ? List.of() : items;
        } catch (Exception e) {
            throw new IllegalArgumentException("Não foi possível serializar o carrinho.", e);
        }
    }

    @Transactional
    public void limpar(String phone) {
        carts.deleteById(normalizePhone(phone));
    }

    private List<Map<String, Object>> deserialize(String json) {
        try { return mapper.readValue(json, CART_TYPE); }
        catch (Exception e) { throw new IllegalStateException("Carrinho armazenado possui JSON inválido.", e); }
    }

    private String normalizePhone(String phone) {
        if (phone == null) return "";
        return phone.replaceAll("\\D", "");
    }
}
