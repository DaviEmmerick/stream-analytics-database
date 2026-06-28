-- A. Comentários por vídeo em ordem cronológica (corrige o índice #3)
CREATE INDEX idx_comentario_video_data ON Comentario(id_video, data_hora);
-- Justificativa: a consulta real do chat é "WHERE id_video = X ORDER BY data_hora".
-- Sem id_video na composição, o índice de data isolado não elimina o scan na tabela toda.
-- Overhead de insert: alto volume de comentários, mas o ganho de leitura supera,
-- já que essa é a query mais executada da plataforma (toda vez que alguém abre um vídeo).

-- B. Ranking real de doadores (corrige o problema do índice #2)
CREATE INDEX idx_comentario_usuario ON Comentario(id_usuario);
-- Justificativa: para somar doações por usuário é preciso join Doacao -> Comentario -> Usuario.
-- Esse índice de apoio acelera esse join, que hoje não tem nenhum índice de suporte
-- (id_usuario em Comentario não tem índice e é FK de alto volume).

-- C. Inscrições ativas por canal (suporte a "quantos membros tem o canal")
CREATE INDEX idx_inscricao_canal ON Inscricao(id_canal);
-- Justificativa: contagem de inscritos por canal é uma métrica exibida constantemente
-- (estilo "X inscritos"). A PK é (id_membro, id_canal), então buscar por id_canal isolado
-- não usa a PK eficientemente — Postgres teria que escanear o índice inteiro.

-- D. Vídeos por canal ordenados por data (página do canal)
CREATE INDEX idx_video_canal_data ON Video(id_canal, data_hora DESC);
-- Justificativa: a tela de "vídeos do canal X, mais recentes primeiro" é uma das mais acessadas.
-- UNIQUE(id_canal, titulo, data_hora) existente não serve essa ordenação por data sozinha
-- pois titulo está no meio da chave.

-- E. Status de doação para fila de processamento/moderação
CREATE INDEX idx_doacao_status ON Doacao(status) WHERE status <> 'lido';
-- Justificativa: índice parcial — útil pois o caso de uso real é encontrar rapidamente
-- doações pendentes ('recebido') para exibir/processar, e cardinalidade de status não-lido
-- é uma fração pequena da tabela total ao longo do tempo. Índice parcial reduz overhead
-- de escrita comparado a indexar a coluna inteira.