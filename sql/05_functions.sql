
-----------------------------------------------------------------------------
-- CONSULTA 1: Canais patrocinados e valores por empresa
-- ------------------------------------------------------------------------------
-- Bloco anônimo para criar o tipo com segurança se ele não existir
DO $$ 

BEGIN
    IF NOT EXISTS (SELECT 1 FROM pg_type WHERE typname = 'relatorio_patrocinio') THEN
        CREATE TYPE relatorio_patrocinio AS (
            nome_empresa VARCHAR(150),
            nome_canal VARCHAR(100),
            nick_streamer VARCHAR(50),
            valor NUMERIC(10,2)
        );
    END IF;
END $$;

CREATE OR REPLACE FUNCTION sp_canais_patrocinados(
    p_nome_empresa VARCHAR DEFAULT NULL
)
RETURNS SETOF relatorio_patrocinio AS $$
BEGIN
    RETURN QUERY
    SELECT
        e.nome::VARCHAR(150),
        c.nome::VARCHAR(100),
        u.nick::VARCHAR(50),
        p.valor::NUMERIC(10,2)
    FROM Patrocina p
    JOIN Empresa e ON e.id = p.id_empresa
    JOIN Canal c ON c.id = p.id_canal
    JOIN Streamer s ON s.id_usuario = c.id_streamer
    JOIN Usuario u ON u.id = s.id_usuario
    WHERE p_nome_empresa IS NULL
       OR e.nome ILIKE '%' || p_nome_empresa || '%'
    ORDER BY p.valor DESC;
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
        c.nome::VARCHAR,
        i.nivel::INTEGER,
        COUNT(i.id_membro)::BIGINT
    FROM Inscricao i
    JOIN Canal c ON c.id = i.id_canal
    GROUP BY c.nome, i.nivel
    ORDER BY c.nome, i.nivel;
END;
$$ LANGUAGE plpgsql;

-- ------------------------------------------------------------------------------
-- CONSULTA 3: Ranking de Streamers
-- ------------------------------------------------------------------------------
CREATE OR REPLACE FUNCTION sp_ranking_streamers(
    p_criterio VARCHAR DEFAULT 'doacoes'
)
RETURNS TABLE (
    nick_streamer VARCHAR,
    total_acumulado NUMERIC
) AS $$
BEGIN
    IF p_criterio = 'views' THEN
        RETURN QUERY
        SELECT
            u.nick::VARCHAR,
            SUM(v.visu_total)::NUMERIC
        FROM Video v
        JOIN Canal c ON c.id = v.id_canal
        JOIN Streamer s ON s.id_usuario = c.id_streamer
        JOIN Usuario u ON u.id = s.id_usuario
        GROUP BY u.nick
        ORDER BY SUM(v.visu_total) DESC;
    ELSE
        -- Retorna o Streamer dono do Canal que recebeu a doação via comentário
        RETURN QUERY
        SELECT
            u_streamer.nick::VARCHAR,
            SUM(d.valor)::NUMERIC
        FROM Doacao d
        JOIN Comentario c ON c.id = d.id_comentario
        JOIN Video v ON v.id = c.id_video
        JOIN Canal ca ON ca.id = v.id_canal
        JOIN Streamer s ON s.id_usuario = ca.id_streamer
        JOIN Usuario u_streamer ON u_streamer.id = s.id_usuario
        WHERE d.status = 'recebido'
        GROUP BY u_streamer.nick
        ORDER BY SUM(d.valor) DESC;
    END IF;
END;
$$ LANGUAGE plpgsql;

-- ------------------------------------------------------------------------------
-- CONSULTA 4: Comentários e SuperChats de um vídeo
-- ------------------------------------------------------------------------------
CREATE OR REPLACE FUNCTION sp_comentarios_superchat(
    p_titulo_video VARCHAR
)
RETURNS TABLE (
    nick_usuario VARCHAR,
    texto_comentario TEXT,
    data_hora TIMESTAMP,
    valor_doacao NUMERIC,
    status_doacao VARCHAR
) AS $$
BEGIN
    RETURN QUERY
    SELECT
        u.nick::VARCHAR,
        c.texto,
        c.data_hora,
        COALESCE(d.valor, 0)::NUMERIC,
        COALESCE(d.status, 'sem doacao')::VARCHAR
    FROM Comentario c
    JOIN Usuario u ON u.id = c.id_usuario
    JOIN Video v ON v.id = c.id_video
    LEFT JOIN Doacao d ON d.id_comentario = c.id
    WHERE v.titulo = p_titulo_video
      AND c.online = TRUE
    ORDER BY c.data_hora;
END;
$$ LANGUAGE plpgsql;

-- ------------------------------------------------------------------------------
-- CONSULTA 5: Top patrocínios
-- ------------------------------------------------------------------------------
CREATE OR REPLACE FUNCTION sp_top_patrocinios(
    p_limite INTEGER DEFAULT 10
)
RETURNS TABLE (
    nome_empresa VARCHAR,
    nome_canal VARCHAR,
    nick_streamer VARCHAR,
    valor NUMERIC
) AS $$
BEGIN
    RETURN QUERY
    SELECT
        e.nome::VARCHAR,
        c.nome::VARCHAR,
        u.nick::VARCHAR,
        p.valor::NUMERIC
    FROM Patrocina p
    JOIN Empresa e ON e.id = p.id_empresa
    JOIN Canal c ON c.id = p.id_canal
    JOIN Streamer s ON s.id_usuario = c.id_streamer
    JOIN Usuario u ON u.id = s.id_usuario
    ORDER BY p.valor DESC
    LIMIT p_limite;
END;
$$ LANGUAGE plpgsql;

-- ------------------------------------------------------------------------------
-- CONSULTA 6: Collabs vs Solo (Corrigida via CTE)
-- ------------------------------------------------------------------------------
CREATE OR REPLACE FUNCTION sp_analise_collabs()
RETURNS TABLE (
    tipo_video VARCHAR,
    qtd_videos BIGINT,
    media_visualizacoes NUMERIC
) AS $$
BEGIN
    RETURN QUERY
    WITH classificado_videos AS (
        SELECT 
            v.id,
            v.visu_total,
            CASE 
                WHEN COUNT(p.id_streamer_convidado) > 0 THEN 'Collab'
                ELSE 'Solo'
            END AS tipo
        FROM Video v
        LEFT JOIN Participa p ON p.id_video = v.id
        GROUP BY v.id, v.visu_total
    )
    SELECT 
        cv.tipo::VARCHAR,
        COUNT(cv.id)::BIGINT,
        ROUND(AVG(cv.visu_total), 2)::NUMERIC
    FROM classificado_videos cv
    GROUP BY cv.tipo;
END;
$$ LANGUAGE plpgsql;

-- ------------------------------------------------------------------------------
-- CONSULTA 7: Conversão por país
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
        p.nome::VARCHAR,
        COUNT(DISTINCT u.id)::BIGINT,
        COUNT(DISTINCT s.id_usuario)::BIGINT,
        COUNT(DISTINCT m.id_usuario)::BIGINT
    FROM Pais p
    LEFT JOIN Usuario u ON u.ddi_pais_reside = p.ddi
    LEFT JOIN Streamer s ON s.id_usuario = u.id
    LEFT JOIN Membro m ON m.id_usuario = u.id
    GROUP BY p.nome;
END;
$$ LANGUAGE plpgsql;

-- ------------------------------------------------------------------------------
-- CONSULTA 8: Histórico de pagamentos
-- ------------------------------------------------------------------------------
CREATE OR REPLACE FUNCTION sp_historico_pagamentos(
    p_nick_usuario VARCHAR
)
RETURNS TABLE (
    id_doacao INTEGER,
    valor NUMERIC,
    status VARCHAR,
    metodo_pagamento VARCHAR
) AS $$
BEGIN
    RETURN QUERY
    SELECT
        d.id::INTEGER,
        d.valor::NUMERIC,
        d.status::VARCHAR,
        CASE
            WHEN cc.id_doacao IS NOT NULL THEN 'Cartao'
            WHEN pp.id_doacao IS NOT NULL THEN 'Paypal'
            WHEN btc.id_doacao IS NOT NULL THEN 'Bitcoin'
            WHEN mp.id_doacao IS NOT NULL THEN 'Plataforma'
            ELSE 'Desconhecido'
        END::VARCHAR
    FROM Doacao d
    JOIN Comentario c ON c.id = d.id_comentario
    JOIN Usuario u ON u.id = c.id_usuario
    LEFT JOIN Cartao_Cred cc ON cc.id_doacao = d.id
    LEFT JOIN Paypal pp ON pp.id_doacao = d.id
    LEFT JOIN BTC btc ON btc.id_doacao = d.id
    LEFT JOIN Mec_plat mp ON mp.id_doacao = d.id
    WHERE u.nick = p_nick_usuario
    ORDER BY d.id DESC;
END;
$$ LANGUAGE plpgsql;