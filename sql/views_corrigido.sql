-- ============================================================================
-- 03_views.sql  —  Visões (conjunto final justificado)
-- ----------------------------------------------------------------------------
-- Critério: toda view aqui ATENDE a uma consulta real do trabalho (view que
-- não responde a nenhuma das 8 consultas é decoração e foi descartada).
-- Conjunto: 1 MATERIALIZADA (consolida 5 consultas) + 2 VIRTUAIS (detalhe).
--
-- ORDEM DE EXECUÇÃO: este arquivo é estrutura (PL/pgSQL) e roda ANTES da carga.
-- Por isso a view materializada é criada com WITH NO DATA (estrutura vazia) e
-- populada depois, no arquivo de chamadas de teste, com:
--     REFRESH MATERIALIZED VIEW vw_receita_canal;   (o 1o NÃO pode ser CONCURRENTLY)
-- As views virtuais não guardam dados, então podem ser criadas já aqui.
-- ============================================================================


-- ============================================================================
-- VIEW 1 (MATERIALIZADA) — vw_receita_canal
-- ATENDE: consultas 3, 5, 6, 7 e 8 (uma view respondendo cinco perguntas).
-- ----------------------------------------------------------------------------
-- JUSTIFICATIVA DO TIPO (materializada): agrega sobre Doacao (a maior tabela) e
-- o resultado é reaproveitado por 5 consultas de ranking/relatório, que toleram
-- dado levemente defasado. Recomputar a cada chamada seria desperdício; melhor
-- "congelar" e atualizar via REFRESH sob demanda.
--
-- ANTI FAN-OUT: cada fonte de receita é agregada na SUA subconsulta
-- (GROUP BY id_canal) ANTES de ligar ao canal. Um join plano das três fontes
-- multiplicaria linhas (patrocínios x membros x doações) e inflaria os SUM().
--
-- NOTA: total_membros_mes é valor MENSAL; patrocínio e doações são acumulados.
-- receita_total soma os três conforme o enunciado.
-- ============================================================================
DROP MATERIALIZED VIEW IF EXISTS vw_receita_canal CASCADE;

CREATE MATERIALIZED VIEW vw_receita_canal AS
SELECT
    c.id                                AS id_canal,
    c.nome                              AS nome_canal,
    c.id_plataforma                     AS id_plataforma,
    u.nick                              AS nick_streamer,
    COALESCE(pat.total_patrocinio, 0)   AS total_patrocinio,
    COALESCE(mem.total_membros_mes, 0)  AS total_membros_mes,
    COALESCE(don.total_doacoes,    0)   AS total_doacoes,
      COALESCE(pat.total_patrocinio, 0)
    + COALESCE(mem.total_membros_mes, 0)
    + COALESCE(don.total_doacoes,    0) AS receita_total
FROM Canal c
JOIN Streamer s ON s.id_usuario = c.id_streamer
JOIN Usuario  u ON u.id         = s.id_usuario
LEFT JOIN (
    SELECT id_canal, SUM(valor) AS total_patrocinio
    FROM Patrocina GROUP BY id_canal
) pat ON pat.id_canal = c.id
LEFT JOIN (
    SELECT i.id_canal, SUM(nc.valor_nivel) AS total_membros_mes
    FROM Inscricao i
    JOIN NivelCanal nc ON nc.id_canal = i.id_canal AND nc.nivel = i.nivel
    GROUP BY i.id_canal
) mem ON mem.id_canal = c.id
LEFT JOIN (
    SELECT v.id_canal, SUM(d.valor) AS total_doacoes
    FROM Doacao d
    JOIN Comentario cm ON cm.id = d.id_comentario
    JOIN Video      v  ON v.id  = cm.id_video
    WHERE d.status IN ('recebido', 'lido')
    GROUP BY v.id_canal
) don ON don.id_canal = c.id
WITH NO DATA;

-- Índice único: habilita REFRESH ... CONCURRENTLY e acelera a leitura por canal.
CREATE UNIQUE INDEX idx_vw_receita_canal ON vw_receita_canal (id_canal);


-- ============================================================================
-- VIEW 2 (VIRTUAL) — vw_resumo_financeiro_canal
-- ATENDE: consulta 1 (canais patrocinados e valores, por empresa).
-- ----------------------------------------------------------------------------
-- JUSTIFICATIVA DO TIPO (virtual): patrocínios são apenas os vigentes (sem
-- histórico), consultados em tempo real; é um join simples, sem agregação
-- pesada -> materializar não traria ganho.
-- POR QUE NÃO É REDUNDANTE COM A VIEW 1: a View 1 traz o TOTAL de patrocínio por
-- canal (perde o detalhe); esta traz uma linha POR PAR empresa-canal, que é o
-- grão que a consulta 1 precisa. Encapsula o join e esconde as FKs.
-- ============================================================================
CREATE OR REPLACE VIEW vw_resumo_financeiro_canal AS
SELECT
    e.nome  AS empresa,
    c.nome  AS nome_canal,
    u.nick  AS nick_streamer,
    p.valor AS valor_patrocinio
FROM Patrocina p
JOIN Empresa  e ON e.id = p.id_empresa
JOIN Canal    c ON c.id = p.id_canal
JOIN Streamer s ON s.id_usuario = c.id_streamer
JOIN Usuario  u ON u.id         = s.id_usuario;


-- ============================================================================
-- VIEW 3 (VIRTUAL) — vw_doacoes_por_video
-- ATENDE: consulta 4 (soma das doações de comentários "lidos", por vídeo).
-- ----------------------------------------------------------------------------
-- JUSTIFICATIVA DO TIPO (virtual): é cenário operacional/tempo real — uma
-- doação recém-lida deve aparecer na hora, então dado congelado seria ruim.
-- Encapsula o filtro de status 'lido' e a cadeia Video->Comentario->Doacao.
-- ('lido' é status da DOAÇÃO; como comentário->doação é 1:0..1, "comentário
-- lido" = comentário cuja doação tem status 'lido'.)
-- SUBSTITUI a antiga vw_superchats_vip, que filtrava por valor >= 100 (critério
-- que não corresponde a nenhuma consulta).
-- ============================================================================
CREATE OR REPLACE VIEW vw_doacoes_por_video AS
SELECT
    v.id     AS id_video,
    v.titulo AS titulo,
    c.id     AS id_canal,
    c.nome   AS nome_canal,
    SUM(d.valor) AS total_doacoes_lidas
FROM Video v
JOIN Canal      c  ON c.id  = v.id_canal
JOIN Comentario cm ON cm.id_video = v.id
JOIN Doacao     d  ON d.id_comentario = cm.id
WHERE d.status = 'lido'
GROUP BY v.id, v.titulo, c.id, c.nome;


-- ============================================================================
-- VIEWS DESCARTADAS (documentar é parte da justificativa)
-- ----------------------------------------------------------------------------
--   * vw_engajamento_videos : nenhuma das 8 consultas pede métricas de
--     audiência de vídeo -> otimizaria uma busca que ninguém faz. Removida.
--   * vw_superchats_vip     : filtrava doações por valor >= 100; nenhuma
--     consulta usa esse critério. Foi reescrita como vw_doacoes_por_video
--     (mesmo espírito, filtro 'lido' correto da consulta 4).
--
-- Consumo pelas functions:
--   View 1 -> consultas 3 (sp_doacoes_por_canal) e 5-8 (sp_top_canais_*)
--   View 2 -> consulta 1  (sp_canais_patrocinados)
--   View 3 -> consulta 4  (sp_doacoes_lidas_por_video)
-- A consulta 2 não tem view (grão de usuário, join simples, não se repete).
-- ============================================================================
