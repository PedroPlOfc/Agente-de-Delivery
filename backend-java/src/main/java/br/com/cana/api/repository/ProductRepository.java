package br.com.cana.api.repository;

import br.com.cana.api.entity.ProductEntity;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.data.jpa.repository.Query;
import org.springframework.data.repository.query.Param;
import java.util.List;
import java.util.Optional;

public interface ProductRepository extends JpaRepository<ProductEntity, Integer> {
    @Query("""
        select p from ProductEntity p
        join fetch p.categoria c
        where p.ativo = true and lower(p.nome) like lower(concat('%', :termo, '%'))
        order by p.nome
        """)
    List<ProductEntity> buscarPorNome(@Param("termo") String termo);

    @Query("select p from ProductEntity p join fetch p.categoria where p.codigoBarras = :codigo and p.ativo = true")
    Optional<ProductEntity> buscarPorCodigo(@Param("codigo") String codigo);

    @Query("select p from ProductEntity p join fetch p.categoria where p.id = :id and p.ativo = true")
    Optional<ProductEntity> buscarAtivoPorId(@Param("id") Integer id);

    @Query("select p from ProductEntity p join fetch p.categoria where lower(p.nome) = lower(:nome) and p.ativo = true")
    Optional<ProductEntity> buscarNomeExato(@Param("nome") String nome);

    @Query("select p from ProductEntity p join fetch p.categoria where p.ativo = true order by p.nome")
    List<ProductEntity> listarAtivos();

    long countByAtivoTrue();
}
