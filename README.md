# Datadog E-commerce — Prática de Observabilidade

> **Importante:** o foco deste repositório **não é a construção da aplicação**.
> A API de e-commerce aqui presente é um app simples e já pronto, usado apenas como
> **fonte de dados** para praticar observabilidade com o **Datadog**.

## Objetivo da prática

Utilizar uma API fictícia de pedidos (`orders-api`) conectada ao Datadog para exercitar,
na prática, os conceitos de observabilidade:

- **Métricas** — envio de métricas customizadas e análise de tendências.
- **Logs** — envio de logs estruturados com contexto do pedido e investigação de falhas.
- **Dashboards** — visualização do comportamento da aplicação e de indicadores do negócio.
- **Alertas (Monitors)** — detecção automática de anomalias e aumento de erros.
- **Visão de negócio** — transformar dados técnicos em informações úteis para um e-commerce fictício
  (ex.: quais formas de pagamento mais falham, quanto valor em pedidos está sendo perdido).

## Como o app gera os dados

A API (FastAPI) expõe dois endpoints:

| Endpoint | Descrição |
|---|---|
| `GET /health` | Health check da aplicação |
| `POST /orders` | Processa um pedido fictício |

Exemplo de pedido:

```json
{
  "order_id": "ORD-1001",
  "customer_id": "CUST-42",
  "amount": 259.90,
  "payment_method": "pix"
}
```

Para simular falhas, basta enviar um `order_id` que comece com **`ORD-ERROR`**. Nesse caso o app:

1. Classifica o erro:
   - `payment_method = boleto` → `payment_validation_error` ("Falha na validacao do boleto")
   - demais métodos → `order_processing_error` ("Falha generica no processamento")
2. Envia a **métrica** `ecommerce.orders.errors` (tipo `count`) ao Datadog com as tags
   `service:orders-api`, `env:production`, `version:1.0.0`, `region:sa-east-1`.
3. Envia um **log** de erro ao Datadog (`service:orders-api`, `source:python`) contendo
   `order_id`, `customer_id`, `amount`, `payment_method`, `status`, `error_type` e `error_message`.

Pedidos sem erro retornam `status: success` e geram apenas log local.

## O que foi praticado no Datadog

### Métricas
- Consulta da métrica `ecommerce.orders.errors` no Metrics Explorer.
- Uso das tags (`service`, `env`, `version`, `region`) para filtrar e agrupar os dados.

### Logs
- Busca e filtragem dos logs de erro do `orders-api` no Log Explorer.
- Extração dos atributos do log (`error_type`, `payment_method`, `amount`, etc.) para
  criar facets e permitir agrupamentos e análises.

### Dashboards
Painéis construídos combinando métricas e logs, como:
- Volume de erros de pedidos ao longo do tempo.
- Erros por tipo (`error_type`) e por forma de pagamento (`payment_method`).
- Valor total (`amount`) de pedidos que falharam — estimativa de receita impactada.
- Lista dos últimos pedidos com erro para investigação rápida.

### Alertas (Monitors)
- Monitor sobre a métrica `ecommerce.orders.errors` disparando quando o número de erros
  ultrapassa um limite em uma janela de tempo.
- Monitor baseado em logs para falhas específicas (ex.: aumento de erros de validação de boleto).

### Informações para o negócio (fictício)
Perguntas que a observabilidade ajuda a responder:
- A taxa de falhas nos pedidos está aumentando?
- Qual forma de pagamento gera mais problemas?
- Quanto em vendas está sendo perdido por erros no processamento?
- Quais clientes foram impactados?

## Como executar

### Pré-requisitos
- Python 3.10+
- Uma conta no Datadog com uma **API Key**

### Instalação

```bash
python -m venv .venv
# Windows
.venv\Scripts\activate
# Linux/macOS
source .venv/bin/activate

pip install fastapi uvicorn python-dotenv datadog-api-client
```

### Configuração

Crie um arquivo `.env` na raiz do projeto (ele já está no `.gitignore`):

```env
DD_API_KEY=sua_api_key
DD_SITE=datadoghq.com   # ou o site da sua conta, ex.: us5.datadoghq.com
```

### Subindo a API

```bash
uvicorn app:app --reload
```

A documentação interativa fica disponível em `http://localhost:8000/docs`.

### Gerando dados

```bash
# Pedido com sucesso
curl -X POST http://localhost:8000/orders -H "Content-Type: application/json" \
  -d '{"order_id":"ORD-1001","customer_id":"CUST-1","amount":150.0,"payment_method":"pix"}'

# Pedido com erro (boleto)
curl -X POST http://localhost:8000/orders -H "Content-Type: application/json" \
  -d '{"order_id":"ORD-ERROR-1","customer_id":"CUST-2","amount":320.5,"payment_method":"boleto"}'
```

Envie vários pedidos (com e sem erro, variando forma de pagamento e valor) para popular
as métricas, logs e dashboards no Datadog.

## Estrutura

```
.
├── app.py                     # API de pedidos (fonte dos dados enviados ao Datadog)
├── scripts/
│   └── generate_orders.py     # Script para geração de pedidos (reservado)
├── requierments.txt
└── .env                       # Credenciais do Datadog (não versionado)
```

## Tecnologias

- **Python** + **FastAPI**
- **Datadog** (Metrics, Logs, Dashboards, Monitors)
- **datadog-api-client** para envio de métricas e logs via API
