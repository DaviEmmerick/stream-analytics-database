-- TRIGGER 1: Manter a qtd de usuários da plataforma atualizados

CREATE OR REPLACE FUNCTION fn_atualiza_qtd_usuarios_plat()
RETURNS TRIGGER AS $$
BEGIN
    
    IF TG_OP = 'INSERT' THEN
    
        UPDATE Plataforma SET qtd_usuarios = COALESCE(qtd_usuarios, 0) + 1 WHERE id = NEW.id_plataforma;

        RETURN NEW;

    ELSIF TG_OP = 'DELETE' THEN
        
        UPDATE Plataforma SET qtd_usuarios = qtd_usuarios - 1 WHERE id = OLD.id_plataforma;

        RETURN OLD;

    ELSIF TG_OP = 'UPDATE' THEN
        
        IF OLD.id_plataforma <> NEW.id_plataforma THEN
        
            UPDATE Plataforma SET qtd_usuarios = qtd_usuarios - 1 WHERE id = OLD.id_plataforma;
            UPDATE Plataforma SET qtd_usuarios = COALESCE(qtd_usuarios, 0) + 1 WHERE id = NEW.id_plataforma;

        END IF;

        RETURN NEW;

    END IF;
    RETURN NULL;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trg_atualiza_qtd_usuarios
AFTER INSERT OR DELETE OR UPDATE ON TemConta
FOR EACH ROW EXECUTE FUNCTION fn_atualiza_qtd_usuarios_plat();

-- TRIGGER 2: Atualização automática da quantidade de vídeos do Canal

CREATE OR REPLACE FUNCTION fn_atualiza_qtd_videos()
RETURNS TRIGGER AS $$
BEGIN

    IF TG_OP = 'INSERT' THEN
        UPDATE Canal

        SET qtd_videos = qtd_videos + 1

        WHERE id = NEW.id_canal;


        RETURN NEW;

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

-- TRIGGER 3: Garantir a exclusividade do pagamento

CREATE OR REPLACE FUNCTION fn_pagamento_exclusivo()
RETURNS TRIGGER AS $$
DECLARE
    qtd_encontrada INT;
BEGIN
    -- Soma quantas vezes esse id_doacao aparece nas 4 tabelas de pagamento
    SELECT (
        (SELECT COUNT(*) FROM Cartao_Cred WHERE id_doacao = NEW.id_doacao) +
        (SELECT COUNT(*) FROM Paypal WHERE id_doacao = NEW.id_doacao) +
        (SELECT COUNT(*) FROM BTC WHERE id_doacao = NEW.id_doacao) +
        (SELECT COUNT(*) FROM Mec_plat WHERE id_doacao = NEW.id_doacao)
    
    ) INTO qtd_encontrada;

    -- Se já encontrou em alguma, bloqueia a inserção
    IF qtd_encontrada > 0 THEN
        
        RAISE EXCEPTION 'Erro de Integridade: Esta doação (ID %) já possui um método de pagamento registrado.', NEW.id_doacao;

    END IF;

    RETURN NEW;
END;

$$ LANGUAGE plpgsql;

CREATE TRIGGER trg_exclusivo_cartao BEFORE INSERT ON Cartao_Cred FOR EACH ROW EXECUTE FUNCTION fn_pagamento_exclusivo();
CREATE TRIGGER trg_exclusivo_paypal BEFORE INSERT ON Paypal FOR EACH ROW EXECUTE FUNCTION fn_pagamento_exclusivo();
CREATE TRIGGER trg_exclusivo_btc BEFORE INSERT ON BTC FOR EACH ROW EXECUTE FUNCTION fn_pagamento_exclusivo();
CREATE TRIGGER trg_exclusivo_mec BEFORE INSERT ON Mec_plat FOR EACH ROW EXECUTE FUNCTION fn_pagamento_exclusivo();