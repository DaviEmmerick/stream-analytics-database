-- =====================================================
-- 1. VIEW DE RESUMO FINANCEIRO DOS CANAIS
-- =====================================================
-- Justificativa:
-- Mostra os patrocínios recebidos por cada canal,
-- relacionando empresa e streamer sem expor as FKs.

CREATE OR REPLACE VIEW vw_resumo_financeiro_canal AS

SELECT
    c.nome AS nome_canal,
    u.nick AS nome_streamer,
    e.nome AS empresa_patrocinadora,
    p.valor AS valor_patrocinio

FROM Canal c

JOIN Patrocina p
    ON c.id = p.id_canal

JOIN Empresa e
    ON e.id = p.id_empresa

JOIN Streamer s
    ON s.id_usuario = c.id_streamer

JOIN Usuario u
    ON u.id = s.id_usuario;



-- =====================================================
-- 2. VIEW DE ENGAJAMENTO DOS VÍDEOS
-- =====================================================
-- Justificativa:
-- Consolida métricas de audiência dos vídeos junto
-- com informações do canal.

CREATE OR REPLACE VIEW vw_engajamento_videos AS

SELECT

    v.titulo,
    v.tema,
    v.duracao,
    v.visu_simulta AS espectadores_simultaneos,
    v.visu_total AS visualizacoes_totais,

    c.nome AS nome_canal,

    c.tipo AS tipo_canal,

    u.nick AS streamer


FROM Video v


JOIN Canal c

    ON v.id_canal = c.id


JOIN Streamer s

    ON c.id_streamer = s.id_usuario


JOIN Usuario u

    ON s.id_usuario = u.id


WHERE v.visu_total > 0;



-- =====================================================
-- 3. VIEW DE SUPERCHATS VIP
-- =====================================================
-- Justificativa:
-- Exibe apenas doações de alto valor sem expor
-- informações de pagamento.

CREATE OR REPLACE VIEW vw_superchats_vip AS


SELECT

    u.nick AS doador,
    d.valor,
    d.status,
    c.texto AS mensagem,
    v.titulo AS titulo_video


FROM Doacao d
JOIN Comentario c

    ON d.id_comentario = c.id
JOIN Usuario u

    ON c.id_usuario = u.id
JOIN Video v

    ON c.id_video = v.id
WHERE d.valor >= 100.00
ORDER BY d.valor DESC;