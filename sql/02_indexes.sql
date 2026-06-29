-- 1. Índice de cobertura na tabela Patrocina.
-- Justificativa: Cobre as operações de JOIN e elimina a necessidade de acessar 
-- a tabela original (heap lookup) para resgatar o campo 'valor'.
CREATE INDEX idx_patrocina_canal
    ON Patrocina (id_canal) INCLUDE (valor);

-- 2. Índice composto de cobertura na tabela NivelCanal.
-- Justificativa: A chave composta cobre eficientemente o 'ON' duplo exigido 
-- nos JOINs com a tabela de Inscricao, já entregando o 'valor_nivel' pelas folhas da B-Tree.
CREATE INDEX idx_nivelcanal_valor
    ON NivelCanal (id_canal, nivel) INCLUDE (valor_nivel);

-- 3. Índice de cobertura na tabela Video.
-- Justificativa: Cobre o caminho crítico das consultas de agregação de receita, 
-- acelerando os saltos de busca na cadeia de doações.
CREATE INDEX idx_video_canal
    ON Video (id_canal) INCLUDE (id);

-- 4. Índice de cobertura na tabela Comentario.
-- Justificativa: Novo índice criado para cobrir o único "hop" (salto) que não 
-- possuía índice na navegação completa via nested loop: Doacao -> Comentario -> Video -> Canal.
CREATE INDEX idx_comentario_video
    ON Comentario (id_video) INCLUDE (id);

-- 5. Índice composto na tabela Inscricao.
-- Justificativa: Índice novo e abrangente. A ordem das colunas cobre tanto a busca 
-- isolada por membro (prefixo) quanto os JOINs específicos por canal+nivel (sufixo), 
-- otimizando a indexação sem inchar o disco com índices redundantes.
CREATE INDEX idx_inscricao_membro_canal_nivel
    ON Inscricao (id_membro, id_canal, nivel);
