package br.com.cana.api.repository;

import br.com.cana.api.entity.StockEntity;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.data.jpa.repository.Lock;
import org.springframework.data.jpa.repository.Query;
import org.springframework.data.repository.query.Param;
import jakarta.persistence.LockModeType;
import java.util.Optional;

public interface StockRepository extends JpaRepository<StockEntity, Integer> {
    Optional<StockEntity> findByProduto_Id(Integer produtoId);

    @Lock(LockModeType.PESSIMISTIC_WRITE)
    @Query("select s from StockEntity s where s.produto.id = :produtoId")
    Optional<StockEntity> findByProdutoIdForUpdate(@Param("produtoId") Integer produtoId);
}
