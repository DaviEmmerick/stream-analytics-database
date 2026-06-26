
-- 1. ESTRUTURA CORPORATIVA E PAÍSES

CREATE TABLE Moeda (
    id SERIAL PRIMARY KEY, 
    nome_moeda VARCHAR(50) UNIQUE NOT NULL,
    fat_conversao DECIMAL(10, 4) NOT NULL CHECK (fat_conversao > 0)
);

CREATE TABLE Pais (
    ddi INT PRIMARY KEY, 
    nome VARCHAR(100) NOT NULL,
    id_moeda INT NOT NULL,
    FOREIGN KEY (id_moeda) REFERENCES Moeda(id)
);

CREATE TABLE Empresa (
    id SERIAL PRIMARY KEY,
    nome VARCHAR(150) NOT NULL,
    nome_fantasia VARCHAR(150),
    id_nacional VARCHAR(50) UNIQUE NOT NULL,
    ddi_pais_sede INT NOT NULL,
    FOREIGN KEY (ddi_pais_sede) REFERENCES Pais(ddi)
);

-- 2. PLATAFORMAS, USUÁRIOS E ESPECIALIZAÇÕES

CREATE TABLE Plataforma (
    id SERIAL PRIMARY KEY,
    nome VARCHAR(100) NOT NULL,
    qtd_usuarios INT,
    data_fundacao DATE,
    id_empresa_funda INT NOT NULL,
    id_empresa_resp INT NOT NULL,
    FOREIGN KEY (id_empresa_funda) REFERENCES Empresa(id),
    FOREIGN KEY (id_empresa_resp) REFERENCES Empresa(id)
);

CREATE TABLE Usuario (
    id SERIAL PRIMARY KEY,
    nick VARCHAR(50) UNIQUE NOT NULL, 
    email VARCHAR(150) UNIQUE NOT NULL,
    data_nasc DATE NOT NULL,
    telefone VARCHAR(30),
    end_postal VARCHAR(200),
    ddi_pais_reside INT NOT NULL,
    FOREIGN KEY (ddi_pais_reside) REFERENCES Pais(ddi)
);

CREATE TABLE Streamer (
    id_usuario INT PRIMARY KEY, 
    nro_passaporte VARCHAR(50) UNIQUE NOT NULL,
    ddi_pais_nacionalidade INT NOT NULL,
    FOREIGN KEY (id_usuario) REFERENCES Usuario(id) ON DELETE CASCADE,
    FOREIGN KEY (ddi_pais_nacionalidade) REFERENCES Pais(ddi)
);

CREATE TABLE Membro (
    id_usuario INT PRIMARY KEY,
    FOREIGN KEY (id_usuario) REFERENCES Usuario(id) ON DELETE CASCADE
);

CREATE TABLE TemConta (
    id_usuario INT NOT NULL,
    id_plataforma INT NOT NULL,
    nro_usuario VARCHAR(50) NOT NULL,
    PRIMARY KEY (id_usuario, id_plataforma),
    FOREIGN KEY (id_usuario) REFERENCES Usuario(id) ON DELETE CASCADE,
    FOREIGN KEY (id_plataforma) REFERENCES Plataforma(id)
);

-- 3. CANAIS, MONETIZAÇÃO E INSCRIÇÕES

CREATE TABLE Canal (
    id SERIAL PRIMARY KEY, 
    id_plataforma INT NOT NULL,
    id_streamer INT NOT NULL,
    nome VARCHAR(100) NOT NULL,
    tipo VARCHAR(50) CHECK (tipo IN ('privado', 'público', 'misto')),
    data_inicio DATE,
    descricao TEXT,
    qtd_videos INT DEFAULT 0,
    UNIQUE (nome, id_plataforma), 
    FOREIGN KEY (id_plataforma) REFERENCES Plataforma(id),
    FOREIGN KEY (id_streamer) REFERENCES Streamer(id_usuario) ON DELETE CASCADE
);

CREATE TABLE Patrocina (
    id_empresa INT NOT NULL,
    id_canal INT NOT NULL,
    valor DECIMAL(12, 2) NOT NULL CHECK (valor > 0),
    PRIMARY KEY (id_empresa, id_canal),
    FOREIGN KEY (id_empresa) REFERENCES Empresa(id),
    FOREIGN KEY (id_canal) REFERENCES Canal(id) ON DELETE CASCADE
);

CREATE TABLE NivelCanal (
    id_canal INT NOT NULL,
    nivel INT CHECK (nivel BETWEEN 1 AND 5),
    valor_nivel DECIMAL(10, 2) NOT NULL CHECK (valor_nivel > 0),
    gif VARCHAR(255),
    PRIMARY KEY (id_canal, nivel),
    FOREIGN KEY (id_canal) REFERENCES Canal(id) ON DELETE CASCADE
);

CREATE TABLE Inscricao (
    id_membro INT NOT NULL,
    id_canal INT NOT NULL,
    nivel INT NOT NULL,
    PRIMARY KEY (id_membro, id_canal),
    FOREIGN KEY (id_membro) REFERENCES Membro(id_usuario) ON DELETE CASCADE,
    FOREIGN KEY (id_canal, nivel) REFERENCES NivelCanal(id_canal, nivel) ON DELETE CASCADE
);

-- 4. VÍDEOS, PARTICIPAÇÕES E COMENTÁRIOS

CREATE TABLE Video (
    id SERIAL PRIMARY KEY,
    id_canal INT NOT NULL,
    titulo VARCHAR(150) NOT NULL,
    data_hora TIMESTAMP NOT NULL,
    duracao INT,
    visu_simulta INT DEFAULT 0,
    tema VARCHAR(100),
    visu_total INT DEFAULT 0,
    UNIQUE (id_canal, titulo, data_hora), 
    FOREIGN KEY (id_canal) REFERENCES Canal(id) ON DELETE CASCADE
);

CREATE TABLE Participa (
    id_video INT NOT NULL,
    id_streamer_convidado INT NOT NULL,
    PRIMARY KEY (id_video, id_streamer_convidado),
    FOREIGN KEY (id_video) REFERENCES Video(id) ON DELETE CASCADE,
    FOREIGN KEY (id_streamer_convidado) REFERENCES Streamer(id_usuario) ON DELETE CASCADE
);

CREATE TABLE Comentario (
    id SERIAL PRIMARY KEY,
    id_video INT NOT NULL,
    id_usuario INT NOT NULL,
    sequencial INT NOT NULL,
    texto TEXT NOT NULL,
    data_hora TIMESTAMP NOT NULL,
    online BOOLEAN DEFAULT TRUE,
    UNIQUE (id_video, sequencial), 
    FOREIGN KEY (id_video) REFERENCES Video(id) ON DELETE CASCADE,
    FOREIGN KEY (id_usuario) REFERENCES Usuario(id) ON DELETE CASCADE
);

-- 5. DOAÇÕES E ESPECIFICAÇÕES DE PAGAMENTO

CREATE TABLE Doacao (
    id SERIAL PRIMARY KEY,
    id_comentario INT UNIQUE NOT NULL, 
    valor DECIMAL(10, 2) NOT NULL CHECK (valor > 0),
    status VARCHAR(50) CHECK (status IN ('recusado', 'recebido', 'lido')),
    FOREIGN KEY (id_comentario) REFERENCES Comentario(id) ON DELETE CASCADE
);

CREATE TABLE Cartao_Cred (
    id_doacao INT PRIMARY KEY,                   
    numero VARCHAR(20) NOT NULL,
    bandeira VARCHAR(50) NOT NULL,
    data_hora_cartao TIMESTAMP NOT NULL,
    FOREIGN KEY (id_doacao) REFERENCES Doacao(id) ON DELETE CASCADE
);

CREATE TABLE Paypal (
    id_doacao INT PRIMARY KEY,                   
    id_paypal VARCHAR(100) NOT NULL,
    FOREIGN KEY (id_doacao) REFERENCES Doacao(id) ON DELETE CASCADE
);

CREATE TABLE BTC (
    id_doacao INT PRIMARY KEY,                   
    tx_id VARCHAR(150) NOT NULL,
    FOREIGN KEY (id_doacao) REFERENCES Doacao(id) ON DELETE CASCADE
);
    
CREATE TABLE Mec_plat (
    id_doacao INT PRIMARY KEY,                   
    sequencial_mec INT NOT NULL,
    FOREIGN KEY (id_doacao) REFERENCES Doacao(id) ON DELETE CASCADE
);