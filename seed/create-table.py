import os
import random
from datetime import datetime, timedelta
import sys
import psycopg2
from psycopg2.extras import execute_values
from faker import Faker
from dotenv import load_dotenv

env_path = os.path.join(os.path.dirname(__file__), '..', '.env')
load_dotenv(dotenv_path=env_path)

fake = Faker(['pt_BR', 'en_US'])
Faker.seed(42)
random.seed(42)

def banco_ja_populado(cur):
    try:
        cur.execute("SELECT COUNT(*) FROM Moeda;")
        quantidade = cur.fetchone()[0]
        return quantidade > 0
    except Exception as e:
        cur.co

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
# SEED
# ──────────────────────────────────────────────
def popular_banco(cur):
    print("\n🚀 INICIANDO CARGA — meta: ~1000 tuplas por tabela")
    print("-" * 70)

    # 1. MOEDAS (1000)
    dados_moeda = []
    moedas_geradas = set()
    tentativas = 0
    while len(dados_moeda) < 1000 and tentativas < 5000:
        tentativas += 1
        codigo = fake.currency_code()
        if codigo in moedas_geradas:
            codigo = f"{codigo[:2]}{random.randint(10, 99)}"
        if codigo not in moedas_geradas and len(codigo) <= 10:
            moedas_geradas.add(codigo)
            taxa = round(random.uniform(0.01, 10.0), 4)
            dados_moeda.append((codigo, taxa))

    execute_values(
        cur,
        "INSERT INTO Moeda (nome_moeda, fat_conversao) VALUES %s ON CONFLICT DO NOTHING",
        dados_moeda,
    )
    lista_moedas = list(moedas_geradas)
    print(f"✅ Moedas: {len(dados_moeda)}")

    # 2. PAÍSES (1000)
    dados_pais = []
    ddis_gerados = set()
    while len(dados_pais) < 1000:
        ddi = random.randint(1, 99999)
        if ddi not in ddis_gerados:
            ddis_gerados.add(ddi)
            nome = fake.country()[:50] + f"_{ddi}"   # garante unicidade
            moeda = random.choice(lista_moedas)
            dados_pais.append((ddi, nome, moeda))

    execute_values(
        cur,
        "INSERT INTO Pais (ddi, nome, nome_moeda) VALUES %s ON CONFLICT DO NOTHING",
        dados_pais,
    )
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

    execute_values(
        cur,
        "INSERT INTO Empresa (numero, nome, nome_fantasia, id_nacional, ddi_pais_sede) VALUES %s ON CONFLICT DO NOTHING",
        dados_empresa,
    )
    lista_empresas = [e[0] for e in dados_empresa]
    print(f"✅ Empresas: {len(dados_empresa)}")

    # 4. PLATAFORMAS (1000)
    dados_plataforma = []
    for i in range(1, 1001):
        nome = f"{fake.word().capitalize()} Stream {i}"[:50]
        qtd_users = random.randint(1000, 10_000_000)
        data_fund = fake.date_between(start_date="-15y", end_date="-1y")
        emp_funda = random.choice(lista_empresas)
        emp_resp = random.choice(lista_empresas)
        dados_plataforma.append((i, nome, qtd_users, data_fund, emp_funda, emp_resp))

    execute_values(
        cur,
        "INSERT INTO Plataforma (numero, nome, qtd_usuarios, data_fundacao, empresa_funda_nro, empresa_resp_nro) VALUES %s ON CONFLICT DO NOTHING",
        dados_plataforma,
    )
    lista_plataformas = [p[0] for p in dados_plataforma]
    print(f"✅ Plataformas: {len(dados_plataforma)}")

    # 5. USUÁRIOS (1000)
    dados_usuario = []
    nicks_gerados = []
    for i in range(1000):
        nick = f"{fake.user_name().lower()}_{i}"[:50]
        email = f"user{i}@{fake.free_email_domain()}"[:100]
        data_nasc = fake.date_of_birth(minimum_age=13, maximum_age=60)
        telefone = fake.phone_number()[:30]
        end_postal = fake.address().replace("\n", ", ")[:200]
        ddi = random.choice(lista_ddis)
        dados_usuario.append((nick, email, data_nasc, telefone, end_postal, ddi))
        nicks_gerados.append(nick)

    execute_values(
        cur,
        "INSERT INTO Usuario (nick, email, data_nasc, telefone, end_postal, ddi_pais_reside) VALUES %s ON CONFLICT DO NOTHING",
        dados_usuario,
    )
    print(f"✅ Usuários: {len(dados_usuario)}")

    # 6. STREAMERS (400) e MEMBROS (600)
    streamers = nicks_gerados[:400]
    membros = nicks_gerados[400:]

    dados_streamer = []
    passaportes = set()
    for nick in streamers:
        passport = fake.passport_number()[:20]
        while passport in passaportes:
            passport = fake.passport_number()[:20] + str(random.randint(0, 9))
        passaportes.add(passport)
        ddi_nac = random.choice(lista_ddis)
        dados_streamer.append((nick, passport, ddi_nac))

    execute_values(
        cur,
        "INSERT INTO Streamer (nick_streamer, nro_passaporte, ddi_pais_nacionalidade) VALUES %s ON CONFLICT DO NOTHING",
        dados_streamer,
    )
    print(f"✅ Streamers: {len(dados_streamer)}")

    dados_membro = [(nick,) for nick in membros]
    execute_values(
        cur,
        "INSERT INTO Membro (nick_membro) VALUES %s ON CONFLICT DO NOTHING",
        dados_membro,
    )
    print(f"✅ Membros: {len(dados_membro)}")

    # 7. TEM_CONTA (1000)
    dados_tem_conta = []
    pares_conta = set()
    tentativas = 0
    while len(dados_tem_conta) < 1000 and tentativas < 10000:
        tentativas += 1
        nick = random.choice(nicks_gerados)
        plat = random.choice(lista_plataformas)
        par = (nick, plat)
        if par not in pares_conta:
            pares_conta.add(par)
            nro_user = f"usr_{fake.lexify('??????????')}"[:50]
            dados_tem_conta.append((nick, plat, nro_user))

    execute_values(
        cur,
        "INSERT INTO TemConta (nick_usuario, nro_plataforma, nro_usuario) VALUES %s ON CONFLICT DO NOTHING",
        dados_tem_conta,
    )
    print(f"✅ TemConta: {len(dados_tem_conta)}")

    # 8. CANAIS (1000)
    dados_canal = []
    canais_criados = []
    pares_canal = set()
    tentativas = 0
    while len(dados_canal) < 1000 and tentativas < 10000:
        tentativas += 1
        streamer = random.choice(streamers)
        plat = random.choice(lista_plataformas)
        idx = len(dados_canal)
        nome_canal = f"Canal_{streamer[:15]}_{idx}"[:50]
        par = (nome_canal, plat, streamer)
        if par not in pares_canal:
            pares_canal.add(par)
            tipo = random.choice(["privado", "público", "misto"])
            data_ini = fake.date_between(start_date="-5y", end_date="today")
            desc = fake.text(max_nb_chars=100)
            dados_canal.append((nome_canal, plat, streamer, tipo, data_ini, desc))
            canais_criados.append((nome_canal, plat, streamer))

    execute_values(
        cur,
        "INSERT INTO Canal (nome, nro_plataforma, nick_streamer, tipo, data_inicio, descricao) VALUES %s ON CONFLICT DO NOTHING",
        dados_canal,
    )
    print(f"✅ Canais: {len(dados_canal)}")

    # 9. NÍVEIS DE CANAL (1000 — ~1 nível por canal, alguns com 2)
    dados_nivel = []
    niveis_criados = []
    # 500 canais com 2 níveis = 1000
    for idx, canal in enumerate(canais_criados):
        qtd_niveis = 2 if idx < 500 else 1
        for nivel in range(1, qtd_niveis + 1):
            valor = round(random.uniform(5.0, 50.0), 2)
            gif = f"https://cdn.exemplo.com/gif/{canal[0][:10]}_{nivel}.gif"[:255]
            dados_nivel.append((canal[0], canal[1], canal[2], nivel, valor, gif))
            niveis_criados.append((canal[0], canal[1], canal[2], nivel))

    execute_values(
        cur,
        "INSERT INTO NivelCanal (nome_canal, nro_plataforma, nick_streamer, nivel, valor_nivel, gif) VALUES %s ON CONFLICT DO NOTHING",
        dados_nivel,
    )
    print(f"✅ NivelCanal: {len(dados_nivel)}")

    # 10. INSCRIÇÕES (1000)
    dados_inscricao = []
    pares_inscricao = set()
    tentativas = 0
    while len(dados_inscricao) < 1000 and tentativas < 20000:
        tentativas += 1
        membro = random.choice(membros)
        nivel_info = random.choice(niveis_criados)
        par = (membro, nivel_info[0], nivel_info[1], nivel_info[2], nivel_info[3])
        if par not in pares_inscricao:
            pares_inscricao.add(par)
            dados_inscricao.append(par)

    execute_values(
        cur,
        "INSERT INTO Inscricao (nick_membro, nome_canal, nro_plataforma, nick_streamer, nivel) VALUES %s ON CONFLICT DO NOTHING",
        dados_inscricao,
    )
    print(f"✅ Inscrições: {len(dados_inscricao)}")

    # 11. VÍDEOS (1000)
    dados_video = []
    videos_criados = []
    for i in range(1000):
        canal = random.choice(canais_criados)
        titulo = f"Video_{i}_{fake.word()}"[:100]
        data_hora = datetime.now() - timedelta(
            days=random.randint(1, 730), minutes=random.randint(1, 1440)
        )
        duracao = random.randint(60, 14400)
        visu_simul = random.randint(10, 50000)
        tema = random.choice(["Gaming", "Educação", "Música", "Artes", "Tecnologia"])[:50]
        visu_tot = visu_simul * random.randint(2, 20)
        dados_video.append(
            (titulo, data_hora, canal[0], canal[1], canal[2], duracao, visu_simul, tema, visu_tot)
        )
        videos_criados.append((titulo, data_hora, canal[0], canal[1], canal[2]))

    execute_values(
        cur,
        "INSERT INTO Video (titulo, data_hora, nome_canal, nro_plataforma, nick_streamer, duracao, visu_simulta, tema, visu_total) VALUES %s ON CONFLICT DO NOTHING",
        dados_video,
    )
    print(f"✅ Vídeos: {len(dados_video)}")

    # 12. PARTICIPA / COLLABS (1000)
    dados_participa = []
    pares_participa = set()
    tentativas = 0
    while len(dados_participa) < 1000 and tentativas < 20000:
        tentativas += 1
        video = random.choice(videos_criados)
        convidado = random.choice(streamers)
        par = (convidado, video[0], video[1], video[4])
        if convidado != video[4] and par not in pares_participa:
            pares_participa.add(par)
            dados_participa.append(
                (convidado, video[0], video[1], video[2], video[3], video[4])
            )

    execute_values(
        cur,
        "INSERT INTO Participa (nick_streamer_convidado, titulo_video, data_hora_video, nome_canal, nro_plataforma, nick_streamer_dono) VALUES %s ON CONFLICT DO NOTHING",
        dados_participa,
    )
    print(f"✅ Participações: {len(dados_participa)}")

    # 13. COMENTÁRIOS (1000) — sequencial por vídeo, sem colisão de PK
    dados_comentario = []
    comentarios_criados = []
    seq_por_video: dict = {}
    for _ in range(1000):
        video = random.choice(videos_criados)
        chave_video = (video[0], video[1], video[2], video[3], video[4])
        seq = seq_por_video.get(chave_video, 0) + 1
        seq_por_video[chave_video] = seq

        usuario = random.choice(nicks_gerados)
        texto = fake.sentence()[:200]
        data_hora_coment = video[1] + timedelta(minutes=random.randint(1, 1440))
        online = random.choice([True, False])

        tupla = (
            seq, usuario,
            video[0], video[1], video[2], video[3], video[4],
            texto, data_hora_coment, online,
        )
        dados_comentario.append(tupla)
        comentarios_criados.append(tupla)

    execute_values(
        cur,
        """INSERT INTO Comentario
           (sequencial, nick_usuario, titulo_video, data_hora_video,
            nome_canal, nro_plataforma, nick_streamer,
            texto, data_hora, online)
           VALUES %s ON CONFLICT DO NOTHING""",
        dados_comentario,
    )
    print(f"✅ Comentários: {len(dados_comentario)}")

    # 14. DOAÇÕES + PAGAMENTOS (1000 doações — 250 por método)
    dados_doacao = []
    dados_cartao, dados_paypal, dados_btc, dados_mec = [], [], [], []

    amostra = random.sample(comentarios_criados, min(1000, len(comentarios_criados)))

    for i, c in enumerate(amostra, start=1):
        valor = round(random.uniform(5.0, 500.0), 2)
        status = random.choice(["recusado", "recebido", "lido"])

        base = (i, c[0], c[1], c[2], c[3], c[4], c[5], c[6])
        dados_doacao.append((*base, valor, status))

        if i <= 250:
            numero = fake.credit_card_number()[:20]
            bandeira = random.choice(["VISA", "MASTERCARD", "ELO"])[:20]
            dados_cartao.append((*base, numero, bandeira, datetime.now()))
        elif i <= 500:
            id_paypal = f"paypal_{i}@{fake.free_email_domain()}"[:100]
            dados_paypal.append((*base, id_paypal))
        elif i <= 750:
            tx_id = fake.sha256()[:64]
            dados_btc.append((*base, tx_id))
        else:
            seq_mec = random.randint(1, 9999)
            dados_mec.append((*base, seq_mec))

    execute_values(
        cur,
        """INSERT INTO Doacao
           (sequencial_doacao, sequencial_coment, nick_usuario,
            titulo_video, data_hora_video, nome_canal, nro_plataforma,
            nick_streamer, valor, status)
           VALUES %s ON CONFLICT DO NOTHING""",
        dados_doacao,
    )
    print(f"✅ Doações: {len(dados_doacao)}")

    execute_values(
        cur,
        """INSERT INTO Cartao_Cred
           (sequencial_doacao, sequencial_coment, nick_usuario,
            titulo_video, data_hora_video, nome_canal, nro_plataforma,
            nick_streamer, numero, bandeira, data_hora_cartao)
           VALUES %s ON CONFLICT DO NOTHING""",
        dados_cartao,
    )

    execute_values(
        cur,
        """INSERT INTO Paypal
           (sequencial_doacao, sequencial_coment, nick_usuario,
            titulo_video, data_hora_video, nome_canal, nro_plataforma,
            nick_streamer, id_paypal)
           VALUES %s ON CONFLICT DO NOTHING""",
        dados_paypal,
    )

    execute_values(
        cur,
        """INSERT INTO BTC
           (sequencial_doacao, sequencial_coment, nick_usuario,
            titulo_video, data_hora_video, nome_canal, nro_plataforma,
            nick_streamer, tx_id)
           VALUES %s ON CONFLICT DO NOTHING""",
        dados_btc,
    )

    execute_values(
        cur,
        """INSERT INTO Mec_plat
           (sequencial_doacao, sequencial_coment, nick_usuario,
            titulo_video, data_hora_video, nome_canal, nro_plataforma,
            nick_streamer, sequencial_mec)
           VALUES %s ON CONFLICT DO NOTHING""",
        dados_mec,
    )
    print(f"✅ Pagamentos: 250 Cartão | 250 PayPal | 250 BTC | 250 Mec_plat")

    # 15. PATROCÍNIOS (1000)
    dados_patrocina = []
    pares_patrocina = set()
    tentativas = 0
    while len(dados_patrocina) < 1000 and tentativas < 20000:
        tentativas += 1
        canal = random.choice(canais_criados)
        empresa = random.choice(lista_empresas)
        par = (empresa, canal[0], canal[1], canal[2])
        if par not in pares_patrocina:
            pares_patrocina.add(par)
            valor = round(random.uniform(1000.0, 50000.0), 2)
            dados_patrocina.append((*par, valor))

    execute_values(
        cur,
        "INSERT INTO Patrocina (nro_empresa, nome_canal, nro_plataforma, nick_streamer, valor) VALUES %s ON CONFLICT DO NOTHING",
        dados_patrocina,
    )
    print(f"✅ Patrocínios: {len(dados_patrocina)}")

    print("-" * 70)
    print("🎉 BANCO POPULADO COM SUCESSO!")


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