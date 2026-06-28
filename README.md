# Stream DB

Sistema de Banco de Dados Relacional projetado para catalogar e analisar o ecossistema de Streamers, Plataformas, Monetização e Engajamento de Audiência.

---

## Como Executar o Projeto

Pré-requisitos:

->Antes de começar, certifique-se de ter instalado em sua máquina:
-> Docker e Docker Compose

### Passo a Passo

1. Configurar as Variáveis de Ambiente

Copie o arquivo .env:

Certifique-se de que as variáveis POSTGRES_USER, POSTGRES_PASSWORD e POSTGRES_DB estejam preenchidas no seu .env.

2. Subir os Contêineres

docker compose up -d

3. Verificar o Status da Execução

docker logs -f streamer_seeder

---

## Sobre o Projeto

Este repositório contém a modelagem Conceitual, Lógica e Física, além da implementação completa de uma base de dados normalizada para gerenciar informações de transmissões ao vivo. 

O ambiente foi otimizado para cenários de alta leitura utilizando:
* **Índices estratégicos**
* **Views Materializadas**
* **Triggers**
* **Stored Procedures**
* **Controle de consistência e integridade**

---

## Tecnologias e Ferramentas

O projeto é empacotado para execução rápida e isolada, garantindo que o ambiente seja idêntico para todos os desenvolvedores.

* **Banco de Dados:** PostgreSQL 16
* **Data Seeding:** Python 3.11 (com biblioteca Faker)
* **Infraestrutura:** Docker Compose
* **Client (Opcional):** pgAdmin 4

---

## 📂 Estrutura do Repositório

A arquitetura segue um fluxo modular baseado em scripts SQL sequenciais e contêineres:

```text
├── docker-compose.yml   # Orquestração do Banco e do Script de População
├── .env.example         # Template de variáveis de ambiente
├── seed/                # Script Python (Faker) para gerar dados realistas
└── sql/
    ├── 01_schema.sql    # DDL: Criação de tabelas, PKs, FKs e normalização
    ├── 02_indexes.sql   # Índices de performance (B-Tree)
    ├── 03_views.sql     # Views virtuais e materializadas
    ├── 04_triggers.sql  # PL/pgSQL: Regras de negócio e consistência
    ├── 05_functions.sql # Stored Procedures para as questões de negócio
    └── 06_seed.sql      # (Opcional) DML para inserções estáticas