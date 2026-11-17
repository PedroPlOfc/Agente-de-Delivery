---
date: 2026-11-17T01:40
tags:
  - Projetos
  - inteligênciaArtificial
  - agente
  - python
cssclasses:
  - page-manila
---

# O Cana nada mais é do que um agente de inteligência artificial desenvolvido para automatizar o atendimento, a extração de listas de compras e o fechamento de pedidos de delivery via WhatsApp.

- **Compreensão de linguagem natural:** interpreta mensagens informais, converte unidades de medida automaticamente (como *"meio quilo"* para `0.5 kg` e *"1 dúzia"* para `12 un`) e separa preferências de marca ou observações de preparo.

- **Gestão inteligente de sacola:** mantém o histórico do carrinho ao longo da conversa, permitindo adicionar, remover ou substituir itens sem perder o contexto, além de classificar produtos por setor (Hortifruti, Mercearia, Laticínios, Bebidas e Açougue).

- **Fechamento completo do pedido:** identifica endereço de entrega, complementos, forma de pagamento e cálculo de troco.

- **Resiliência em camadas (Fallback):** opera com `gemini-3.6-flash` como motor principal, `gemini-3.5-flash` como reserva imediata e um motor local de contingência para garantir respostas mesmo em picos de instabilidade das APIs externas.

## Arquitetura & Stack

- **Backend:** Python com FastAPI (`main.py`), utilizando `google-genai` e LangChain para *Structured Outputs* e consultas ao banco via *Automatic Function Calling (AFC)*.
- **Integração WhatsApp:** Evolution API v2.1.0 rodando em container Docker.
- **Banco de Dados & Cache:** PostgreSQL (catálogo de produtos e persistência de pedidos) e Redis orquestrados via Docker Compose.
- **Painel de Testes:** Interface web (`index.html`) que simula o fluxo de chat e exibe a atualização da Sacola de Compras em tempo real.

Para detalhes da arquitetura do projeto, visite [[Cana - Arquitetura]]

## Próximos Passos

- [ ] Parear a instância do WhatsApp via QR Code na Evolution API.
- [ ] Exibir o cálculo detalhado de subtotal, taxa de entrega e troco direto no card da sacola.
- [x] Migrar esta nota de `#Temporario` para a documentação definitiva do projeto.

-