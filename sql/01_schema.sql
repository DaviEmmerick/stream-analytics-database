
CREATE TABLE Moeda (
    id INT PRIMARY KEY,                         
    nome_moeda VARCHAR(50) UNIQUE NOT NULL,
    fat_conversao DECIMAL(10, 4) NOT NULL
);

CREATE TABLE Pais (
    ddi INT PRIMARY KEY,                         
    nome VARCHAR(100) NOT NULL,
    nome_moeda VARCHAR(50) NOT NULL,
    FOREIGN KEY (nome_moeda) REFERENCES Moeda(nome_moeda)
);

CREATE TABLE Empresa (
    numero INT  NOT NULL PRIMARY KEY,
    nome VARCHAR(150) NOT NULL,
    nome_fantasia VARCHAR(150),
    id_nacional VARCHAR(50) UNIQUE NOT NULL,
    ddi_pais_sede INT NOT NULL,
    FOREIGN KEY (ddi_pais_sede) REFERENCES Pais(ddi)
);

-- 2. PLATAFORMAS, USUÁRIOS E ESPECIALIZAÇÕES

CREATE TABLE Plataforma (
    numero INT PRIMARY KEY,                      
    nome VARCHAR(100) NOT NULL,
    qtd_usuarios INT,
    data_fundacao DATE,
    empresa_funda_nro INT NOT NULL,
    empresa_resp_nro INT NOT NULL,
    FOREIGN KEY (empresa_funda_nro) REFERENCES Empresa(numero),
    FOREIGN KEY (empresa_resp_nro) REFERENCES Empresa(numero)
);

CREATE TABLE Usuario (
    id INT PRIMARY KEY,                         
    nick VARCHAR(50) UNIQUE NOT NULL,           
    email VARCHAR(150) UNIQUE NOT NULL,
    data_nasc DATE NOT NULL,
    telefone VARCHAR(30),
    end_postal VARCHAR(200),
    ddi_pais_reside INT NOT NULL,
    FOREIGN KEY (ddi_pais_reside) REFERENCES Pais(ddi)
);

CREATE TABLE Streamer (
    id INT PRIMARY KEY,                          
    nick_streamer VARCHAR(50) UNIQUE NOT NULL,   
    nro_passaporte VARCHAR(50) UNIQUE NOT NULL,
    ddi_pais_nacionalidade INT NOT NULL,
    FOREIGN KEY (nick_streamer) REFERENCES Usuario(nick) ON DELETE CASCADE,
    FOREIGN KEY (ddi_pais_nacionalidade) REFERENCES Pais(ddi)
);

CREATE TABLE Membro (                            
    id INT PRIMARY KEY,
    nick_membro VARCHAR(50) UNIQUE NOT NULL,
    FOREIGN KEY (nick_membro) REFERENCES Usuario(nick) ON DELETE CASCADE
);

CREATE TABLE TemConta (
    id INT PRIMARY KEY,                          
    nick_usuario VARCHAR(50),
    nro_plataforma INT,
    nro_usuario VARCHAR(50) UNIQUE NOT NULL,
    FOREIGN KEY (nick_usuario) REFERENCES Usuario(nick) ON DELETE CASCADE,
    FOREIGN KEY (nro_plataforma) REFERENCES Plataforma(numero)
);

-- 3. CANAIS, MONETIZAÇÃO E INSCRIÇÕES

CREATE TABLE Canal (
    id INT PRIMARY KEY,                          
    nome VARCHAR(100),
    nro_plataforma INT,
    nick_streamer VARCHAR(50),
    tipo VARCHAR(50),
    data_inicio DATE,
    descricao TEXT,
    qtd_videos INT DEFAULT 0,
    UNIQUE (nome, nro_plataforma, nick_streamer), 
    FOREIGN KEY (nro_plataforma) REFERENCES Plataforma(numero),
    FOREIGN KEY (nick_streamer) REFERENCES Streamer(nick_streamer) ON DELETE CASCADE
);

CREATE TABLE Patrocina (
    id INT PRIMARY KEY,                          
    nro_empresa INT,
    nome_canal VARCHAR(100),
    nro_plataforma INT,
    nick_streamer VARCHAR(50),
    valor DECIMAL(12, 2) NOT NULL,
    FOREIGN KEY (nro_empresa) REFERENCES Empresa(numero),
    FOREIGN KEY (nome_canal, nro_plataforma, nick_streamer) REFERENCES Canal(nome, nro_plataforma, nick_streamer) ON DELETE CASCADE
);

CREATE TABLE NivelCanal (
    id INT PRIMARY KEY,
    nome_canal VARCHAR(100),
    nro_plataforma INT,
    nick_streamer VARCHAR(50),
    nivel INT,
    valor_nivel DECIMAL(10, 2) NOT NULL,
    gif VARCHAR(255),
    UNIQUE (nome_canal, nro_plataforma, nick_streamer, nivel),
    FOREIGN KEY (nome_canal, nro_plataforma, nick_streamer) REFERENCES Canal(nome, nro_plataforma, nick_streamer) ON DELETE CASCADE
);

CREATE TABLE Inscricao (
    id INT PRIMARY KEY,
    nick_membro VARCHAR(50),
    id_nivel_canal INT NOT NULL,
    FOREIGN KEY (nick_membro) REFERENCES Membro(nick_membro) ON DELETE CASCADE,
    FOREIGN KEY (id_nivel_canal) REFERENCES NivelCanal(id)
);

-- 4. VÍDEOS, PARTICIPAÇÕES E COMENTÁRIOS

CREATE TABLE Video (
    titulo VARCHAR(150),
    data_hora TIMESTAMP,
    nome_canal VARCHAR(100),
    nro_plataforma INT,
    nick_streamer VARCHAR(50),
    duracao INT,
    visu_simulta INT DEFAULT 0,
    tema VARCHAR(100),
    visu_total INT DEFAULT 0,
    PRIMARY KEY (titulo, data_hora, nome_canal, nro_plataforma, nick_streamer),
    FOREIGN KEY (nome_canal, nro_plataforma, nick_streamer) REFERENCES Canal(nome, nro_plataforma, nick_streamer) ON DELETE CASCADE
);

CREATE TABLE Participa (
    nick_streamer_convidado VARCHAR(50),
    titulo_video VARCHAR(150),
    data_hora_video TIMESTAMP,
    nome_canal VARCHAR(100),
    nro_plataforma INT,
    nick_streamer_dono VARCHAR(50),
    PRIMARY KEY (nick_streamer_convidado, titulo_video, data_hora_video, nome_canal, nro_plataforma, nick_streamer_dono),
    FOREIGN KEY (nick_streamer_convidado) REFERENCES Streamer(nick_streamer),
    FOREIGN KEY (titulo_video, data_hora_video, nome_canal, nro_plataforma, nick_streamer_dono)
        REFERENCES Video(titulo, data_hora, nome_canal, nro_plataforma, nick_streamer) ON DELETE CASCADE
);

CREATE TABLE Comentario (
    sequencial INT,
    nick_usuario VARCHAR(50),
    titulo_video VARCHAR(150),
    data_hora_video TIMESTAMP,
    nome_canal VARCHAR(100),
    nro_plataforma INT,
    nick_streamer VARCHAR(50),
    texto TEXT NOT NULL,
    data_hora TIMESTAMP NOT NULL,
    online BOOLEAN DEFAULT TRUE,
    PRIMARY KEY (sequencial, nick_usuario, titulo_video, data_hora_video, nome_canal, nro_plataforma, nick_streamer),
    FOREIGN KEY (nick_usuario) REFERENCES Usuario(nick),
    FOREIGN KEY (titulo_video, data_hora_video, nome_canal, nro_plataforma, nick_streamer)
        REFERENCES Video(titulo, data_hora, nome_canal, nro_plataforma, nick_streamer) ON DELETE CASCADE
);

-- 5. DOAÇÕES E ESPECIFICAÇÕES DE PAGAMENTO

CREATE TABLE Doacao (
    id INT PRIMARY KEY,                          
    sequencial_coment INT NOT NULL,
    nick_usuario VARCHAR(50) NOT NULL,
    titulo_video VARCHAR(150) NOT NULL,
    data_hora_video TIMESTAMP NOT NULL,
    nome_canal VARCHAR(100) NOT NULL,
    nro_plataforma INT NOT NULL,
    nick_streamer VARCHAR(50) NOT NULL,
    valor DECIMAL(10, 2) NOT NULL,
    status VARCHAR(50) CHECK (status IN ('recusado', 'recebido', 'lido')),
    FOREIGN KEY (sequencial_coment, nick_usuario, titulo_video, data_hora_video, nome_canal, nro_plataforma, nick_streamer)
        REFERENCES Comentario(sequencial, nick_usuario, titulo_video, data_hora_video, nome_canal, nro_plataforma, nick_streamer) ON DELETE CASCADE
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