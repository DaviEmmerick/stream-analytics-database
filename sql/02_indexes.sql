CREATE INDEX idx_patrocina_canal
    ON Patrocina (id_canal) INCLUDE (valor);

CREATE INDEX idx_nivelcanal_valor
    ON NivelCanal (id_canal, nivel) INCLUDE (valor_nivel);

CREATE INDEX idx_video_canal
    ON Video (id_canal) INCLUDE (id);

CREATE INDEX idx_comentario_video
    ON Comentario (id_video) INCLUDE (id);


CREATE INDEX idx_inscricao_membro_canal_nivel
    ON Inscricao (id_membro, id_canal, nivel);

