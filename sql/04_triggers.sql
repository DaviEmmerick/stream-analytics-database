-- ------------------------------------------------------------------------------
-- TRIGGER 1: Validação de Segurança (Impede Doações Negativas ou Zeradas)
-- Justificativa: Garante a integridade financeira da plataforma diretamente 
-- na camada de dados, impedindo bugs da aplicação que possam gerar "dinheiro negativo".
-- ------------------------------------------------------------------------------

-- 1.1 Criar a Função do Gatilho
CREATE OR REPLACE FUNCTION fn_valida_doacao()
RETURNS TRIGGER AS $$
BEGIN
    -- Se o valor que estão a tentar inserir (NEW.valor) for menor ou igual a zero, aborta!
    IF NEW.valor <= 0 THEN
        RAISE EXCEPTION 'Operação Bloqueada: O valor da doação deve ser estritamente maior que zero. Valor recebido: %', NEW.valor;
    END IF;
    
    -- Se estiver tudo bem, permite que a inserção continue
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- 1.2 Ligar o Gatilho à Tabela Doacao
DROP TRIGGER IF EXISTS trg_valida_doacao ON Doacao;

CREATE TRIGGER trg_valida_doacao
BEFORE INSERT OR UPDATE ON Doacao
FOR EACH ROW
EXECUTE FUNCTION fn_valida_doacao();


-- ------------------------------------------------------------------------------
-- TRIGGER 2: Automatização (Atualiza o contador de vídeos do Canal)
-- Justificativa: Manter dados agregados (desnormalizados) atualizados automaticamente 
-- melhora a performance de leitura do perfil do Canal.
-- ------------------------------------------------------------------------------

-- 2.1 Criar a Função do Gatilho
CREATE OR REPLACE FUNCTION fn_atualiza_qtd_videos()
RETURNS TRIGGER AS $$
BEGIN
    -- Se a ação for um NOVO vídeo (INSERT)
    IF TG_OP = 'INSERT' THEN
        UPDATE Canal
        SET qtd_videos = qtd_videos + 1
        WHERE nome = NEW.nome_canal 
          AND nro_plataforma = NEW.nro_plataforma 
          AND nick_streamer = NEW.nick_streamer;
        RETURN NEW;
        
    -- Se a ação for APAGAR um vídeo (DELETE)
    ELSIF TG_OP = 'DELETE' THEN
        UPDATE Canal
        SET qtd_videos = qtd_videos - 1
        WHERE nome = OLD.nome_canal 
          AND nro_plataforma = OLD.nro_plataforma 
          AND nick_streamer = OLD.nick_streamer;
        RETURN OLD;
    END IF;
    
    RETURN NULL;
END;
$$ LANGUAGE plpgsql;

-- 2.2 Ligar o Gatilho à Tabela Video
DROP TRIGGER IF EXISTS trg_atualiza_qtd_videos ON Video;

CREATE TRIGGER trg_atualiza_qtd_videos
AFTER INSERT OR DELETE ON Video
FOR EACH ROW
EXECUTE FUNCTION fn_atualiza_qtd_videos();
