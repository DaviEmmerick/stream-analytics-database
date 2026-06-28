CREATE INDEX idx_patrocina_canal
    ON Patrocina (id_canal) INCLUDE (valor);


CREATE INDEX idx_inscricao_canal_nivel
    ON Inscricao (id_canal, nivel);


CREATE INDEX idx_nivelcanal_valor
    ON NivelCanal (id_canal, nivel) INCLUDE (valor_nivel);


CREATE INDEX idx_doacao_validas
    ON Doacao (id_comentario) INCLUDE (valor)
    WHERE status IN ('recebido', 'lido');


CREATE INDEX idx_video_canal
    ON Video (id_canal) INCLUDE (id);

