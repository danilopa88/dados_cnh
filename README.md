# Projeto Dados CNH - Modern Data Lakehouse 🚛❄️

Bem-vindo ao repositório do **Modern Data Lakehouse para Dados de Condutores (CNH)**. Este projeto foi concebido para ser uma demonstração "Estado da Arte" (State-of-the-Art) de como equipes de Engenharia de Dados corporativas estruturam seus ambientes usando componentes de código aberto de altíssimo desempenho, superando as lentidões e custos dos antigos Data Warehouses locais.

O projeto implementa uma **Arquitetura Medallion (Bronze, Silver, Gold)** com foco em dados massivos, separando totalmente a camada de Processamento, Armazenamento e Governança num ecossistema isolado e sustentável.

---

## 🏗️ A Arquitetura Física e Lógica

Para evitar os conhecidos conflitos do ecossistema Windows com volumes do Docker (como bloqueios de permissões ou I/O engasgado), optamos por migrar todo o ambiente do Lakehouse para dentro de uma máquina virtual isolada rodando Linux.

### Tecnologias Escolhidas
1. **VirtualBox + Ubuntu Server:** O motor físico (VM com >= 40GB de disco para suportar Imagens Docker pesadas). O desenvolvimento acontece remotamente usando a extensão **VS Code Remote - SSH**.
2. **MinIO:** O sistema nervoso de longo prazo (Storage). Ele emula todos os comportamentos de um Bucket Amazon S3 rodando localmente na nossa própria máquina.
3. **Apache Iceberg:** O "cérebro" das tabelas. Ele substitui os clássicos e frágeis diretórios de Parquet do Hive, permitindo transações ACID (Insert/Update/Delete clássicos) em cima de arquivos perdidos no S3.
4. **Project Nessie:** O Catálogo Governamental. Funciona exatamente como um "Git", mas para os seus dados. Ele permite criar *branches* das tabelas para testes em desenvolvimento sem afetar o dado de produção, controlando o Apache Iceberg.
5. **Trino (Antes PrestoSQL):** O Motor Ferrari (Query Engine). Um processador SQL maciçamente distribuído que não salva dados, ele apenas varre o MinIO a velocidades absurdas utilizando o catálogo do Nessie.
6. **dlt (Data Load Tool):** A biblioteca em Python ágil responsável por buscar os dados das "fontes" e inseri-los suavemente na camada Bronze crua.
7. **SQLMesh:** O framework de transformação moderno (que desafia o dbt). Ele entende o fluxo das tabelas, cria Views incrementais e constrói de forma inteligente as tabelas Silver e Gold no Iceberg passando comandos para o Trino.

---

## 🚀 Guia de Operação da Infraestrutura

Todo o projeto supõe que você está conectado via `SSH` dentro da sua Máquina Virtual (Linux) através do VS Code. **Nunca rode isso diretamente no Windows.**

### 1. Requisitos Prévios do Servidor (Linux VM)
Como o ambiente exige muito armazenamento transiente de imagens, a VM requer **acessos corretos e instalações**:
```bash
# Atualizações base, instalação do Python, e criação do ambiente Docker
sudo apt update && sudo apt install openssh-server docker.io docker-compose python3-pip python3-venv -y

# Autorizando o usuário a controlar os containers sem exigir `sudo`
sudo usermod -aG docker $USER
```

### 2. Ativando o Data Lakehouse (Containers)
Com a infraestrutura de rede na VM alinhada, podemos "acordar" os microsserviços. Eles estão mapeados no arquivo `docker-compose.yml`.
```bash
# Entrar no diretório dos manifestos Docker
cd infra/lakehouse

# Iniciar MinIO, Nessie e Trino em segundo plano
docker-compose up -d
```
> **Dica Visual:** No seu VS Code Remoto, use a funcionalidade **"Ports (Portas)"** para encaminhar a porta `9001` (Modo Gráfico do MinIO) e `8080` (Modo Gráfico do Trino) para conseguir abrir no Google Chrome do seu Windows utilizando o endereço `http://localhost:X`.

### 3. A Ingestão Inicial: Dados Brutos (Camada Semente / Bronze)
Neste projeto, utilizamos scripts geradores localizados em `scripts/` para simular um fluxo de motoristas.

```bash
# Ativação do ambiente Python Seguro
python3 -m venv .venv
source .venv/bin/activate
pip install pandas dlt "dlt[pyiceberg]" s3fs tzdata sqlmesh[trino]

# Gerar 1000 CPFs sintéticos em motoristas_fake.csv
python3 scripts/generate_sample_data.py

# Injetar dados no Datalake via DLT
# Nota: Podemos usar SQLMesh Seeds para ingerir diretamente o CSV como Iceberg
```

### 4. Transformação, Validação e Modelagem (SQLMesh)
Para que os dados brutos deixem de ser arquivos "soltos", nós ativamos nossa engine de Transformação (SQLMesh) para materializá-los.

```bash
# O SQLMesh precisa estar devidamente configurado via config.yaml.
sqlmesh info
sqlmesh plan
```
O comando `plan` compara o ambiente de arquivos (`/models`, `/seeds`) com o que já foi criado no Iceberg, gera o código SQL responsável por inserir os dados na tabela e pede sua autorização para executar os jobs dentro do cluster Trino.

---

## 🛠️ Problemas (Troubleshooting Oficial)

Se você tropeçar nas configurações de ambiente, estas foram as lutas já vencidas nos laboratórios e as respectivas soluções definitivas:

#### 1. VS Code Não conecta - "Could not establish connection to localhost" ou `Connection refused` (Erro de SSH)
Isso significa que o seu VirtualBox não esticou o túnel até o Windows.
**Solução:** Certifique-se de que a VM original tem o "Redirecionamento de Portas" (Port Forwarding) ativado na aba "Módulo NAT", conectando a Porta Host `2222` na Porta Convidado `22`. Se persistir, o identificador digital pode ter expirado. Rode no seu PowerShell (Windows): `ssh-keygen -R "[localhost]:2222"`.

#### 2. VS Code trava na instalação / Terminal Linux diz "[Errno 28] No space left on device"
**Solução:** A sua VirtualBox foi criada com o Disco VDI padrão limitante. Imagens como a do Trino chegam fácil a 2GB+. Redimensione ou crie sua VM com o armazenamento de no mínimo **40GB** e recomece do terminal, senão qualquer log do sistema irá colapsar o HD Virtual.

#### 3. Container do Trino morre na inicialização (`docker logs trino` aponta 26 Erros Guice - `Unable to load AWS Region`)
**Solução:** O arquivo `iceberg.properties` (nosso link entre Trino e S3 Nativo) é rigoroso nas versões recentes. Vá à pasta `/infra/lakehouse/trino/catalog/` e certifique-se de que existem, *literalmente*:
- `fs.native-s3.enabled=true`
- `s3.region=us-east-1` (Indispensável para o S3 SDK compilar as injeções java na porta 8080)

#### 4. O `sqlmesh info` falha com `HTTPConnectionPool ... Connection refused`
**Solução:** O Python Client do lado do SQLMesh está agressivamente buscando `https://localhost:8080`, mas o seu cluster Trino é ambiente de Desenvolvimento Limpo (`http://`).
Basta incluir a chave `http_scheme: http` no bloco de `connection:` do arquivo Mestre `config.yaml` do projeto.

---
🚀 *Feito com muito orgulho usando Python, MinIO e Engenharia Moderna.*
