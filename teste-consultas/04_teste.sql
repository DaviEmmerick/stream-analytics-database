-- ------------------------------------------------------------------------------
-- TESTE 1: Patrocínios por Canal (sp_patrocinio_por_canal)
-- ------------------------------------------------------------------------------
-- 1.1 Retorna todos os patrocínios ordenados pelo maior valor
CALL sp_patrocinio_por_canal();

-- 1.2 Retorna os patrocínios de uma empresa específica (Ex: Empresa com ID 1)
CALL sp_patrocinio_por_canal(1);


-- ------------------------------------------------------------------------------
-- TESTE 2: Resumo de Membros por Usuário (sp_membros_por_usuario)
-- ------------------------------------------------------------------------------
-- 2.1 Retorna o total gasto por todos os usuários nas assinaturas de canais
CALL sp_membros_por_usuario();

-- 2.2 Retorna o resumo de assinaturas de um usuário específico (Ex: Usuário ID 5)
CALL sp_membros_por_usuario(5);


-- ------------------------------------------------------------------------------
-- TESTE 3: Doações Recebidas e Lidas por Canal (sp_doacoes_por_canal)
-- ------------------------------------------------------------------------------
-- 3.1 Retorna o volume total de doações válidas agrupadas por canal
CALL sp_doacoes_por_canal();

-- 3.2 Retorna o volume financeiro de doações de um canal específico (Ex: Canal ID 3)
CALL sp_doacoes_por_canal(3);


-- ------------------------------------------------------------------------------
-- TESTE 4: Doações Lidas por Vídeo (sp_doacoes_lidas_por_video)
-- ------------------------------------------------------------------------------
-- 4.1 Retorna a soma de doações com status 'lido' de todos os vídeos
CALL sp_doacoes_lidas_por_video();

-- 4.2 Retorna a soma de doações lidas de um vídeo específico (Ex: Vídeo ID 10)
CALL sp_doacoes_lidas_por_video(10);


-- ------------------------------------------------------------------------------
-- TESTE 5: Consultando e Atualizando a View Materializada de Receita
-- ------------------------------------------------------------------------------
-- 5.1 Consulta o faturamento total e consolidado de cada canal de forma instantânea
SELECT * FROM mv_receita_canal ORDER BY total_faturamento DESC;

-- 5.2 Comando para forçar a atualização dos dados da View Materializada
-- (Deve ser rodado sempre que novos patrocínios, membros ou doações forem inseridos)
REFRESH MATERIALIZED VIEW mv_receita_canal;