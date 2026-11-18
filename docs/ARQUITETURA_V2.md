# Arquitetura CANA v2

## Decisão de fronteiras

- **Python/FastAPI:** entrada e saída de mensagens, simulador web, webhook, chamadas ao provedor de IA, interpretação da intenção e formatação da resposta.
- **Java/Spring Boot:** fonte de verdade para catálogo, estoque, carrinhos, persistência, validações comerciais e criação/cálculo de pedidos.
- **PostgreSQL:** persistência principal de dados comerciais.
- **Redis:** infraestrutura interna da Evolution API nesta configuração; não guarda carrinhos do CANA.

## Comunicação

O Python acessa exclusivamente `app/java_api.py` para chamar o backend Java por HTTP/JSON. Em Docker, a URL interna é `http://java-api:8081`. O token `INTERNAL_API_TOKEN` é compartilhado somente entre os dois serviços e é enviado no cabeçalho `X-Internal-Token`.

## Fluxo de mensagem

1. O cliente envia mensagem pelo simulador ou WhatsApp.
2. O FastAPI valida o payload e recupera o carrinho na API Java.
3. O agente interpreta a mensagem e propõe a lista estruturada.
4. O Python consulta o catálogo Java para normalizar produtos e obter seus IDs oficiais.
5. O Python envia a lista atualizada à API Java.
6. O Java persiste o carrinho no PostgreSQL.
7. O Python formata a resposta e, quando a origem é WhatsApp, envia pela Evolution API.

## Regras importantes

- O modelo de IA nunca é fonte confiável de ID, preço ou estoque. O ID do produto é sempre consultado no backend Java.
- A criação de pedido é explícita. O sistema não deve transformar uma lista provisória em pedido confirmado sem confirmação do cliente.
- O cálculo de subtotal e total usa o preço cadastrado no Java.
- Carrinho não usa fallback de memória quando Java está indisponível: a API retorna erro de disponibilidade em vez de fingir que persistiu.
- A migração SQL cria objetos ausentes sem executar `DROP TABLE`.

## Limitações conhecidas da versão

- O fluxo de conversa ainda é orquestrado em Python; regras transacionais e persistência comercial estão em Java.
- A criação do pedido está disponível na API Java, mas ainda precisa ser conectada a uma etapa explícita de confirmação do cliente no fluxo conversacional.
- O estoque é consultado, mas ainda não é reservado nem decrementado automaticamente na criação do pedido.
- A deduplicação dos eventos WhatsApp está em memória no processo Python; a persistência de IDs de eventos é uma etapa futura.


## CANA Admin

O painel `/admin` é uma interface HTML servida pelo FastAPI. O Python funciona apenas como camada de apresentação/proxy same-origin. O acesso ao PostgreSQL e todas as regras de catálogo, estoque, movimentações e pedidos permanecem no serviço Spring Boot. As rotas administrativas exigem token HMAC com expiração e também o token interno Python→Java.

A migração Flyway V2 cria `admin_users` e `movimentacoes_estoque`, acrescenta `estoque_minimo` em `produtos` e `estoque_baixado` em `pedidos`, e completa um catálogo de demonstração limitado a 30 produtos ativos. Nicolas (`nicolas`, papel ADMIN) e Pedro Lucas (`pedro.lucas`, papel STAFF) são criados na primeira inicialização com senha provisória `123`, armazenada com PBKDF2.
