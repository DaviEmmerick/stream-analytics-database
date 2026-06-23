import os
import random
from datetime import datetime, timedelta
import psycopg2
from psycopg2.extras import execute_values
from faker import Faker
from dotenv import load_dotenv

# Carrega variáveis de ambiente
env_path = os.path.join(os.path.dirname(__file__), '..', '.env')
load_dotenv(dotenv_path=env_path)

# Inicializa o Faker
fake = Faker(['pt_BR', 'en_US'])
Faker.seed(42)
random.seed(42)

def conectar_banco():
    print("🔌 Conectando ao banco de dados...")
    try:
        return psycopg2.connect(
            host=os.getenv("DB_HOST"),
            port=os.getenv("DB_PORT"),
            dbname=os.getenv("DB_NAME"),
            user=os.getenv("DB_USER"),
            password=os.getenv("DB_PASSWORD"),
            client_encoding='UTF8'
        )
    except Exception as e:
        print(f"❌ Erro ao conectar: {e}")
        exit(1)

def popular_banco(cur):
    print("\n🚀 INICIANDO CARGA CONSOLIDADA (Limites: 100 a 1000 tuplas por tabela)")
    print("-" * 70)

    # ==========================================
    # 1. MOEDAS (Qtd: 150)
    # ==========================================
    dados_moeda = []
    moedas_geradas = set()
    while len(dados_moeda) < 150:
        codigo = fake.currency_code()
        # Garante unicidade e adiciona sufixos caso o Faker repita muito
        if codigo in moedas_geradas:
            codigo = f"{codigo[:2]}{random.randint(0,9)}"
        if codigo not in moedas_geradas:
            moedas_geradas.add(codigo)
            taxa = round(random.uniform(0.01, 10.0), 4)
            dados_moeda.append((codigo, taxa))
            
    execute_values(cur, "INSERT INTO Moeda (nome_moeda, fat_conversao) VALUES %s ON CONFLICT DO NOTHING", dados_moeda)
    lista_moedas = list(moedas_geradas)
    print(f"✅ Moedas inseridas: {len(dados_moeda)}")

    # ==========================================
    # 2. PAÍSES (Qtd: 150)
    # ==========================================
    dados_pais = []
    ddis_gerados = set()
    while len(dados_pais) < 150:
        ddi = random.randint(1, 9999)
        if ddi not in ddis_gerados:
            ddis_gerados.add(ddi)
            nome = fake.unique.country()[:50]
            moeda = random.choice(lista_moedas)
            dados_pais.append((ddi, nome, moeda))
            
    execute_values(cur, "INSERT INTO Pais (ddi, nome, nome_moeda) VALUES %s ON CONFLICT DO NOTHING", dados_pais)
    lista_ddis = list(ddis_gerados)
    print(f"✅ Países inseridos: {len(dados_pais)}")

    # ==========================================
    # 3. EMPRESAS (Qtd: 150)
    # ==========================================
    dados_empresa = []
    for i in range(1, 151):
        nome = fake.company()[:50]
        fantasia = (nome + " Media")[:50]
        id_nac = fake.bban()[:20]
        ddi = random.choice(lista_ddis)
        dados_empresa.append((i, nome, fantasia, id_nac, ddi))
        
    execute_values(cur, "INSERT INTO Empresa (numero, nome, nome_fantasia, id_nacional, ddi_pais_sede) VALUES %s ON CONFLICT DO NOTHING", dados_empresa)
    lista_empresas = [e[0] for e in dados_empresa]
    print(f"✅ Empresas inseridas: {len(dados_empresa)}")

    # ==========================================
    # 4. PLATAFORMAS (Qtd: 100)
    # ==========================================
    dados_plataforma = []
    for i in range(1, 101):
        nome = f"{fake.word().capitalize()} Stream {i}"[:50]
        qtd_users = random.randint(1000, 1000000)
        data_fund = fake.date_between(start_date='-15y', end_date='-1y')
        emp_funda = random.choice(lista_empresas)
        emp_resp = random.choice(lista_empresas)
        dados_plataforma.append((i, nome, qtd_users, data_fund, emp_funda, emp_resp))
        
    execute_values(cur, "INSERT INTO Plataforma (numero, nome, qtd_usuarios, data_fundacao, empresa_funda_nro, empresa_resp_nro) VALUES %s ON CONFLICT DO NOTHING", dados_plataforma)
    lista_plataformas = [p[0] for p in dados_plataforma]
    print(f"✅ Plataformas inseridas: {len(dados_plataforma)}")

    # ==========================================
    # 5. USUÁRIOS (Qtd: 1000)
    # ==========================================
    dados_usuario = []
    nicks_gerados = []
    for i in range(1000):
        nick = f"{fake.user_name().lower()}_{i}"[:50]
        email = f"{nick}@{fake.free_email_domain()}"[:100]
        data_nasc = fake.date_of_birth(minimum_age=13, maximum_age=60)
        telefone = fake.phone_number()[:30]
        end_postal = fake.address().replace('\n', ', ')[:200]
        ddi = random.choice(lista_ddis)
        
        dados_usuario.append((nick, email, data_nasc, telefone, end_postal, ddi))
        nicks_gerados.append(nick)
        
    execute_values(cur, "INSERT INTO Usuario (nick, email, data_nasc, telefone, end_postal, ddi_pais_reside) VALUES %s ON CONFLICT DO NOTHING", dados_usuario)
    print(f"✅ Usuários inseridos: {len(dados_usuario)}")

    # ==========================================
    # 6. STREAMERS (300) E MEMBROS (700)
    # ==========================================
    streamers = nicks_gerados[:300]
    membros = nicks_gerados[300:]
    
    dados_streamer = []
    for nick in streamers:
        passaporte = fake.unique.passport_number()[:20]
        ddi_nac = random.choice(lista_ddis)
        dados_streamer.append((nick, passaporte, ddi_nac))
    execute_values(cur, "INSERT INTO Streamer (nick_streamer, nro_passaporte, ddi_pais_nacionalidade) VALUES %s ON CONFLICT DO NOTHING", dados_streamer)
    print(f"✅ Streamers inseridos: {len(dados_streamer)}")

    dados_membro = [(nick,) for nick in membros]
    execute_values(cur, "INSERT INTO Membro (nick_membro) VALUES %s ON CONFLICT DO NOTHING", dados_membro)
    print(f"✅ Membros inseridos: {len(dados_membro)}")

    # ==========================================
    # 7. TEM_CONTA (Qtd: 800 vínculos)
    # ==========================================
    dados_tem_conta = []
    usuarios_selecionados = random.sample(nicks_gerados, 800)
    for nick in usuarios_selecionados:
        plat = random.choice(lista_plataformas)
        nro_user = f"usr_{fake.lexify('????????')}"[:50]
        dados_tem_conta.append((nick, plat, nro_user))
        
    execute_values(cur, "INSERT INTO TemConta (nick_usuario, nro_plataforma, nro_usuario) VALUES %s ON CONFLICT DO NOTHING", dados_tem_conta)
    print(f"✅ Vínculos (TemConta) inseridos: {len(dados_tem_conta)}")

    # ==========================================
    # 8. CANAIS (Qtd: 400)
    # ==========================================
    dados_canal = []
    canais_criados = [] # Armazena (nome_canal, nro_plataforma, nick_streamer)
    for i in range(400):
        streamer = random.choice(streamers)
        plat = random.choice(lista_plataformas)
        nome_canal = f"Canal_{streamer}_{i}"[:50]
        tipo = random.choice(['privado', 'público', 'misto'])
        data_ini = fake.date_between(start_date='-5y', end_date='today')
        desc = fake.text(max_nb_chars=100)
        
        dados_canal.append((nome_canal, plat, streamer, tipo, data_ini, desc))
        canais_criados.append((nome_canal, plat, streamer))
        
    execute_values(cur, "INSERT INTO Canal (nome, nro_plataforma, nick_streamer, tipo, data_inicio, descricao) VALUES %s ON CONFLICT DO NOTHING", dados_canal)
    print(f"✅ Canais inseridos: {len(dados_canal)}")

    # ==========================================
    # 9. NIVEIS DE CANAL (Qtd: 800)
    # ==========================================
    dados_nivel = []
    niveis_criados = [] # Para usar nas inscrições
    # Vamos criar 2 níveis para cada um dos 400 canais
    for canal in canais_criados:
        for nivel in [1, 2]:
            valor = round(random.uniform(5.0, 50.0), 2)
            gif = f"https://exemplo.com/gif_{nivel}.gif"[:255]
            dados_nivel.append((canal[0], canal[1], canal[2], nivel, valor, gif))
            niveis_criados.append((canal[0], canal[1], canal[2], nivel))
            
    execute_values(cur, "INSERT INTO NivelCanal (nome_canal, nro_plataforma, nick_streamer, nivel, valor_nivel, gif) VALUES %s ON CONFLICT DO NOTHING", dados_nivel)
    print(f"✅ Níveis de Canal inseridos: {len(dados_nivel)}")

    # ==========================================
    # 10. INSCRIÇÕES (Qtd: 600)
    # ==========================================
    dados_inscricao = []
    membros_sortudos = random.sample(membros, 600)
    for membro in membros_sortudos:
        canal_escolhido = random.choice(niveis_criados) # Pega um canal e um nível válido
        dados_inscricao.append((membro, canal_escolhido[0], canal_escolhido[1], canal_escolhido[2], canal_escolhido[3]))
        
    execute_values(cur, "INSERT INTO Inscricao (nick_membro, nome_canal, nro_plataforma, nick_streamer, nivel) VALUES %s ON CONFLICT DO NOTHING", dados_inscricao)
    print(f"✅ Inscrições inseridas: {len(dados_inscricao)}")

    # ==========================================
    # 11. VÍDEOS (Qtd: 1000) E PARTICIPA (Qtd: 400)
    # ==========================================
    dados_video = []
    videos_criados = []
    for i in range(1000):
        canal = random.choice(canais_criados)
        titulo = f"Video_{fake.word()}_{i}"[:100]
        data_hora = datetime.now() - timedelta(days=random.randint(1, 365), minutes=random.randint(1, 1440))
        duracao = random.randint(60, 14400)
        visu_simul = random.randint(10, 5000)
        tema = random.choice(['Gaming', 'Educação', 'Música', 'Artes'])[:50]
        visu_tot = visu_simul * random.randint(2, 10)
        
        dados_video.append((titulo, data_hora, canal[0], canal[1], canal[2], duracao, visu_simul, tema, visu_tot))
        videos_criados.append((titulo, data_hora, canal[0], canal[1], canal[2]))
        
    execute_values(cur, "INSERT INTO Video (titulo, data_hora, nome_canal, nro_plataforma, nick_streamer, duracao, visu_simulta, tema, visu_total) VALUES %s ON CONFLICT DO NOTHING", dados_video)
    print(f"✅ Vídeos inseridos: {len(dados_video)}")

    # Participações (Collabs)
    dados_participa = []
    for _ in range(400):
        video = random.choice(videos_criados)
        convidado = random.choice(streamers)
        # Evita que o streamer dono seja o convidado dele mesmo
        if convidado != video[4]: 
            dados_participa.append((convidado, video[0], video[1], video[2], video[3], video[4]))
    execute_values(cur, "INSERT INTO Participa (nick_streamer_convidado, titulo_video, data_hora_video, nome_canal, nro_plataforma, nick_streamer_dono) VALUES %s ON CONFLICT DO NOTHING", dados_participa)
    print(f"✅ Participações inseridas: {len(dados_participa)}")

    # ==========================================
    # 12. COMENTÁRIOS (Qtd: 1000)
    # ==========================================
    dados_comentario = []
    comentarios_criados = []
    for i in range(1, 1001):
        video = random.choice(videos_criados)
        usuario = random.choice(nicks_gerados)
        texto = fake.sentence()[:200]
        data_hora_coment = video[1] + timedelta(minutes=random.randint(1, 120))
        online = random.choice([True, False])
        
        tupla = (i, usuario, video[0], video[1], video[2], video[3], video[4], texto, data_hora_coment, online)
        dados_comentario.append(tupla)
        comentarios_criados.append(tupla) # Guarda a chave primária completa
        
    execute_values(cur, "INSERT INTO Comentario (sequencial, nick_usuario, titulo_video, data_hora_video, nome_canal, nro_plataforma, nick_streamer, texto, data_hora, online) VALUES %s ON CONFLICT DO NOTHING", dados_comentario)
    print(f"✅ Comentários inseridos: {len(dados_comentario)}")

    # ==========================================
    # 13. DOAÇÕES E PAGAMENTOS (Qtd Exata: 800 doações totais)
    # Divididos exatamente em 200 para cada método
    # ==========================================
    dados_doacao = []
    dados_cartao, dados_paypal, dados_btc, dados_mec = [], [], [], []
    
    # Pega 800 comentários únicos para fazer as doações
    comentarios_com_doacao = random.sample(comentarios_criados, 800)
    
    for i, c in enumerate(comentarios_com_doacao, start=1):
        valor = round(random.uniform(5.0, 500.0), 2)
        status = random.choice(['recusado', 'recebido', 'lido'])
        
        # tupla base da doação: (seq_doacao, seq_coment, nick_user, titulo_vid, data_vid, nome_canal, nro_plat, nick_streamer)
        tupla_base_doacao = (i, c[0], c[1], c[2], c[3], c[4], c[5], c[6])
        
        # Junta com valor e status para a tabela Doacao
        dados_doacao.append((*tupla_base_doacao, valor, status))
        
        # Distribui perfeitamente (200 pra cada)
        if i <= 200:
            numero = fake.credit_card_number()[:20]
            bandeira = random.choice(['VISA', 'MASTERCARD', 'ELO'])[:20]
            dados_cartao.append((*tupla_base_doacao, numero, bandeira, datetime.now()))
        elif i <= 400:
            id_paypal = fake.email()[:100]
            dados_paypal.append((*tupla_base_doacao, id_paypal))
        elif i <= 600:
            tx_id = fake.sha256()[:64]
            dados_btc.append((*tupla_base_doacao, tx_id))
        else:
            seq_mec = random.randint(1, 1000)
            dados_mec.append((*tupla_base_doacao, seq_mec))

    execute_values(cur, "INSERT INTO Doacao (sequencial_doacao, sequencial_coment, nick_usuario, titulo_video, data_hora_video, nome_canal, nro_plataforma, nick_streamer, valor, status) VALUES %s ON CONFLICT DO NOTHING", dados_doacao)
    print(f"✅ Doações inseridas: {len(dados_doacao)}")
    
    execute_values(cur, "INSERT INTO Cartao_Cred (...) VALUES %s".replace("...", "sequencial_doacao, sequencial_coment, nick_usuario, titulo_video, data_hora_video, nome_canal, nro_plataforma, nick_streamer, numero, bandeira, data_hora_cartao"), dados_cartao)
    execute_values(cur, "INSERT INTO Paypal (...) VALUES %s".replace("...", "sequencial_doacao, sequencial_coment, nick_usuario, titulo_video, data_hora_video, nome_canal, nro_plataforma, nick_streamer, id_paypal"), dados_paypal)
    execute_values(cur, "INSERT INTO BTC (...) VALUES %s".replace("...", "sequencial_doacao, sequencial_coment, nick_usuario, titulo_video, data_hora_video, nome_canal, nro_plataforma, nick_streamer, tx_id"), dados_btc)
    execute_values(cur, "INSERT INTO Mec_plat (...) VALUES %s".replace("...", "sequencial_doacao, sequencial_coment, nick_usuario, titulo_video, data_hora_video, nome_canal, nro_plataforma, nick_streamer, sequencial_mec"), dados_mec)
    print(f"✅ Pagamentos inseridos: 200 Cartão | 200 PayPal | 200 BTC | 200 Mec_plat")

    # ==========================================
    # 14. PATROCÍNA (Qtd: 400)
    # ==========================================
    dados_patrocina = []
    canais_patrocinados = random.sample(canais_criados, 400) # Seleciona 400 canais únicos
    for canal in canais_patrocinados:
        empresa = random.choice(lista_empresas)
        valor = round(random.uniform(1000.0, 50000.0), 2)
        dados_patrocina.append((empresa, canal[0], canal[1], canal[2], valor))
        
    execute_values(cur, "INSERT INTO Patrocina (nro_empresa, nome_canal, nro_plataforma, nick_streamer, valor) VALUES %s ON CONFLICT DO NOTHING", dados_patrocina)
    print(f"✅ Patrocínios inseridos: {len(dados_patrocina)}")

    print("-" * 70)
    print("🎉 BANCO DE DADOS POPULADO COM SUCESSO!")

def main():
    conn = None
    try:
        conn = conectar_banco()
        cur = conn.cursor()
        popular_banco(cur)
        conn.commit() 
    except Exception as e:
        print(f"\n❌ Erro Crítico durante a execução: {e}")
        if conn:
            conn.rollback() 
    finally:
        if conn:
            cur.close()
            conn.close()
            print("🔌 Conexão encerrada de forma segura.")

if __name__ == '__main__':
    main()
