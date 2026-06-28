# Relatório - Decisões de Projeto

O projeto de banco de dados foi estruturado com foco primordial em alta performance, escalabilidade e integridade referencial. A principal decisão arquitetônica do Modelo Lógico foi a adoção sistemática de identificadores artificiais numéricos (id SERIAL) para as entidades do sistema, especialmente nas de maior volume transacional, como vídeos, comentários e doações. Essa estratégia substitui a propagação de chaves primárias naturais e compostas pesadas, reduzindo drasticamente o inchaço dos índices em disco e otimizando o custo computacional (CPU e RAM) das operações de junção (JOINs).

Para garantir que essa otimização técnica não comprometesse a consistência das regras de negócio, as identidades reais dos registros (como nomes de canais, nicks e sequenciais) foram rigorosamente isoladas e protegidas através de chaves alternativas (Unique Keys).

## Indíces

A estratégia de indexação foi desenhada para suportar cenários de leitura intensiva (Heavy-Read), aplicando índices B-Tree explicitamente nas chaves estrangeiras para otimizar as volumosas operações de junção e evitar varreduras completas nas tabelas (Full Table Scans). Além disso, as chaves lógicas de negócio (como nicks de usuários e nomes de canais) receberam restrições UNIQUE, criando índices exclusivos que garantem buscas instantâneas e protegem a identidade dos registros, enquanto o uso de chaves primárias numéricas curtas mantém as páginas de índice compactadas para maximizar o uso do cache na memória RAM.

## Views

A camada de Views atua como uma interface de abstração essencial entre a complexidade estrutural do modelo relacional e a camada de aplicação, encapsulando junções extensas para simplificar o acesso rotineiro e proteger o código cliente de eventuais mudanças estruturais subjacentes. Adicionalmente, foram planejadas Views Materializadas para relatórios de agregação pesados, permitindo o pré-processamento e o armazenamento físico de sumarizações históricas, o que transforma consultas de alto custo computacional em leituras instantâneas ideais para alimentar dashboards operacionais sem onerar o banco em tempo real.

## Triggers

Os gatilhos (Triggers) foram implementados como a principal linha de defesa para assegurar a integridade de regras de negócio complexas que extrapolam a capacidade das restrições nativas (como CHECK e FOREIGN KEY). Eles atuam proativamente na validação de relacionamentos de arcos exclusivos na monetização — garantindo, via Rollback, que uma doação seja associada a um e apenas um método de pagamento — e na manutenção automatizada de dados derivados (como a contagem de vídeos de um canal), eliminando gargalos de agregação durante as leituras comuns.

## Functions

A adoção de funções armazenadas (Stored Functions) em PL/pgSQL centraliza o processamento analítico diretamente no servidor de banco de dados, reduzindo drasticamente o overhead de rede ao evitar a transferência de grandes volumes de dados brutos para a memória da aplicação. Essa decisão arquitetônica permitiu encapsular lógicas de negócio complexas, agrupamentos dinâmicos via Common Table Expressions (CTEs) e relatórios gerenciais estruturados, devolvendo tabelas tipadas de forma consolidada, rápida, segura e com planos de execução altamente otimizados pelo motor do PostgreSQL.