import os
import sys
import psycopg2
from faker import Faker
from datetime import datetime, timedelta
import random

# Configuração do banco de dados (lê do ambiente)
DB_HOST = os.getenv('DB_HOST')
DB_PORT = os.getenv('DB_PORT')
DB_USER = os.getenv('DB_USER')
DB_PASSWORD = os.getenv('DB_PASSWORD')
DB_NAME = os.getenv('DB_NAME')

# Validar se variáveis obrigatórias foram definidas
if not all([DB_HOST, DB_PORT, DB_USER, DB_PASSWORD, DB_NAME]):
    print("❌ Erro: Variáveis de ambiente não configuradas!")
    print("   Defina: DB_HOST, DB_PORT, DB_USER, DB_PASSWORD, DB_NAME")
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
    ('CNY', 0.14),   
    ('TRY', 0.031),
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
        exit(1)

def populate_moedas(cursor, conn):
    print("\n📍 Populando MOEDAS...")
    sucesso, falhas = 0, 0
    for nome_moeda, taxa in MOEDAS:
        try:
            cursor.execute(
                "INSERT INTO Moeda (nome_moeda, fat_conversao) VALUES (%s, %s) ON CONFLICT DO NOTHING",
                (nome_moeda, taxa)
            )
            sucesso += 1
        except psycopg2.Error as e:
            conn.rollback()
            falhas += 1
            print(f"   [!] Erro Moeda ({nome_moeda}): {e.pgerror.strip()}")
    conn.commit()
    print(f"   ✓ {sucesso} inseridas | ❌ {falhas} falhas")

def populate_paises(cursor, conn):
    print("\n📍 Populando PAISES...")
    sucesso, falhas = 0, 0
    for ddi, nome, moeda in PAISES:
        try:
            cursor.execute(
                "INSERT INTO Pais (ddi, nome, nome_moeda) VALUES (%s, %s, %s) ON CONFLICT DO NOTHING",
                (ddi, nome, moeda)
            )
            sucesso += 1
        except psycopg2.Error as e:
            conn.rollback()
            falhas += 1
            print(f"   [!] Erro País ({nome}): {e.pgerror.strip()}")
    conn.commit()
    print(f"   ✓ {sucesso} inseridos | ❌ {falhas} falhas")

def populate_empresas(cursor, conn, num_empresas=10):
    print(f"\n📍 Populando EMPRESAS ({num_empresas})...")
    sucesso, falhas = 0, 0
    for i in range(num_empresas):
        nome_empresa = fake.company()[:50]
        nome_fantasia = (fake.name() + " Media")[:50]
        id_nacional = fake.bban()[:20]
        ddi_pais = random.choice(PAISES)[0]
        
        try:
            cursor.execute(
                "INSERT INTO Empresa (numero, nome, nome_fantasia, id_nacional, ddi_pais_sede) VALUES (%s, %s, %s, %s, %s)",
                (i+1, nome_empresa, nome_fantasia, id_nacional, ddi_pais)
            )
            sucesso += 1
        except psycopg2.Error as e:
            conn.rollback()
            falhas += 1
            print(f"   [!] Erro Empresa: {e.pgerror.strip()}")
    conn.commit()
    print(f"   ✓ {sucesso} inseridas | ❌ {falhas} falhas")

def populate_plataformas(cursor, conn, num_plataformas=5):
    print(f"\n📍 Populando PLATAFORMAS ({num_plataformas})...")
    nomes_plataformas = ['Twitch', 'YouTube', 'TikTok Live', 'Facebook Gaming', 'Kick']
    sucesso, falhas = 0, 0
    
    for i in range(min(num_plataformas, len(nomes_plataformas))):
        nome = nomes_plataformas[i][:50]
        qtd_usuarios = random.randint(100000, 10000000)
        data_fundacao = fake.date_between(start_date='-15y', end_date='-1y')
        empresa_funda = random.randint(1, 10)
        empresa_resp = random.randint(1, 10)
        
        try:
            cursor.execute(
                "INSERT INTO Plataforma (numero, nome, qtd_usuarios, data_fundacao, empresa_funda_nro, empresa_resp_nro) VALUES (%s, %s, %s, %s, %s, %s)",
                (i+1, nome, qtd_usuarios, data_fundacao, empresa_funda, empresa_resp)
            )
            sucesso += 1
        except psycopg2.Error as e:
            conn.rollback()
            falhas += 1
            print(f"   [!] Erro Plataforma ({nome}): {e.pgerror.strip()}")
    conn.commit()
    print(f"   ✓ {sucesso} inseridas | ❌ {falhas} falhas")

def populate_usuarios(cursor, conn, num_usuarios=50):
    print(f"\n📍 Populando USUARIOS ({num_usuarios})...")
    usuarios = []
    sucesso, falhas = 0, 0
    
    for i in range(num_usuarios):
        nick = f"{fake.user_name()}_{i}".replace('.', '_')[:50]
        email = fake.email()[:100]
        data_nasc = fake.date_between(start_date='-60y', end_date='-18y')
        telefone = fake.phone_number()[:30]
        end_postal = fake.address().replace('\n', ', ')[:200]
        ddi_pais = random.choice(PAISES)[0]
        
        try:
            cursor.execute(
                "INSERT INTO Usuario (nick, email, data_nasc, telefone, end_postal, ddi_pais_reside) VALUES (%s, %s, %s, %s, %s, %s)",
                (nick, email, data_nasc, telefone, end_postal, ddi_pais)
            )
            usuarios.append(nick)
            sucesso += 1
        except psycopg2.Error as e:
            conn.rollback()
            falhas += 1
            print(f"   [!] Erro Usuário ({nick}): {e.pgerror.strip()}")
            
    conn.commit()
    print(f"   ✓ {sucesso} inseridos | ❌ {falhas} falhas")
    return usuarios

def populate_streamers(cursor, conn, usuarios):
    if not usuarios:
        print("\n📍 Populando STREAMERS... (Cancelado: Nenhum usuário encontrado)")
        return []
        
    quantidade = len(usuarios) // 2
    print(f"\n📍 Populando STREAMERS ({quantidade})...")
    streamers = []
    sucesso, falhas = 0, 0
    
    for nick in usuarios[:quantidade]:
        nro_passaporte = fake.passport_number()[:20]
        ddi_pais = random.choice(PAISES)[0]
        
        try:
            cursor.execute(
                "INSERT INTO Streamer (nick_streamer, nro_passaporte, ddi_pais_nacionalidade) VALUES (%s, %s, %s)",
                (nick, nro_passaporte, ddi_pais)
            )
            streamers.append(nick)
            sucesso += 1
        except psycopg2.Error as e:
            conn.rollback()
            falhas += 1
            print(f"   [!] Erro Streamer ({nick}): {e.pgerror.strip()}")
            
    conn.commit()
    print(f"   ✓ {sucesso} inseridos | ❌ {falhas} falhas")
    return streamers

def populate_membros(cursor, conn, usuarios):
    if not usuarios:
        return []
        
    quantidade = len(usuarios) - (len(usuarios) // 2)
    print(f"\n📍 Populando MEMBROS ({quantidade})...")
    membros = []
    sucesso, falhas = 0, 0
    
    for nick in usuarios[len(usuarios)//2:]:
        try:
            cursor.execute(
                "INSERT INTO Membro (nick_membro) VALUES (%s)",
                (nick,)
            )
            membros.append(nick)
            sucesso += 1
        except psycopg2.Error as e:
            conn.rollback()
            falhas += 1
            print(f"   [!] Erro Membro ({nick}): {e.pgerror.strip()}")
            
    conn.commit()
    print(f"   ✓ {sucesso} inseridos | ❌ {falhas} falhas")
    return membros

def populate_tem_conta(cursor, conn, usuarios, num_plataformas=5):
    print(f"\n📍 Populando TEM_CONTA...")
    sucesso, falhas = 0, 0
    
    for nick in usuarios:
        num_plataformas_user = random.randint(1, num_plataformas)
        plataformas = random.sample(range(1, num_plataformas+1), num_plataformas_user)
        
        for nro_plataforma in plataformas:
            nro_usuario = f"user_{fake.lexify('????????')}_{nro_plataforma}"[:50]
            
            try:
                cursor.execute(
                    "INSERT INTO TemConta (nick_usuario, nro_plataforma, nro_usuario) VALUES (%s, %s, %s)",
                    (nick, nro_plataforma, nro_usuario)
                )
                sucesso += 1
            except psycopg2.Error as e:
                conn.rollback()
                falhas += 1
                
    conn.commit()
    print(f"   ✓ {sucesso} vínculos inseridos | ❌ {falhas} falhas")

def populate_canais(cursor, conn, streamers, num_plataformas=5):
    print(f"\n📍 Populando CANAIS...")
    canais = []
    sucesso, falhas = 0, 0
    
    for streamer in streamers:
        num_canais = random.randint(1, 3)
        for _ in range(num_canais):
            nome_canal = fake.word().title()[:50] + f"_{random.randint(1,100)}"
            nro_plataforma = random.randint(1, num_plataformas)
            tipo = random.choice(TIPOS_CANAL)
            data_inicio = fake.date_between(start_date='-5y', end_date='-1y')
            descricao = fake.text(max_nb_chars=150)
            
            try:
                cursor.execute(
                    "INSERT INTO Canal (nome, nro_plataforma, nick_streamer, tipo, data_inicio, descricao) VALUES (%s, %s, %s, %s, %s, %s)",
                    (nome_canal, nro_plataforma, streamer, tipo, data_inicio, descricao)
                )
                canais.append((nome_canal, nro_plataforma, streamer))
                sucesso += 1
            except psycopg2.Error as e:
                conn.rollback()
                falhas += 1
                print(f"   [!] Erro Canal ({nome_canal}): {e.pgerror.strip()}")
                
    conn.commit()
    print(f"   ✓ {sucesso} inseridos | ❌ {falhas} falhas")
    return canais

def populate_niveis_canal(cursor, conn, canais):
    print(f"\n📍 Populando NIVEIS_CANAL...")
    sucesso, falhas = 0, 0
    
    for nome_canal, nro_plataforma, nick_streamer in canais:
        num_niveis = random.randint(2, 5)
        for nivel in range(1, num_niveis + 1):
            valor_nivel = round(random.uniform(1.0, 50.0), 2)
            gif = f"https://example.com/g_{nivel}.gif"[:255]
            
            try:
                cursor.execute(
                    "INSERT INTO NivelCanal (nome_canal, nro_plataforma, nick_streamer, nivel, valor_nivel, gif) VALUES (%s, %s, %s, %s, %s, %s)",
                    (nome_canal, nro_plataforma, nick_streamer, nivel, valor_nivel, gif)
                )
                sucesso += 1
            except psycopg2.Error as e:
                conn.rollback()
                falhas += 1
                
    conn.commit()
    print(f"   ✓ {sucesso} níveis criados | ❌ {falhas} falhas")

def populate_inscricoes(cursor, conn, membros, canais):
    print(f"\n📍 Populando INSCRICOES...")
    sucesso, falhas = 0, 0
    
    for membro in membros:
        if not canais:
            break
        canais_inscritos = random.sample(canais, min(random.randint(1, 5), len(canais)))
        
        for nome_canal, nro_plataforma, nick_streamer in canais_inscritos:
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
                    sucesso += 1
            except psycopg2.Error as e:
                conn.rollback()
                falhas += 1
                
    conn.commit()
    print(f"   ✓ {sucesso} inscrições feitas | ❌ {falhas} falhas")

def populate_videos(cursor, conn, canais):
    print(f"\n📍 Populando VIDEOS...")
    videos = []
    sucesso, falhas = 0, 0
    
    for nome_canal, nro_plataforma, nick_streamer in canais:
        num_videos = random.randint(2, 5)
        for _ in range(num_videos):
            titulo = fake.sentence(nb_words=4)[:100]
            data_hora = fake.date_time_between(start_date='-1y', end_date='now')
            duracao = random.randint(600, 14400)
            visu_simulta = random.randint(100, 50000)
            tema = random.choice(TEMAS)[:50]
            visu_total = random.randint(1000, 1000000)
            
            try:
                cursor.execute(
                    "INSERT INTO Video (titulo, data_hora, nome_canal, nro_plataforma, nick_streamer, duracao, visu_simulta, tema, visu_total) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)",
                    (titulo, data_hora, nome_canal, nro_plataforma, nick_streamer, duracao, visu_simulta, tema, visu_total)
                )
                videos.append((titulo, data_hora, nome_canal, nro_plataforma, nick_streamer))
                sucesso += 1
            except psycopg2.Error as e:
                conn.rollback()
                falhas += 1
                
    conn.commit()
    print(f"   ✓ {sucesso} vídeos inseridos | ❌ {falhas} falhas")
    return videos

def populate_participa(cursor, conn, videos, streamers):
    print(f"\n📍 Populando PARTICIPA...")
    sucesso, falhas = 0, 0
    
    for titulo_video, data_hora_video, nome_canal, nro_plataforma, nick_streamer_dono in videos:
        num_convidados = random.randint(0, 2)
        if not streamers:
            continue
            
        convidados = random.sample(streamers, min(num_convidados, len(streamers)))
        for convidado in convidados:
            if convidado != nick_streamer_dono:
                try:
                    cursor.execute(
                        "INSERT INTO Participa (nick_streamer_convidado, titulo_video, data_hora_video, nome_canal, nro_plataforma, nick_streamer_dono) VALUES (%s, %s, %s, %s, %s, %s)",
                        (convidado, titulo_video, data_hora_video, nome_canal, nro_plataforma, nick_streamer_dono)
                    )
                    sucesso += 1
                except psycopg2.Error as e:
                    conn.rollback()
                    falhas += 1
                    
    conn.commit()
    print(f"   ✓ {sucesso} participações | ❌ {falhas} falhas")

def populate_comentarios(cursor, conn, videos, usuarios):
    print(f"\n📍 Populando COMENTARIOS...")
    comentarios = []
    sucesso, falhas = 0, 0
    
    for titulo_video, data_hora_video, nome_canal, nro_plataforma, nick_streamer in videos:
        num_comentarios = random.randint(5, 15)
        for seq in range(1, num_comentarios + 1):
            nick_usuario = random.choice(usuarios)
            texto = fake.text(max_nb_chars=200)
            data_hora_comentario = data_hora_video + timedelta(hours=random.randint(0, 24))
            online = random.choice([True, False])
            
            try:
                cursor.execute(
                    "INSERT INTO Comentario (sequencial, nick_usuario, titulo_video, data_hora_video, nome_canal, nro_plataforma, nick_streamer, texto, data_hora, online) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)",
                    (seq, nick_usuario, titulo_video, data_hora_video, nome_canal, nro_plataforma, nick_streamer, texto, data_hora_comentario, online)
                )
                comentarios.append((seq, nick_usuario, titulo_video, data_hora_video, nome_canal, nro_plataforma, nick_streamer))
                sucesso += 1
            except psycopg2.Error as e:
                conn.rollback()
                falhas += 1
                
    conn.commit()
    print(f"   ✓ {sucesso} comentários inseridos | ❌ {falhas} falhas")
    return comentarios

def populate_doacoes(cursor, conn, comentarios):
    print(f"\n📍 Populando DOACOES...")
    doacoes = []
    sucesso, falhas = 0, 0
    
    for seq_comentario, (seq, nick_usuario, titulo_video, data_hora_video, nome_canal, nro_plataforma, nick_streamer) in enumerate(comentarios, 1):
        if random.random() < 0.2:  # 20%
            seq_doacao = seq_comentario
            valor = round(random.uniform(1.0, 500.0), 2)
            status = random.choice(['recusado', 'recebido', 'lido'])
            
            try:
                cursor.execute(
                    "INSERT INTO Doacao (sequencial_doacao, sequencial_coment, nick_usuario, titulo_video, data_hora_video, nome_canal, nro_plataforma, nick_streamer, valor, status) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)",
                    (seq_doacao, seq, nick_usuario, titulo_video, data_hora_video, nome_canal, nro_plataforma, nick_streamer, valor, status)
                )
                doacoes.append((seq_doacao, seq, nick_usuario, titulo_video, data_hora_video, nome_canal, nro_plataforma, nick_streamer))
                sucesso += 1
            except psycopg2.Error as e:
                conn.rollback()
                falhas += 1
                
    conn.commit()
    print(f"   ✓ {sucesso} doações inseridas | ❌ {falhas} falhas")
    return doacoes

def populate_pagamentos(cursor, conn, doacoes):
    print(f"\n📍 Populando FORMAS DE PAGAMENTO...")
    sucesso, falhas = 0, 0
    
    for seq_doacao, seq_comentario, nick_usuario, titulo_video, data_hora_video, nome_canal, nro_plataforma, nick_streamer in doacoes:
        metodo = random.choice(['cartao', 'paypal', 'btc', 'mecplat'])
        
        try:
            if metodo == 'cartao':
                numero = fake.credit_card_number(card_type='visa')[:20]
                bandeira = random.choice(BANDEIRAS)[:20]
                data_hora_cartao = datetime.now()
                cursor.execute(
                    "INSERT INTO Cartao_Cred (sequencial_doacao, sequencial_coment, nick_usuario, titulo_video, data_hora_video, nome_canal, nro_plataforma, nick_streamer, numero, bandeira, data_hora_cartao) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)",
                    (seq_doacao, seq_comentario, nick_usuario, titulo_video, data_hora_video, nome_canal, nro_plataforma, nick_streamer, numero, bandeira, data_hora_cartao)
                )
            elif metodo == 'paypal':
                id_paypal = fake.email()[:100]
                cursor.execute(
                    "INSERT INTO Paypal (sequencial_doacao, sequencial_coment, nick_usuario, titulo_video, data_hora_video, nome_canal, nro_plataforma, nick_streamer, id_paypal) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)",
                    (seq_doacao, seq_comentario, nick_usuario, titulo_video, data_hora_video, nome_canal, nro_plataforma, nick_streamer, id_paypal)
                )
            elif metodo == 'btc':
                tx_id = fake.sha256()[:64]
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
            sucesso += 1
        except psycopg2.Error as e:
            conn.rollback()
            falhas += 1
            
    conn.commit()
    print(f"   ✓ {sucesso} pagamentos | ❌ {falhas} falhas")

def populate_patrocina(cursor, conn, canais, num_empresas=10):
    print(f"\n📍 Populando PATROCINA...")
    sucesso, falhas = 0, 0
    
    for nome_canal, nro_plataforma, nick_streamer in canais:
        num_patrocinadores = random.randint(0, 2)
        empresas = random.sample(range(1, num_empresas + 1), min(num_patrocinadores, num_empresas))
        
        for nro_empresa in empresas:
            valor = round(random.uniform(100.0, 10000.0), 2)
            try:
                cursor.execute(
                    "INSERT INTO Patrocina (nro_empresa, nome_canal, nro_plataforma, nick_streamer, valor) VALUES (%s, %s, %s, %s, %s)",
                    (nro_empresa, nome_canal, nro_plataforma, nick_streamer, valor)
                )
                sucesso += 1
            except psycopg2.Error as e:
                conn.rollback()
                falhas += 1
                
    conn.commit()
    print(f"   ✓ {sucesso} patrocínios | ❌ {falhas} falhas")

def main():
    print("=" * 60)
    print("🚀 INICIANDO POPULAÇÃO DO BANCO DE DADOS COM FAKER")
    print("=" * 60)
    
    conn = connect_db()
    cursor = conn.cursor()
    
    try:
        populate_moedas(cursor, conn)
        populate_paises(cursor, conn)
        populate_empresas(cursor, conn, num_empresas=10)
        populate_plataformas(cursor, conn, num_plataformas=5)
        
        usuarios = populate_usuarios(cursor, conn, num_usuarios=30)
        streamers = populate_streamers(cursor, conn, usuarios)
        membros = populate_membros(cursor, conn, usuarios)
        
        populate_tem_conta(cursor, conn, usuarios)
        
        canais = populate_canais(cursor, conn, streamers)
        populate_niveis_canal(cursor, conn, canais)
        populate_inscricoes(cursor, conn, membros, canais)
        populate_patrocina(cursor, conn, canais)
        
        videos = populate_videos(cursor, conn, canais)
        populate_participa(cursor, conn, videos, streamers)
        comentarios = populate_comentarios(cursor, conn, videos, usuarios)
        
        doacoes = populate_doacoes(cursor, conn, comentarios)
        populate_pagamentos(cursor, conn, doacoes)
        
        print("\n" + "=" * 60)
        print("✅ TENTATIVA DE POPULAÇÃO CONCLUÍDA! (Verifique os logs acima)")
        print("=" * 60)
        
    except Exception as e:
        print(f"\n❌ Erro crítico: {e}")
        conn.rollback()
    finally:
        cursor.close()
        conn.close()
        print("\n🔌 Conexão fechada")

if __name__ == "__main__":
    main()