-- ==============================================================================
-- PROJETO BD2 - FUNCTIONS E PROCEDURES
-- ==============================================================================

-- ------------------------------------------------------------------------------
-- CONSULTA 1: Canais patrocinados e valores por empresa (Parâmetro Opcional)
-- ------------------------------------------------------------------------------
CREATE TYPE relatorio_patrocinio AS (
    nome_empresa VARCHAR(50),
    nome_canal VARCHAR(100),
    nick_streamer VARCHAR(50),
    valor NUMERIC(10,2)
);

CREATE OR REPLACE FUNCTION sp_canais_patrocinados(p_nome_empresa VARCHAR DEFAULT NULL)
RETURNS SETOF relatorio_patrocinio AS $$
BEGIN
    IF p_nome_empresa IS NULL THEN
        RETURN QUERY
        SELECT e.nome, p.nome_canal, p.nick_streamer, p.valor
        FROM Patrocina p
        JOIN Empresa e ON p.nro_empresa = e.numero
        ORDER BY p.valor DESC;
    ELSE
        RETURN QUERY
        SELECT e.nome, p.nome_canal, p.nick_streamer, p.valor
        FROM Patrocina p
        JOIN Empresa e ON p.nro_empresa = e.numero
        WHERE e.nome ILIKE '%' || p_nome_empresa || '%'
        ORDER BY p.valor DESC;
    END IF;
END;
$$ LANGUAGE plpgsql;

-- ------------------------------------------------------------------------------
-- CONSULTA 2: Níveis de canais e quantidade de membros
-- ------------------------------------------------------------------------------
CREATE OR REPLACE FUNCTION sp_membros_por_nivel()
RETURNS TABLE (
    nome_canal VARCHAR,
    nivel INTEGER,
    quantidade_membros BIGINT
) AS $$
BEGIN
    RETURN QUERY
    SELECT 
        i.nome_canal,
        i.nivel,
        COUNT(i.nick_membro) AS quantidade_membros
    FROM Inscricao i
    GROUP BY i.nome_canal, i.nivel
    ORDER BY i.nome_canal, i.nivel;
END;
$$ LANGUAGE plpgsql;

-- ------------------------------------------------------------------------------
-- CONSULTA 3: Ranking de Streamers (Parâmetro: 'doacoes' ou 'views')
-- ------------------------------------------------------------------------------
CREATE OR REPLACE FUNCTION sp_ranking_streamers(p_criterio VARCHAR DEFAULT 'doacoes')
RETURNS TABLE (
    nick_streamer VARCHAR,
    total_acumulado NUMERIC
) AS $$
BEGIN
    IF p_criterio = 'views' THEN
        RETURN QUERY
        SELECT v.nick_streamer, SUM(v.visu_total)::NUMERIC AS total_acumulado
        FROM Video v
        GROUP BY v.nick_streamer
        ORDER BY total_acumulado DESC;
    ELSE
        -- Default: Ranking por valor arrecadado em doações recebidas
        RETURN QUERY
        SELECT d.nick_streamer, SUM(d.valor)::NUMERIC AS total_acumulado
        FROM Doacao d
        WHERE d.status = 'recebido'
        GROUP BY d.nick_streamer
        ORDER BY total_acumulado DESC;
    END IF;
END;
$$ LANGUAGE plpgsql;

-- ==============================================================================
-- PARTE 2 - NOVAS CONSULTAS (4 a 8)
-- ==============================================================================

-- ------------------------------------------------------------------------------
-- CONSULTA 4: Comentários Online e SuperChats de um Vídeo
-- ------------------------------------------------------------------------------
CREATE OR REPLACE FUNCTION sp_comentarios_superchat(p_titulo_video VARCHAR)
RETURNS TABLE (
    nick_usuario VARCHAR,
    texto_comentario VARCHAR,
    data_hora TIMESTAMP,
    valor_doacao NUMERIC,
    status_doacao VARCHAR
) AS $$
BEGIN
    RETURN QUERY
    SELECT 
        c.nick_usuario,
        c.texto,
        c.data_hora,
        COALESCE(d.valor, 0.00) AS valor_doacao,
        COALESCE(d.status, 'sem doacao')::VARCHAR AS status_doacao
    FROM Comentario c
    LEFT JOIN Doacao d ON c.sequencial = d.sequencial_coment 
        AND c.titulo_video = d.titulo_video
    WHERE c.titulo_video = p_titulo_video AND c.online = TRUE
    ORDER BY c.data_hora ASC;
END;
$$ LANGUAGE plpgsql;

-- ------------------------------------------------------------------------------
-- CONSULTA 5: Ranking dos Maiores Patrocínios (Com limite dinâmico)
-- ------------------------------------------------------------------------------
CREATE OR REPLACE FUNCTION sp_top_patrocinios(p_limite INTEGER DEFAULT 10)
RETURNS TABLE (
    nome_empresa VARCHAR,
    nome_canal VARCHAR,
    nick_streamer VARCHAR,
    valor NUMERIC
) AS $$
BEGIN
    RETURN QUERY
    SELECT 
        e.nome,
        p.nome_canal,
        p.nick_streamer,
        p.valor
    FROM Patrocina p
    JOIN Empresa e ON p.nro_empresa = e.numero
    ORDER BY p.valor DESC
    LIMIT p_limite;
END;
$$ LANGUAGE plpgsql;

-- ------------------------------------------------------------------------------
-- CONSULTA 6: Análise de Engajamento: Vídeos com Convidados (Collabs) vs Solos
-- ------------------------------------------------------------------------------
CREATE OR REPLACE FUNCTION sp_analise_collabs()
RETURNS TABLE (
    tipo_video VARCHAR,
    qtd_videos BIGINT,
    media_visualizacoes NUMERIC
) AS $$
BEGIN
    RETURN QUERY
    WITH VideoStats AS (
        SELECT 
            v.titulo,
            v.visu_total,
            CASE 
                WHEN (SELECT COUNT(*) FROM Participa p WHERE p.titulo_video = v.titulo) > 0 THEN 'Collab (Com Convidados)'
                ELSE 'Solo (Sozinho)'
            END AS tipo_video
        FROM Video v
    )
    SELECT 
        vs.tipo_video::VARCHAR,
        COUNT(vs.titulo) AS qtd_videos,
        ROUND(AVG(vs.visu_total), 2) AS media_visualizacoes
    FROM VideoStats vs
    GROUP BY vs.tipo_video;
END;
$$ LANGUAGE plpgsql;

-- ------------------------------------------------------------------------------
-- CONSULTA 7: Taxa de Conversão por País (Usuários que viraram Streamers/Membros)
-- ------------------------------------------------------------------------------
CREATE OR REPLACE FUNCTION sp_taxa_conversao_pais()
RETURNS TABLE (
    nome_pais VARCHAR,
    total_usuarios BIGINT,
    total_streamers BIGINT,
    total_membros BIGINT
) AS $$
BEGIN
    RETURN QUERY
    SELECT 
        p.nome,
        COUNT(DISTINCT u.nick) AS total_usuarios,
        COUNT(DISTINCT s.nick_streamer) AS total_streamers,
        COUNT(DISTINCT m.nick_membro) AS total_membros
    FROM Pais p
    JOIN Usuario u ON p.ddi = u.ddi_pais_reside
    LEFT JOIN Streamer s ON u.nick = s.nick_streamer
    LEFT JOIN Membro m ON u.nick = m.nick_membro
    GROUP BY p.nome
    ORDER BY total_usuarios DESC;
END;
$$ LANGUAGE plpgsql;

-- ------------------------------------------------------------------------------
-- CONSULTA 8: Histórico de Pagamentos de um Usuário (Extrato de Doações)
-- ------------------------------------------------------------------------------
CREATE OR REPLACE FUNCTION sp_historico_pagamentos(p_nick_usuario VARCHAR)
RETURNS TABLE (
    sequencial_doacao INTEGER,
    valor NUMERIC,
    status VARCHAR,
    metodo_pagamento VARCHAR
) AS $$
BEGIN
    RETURN QUERY
    SELECT 
        d.sequencial_doacao,
        d.valor,
        d.status,
        CASE 
            WHEN cc.numero IS NOT NULL THEN 'Cartao de Credito'
            WHEN pp.id_paypal IS NOT NULL THEN 'PayPal'
            WHEN btc.tx_id IS NOT NULL THEN 'Bitcoin'
            WHEN mp.sequencial_mec IS NOT NULL THEN 'Mecanica da Plataforma'
            ELSE 'Desconhecido'
        END::VARCHAR AS metodo_pagamento
    FROM Doacao d
    LEFT JOIN Cartao_Cred cc ON d.sequencial_doacao = cc.sequencial_doacao
    LEFT JOIN Paypal pp ON d.sequencial_doacao = pp.sequencial_doacao
    LEFT JOIN BTC btc ON d.sequencial_doacao = btc.sequencial_doacao
    LEFT JOIN Mec_plat mp ON d.sequencial_doacao = mp.sequencial_doacao
    WHERE d.nick_usuario = p_nick_usuario
    ORDER BY d.sequencial_doacao DESC;
END;
$$ LANGUAGE plpgsql;
