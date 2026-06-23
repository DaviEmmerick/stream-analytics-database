### README provisorio

#### 1. Garanta que o banco está rodando

docker compose up -d

##### 2. Crie o servidor no pgAdmin
Abra o pgAdmin.

Clique com o botão direito em Servers (na barra lateral esquerda).

Vá em Register > Server...


#### 3. Preencha as credenciais
Aba General (Geral):

Name: Digite um nome qualquer (ex: Streamer DB).

Aba Connection (Conexão):

Host name/address: 127.0.0.1 (usar os números costuma ser mais certeiro que escrever localhost)

Port: 5433 

Maintenance database: streamerdb

Username: streamer

Password: streamer123