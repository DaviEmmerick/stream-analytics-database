import os
import random
from datetime import datetime, timedelta
import psycopg2
from psycopg2.extras import execute_values
from faker import Faker
from dotenv import load_dotenv

env_path = os.path.join(os.path.dirname(__file__), '..', '.env')
load_dotenv(dotenv_path=env_path)

fake = Faker(['pt_BR', 'en_US'])
Faker.seed(42)
random.seed(42)

# ──────────────────────────────────────────────
# CONEXÃO
# ──────────────────────────────────────────────
def conectar_banco():
    print("🔌 Conectando ao banco de dados...")
    try:
        conn = psycopg2.connect(
            host=os.getenv("DB_HOST"),
            port=os.getenv("DB_PORT"),
            dbname=os.getenv("DB_NAME"),
            user=os.getenv("DB_USER"),
            password=os.getenv("DB_PASSWORD"),
            client_encoding="UTF8",
        )
        print("✅ Conexão estabelecida.")
        return conn
    except Exception as e:
        print(f"❌ Erro ao conectar: {e}")
        exit(1)


# ──────────────────────────────────────────────
# GUARD — evita duplicação ao rodar container novamente
# ──────────────────────────────────────────────
def banco_ja_populado(cur) -> bool:
    try:
        cur.execute("SELECT COUNT(*) FROM Moeda;")
        return cur.fetchone()[0] > 0
    except Exception:
        return False


# ──────────────────────────────────────────────
# SEED DE ALTA PERFORMANCE (Adaptado ao Novo Schema)
# ──────────────────────────────────────────────
def popular_banco(cur):
    print("\n🚀 INICIANDO CARGA — meta: ~1000 tuplas por tabela")
    print("-" * 70)

    # 1. MOEDAS (1000)
    dados_moeda = []
    moedas_geradas = set()
    id_moeda = 1  
    
    while len(dados_moeda) < 1000:
        codigo = fake.currency_code()
        if codigo in moedas_geradas:
            codigo = f"{codigo[:2]}{random.randint(10, 99)}"
            
        if codigo not in moedas_geradas and len(codigo) <= 10:
            moedas_geradas.add(codigo)
            taxa = round(random.uniform(0.01, 10.0), 4)
            dados_moeda.append((id_moeda, codigo, taxa))
            id_moeda += 1

    execute_values(cur, "INSERT INTO Moeda (id, nome_moeda, fat_conversao) VALUES %s ON CONFLICT DO NOTHING", dados_moeda)
    moedas_ids = [m[0] for m in dados_moeda]
    print(f"✅ Moedas: {len(dados_moeda)}")


    # 2. PAÍSES (1000)
    dados_pais = []
    ddis_gerados = set()
    while len(dados_pais) < 1000:
        ddi = random.randint(1, 99999)
        if ddi not in ddis_gerados:
            ddis_gerados.add(ddi)
            nome = fake.country()[:50] + f"_{ddi}"
            id_m = random.choice(moedas_ids) # Relacionamento NUMÉRICO
            dados_pais.append((ddi, nome, id_m))

    execute_values(cur, "INSERT INTO Pais (ddi, nome, id_moeda) VALUES %s ON CONFLICT DO NOTHING", dados_pais)
    lista_ddis = list(ddis_gerados)
    print(f"✅ Países: {len(dados_pais)}")


    # 3. EMPRESAS (1000)
    dados_empresa = []
    for i in range(1, 1001):
        nome = (fake.company() + f" {i}")[:50]
        fantasia = (nome + " Media")[:50]
        id_nac = fake.bban()[:20]
        ddi = random.choice(lista_ddis)
        dados_empresa.append((i, nome, fantasia, id_nac, ddi))

    execute_values(cur, "INSERT INTO Empresa (id, nome, nome_fantasia, id_nacional, ddi_pais_sede) VALUES %s ON CONFLICT DO NOTHING", dados_empresa)
    empresa_ids = [e[0] for e in dados_empresa]
    print(f"✅ Empresas: {len(dados_empresa)}")


    # 4. PLATAFORMAS (1000)
    dados_plataforma = []
    for i in range(1, 1001):
        nome = f"{fake.word().capitalize()} Stream {i}"[:50]
        qtd_users = random.randint(1000, 10_000_000)
        data_fund = fake.date_between(start_date="-15y", end_date="-1y")
        emp_funda = random.choice(empresa_ids)
        emp_resp = random.choice(empresa_ids)
        dados_plataforma.append((i, nome, qtd_users, data_fund, emp_funda, emp_resp))

    execute_values(cur, "INSERT INTO Plataforma (id, nome, qtd_usuarios, data_fundacao, id_empresa_funda, id_empresa_resp) VALUES %s ON CONFLICT DO NOTHING", dados_plataforma)
    plataforma_ids = [p[0] for p in dados_plataforma]
    print(f"✅ Plataformas: {len(dados_plataforma)}")


    # 5. USUÁRIOS (1000)
    dados_usuario = []
    for i in range(1, 1001):
        nick = f"{fake.user_name().lower()}_{i}"[:50]
        email = f"user{i}@{fake.free_email_domain()}"[:100]
        data_nasc = fake.date_of_birth(minimum_age=13, maximum_age=60)
        telefone = fake.phone_number()[:30]
        end_postal = fake.address().replace("\n", ", ")[:200]
        ddi = random.choice(lista_ddis)
        dados_usuario.append((i, nick, email, data_nasc, telefone, end_postal, ddi))

    execute_values(cur, "INSERT INTO Usuario (id, nick, email, data_nasc, telefone, end_postal, ddi_pais_reside) VALUES %s ON CONFLICT DO NOTHING", dados_usuario)
    usuario_ids = [u[0] for u in dados_usuario]
    print(f"✅ Usuários: {len(dados_usuario)}")


    # 6 e 7. STREAMERS E MEMBROS (Herança PK=FK)
    streamer_ids = usuario_ids[:400]
    membro_ids = usuario_ids[400:]

    dados_streamer = []
    passaportes = set()
    for id_usr in streamer_ids:
        passport = fake.passport_number()[:20]
        while passport in passaportes:
            passport = fake.passport_number()[:20] + str(random.randint(0, 9))
        passaportes.add(passport)
        ddi_nac = random.choice(lista_ddis)
        dados_streamer.append((id_usr, passport, ddi_nac))

    execute_values(cur, "INSERT INTO Streamer (id_usuario, nro_passaporte, ddi_pais_nacionalidade) VALUES %s ON CONFLICT DO NOTHING", dados_streamer)
    print(f"✅ Streamers: {len(dados_streamer)}")

    dados_membro = [(id_usr,) for id_usr in membro_ids]
    execute_values(cur, "INSERT INTO Membro (id_usuario) VALUES %s ON CONFLICT DO NOTHING", dados_membro)
    print(f"✅ Membros: {len(dados_membro)}")


    # 8. TEM_CONTA (1000)
    dados_tem_conta = []
    pares_conta = set()
    while len(dados_tem_conta) < 1000:
        id_usr = random.choice(usuario_ids)
        id_plat = random.choice(plataforma_ids)
        if (id_usr, id_plat) not in pares_conta:
            pares_conta.add((id_usr, id_plat))
            nro_user = f"usr_{fake.lexify('??????????')}"[:50]
            dados_tem_conta.append((id_usr, id_plat, nro_user))

    execute_values(cur, "INSERT INTO TemConta (id_usuario, id_plataforma, nro_usuario) VALUES %s ON CONFLICT DO NOTHING", dados_tem_conta)
    print(f"✅ TemConta: {len(dados_tem_conta)}")


    # 9. CANAIS (1000)
    dados_canal = []
    for i in range(1, 1001):
        id_plat = random.choice(plataforma_ids)
        id_streamer = random.choice(streamer_ids)
        nome = f"Canal_Oficial_{i}"[:100]
        tipo = random.choice(["privado", "público", "misto"])
        data_ini = fake.date_between(start_date="-5y", end_date="today")
        desc = fake.text(max_nb_chars=100)
        dados_canal.append((i, id_plat, id_streamer, nome, tipo, data_ini, desc))

    execute_values(cur, "INSERT INTO Canal (id, id_plataforma, id_streamer, nome, tipo, data_inicio, descricao) VALUES %s ON CONFLICT DO NOTHING", dados_canal)
    canal_ids = [c[0] for c in dados_canal]
    print(f"✅ Canais: {len(dados_canal)}")


    # 10. PATROCÍNIOS (1000)
    dados_patrocina = []
    pares_patrocina = set()
    while len(dados_patrocina) < 1000:
        id_emp = random.choice(empresa_ids)
        id_can = random.choice(canal_ids)
        if (id_emp, id_can) not in pares_patrocina:
            pares_patrocina.add((id_emp, id_can))
            valor = round(random.uniform(1000.0, 50000.0), 2)
            dados_patrocina.append((id_emp, id_can, valor))

    execute_values(cur, "INSERT INTO Patrocina (id_empresa, id_canal, valor) VALUES %s ON CONFLICT DO NOTHING", dados_patrocina)
    print(f"✅ Patrocínios: {len(dados_patrocina)}")


    # 11. NÍVEL CANAL (1000+)
    dados_nivel = []
    niveis_criados = []
    for id_can in canal_ids:
        qtd_niveis = random.randint(1, 3)
        for nivel in range(1, qtd_niveis + 1):
            valor = round(random.uniform(5.0, 50.0), 2)
            gif = f"https://exemplo.com/gif_{id_can}_{nivel}.gif"
            dados_nivel.append((id_can, nivel, valor, gif))
            niveis_criados.append((id_can, nivel))

    execute_values(cur, "INSERT INTO NivelCanal (id_canal, nivel, valor_nivel, gif) VALUES %s ON CONFLICT DO NOTHING", dados_nivel)
    print(f"✅ NivelCanal: {len(dados_nivel)}")


    # 12. INSCRIÇÕES (1000)
    dados_inscricao = []
    pares_inscricao = set()
    while len(dados_inscricao) < 1000:
        id_mem = random.choice(membro_ids)
        nivel_info = random.choice(niveis_criados) # (id_canal, nivel)
        id_can = nivel_info[0]
        nivel = nivel_info[1]
        
        if (id_mem, id_can) not in pares_inscricao:
            pares_inscricao.add((id_mem, id_can))
            dados_inscricao.append((id_mem, id_can, nivel))

    execute_values(cur, "INSERT INTO Inscricao (id_membro, id_canal, nivel) VALUES %s ON CONFLICT DO NOTHING", dados_inscricao)
    print(f"✅ Inscrições: {len(dados_inscricao)}")


    # 13. VÍDEOS (1000)
    dados_video = []
    mapa_dono_video = {} # Para saber quem é o streamer dono do vídeo nas participações
    for i in range(1, 1001):
        canal_info = random.choice(dados_canal) # (id, id_plataforma, id_streamer, ...)
        id_can = canal_info[0]
        id_streamer_dono = canal_info[2]
        
        titulo = f"Video_{i}_{fake.word()}"[:150]
        data_hora = datetime.now() - timedelta(days=random.randint(1, 730), minutes=random.randint(1, 1440))
        duracao = random.randint(60, 14400)
        visu_simul = random.randint(10, 50000)
        tema = random.choice(["Gaming", "Educação", "Música", "Artes", "Tecnologia"])[:100]
        visu_tot = visu_simul * random.randint(2, 20)
        
        dados_video.append((i, id_can, titulo, data_hora, duracao, visu_simul, tema, visu_tot))
        mapa_dono_video[i] = id_streamer_dono

    execute_values(cur, "INSERT INTO Video (id, id_canal, titulo, data_hora, duracao, visu_simulta, tema, visu_total) VALUES %s ON CONFLICT DO NOTHING", dados_video)
    video_ids = [v[0] for v in dados_video]
    print(f"✅ Vídeos: {len(dados_video)}")


    # 14. PARTICIPAÇÕES (1000)
    dados_participa = []
    pares_participa = set()
    while len(dados_participa) < 1000:
        id_vid = random.choice(video_ids)
        dono = mapa_dono_video[id_vid]
        convidado = random.choice(streamer_ids)
        
        # O convidado não pode ser o dono do vídeo
        if convidado != dono and (id_vid, convidado) not in pares_participa:
            pares_participa.add((id_vid, convidado))
            dados_participa.append((id_vid, convidado))

    execute_values(cur, "INSERT INTO Participa (id_video, id_streamer_convidado) VALUES %s ON CONFLICT DO NOTHING", dados_participa)
    print(f"✅ Participações: {len(dados_participa)}")


    # 15. COMENTÁRIOS (1000)
    dados_comentario = []
    for i in range(1, 1001):
        id_vid = random.choice(video_ids)
        id_usr = random.choice(usuario_ids)
        seq = random.randint(1, 99999) # Em seeders, podemos aleatorizar o sequencial
        texto = fake.sentence()[:200]
        data_hora_coment = datetime.now() - timedelta(minutes=random.randint(1, 1440))
        online = random.choice([True, False])
        dados_comentario.append((i, id_vid, id_usr, seq, texto, data_hora_coment, online))

    execute_values(cur, "INSERT INTO Comentario (id, id_video, id_usuario, sequencial, texto, data_hora, online) VALUES %s ON CONFLICT DO NOTHING", dados_comentario)
    comentario_ids = [c[0] for c in dados_comentario]
    print(f"✅ Comentários: {len(dados_comentario)}")


    # 16. DOAÇÕES + PAGAMENTOS (1000)
    dados_doacao = []
    dados_cartao, dados_paypal, dados_btc, dados_mec = [], [], [], []

    for i in range(1, 1001):
        id_coment = comentario_ids[i - 1] # 1 doação por comentário para não dar conflito de Unique
        valor = round(random.uniform(5.0, 500.0), 2)
        status = random.choice(["recusado", "recebido", "lido"])
        dados_doacao.append((i, id_coment, valor, status))

        # Distribui os 1000 pagamentos: 250 para cada tipo
        if i <= 250:
            numero = fake.credit_card_number()[:20]
            bandeira = random.choice(["VISA", "MASTERCARD", "ELO"])[:20]
            dados_cartao.append((i, numero, bandeira, datetime.now()))
        elif i <= 500:
            id_paypal = f"paypal_{i}@{fake.free_email_domain()}"[:100]
            dados_paypal.append((i, id_paypal))
        elif i <= 750:
            tx_id = fake.sha256()[:64]
            dados_btc.append((i, tx_id))
        else:
            seq_mec = random.randint(1, 9999)
            dados_mec.append((i, seq_mec))

    execute_values(cur, "INSERT INTO Doacao (id, id_comentario, valor, status) VALUES %s ON CONFLICT DO NOTHING", dados_doacao)
    print(f"✅ Doações: {len(dados_doacao)}")

    execute_values(cur, "INSERT INTO Cartao_Cred (id_doacao, numero, bandeira, data_hora_cartao) VALUES %s ON CONFLICT DO NOTHING", dados_cartao)
    execute_values(cur, "INSERT INTO Paypal (id_doacao, id_paypal) VALUES %s ON CONFLICT DO NOTHING", dados_paypal)
    execute_values(cur, "INSERT INTO BTC (id_doacao, tx_id) VALUES %s ON CONFLICT DO NOTHING", dados_btc)
    execute_values(cur, "INSERT INTO Mec_plat (id_doacao, sequencial_mec) VALUES %s ON CONFLICT DO NOTHING", dados_mec)
    print(f"✅ Pagamentos: 250 Cartão | 250 PayPal | 250 BTC | 250 Mec_plat")

    print("-" * 70)
    print("🎉 BANCO POPULADO COM SUCESSO E EM ALTA PERFORMANCE!")


# ──────────────────────────────────────────────
# MAIN
# ──────────────────────────────────────────────
def main():
    conn = None
    cur = None
    try:
        conn = conectar_banco()
        cur = conn.cursor()

        if banco_ja_populado(cur):
            print("⚠️  Banco já possui dados — seed ignorado para evitar duplicação.")
            return

        popular_banco(cur)
        conn.commit()
        print("💾 Commit realizado.")

    except Exception as e:
        print(f"\n❌ Erro crítico: {e}")
        if conn:
            conn.rollback()
            print("↩️  Rollback executado.")
    finally:
        if cur:
            cur.close()
        if conn:
            conn.close()
            print("🔌 Conexão encerrada.")


if __name__ == "__main__":
    main()