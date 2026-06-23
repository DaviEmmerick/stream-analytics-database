-- 1. VIEW DE RESUMO FINANCEIRO DOS CANAIS
-- Justificativa: Agrega os patrocínios recebidos por cada canal. 
-- Facilita relatórios gerenciais sem expor as chaves primárias e detalhes técnicos da tabela Empresa.
CREATE OR REPLACE VIEW vw_resumo_financeiro_canal AS
SELECT 
    c.nome AS nome_canal,
    c.nick_streamer,
    e.nome AS nome_empresa_patrocinadora,
    p.valor AS valor_patrocinio
FROM Canal c
JOIN Patrocina p ON c.nome = p.nome_canal 
    AND c.nro_plataforma = p.nro_plataforma 
    AND c.nick_streamer = p.nick_streamer
JOIN Empresa e ON p.nro_empresa = e.numero;

-- 2. VIEW DE ENGAJAMENTO DOS VÍDEOS
-- Justificativa: Consolida métricas de audiência (simultânea e total) com a duração.
-- Ideal para o painel de "Analytics" do Streamer, evitando JOINs repetitivos com a tabela Canal.
CREATE OR REPLACE VIEW vw_engajamento_videos AS
SELECT 
    v.titulo,
    v.tema,
    v.duracao,
    v.visu_simulta AS espectadores_simultaneos,
    v.visu_total AS visualizacoes_totais,
    c.tipo AS tipo_canal
FROM Video v
JOIN Canal c ON v.nome_canal = c.nome 
    AND v.nro_plataforma = c.nro_plataforma 
    AND v.nick_streamer = c.nick_streamer
WHERE v.visu_total > 0;

-- 3. VIEW DE SUPERCHATS (DOAÇÕES MAIORES QUE 100)
-- Justificativa: Filtra apenas as doações de alto valor (Superchats VIPs).
-- Melhora a segurança permitindo que moderadores vejam as mensagens VIP sem acessar dados de pagamentos bancários.
CREATE OR REPLACE VIEW vw_superchats_vip AS
SELECT 
    d.nick_usuario AS doador,
    d.valor,
    d.status,
    c.texto AS mensagem,
    d.titulo_video
FROM Doacao d
JOIN Comentario c ON d.sequencial_coment = c.sequencial
    AND d.titulo_video = c.titulo_video
WHERE d.valor >= 100.00
ORDER BY d.valor DESC;
