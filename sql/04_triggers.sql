-- ------------------------------------------------------------------------------
-- TRIGGER 1: Validação de Segurança (Impede Doações Negativas ou Zeradas)
-- ------------------------------------------------------------------------------

CREATE OR REPLACE FUNCTION fn_valida_doacao()
RETURNS TRIGGER AS $$

BEGIN
    IF NEW.valor <= 0 THEN

        RAISE EXCEPTION 
        'Operação Bloqueada: O valor da doação deve ser maior que zero. Valor recebido: %',
        NEW.valor;

    END IF;
    RETURN NEW;

END;

$$ LANGUAGE plpgsql;
DROP TRIGGER IF EXISTS trg_valida_doacao ON Doacao;

CREATE TRIGGER trg_valida_doacao

BEFORE INSERT OR UPDATE ON Doacao

FOR EACH ROW

EXECUTE FUNCTION fn_valida_doacao();

-- ------------------------------------------------------------------------------
-- TRIGGER 2: Atualização automática da quantidade de vídeos do Canal
-- ------------------------------------------------------------------------------

CREATE OR REPLACE FUNCTION fn_atualiza_qtd_videos()
RETURNS TRIGGER AS $$
BEGIN

    -- Quando inserir vídeo
    IF TG_OP = 'INSERT' THEN
        UPDATE Canal

        SET qtd_videos = qtd_videos + 1

        WHERE id = NEW.id_canal;


        RETURN NEW;

    -- Quando remover vídeo
    ELSIF TG_OP = 'DELETE' THEN
        UPDATE Canal

        SET qtd_videos = qtd_videos - 1

        WHERE id = OLD.id_canal;

        RETURN OLD;
    END IF;
    RETURN NULL;


END;

$$ LANGUAGE plpgsql;

DROP TRIGGER IF EXISTS trg_atualiza_qtd_videos ON Video;
CREATE TRIGGER trg_atualiza_qtd_videos

AFTER INSERT OR DELETE ON Video

FOR EACH ROW

EXECUTE FUNCTION fn_atualiza_qtd_videos();