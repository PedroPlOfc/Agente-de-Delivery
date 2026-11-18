package br.com.cana.api.repository;

import br.com.cana.api.entity.OrderEntity;
import org.springframework.data.jpa.repository.JpaRepository;
import java.util.List;

public interface OrderRepository extends JpaRepository<OrderEntity, Integer> {
    List<OrderEntity> findTop100ByOrderByCriadoEmDesc();
    long countByStatus(String status);
}
