package br.com.cana.api.repository;

import br.com.cana.api.entity.StockMovementEntity;
import org.springframework.data.jpa.repository.JpaRepository;
import java.util.List;

public interface StockMovementRepository extends JpaRepository<StockMovementEntity, Long> {
    List<StockMovementEntity> findTop100ByOrderByCriadoEmDesc();
}
