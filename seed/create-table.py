import os
import sys
import psycopg2
from psycopg2.extras import execute_values
from faker import Faker
from datetime import datetime, timedelta
import random

# Configuração do banco de dados (lê do ambiente)
# Sem defaults - força o uso do .env
DB_HOST = os.getenv('DB_HOST')
DB_PORT = os.getenv('DB_PORT')
DB_USER = os.getenv('DB_USER')
DB_PASSWORD = os.getenv('DB_PASSWORD')
DB_NAME = os.getenv('DB_NAME')

# Validar se variáveis obrigatórias foram definidas
if not all([DB_HOST, DB_PORT, DB_USER, DB_PASSWORD, DB_NAME]):
    print("❌ Erro: Variáveis de ambiente não configuradas!")
    print("   Defina: DB_HOST, DB_PORT, DB_USER, DB_PASSWORD, DB_NAME")
    print("   Use: cp .env.example .env e configure os valores")
    exit(1)

# Inicializar Faker
fake = Faker(['pt_BR', 'en_US'])
Faker.seed(42)
random.seed(42)

# Dados base
MOEDAS = [
    ('USD', 1.0),
    ('EUR', 1.1),
    ('BRL', 0.2),
    ('GBP', 1.27),
    ('JPY', 0.0067),
]

PAISES = [
    (1, 'Estados Unidos', 'USD'),
    (55, 'Brasil', 'BRL'),
    (44, 'Reino Unido', 'GBP'),
    (33, 'França', 'EUR'),
    (49, 'Alemanha', 'EUR'),
    (39, 'Itália', 'EUR'),
    (34, 'Espanha', 'EUR'),
    (81, 'Japão', 'JPY'),
    (86, 'China', 'CNY'),
    (90, 'Turquia', 'TRY'),
]

TIPOS_CANAL = ['privado', 'público', 'misto']
TEMAS = ['Gaming', 'Educação', 'Música', 'Artes', 'Esportes', 'Culinária', 'Tecnologia', 'Viagem']
MOEDAS_CRIPTO = ['BTC', 'ETH', 'USDT']
BANDEIRAS = ['VISA', 'MASTERCARD', 'ELO', 'AMERICAN EXPRESS']

def connect_db():
    """Conectar ao banco de dados"""
    try:
        conn = psycopg2.connect(
            host=DB_HOST,
            port=int(DB_PORT),
            user=DB_USER,
            password=DB_PASSWORD,
            database=DB_NAME,
            client_encoding='UTF8'
        )
        print(f"✅ Conectado ao banco de dados: {DB_NAME}")
        return conn
    except Exception as e:
        print(f"❌ Erro ao conectar: {e}")
        print(f"Variáveis de ambiente:")
        print(f"  DB_HOST: {DB_HOST}")
        print(f"  DB_PORT: {DB_PORT}")
        print(f"  DB_USER: {DB_USER}")
        print(f"  DB_PASSWORD: {'*' * len(DB_PASSWORD) if DB_PASSWORD else 'None'}")
        print(f"  DB_NAME: {DB_NAME}")
        exit()

def populate_moedas(cursor, conn):
    """Popular tabela de moedas"""
    print("\n📍 Populando MOEDAS...")
    for nome_moeda, taxa in MOEDAS:
        try:
            cursor.execute(
                "INSERT INTO Moeda (nome_moeda, fat_conversao) VALUES (%s, %s) ON CONFLICT DO NOTHING",
                (nome_moeda, taxa)
            )
        except psycopg2.IntegrityError:
            conn.rollback()
    conn.commit()
    print(f"   ✓ {len(MOEDAS)} moedas inseridas")

def populate_paises(cursor, conn):
    """Popular tabela de países"""
    print("\n📍 Populando PAISES...")
    for ddi, nome, moeda in PAISES:
        try:
            cursor.execute(
                "INSERT INTO Pais (ddi, nome, nome_moeda) VALUES (%s, %s, %s) ON CONFLICT DO NOTHING",
                (ddi, nome, moeda)
            )
        except psycopg2.IntegrityError:
            conn.rollback()
    conn.commit()
    print(f"   ✓ {len(PAISES)} países inseridos")

def populate_empresas(cursor, conn, num_empresas=10):
    """Popular tabela de empresas"""
    print(f"\n📍 Populando EMPRESAS ({num_empresas})...")
    for i in range(num_empresas):
        nome_empresa = fake.company()
        nome_fantasia = fake.name() + " Media"
        id_nacional = fake.bban()
        ddi_pais = random.choice(PAISES)[0]
        
        try:
            cursor.execute(
                "INSERT INTO Empresa (numero, nome, nome_fantasia, id_nacional, ddi_pais_sede) VALUES (%s, %s, %s, %s, %s)",
                (i+1, nome_empresa, nome_fantasia, id_nacional, ddi_pais)
            )
        except psycopg2.IntegrityError:
            conn.rollback()
    conn.commit()
    print(f"   ✓ {num_empresas} empresas inseridas")

def populate_plataformas(cursor, conn, num_plataformas=5):
    """Popular tabela de plataformas"""
    print(f"\n📍 Populando PLATAFORMAS ({num_plataformas})...")
    nomes_plataformas = ['Twitch', 'YouTube', 'TikTok Live', 'Facebook Gaming', 'Kick']
    
    for i in range(min(num_plataformas, len(nomes_plataformas))):
        nome = nomes_plataformas[i]
        qtd_usuarios = random.randint(100000, 10000000)
        data_fundacao = fake.date_between(start_date='-15y', end_date='-1y')
        empresa_funda = random.randint(1, 10)
        empresa_resp = random.randint(1, 10)
        
        try:
            cursor.execute(
                "INSERT INTO Plataforma (numero, nome, qtd_usuarios, data_fundacao, empresa_funda_nro, empresa_resp_nro) VALUES (%s, %s, %s, %s, %s, %s)",
                (i+1, nome, qtd_usuarios, data_fundacao, empresa_funda, empresa_resp)
            )
        except psycopg2.IntegrityError:
            conn.rollback()
    conn.commit()
    print(f"   ✓ {num_plataformas} plataformas inseridas")

def populate_usuarios(cursor, conn, num_usuarios=50):
    """Popular tabela de usuários"""
    print(f"\n📍 Populando USUARIOS ({num_usuarios})...")
    usuarios = []
    
    for i in range(num_usuarios):
        nick = f"{fake.user_name()}_{i}".replace('.', '_')[:50]
        email = fake.email()
        data_nasc = fake.date_between(start_date='-60y', end_date='-18y')
        telefone = fake.phone_number()[:30]
        end_postal = fake.address()[:200]
        ddi_pais = random.choice(PAISES)[0]
        
        try:
            cursor.execute(
                "INSERT INTO Usuario (nick, email, data_nasc, telefone, end_postal, ddi_pais_reside) VALUES (%s, %s, %s, %s, %s, %s)",
                (nick, email, data_nasc, telefone, end_postal, ddi_pais)
            )
            usuarios.append(nick)
        except psycopg2.IntegrityError:
            conn.rollback()
    
    conn.commit()
    print(f"   ✓ {len(usuarios)} usuários inseridos")
    return usuarios

def populate_streamers(cursor, conn, usuarios):
    """Popular tabela de streamers"""
    print(f"\n📍 Populando STREAMERS ({len(usuarios)//2})...")
    streamers = []
    
    # 50% dos usuários são streamers
    for nick in usuarios[:len(usuarios)//2]:
        nro_passaporte = fake.passport_number()
        ddi_pais = random.choice(PAISES)[0]
        
        try:
            cursor.execute(
                "INSERT INTO Streamer (nick_streamer, nro_passaporte, ddi_pais_nacionalidade) VALUES (%s, %s, %s)",
                (nick, nro_passaporte, ddi_pais)
            )
            streamers.append(nick)
        except psycopg2.IntegrityError:
            conn.rollback()
    
    conn.commit()
    print(f"   ✓ {len(streamers)} streamers inseridos")
    return streamers

def populate_membros(cursor, conn, usuarios):
    """Popular tabela de membros"""
    print(f"\n📍 Populando MEMBROS ({len(usuarios)//2})...")
    membros = []
    
    # Os outros 50% são membros
    for nick in usuarios[len(usuarios)//2:]:
        try:
            cursor.execute(
                "INSERT INTO Membro (nick_membro) VALUES (%s)",
                (nick,)
            )
            membros.append(nick)
        except psycopg2.IntegrityError:
            conn.rollback()
    
    conn.commit()
    print(f"   ✓ {len(membros)} membros inseridos")
    return membros

def populate_tem_conta(cursor, conn, usuarios, num_plataformas=5):
    """Popular tabela TemConta"""
    print(f"\n📍 Populando TEM_CONTA...")
    
    for nick in usuarios:
        num_plataformas_user = random.randint(1, num_plataformas)
        plataformas = random.sample(range(1, num_plataformas+1), num_plataformas_user)
        
        for nro_plataforma in plataformas:
            nro_usuario = f"user_{fake.lexify('??????????')}"
            
            try:
                cursor.execute(
                    "INSERT INTO TemConta (nick_usuario, nro_plataforma, nro_usuario) VALUES (%s, %s, %s)",
                    (nick, nro_plataforma, nro_usuario)
                )
            except psycopg2.IntegrityError:
                conn.rollback()
    
    conn.commit()
    print(f"   ✓ Contas em plataformas associadas")

def populate_canais(cursor, conn, streamers, num_plataformas=5):
    """Popular tabela de canais"""
    print(f"\n📍 Populando CANAIS...")
    canais = []
    
    for streamer in streamers:
        num_canais = random.randint(1, 3)
        
        for _ in range(num_canais):
            nome_canal = fake.word().title()[:100]
            nro_plataforma = random.randint(1, num_plataformas)
            tipo = random.choice(TIPOS_CANAL)
            data_inicio = fake.date_between(start_date='-5y', end_date='-1y')
            descricao = fake.text(max_nb_chars=200)
            
            try:
                cursor.execute(
                    "INSERT INTO Canal (nome, nro_plataforma, nick_streamer, tipo, data_inicio, descricao) VALUES (%s, %s, %s, %s, %s, %s)",
                    (nome_canal, nro_plataforma, streamer, tipo, data_inicio, descricao)
                )
                canais.append((nome_canal, nro_plataforma, streamer))
            except psycopg2.IntegrityError:
                conn.rollback()
    
    conn.commit()
    print(f"   ✓ {len(canais)} canais inseridos")
    return canais

def populate_niveis_canal(cursor, conn, canais):
    """Popular tabela NivelCanal"""
    print(f"\n📍 Populando NIVEIS_CANAL...")
    
    for nome_canal, nro_plataforma, nick_streamer in canais:
        num_niveis = random.randint(2, 5)
        
        for nivel in range(1, num_niveis + 1):
            valor_nivel = round(random.uniform(1.0, 50.0), 2)
            gif = f"https://example.com/gif_{nivel}.gif"
            
            try:
                cursor.execute(
                    "INSERT INTO NivelCanal (nome_canal, nro_plataforma, nick_streamer, nivel, valor_nivel, gif) VALUES (%s, %s, %s, %s, %s, %s)",
                    (nome_canal, nro_plataforma, nick_streamer, nivel, valor_nivel, gif)
                )
            except psycopg2.IntegrityError:
                conn.rollback()
    
    conn.commit()
    print(f"   ✓ Níveis de canais inseridos")

def populate_inscricoes(cursor, conn, membros, canais):
    """Popular tabela Inscricao"""
    print(f"\n📍 Populando INSCRICOES...")
    
    for membro in membros:
        canais_inscritos = random.sample(canais, min(random.randint(1, 5), len(canais)))
        
        for nome_canal, nro_plataforma, nick_streamer in canais_inscritos:
            # Obter níveis disponíveis para o canal
            try:
                cursor.execute(
                    "SELECT nivel FROM NivelCanal WHERE nome_canal = %s AND nro_plataforma = %s AND nick_streamer = %s",
                    (nome_canal, nro_plataforma, nick_streamer)
                )
                niveis = [row[0] for row in cursor.fetchall()]
                
                if niveis:
                    nivel = random.choice(niveis)
                    cursor.execute(
                        "INSERT INTO Inscricao (nick_membro, nome_canal, nro_plataforma, nick_streamer, nivel) VALUES (%s, %s, %s, %s, %s)",
                        (membro, nome_canal, nro_plataforma, nick_streamer, nivel)
                    )
            except psycopg2.IntegrityError:
                conn.rollback()
    
    conn.commit()
    print(f"   ✓ Inscrições inseridas")

def populate_videos(cursor, conn, canais):
    """Popular tabela Video"""
    print(f"\n📍 Populando VIDEOS...")
    videos = []
    
    for nome_canal, nro_plataforma, nick_streamer in canais:
        num_videos = random.randint(5, 20)
        
        for _ in range(num_videos):
            titulo = fake.sentence(nb_words=6)[:150]
            data_hora = fake.date_time_between(start_date='-1y', end_date='now')
            duracao = random.randint(600, 14400)  # 10 min a 4 horas
            visu_simulta = random.randint(100, 50000)
            tema = random.choice(TEMAS)
            visu_total = random.randint(1000, 1000000)
            
            try:
                cursor.execute(
                    "INSERT INTO Video (titulo, data_hora, nome_canal, nro_plataforma, nick_streamer, duracao, visu_simulta, tema, visu_total) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)",
                    (titulo, data_hora, nome_canal, nro_plataforma, nick_streamer, duracao, visu_simulta, tema, visu_total)
                )
                videos.append((titulo, data_hora, nome_canal, nro_plataforma, nick_streamer))
            except psycopg2.IntegrityError:
                conn.rollback()
    
    conn.commit()
    print(f"   ✓ {len(videos)} vídeos inseridos")
    return videos

def populate_participa(cursor, conn, videos, streamers):
    """Popular tabela Participa (convidados em vídeos)"""
    print(f"\n📍 Populando PARTICIPA...")
    
    for titulo_video, data_hora_video, nome_canal, nro_plataforma, nick_streamer_dono in videos:
        num_convidados = random.randint(0, 3)
        convidados = random.sample(streamers, min(num_convidados, len(streamers)))
        
        for convidado in convidados:
            if convidado != nick_streamer_dono:
                try:
                    cursor.execute(
                        "INSERT INTO Participa (nick_streamer_convidado, titulo_video, data_hora_video, nome_canal, nro_plataforma, nick_streamer_dono) VALUES (%s, %s, %s, %s, %s, %s)",
                        (convidado, titulo_video, data_hora_video, nome_canal, nro_plataforma, nick_streamer_dono)
                    )
                except psycopg2.IntegrityError:
                    conn.rollback()
    
    conn.commit()
    print(f"   ✓ Participações inseridas")

def populate_comentarios(cursor, conn, videos, usuarios):
    """Popular tabela Comentario"""
    print(f"\n📍 Populando COMENTARIOS...")
    comentarios = []
    
    for titulo_video, data_hora_video, nome_canal, nro_plataforma, nick_streamer in videos:
        num_comentarios = random.randint(10, 100)
        
        for seq in range(1, num_comentarios + 1):
            nick_usuario = random.choice(usuarios)
            texto = fake.text(max_nb_chars=500)
            data_hora_comentario = data_hora_video + timedelta(hours=random.randint(0, 24))
            online = random.choice([True, False])
            
            try:
                cursor.execute(
                    "INSERT INTO Comentario (sequencial, nick_usuario, titulo_video, data_hora_video, nome_canal, nro_plataforma, nick_streamer, texto, data_hora, online) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)",
                    (seq, nick_usuario, titulo_video, data_hora_video, nome_canal, nro_plataforma, nick_streamer, texto, data_hora_comentario, online)
                )
                comentarios.append((seq, nick_usuario, titulo_video, data_hora_video, nome_canal, nro_plataforma, nick_streamer))
            except psycopg2.IntegrityError:
                conn.rollback()
    
    conn.commit()
    print(f"   ✓ {len(comentarios)} comentários inseridos")
    return comentarios

def populate_doacoes(cursor, conn, comentarios):
    """Popular tabela Doacao"""
    print(f"\n📍 Populando DOACOES...")
    doacoes = []
    
    for seq_comentario, (seq, nick_usuario, titulo_video, data_hora_video, nome_canal, nro_plataforma, nick_streamer) in enumerate(comentarios, 1):
        if random.random() < 0.3:  # 30% dos comentários têm doações
            seq_doacao = seq_comentario
            valor = round(random.uniform(1.0, 500.0), 2)
            status = random.choice(['recusado', 'recebido', 'lido'])
            
            try:
                cursor.execute(
                    "INSERT INTO Doacao (sequencial_doacao, sequencial_coment, nick_usuario, titulo_video, data_hora_video, nome_canal, nro_plataforma, nick_streamer, valor, status) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)",
                    (seq_doacao, seq, nick_usuario, titulo_video, data_hora_video, nome_canal, nro_plataforma, nick_streamer, valor, status)
                )
                doacoes.append((seq_doacao, seq, nick_usuario, titulo_video, data_hora_video, nome_canal, nro_plataforma, nick_streamer))
            except psycopg2.IntegrityError:
                conn.rollback()
    
    conn.commit()
    print(f"   ✓ {len(doacoes)} doações inseridas")
    return doacoes

def populate_pagamentos(cursor, conn, doacoes):
    """Popular tabelas de pagamento (CartaoCredito, PayPal, BTC, MecPlat)"""
    print(f"\n📍 Populando FORMAS DE PAGAMENTO...")
    
    for seq_doacao, seq_comentario, nick_usuario, titulo_video, data_hora_video, nome_canal, nro_plataforma, nick_streamer in doacoes:
        metodo = random.choice(['cartao', 'paypal', 'btc', 'mecplat'])
        
        try:
            if metodo == 'cartao':
                numero = fake.credit_card_number(card_type='visa')
                bandeira = random.choice(BANDEIRAS)
                data_hora_cartao = datetime.now()
                cursor.execute(
                    "INSERT INTO Cartao_Cred (sequencial_doacao, sequencial_coment, nick_usuario, titulo_video, data_hora_video, nome_canal, nro_plataforma, nick_streamer, numero, bandeira, data_hora_cartao) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)",
                    (seq_doacao, seq_comentario, nick_usuario, titulo_video, data_hora_video, nome_canal, nro_plataforma, nick_streamer, numero, bandeira, data_hora_cartao)
                )
            elif metodo == 'paypal':
                id_paypal = fake.email()
                cursor.execute(
                    "INSERT INTO Paypal (sequencial_doacao, sequencial_coment, nick_usuario, titulo_video, data_hora_video, nome_canal, nro_plataforma, nick_streamer, id_paypal) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)",
                    (seq_doacao, seq_comentario, nick_usuario, titulo_video, data_hora_video, nome_canal, nro_plataforma, nick_streamer, id_paypal)
                )
            elif metodo == 'btc':
                tx_id = fake.sha256()
                cursor.execute(
                    "INSERT INTO BTC (sequencial_doacao, sequencial_coment, nick_usuario, titulo_video, data_hora_video, nome_canal, nro_plataforma, nick_streamer, tx_id) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)",
                    (seq_doacao, seq_comentario, nick_usuario, titulo_video, data_hora_video, nome_canal, nro_plataforma, nick_streamer, tx_id)
                )
            else:  # mecplat
                sequencial_mec = random.randint(1, 1000)
                cursor.execute(
                    "INSERT INTO Mec_plat (sequencial_doacao, sequencial_coment, nick_usuario, titulo_video, data_hora_video, nome_canal, nro_plataforma, nick_streamer, sequencial_mec) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)",
                    (seq_doacao, seq_comentario, nick_usuario, titulo_video, data_hora_video, nome_canal, nro_plataforma, nick_streamer, sequencial_mec)
                )
        except psycopg2.IntegrityError:
            conn.rollback()
    
    conn.commit()
    print(f"   ✓ Formas de pagamento inseridas")

def populate_patrocina(cursor, conn, canais, num_empresas=10):
    """Popular tabela Patrocina"""
    print(f"\n📍 Populando PATROCINA...")
    
    for nome_canal, nro_plataforma, nick_streamer in canais:
        num_patrocinadores = random.randint(0, 3)
        empresas = random.sample(range(1, num_empresas + 1), min(num_patrocinadores, num_empresas))
        
        for nro_empresa in empresas:
            valor = round(random.uniform(100.0, 10000.0), 2)
            
            try:
                cursor.execute(
                    "INSERT INTO Patrocina (nro_empresa, nome_canal, nro_plataforma, nick_streamer, valor) VALUES (%s, %s, %s, %s, %s)",
                    (nro_empresa, nome_canal, nro_plataforma, nick_streamer, valor)
                )
            except psycopg2.IntegrityError:
                conn.rollback()
    
    conn.commit()
    print(f"   ✓ Patrocínios inseridos")

def main():
    """Função principal"""
    print("=" * 60)
    print("🚀 INICIANDO POPULAÇÃO DO BANCO DE DADOS COM FAKER")
    print("=" * 60)
    
    conn = connect_db()
    cursor = conn.cursor()
    
    try:
        # Dados base (sem dependências)
        populate_moedas(cursor, conn)
        populate_paises(cursor, conn)
        
        # Estrutura corporativa
        populate_empresas(cursor, conn, num_empresas=10)
        populate_plataformas(cursor, conn, num_plataformas=5)
        
        # Usuários
        usuarios = populate_usuarios(cursor, conn, num_usuarios=50)
        streamers = populate_streamers(cursor, conn, usuarios)
        membros = populate_membros(cursor, conn, usuarios)
        
        # Plataformas e contas
        populate_tem_conta(cursor, conn, usuarios)
        
        # Canais
        canais = populate_canais(cursor, conn, streamers)
        populate_niveis_canal(cursor, conn, canais)
        populate_inscricoes(cursor, conn, membros, canais)
        populate_patrocina(cursor, conn, canais)
        
        # Conteúdo
        videos = populate_videos(cursor, conn, canais)
        populate_participa(cursor, conn, videos, streamers)
        comentarios = populate_comentarios(cursor, conn, videos, usuarios)
        
        # Monetização
        doacoes = populate_doacoes(cursor, conn, comentarios)
        populate_pagamentos(cursor, conn, doacoes)
        
        print("\n" + "=" * 60)
        print("✅ POPULAÇÃO CONCLUÍDA COM SUCESSO!")
        print("=" * 60)
        
    except Exception as e:
        print(f"\n❌ Erro durante população: {e}")
        conn.rollback()
    finally:
        cursor.close()
        conn.close()
        print("\n🔌 Conexão fechada")

if __name__ == "__main__":
    main()
