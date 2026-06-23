-- 1. ÍNDICE POR TEMA DE VÍDEO (B-TREE)
-- Trade-off: Aumenta o custo de inserção de novos vídeos, mas acelera brutalmente 
-- a filtragem de buscas na plataforma (Ex: "Mostrar todos os vídeos de RPG").
CREATE INDEX idx_video_tema ON Video(tema);

-- 2. ÍNDICE POR VALOR DE DOAÇÃO (B-TREE)
-- Trade-off: Doações ocorrem com alta frequência em lives, o que gera overhead de escrita.
-- Porém, é essencial para gerar o ranking em tempo real dos "Maiores Apoiadores" (Top Donators).
CREATE INDEX idx_doacao_valor ON Doacao(valor DESC);

-- 3. ÍNDICE POR DATA DE COMENTÁRIO (B-TREE)
-- Trade-off: Comentários são a entidade com maior volume de INSERTS (overhead alto).
-- Contudo, sem este índice, carregar o chat de um vídeo por ordem cronológica exigiria um Full Table Scan.
CREATE INDEX idx_comentario_data ON Comentario(data_hora);

-- 4. ÍNDICE POR PAÍS DE RESIDÊNCIA DO USUÁRIO (HASH)
-- Trade-off: Baixo impacto em updates (usuários raramente mudam de país).
-- Excelente benefício de leitura para cruzar métricas demográficas de público.
CREATE INDEX idx_usuario_pais ON Usuario(ddi_pais_reside);

-- 5. ÍNDICE COMPOSTO DE PARTICIPAÇÕES (B-TREE)
-- Trade-off: Custo médio de escrita. 
-- Justificativa: Consultas para saber "quais streamers participaram juntos num vídeo" são complexas.
-- Este índice acelera a recuperação de colaborações na plataforma.
CREATE INDEX idx_participa_streamer_video ON Participa(nick_streamer_convidado, titulo_video);
