package br.com.cana.api.repository;

import br.com.cana.api.entity.CategoryEntity;
import org.springframework.data.jpa.repository.JpaRepository;
import java.util.Optional;

public interface CategoryRepository extends JpaRepository<CategoryEntity, Integer> {
    Optional<CategoryEntity> findByNomeIgnoreCase(String nome);
}
