# 🛒 Agente de IA para Delivery — Varejo & Supermercados

![Python](https://img.shields.io/badge/Python-3.10%2B-blue?logo=python&logoColor=white)
![FastAPI](https://img.shields.io/badge/FastAPI-0.110%2B-009688?logo=fastapi&logoColor=white)
![Google Gemini](https://img.shields.io/badge/Google%20Gemini-API-8E44AD?logo=googlegemini&logoColor=white)
![Evolution API](https://img.shields.io/badge/Evolution%20API-v1.8.2-0052CC?logo=whatsapp&logoColor=white)
![Render](https://img.shields.io/badge/Render-Cloud-46E3B7?logo=render&logoColor=white)
![Pydantic](https://img.shields.io/badge/Pydantic-v2-E92063?logo=pydantic&logoColor=white)

Aplicação backend inteligente desenvolvida em Python com **FastAPI**, **Google Gemini API** e **Evolution API**. O sistema recebe mensagens em linguagem natural enviadas por clientes via **WhatsApp**, interpreta pedidos de supermercado em texto livre e os converte instantaneamente em listas de separação estruturadas por setor, enviando a confirmação e tirando dúvidas com o cliente de forma automatizada.

---

## 🎯 Problema vs. Solução

- **Problema:** Clientes enviam pedidos por áudio ou texto sem padrão formal (ex: *"10 reais de queijo coalho"*, *"3 pacotes de fubá coringa"*, *"2kg de carne moída"*). A triagem manual desses pedidos gera gargalos na operação, erros na separação dos itens e demora no atendimento.
- **Solução:** O Agente de IA intercepta os webhooks do WhatsApp enviados pela Evolution API, analisa o pedido com o **Google Gemini**, extrai marcas, unidades (R$, kg, un) e observações, categoriza os produtos por departamento (Açougue, Laticínios, Mercearia, Hortifruti, etc.) e dispara a resposta de confirmação de forma autônoma para o WhatsApp do cliente.

---

## 🏗️ Arquitetura da Solução

```text
 ┌─────────────────┐       ┌──────────────────────┐       ┌────────────────────────────────┐
 │ Cliente envia   │ ────> │ Evolution API        │ ────> │ FastAPI Webhook                │
 │ msg no WhatsApp │       │ (Hospedada no Render)│       │ (/webhook/mercado)             │
 └─────────────────┘       └──────────────────────┘       └────────────────────────────────┘
                                                                          │
                                                                          ▼
 ┌─────────────────┐       ┌──────────────────────┐       ┌────────────────────────────────┐
 │ Cliente recebe  │ <──── │ Evolution API        │ <──── │ Google Gemini API              │
 │ a confirmação   │       │ (/message/sendText)  │       │ (Estruturação e Resposta)      │
 └─────────────────┘       └──────────────────────┘       └────────────────────────────────┘