CREATE OR REPLACE VIEW v_patrocinio_por_canal AS
SELECT
    c.id          AS id_canal,
    c.nome        AS nome_canal,
    e.id          AS id_empresa,
    e.nome        AS nome_empresa,
    p.valor       AS valor_patrocinio
FROM Patrocina p
JOIN Canal   c ON c.id = p.id_canal
JOIN Empresa e ON e.id = p.id_empresa;

-- SP 1: id_empresa é parâmetro opcional
CREATE OR REPLACE PROCEDURE sp_patrocinio_por_canal(
    p_id_empresa INT DEFAULT NULL
)
LANGUAGE plpgsql AS $$
BEGIN
    IF p_id_empresa IS NULL THEN
        SELECT id_empresa, nome_empresa, id_canal, nome_canal, valor_patrocinio
        FROM   v_patrocinio_por_canal
        ORDER BY id_empresa, valor_patrocinio DESC;
    ELSE
        SELECT id_empresa, nome_empresa, id_canal, nome_canal, valor_patrocinio
        FROM   v_patrocinio_por_canal
        WHERE  id_empresa = p_id_empresa
        ORDER BY valor_patrocinio DESC;
    END IF;
END;
$$;


CREATE OR REPLACE VIEW v_membros_por_usuario AS
SELECT
    m.id_usuario,
    u.nick              AS nick_usuario,
    COUNT(i.id_canal)   AS qtd_canais,
    SUM(nc.valor_nivel) AS total_mensal
FROM Membro     m
JOIN Usuario    u  ON u.id        = m.id_usuario
JOIN Inscricao  i  ON i.id_membro = m.id_usuario
JOIN NivelCanal nc ON nc.id_canal = i.id_canal
                  AND nc.nivel    = i.nivel
GROUP BY m.id_usuario, u.nick;

-- SP 2: id_usuario é parâmetro opcional
CREATE OR REPLACE PROCEDURE sp_membros_por_usuario(
    p_id_usuario INT DEFAULT NULL
)
LANGUAGE plpgsql AS $$
BEGIN
    IF p_id_usuario IS NULL THEN
        SELECT id_usuario, nick_usuario, qtd_canais, total_mensal
        FROM   v_membros_por_usuario
        ORDER BY total_mensal DESC;
    ELSE
        SELECT id_usuario, nick_usuario, qtd_canais, total_mensal
        FROM   v_membros_por_usuario
        WHERE  id_usuario = p_id_usuario;
    END IF;
END;
$$;


CREATE OR REPLACE VIEW v_doacoes_por_canal AS
SELECT
    c.id            AS id_canal,
    c.nome          AS nome_canal,
    COUNT(d.id)     AS qtd_doacoes,
    SUM(d.valor)    AS total_doacoes
FROM Doacao     d
JOIN Comentario cm ON cm.id    = d.id_comentario
JOIN Video       v ON v.id     = cm.id_video
JOIN Canal       c ON c.id     = v.id_canal
WHERE d.status IN ('recebido', 'lido')
GROUP BY c.id, c.nome;

-- SP 3: id_canal é parâmetro opcional; resultado ordenado por total
CREATE OR REPLACE PROCEDURE sp_doacoes_por_canal(
    p_id_canal INT DEFAULT NULL
)
LANGUAGE plpgsql AS $$
BEGIN
    IF p_id_canal IS NULL THEN
        SELECT id_canal, nome_canal, qtd_doacoes, total_doacoes
        FROM   v_doacoes_por_canal
        ORDER BY total_doacoes DESC;
    ELSE
        SELECT id_canal, nome_canal, qtd_doacoes, total_doacoes
        FROM   v_doacoes_por_canal
        WHERE  id_canal = p_id_canal;
    END IF;
END;
$$;


CREATE OR REPLACE VIEW v_doacoes_lidas_por_video AS
SELECT
    v.id            AS id_video,
    v.titulo        AS titulo_video,
    c.id            AS id_canal,
    c.nome          AS nome_canal,
    COUNT(d.id)     AS qtd_lidas,
    SUM(d.valor)    AS total_lidas
FROM Doacao     d
JOIN Comentario cm ON cm.id    = d.id_comentario
JOIN Video       v ON v.id     = cm.id_video
JOIN Canal       c ON c.id     = v.id_canal
WHERE d.status = 'lido'
GROUP BY v.id, v.titulo, c.id, c.nome;

-- SP 4: id_video é parâmetro opcional
CREATE OR REPLACE PROCEDURE sp_doacoes_lidas_por_video(
    p_id_video INT DEFAULT NULL
)
LANGUAGE plpgsql AS $$
BEGIN
    IF p_id_video IS NULL THEN
        SELECT id_video, titulo_video, nome_canal, qtd_lidas, total_lidas
        FROM   v_doacoes_lidas_por_video
        ORDER BY total_lidas DESC;
    ELSE
        SELECT id_video, titulo_video, nome_canal, qtd_lidas, total_lidas
        FROM   v_doacoes_lidas_por_video
        WHERE  id_video = p_id_video;
    END IF;
END;
$$;


CREATE MATERIALIZED VIEW mv_receita_canal AS
WITH receita_patrocinio AS (
    SELECT id_canal,
           COALESCE(SUM(valor), 0)       AS total_patrocinio
    FROM   Patrocina
    GROUP BY id_canal
),
receita_membros AS (
    SELECT i.id_canal,
           COALESCE(SUM(nc.valor_nivel), 0) AS total_membros
    FROM   Inscricao  i
    JOIN   NivelCanal nc ON nc.id_canal = i.id_canal
                        AND nc.nivel    = i.nivel
    GROUP BY i.id_canal
),
receita_doacoes AS (
    SELECT v.id_canal,
           COALESCE(SUM(d.valor), 0)     AS total_doacoes
    FROM   Doacao     d
    JOIN   Comentario cm ON cm.id  = d.id_comentario
    JOIN   Video       v ON v.id   = cm.id_video
    WHERE  d.status IN ('recebido', 'lido')
    GROUP BY v.id_canal
)
SELECT
    c.id                                      AS id_canal,
    c.nome                                    AS nome_canal,
    COALESCE(rp.total_patrocinio, 0)          AS total_patrocinio,
    COALESCE(rm.total_membros,    0)          AS total_membros,
    COALESCE(rd.total_doacoes,    0)          AS total_doacoes,
    COALESCE(rp.total_patrocinio, 0)
    + COALESCE(rm.total_membros,  0)
    + COALESCE(rd.total_doacoes,  0)          AS total_faturamento
FROM   Canal c
LEFT JOIN receita_patrocinio rp ON rp.id_canal = c.id
LEFT JOIN receita_membros    rm ON rm.id_canal = c.id
LEFT JOIN receita_doacoes    rd ON rd.id_canal = c.id
WITH DATA;


CREATE OR REPLACE FUNCTION fn_auto_sequencial_comentario()
RETURNS TRIGGER LANGUAGE plpgsql AS $$
DECLARE
    v_proximo INT;
BEGIN
    -- Lock advisory por vídeo: evita race condition sem bloquear a tabela inteira
    PERFORM pg_advisory_xact_lock(NEW.id_video::BIGINT);

    SELECT COALESCE(MAX(sequencial), 0) + 1
      INTO v_proximo
      FROM Comentario
     WHERE id_video = NEW.id_video;

    NEW.sequencial := v_proximo;
    RETURN NEW;
END;
$$;

CREATE OR REPLACE TRIGGER tg_auto_sequencial_comentario
    BEFORE INSERT ON Comentario
    FOR EACH ROW
    EXECUTE FUNCTION fn_auto_sequencial_comentario();



CREATE OR REPLACE FUNCTION fn_qtd_videos_increment()
RETURNS TRIGGER LANGUAGE plpgsql AS $$
BEGIN
    UPDATE Canal
       SET qtd_videos = qtd_videos + 1
     WHERE id = NEW.id_canal;
    RETURN NEW;
END;
$$;

CREATE OR REPLACE TRIGGER tg_qtd_videos_insert
    AFTER INSERT ON Video
    FOR EACH ROW
    EXECUTE FUNCTION fn_qtd_videos_increment();

-- ----

CREATE OR REPLACE FUNCTION fn_qtd_videos_decrement()
RETURNS TRIGGER LANGUAGE plpgsql AS $$
BEGIN
    UPDATE Canal
       SET qtd_videos = GREATEST(qtd_videos - 1, 0)
     WHERE id = OLD.id_canal;
    RETURN OLD;
END;
$$;

CREATE OR REPLACE TRIGGER tg_qtd_videos_delete
    AFTER DELETE ON Video
    FOR EACH ROW
    EXECUTE FUNCTION fn_qtd_videos_decrement();

-- ----
-- Caso raro: vídeo movido de canal (UPDATE id_canal)
CREATE OR REPLACE FUNCTION fn_qtd_videos_update()
RETURNS TRIGGER LANGUAGE plpgsql AS $$
BEGIN
    IF OLD.id_canal <> NEW.id_canal THEN
        UPDATE Canal SET qtd_videos = GREATEST(qtd_videos - 1, 0) WHERE id = OLD.id_canal;
        UPDATE Canal SET qtd_videos = qtd_videos + 1               WHERE id = NEW.id_canal;
    END IF;
    RETURN NEW;
END;
$$;

CREATE OR REPLACE TRIGGER tg_qtd_videos_update
    AFTER UPDATE OF id_canal ON Video
    FOR EACH ROW
    WHEN (OLD.id_canal IS DISTINCT FROM NEW.id_canal)
    EXECUTE FUNCTION fn_qtd_videos_update();


CREATE OR REPLACE FUNCTION fn_doacao_tipo_exclusivo()
RETURNS TRIGGER LANGUAGE plpgsql AS $$
DECLARE
    v_count INT;
    v_tabela_origem TEXT := TG_TABLE_NAME;  -- nome da tabela que disparou
BEGIN
    SELECT (
        CASE WHEN v_tabela_origem <> 'cartao_cred' THEN
            (SELECT COUNT(*) FROM Cartao_Cred WHERE id_doacao = NEW.id_doacao)
        ELSE 0 END
        +
        CASE WHEN v_tabela_origem <> 'paypal' THEN
            (SELECT COUNT(*) FROM Paypal WHERE id_doacao = NEW.id_doacao)
        ELSE 0 END
        +
        CASE WHEN v_tabela_origem <> 'btc' THEN
            (SELECT COUNT(*) FROM BTC WHERE id_doacao = NEW.id_doacao)
        ELSE 0 END
        +
        CASE WHEN v_tabela_origem <> 'mec_plat' THEN
            (SELECT COUNT(*) FROM Mec_plat WHERE id_doacao = NEW.id_doacao)
        ELSE 0 END
    ) INTO v_count;

    IF v_count > 0 THEN
        RAISE EXCEPTION
            'Doacao id=% já possui um tipo de pagamento registrado. '
            'Cada doação deve ter exatamente um tipo.',
            NEW.id_doacao;
    END IF;

    RETURN NEW;
END;
$$;

CREATE OR REPLACE TRIGGER tg_cartao_tipo_exclusivo
    BEFORE INSERT ON Cartao_Cred
    FOR EACH ROW
    EXECUTE FUNCTION fn_doacao_tipo_exclusivo();

CREATE OR REPLACE TRIGGER tg_paypal_tipo_exclusivo
    BEFORE INSERT ON Paypal
    FOR EACH ROW
    EXECUTE FUNCTION fn_doacao_tipo_exclusivo();

CREATE OR REPLACE TRIGGER tg_btc_tipo_exclusivo
    BEFORE INSERT ON BTC
    FOR EACH ROW
    EXECUTE FUNCTION fn_doacao_tipo_exclusivo();

CREATE OR REPLACE TRIGGER tg_mecplat_tipo_exclusivo
    BEFORE INSERT ON Mec_plat
    FOR EACH ROW
    EXECUTE FUNCTION fn_doacao_tipo_exclusivo();


CREATE OR REPLACE FUNCTION fn_doacao_status_transicao()
RETURNS TRIGGER LANGUAGE plpgsql AS $$
BEGIN
    -- Status não mudou: ok
    IF OLD.status = NEW.status THEN
        RETURN NEW;
    END IF;

    -- 'recusado' é estado final — nenhuma transição permitida
    IF OLD.status = 'recusado' THEN
        RAISE EXCEPTION
            'Doacao id=%: status "recusado" é final e não pode ser alterado.',
            OLD.id;
    END IF;

    -- 'lido' é estado final — nenhuma transição permitida
    IF OLD.status = 'lido' THEN
        RAISE EXCEPTION
            'Doacao id=%: status "lido" é final e não pode ser alterado.',
            OLD.id;
    END IF;

    -- 'recebido' → apenas 'lido' é permitido
    IF OLD.status = 'recebido' AND NEW.status <> 'lido' THEN
        RAISE EXCEPTION
            'Doacao id=%: transição inválida de "recebido" para "%". '
            'Única transição permitida: recebido → lido.',
            OLD.id, NEW.status;
    END IF;

    RETURN NEW;
END;
$$;

CREATE OR REPLACE TRIGGER tg_doacao_status_transicao
    BEFORE UPDATE OF status ON Doacao
    FOR EACH ROW
    EXECUTE FUNCTION fn_doacao_status_transicao();


CREATE OR REPLACE FUNCTION fn_patrocinio_upsert()
RETURNS TRIGGER LANGUAGE plpgsql AS $$
DECLARE
    v_existe INT;
BEGIN
    SELECT COUNT(*) INTO v_existe
      FROM Patrocina
     WHERE id_empresa = NEW.id_empresa
       AND id_canal   = NEW.id_canal;

    IF v_existe > 0 THEN
        -- Atualiza o valor do patrocínio vigente (renovação)
        UPDATE Patrocina
           SET valor = NEW.valor
         WHERE id_empresa = NEW.id_empresa
           AND id_canal   = NEW.id_canal;

        -- Cancela o INSERT original (já tratamos via UPDATE)
        RETURN NULL;
    END IF;

    RETURN NEW;
END;
$$;

CREATE OR REPLACE TRIGGER tg_patrocinio_upsert
    BEFORE INSERT ON Patrocina
    FOR EACH ROW
    EXECUTE FUNCTION fn_patrocinio_upsert();


CREATE OR REPLACE FUNCTION fn_inscricao_upsert()
RETURNS TRIGGER LANGUAGE plpgsql AS $$
DECLARE
    v_existe INT;
BEGIN
    SELECT COUNT(*) INTO v_existe
      FROM Inscricao
     WHERE id_membro = NEW.id_membro
       AND id_canal  = NEW.id_canal;

    IF v_existe > 0 THEN
        -- Atualiza o nível da inscrição vigente (mudança de nível)
        UPDATE Inscricao
           SET nivel = NEW.nivel
         WHERE id_membro = NEW.id_membro
           AND id_canal  = NEW.id_canal;

        -- Cancela o INSERT original
        RETURN NULL;
    END IF;

    RETURN NEW;
END;
$$;

CREATE OR REPLACE TRIGGER tg_inscricao_upsert
    BEFORE INSERT ON Inscricao
    FOR EACH ROW
    EXECUTE FUNCTION fn_inscricao_upsert();

