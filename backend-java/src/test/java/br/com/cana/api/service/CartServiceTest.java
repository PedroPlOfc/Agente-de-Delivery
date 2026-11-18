package br.com.cana.api.service;

import br.com.cana.api.entity.CartEntity;
import br.com.cana.api.repository.CartRepository;
import com.fasterxml.jackson.databind.ObjectMapper;
import org.junit.jupiter.api.Test;
import java.util.List;
import java.util.Map;
import java.util.Optional;
import static org.junit.jupiter.api.Assertions.*;
import static org.mockito.ArgumentMatchers.any;
import static org.mockito.Mockito.*;

class CartServiceTest {
    @Test
    void carregaCarrinhoNormalizandoTelefone() {
        CartRepository repository = mock(CartRepository.class);
        CartService service = new CartService(repository, new ObjectMapper());
        when(repository.findById("5581999999999")).thenReturn(
                Optional.of(new CartEntity("5581999999999", "[{\"produto\":\"Arroz\",\"quantidade\":2}]")));

        List<Map<String, Object>> result = service.carregar("+55 (81) 99999-9999");

        assertEquals(1, result.size());
        assertEquals("Arroz", result.get(0).get("produto"));
        verify(repository).findById("5581999999999");
    }

    @Test
    void salvaCarrinhoNaPersistenciaJava() {
        CartRepository repository = mock(CartRepository.class);
        CartService service = new CartService(repository, new ObjectMapper());
        when(repository.findById("5581999999999")).thenReturn(Optional.empty());
        when(repository.save(any(CartEntity.class))).thenAnswer(invocation -> invocation.getArgument(0));
        List<Map<String, Object>> items = List.of(Map.of("produto", "Feijão", "quantidade", 1));

        List<Map<String, Object>> result = service.salvar("5581999999999", items);

        assertEquals(items, result);
        verify(repository).save(any(CartEntity.class));
    }
}
