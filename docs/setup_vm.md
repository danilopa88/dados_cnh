# Guia de Configuração: Modern Data Lakehouse na VM 🚀

Este guia contém o passo a passo para replicar a estrutura do Lakehouse dentro da sua máquina virtual Ubuntu.

---

## ⚡ Acesso Remoto (Windows Terminal -> VM)

Para facilitar o copiar/colar de blocos de código grandes, recomenda-se acessar a VM através do terminal do seu Windows (PowerShell/CMD).

### 1. Na VM Ubuntu (Preparação)
Garanta que o servidor de SSH está instalado e rodando:
```bash
sudo apt update && sudo apt install openssh-server -y
```

### 2. No VirtualBox (Redirecionamento de Portas)
1. Vá em **Configurações** da sua VM > **Rede** > **Adaptador 1**.
2. Clique em **Avançado** > **Redirecionamento de Portas**.
3. Adicione uma nova regra com:
   - **Nome:** `SSH`
   - **Protocolo:** `TCP`
   - **Porta Hospedeira (Windows):** `2222`
   - **Porta Convidada (VM):** `22`

### 3. No Windows (Conexão)
Abra o **PowerShell** no Windows e digite:
```powershell
ssh -p 2222 cnh_server@127.0.0.1
```
*(Substitua `cnh_server` pelo seu usuário da VM se for diferente)*

---

## 🏗️ 1. Criar a Estrutura e Arquivos na VM

Copie o bloco abaixo integralmente e cole no terminal da sua VM. Ele garantirá que a estrutura seja criada corretamente a partir da sua pasta pessoal.

```bash
# Garantir que estamos na home para evitar pastas aninhadas
cd ~

# Criar estrutura de diretórios
mkdir -p infra/lakehouse/trino/catalog infra/lakehouse/minio_init

# 1.1 Criar configuração do Trino (Iceberg + Nessie Nativo)
cat <<EOF > infra/lakehouse/trino/catalog/iceberg.properties
connector.name=iceberg
iceberg.catalog.type=nessie
iceberg.nessie-catalog.uri=http://nessie:19120/api/v1
iceberg.nessie-catalog.default-warehouse-dir=s3://warehouse
iceberg.nessie-catalog.ref=main
fs.native-s3.enabled=true
s3.endpoint=http://minio:9000
s3.path-style-access=true
s3.aws-access-key=minioadmin
s3.aws-secret-key=minioadmin
s3.region=us-east-1
EOF

# 1.2 Criar script de inicialização do MinIO
cat <<EOF > infra/lakehouse/minio_init/entrypoint.sh
#!/bin/sh
/usr/bin/mc alias set local http://minio:9000 minioadmin minioadmin;
/usr/bin/mc mb local/warehouse;
/usr/bin/mc anonymous set public local/warehouse;
exit 0;
EOF
chmod +x infra/lakehouse/minio_init/entrypoint.sh

# 1.3 Criar o Docker Compose (com dependências e caminhos limpos)
cat <<EOF > infra/lakehouse/docker-compose.yml
services:
  minio:
    image: minio/minio
    container_name: minio
    environment:
      - MINIO_ROOT_USER=minioadmin
      - MINIO_ROOT_PASSWORD=minioadmin
    ports:
      - "9001:9001"
      - "9000:9000"
    command: server /data --console-address ":9001"
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:9000/minio/health/live"]
      interval: 5s
      timeout: 5s
      retries: 5
    networks:
      - lakehouse

  nessie:
    image: projectnessie/nessie:latest
    container_name: nessie
    ports:
      - "19120:19120"
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:19120/health/live"]
      interval: 5s
      timeout: 5s
      retries: 5
    networks:
      - lakehouse

  trino:
    image: trinodb/trino:latest
    container_name: trino
    depends_on:
      minio:
        condition: service_healthy
      nessie:
        condition: service_healthy
    ports:
      - "8080:8080"
    volumes:
      - ./trino/catalog:/etc/trino/catalog
    networks:
      - lakehouse

  minio-init:
    image: minio/mc
    container_name: minio-init
    depends_on:
      minio:
        condition: service_healthy
    volumes:
      - ./minio_init/entrypoint.sh:/entrypoint.sh
    entrypoint: /bin/sh /entrypoint.sh
    networks:
      - lakehouse

networks:
  lakehouse:
    driver: bridge
EOF
```

---

## 2. Subir o Stack

Com os arquivos criados, basta entrar na pasta e iniciar os containers:

```bash
cd infra/lakehouse
docker compose up -d
```

---

## 3. Verificação Rápida

### Acesso via Navegador
- **MinIO:** `http://localhost:9001` (User: `minioadmin` / Pass: `minioadmin`)
- **Trino:** `http://localhost:8080`

### Teste de Dados (SQL)
Rode o comando abaixo para criar uma tabela e inserir um dado de teste no Iceberg:

```bash
# Entrar no Trino
docker exec -it trino trino

# Comandos SQL (dentro do Trino)
CREATE TABLE iceberg.default.verify_install (id int, status varchar);
INSERT INTO iceberg.default.verify_install VALUES (1, 'Funcionando!');
SELECT * FROM iceberg.default.verify_install;
```

> [!TIP]
> Se você estiver acessando do Windows (host), certifique-se de que o Port Forwarding no VirtualBox está configurado para as portas 9001 e 8080, ou que a rede está em modo Bridge.

---

## 📘 Explicação Técnica (O que cada parte faz)

### 1. Preparação de Canteiro de Obras (`mkdir -p` e `cd ~`)
*   **`cd ~`**: Garante que o script comece na sua pasta pessoal (`/home/cnh_server`). Isso evita a criação de pastas aninhadas (uma pasta dentro da outra por erro de localização).
*   **`mkdir -p`**: Cria a estrutura exata de diretórios necessária para o Docker. O parâmetro `-p` garante que as pastas "pai" sejam criadas automaticamente e evita erros caso elas já existam.

### 1. Conector Iceberg Nativo (`iceberg.properties`)
Este arquivo é o cérebro que ensina o Trino a falar com o seu Lakehouse:
*   **`connector.name=iceberg`**: Define que este catálogo usará o motor do Apache Iceberg.
*   **`iceberg.catalog.type=nessie`**: Escolhe o Nessie como o "gerente" (catálogo) das tabelas.
*   **`iceberg.nessie-catalog.uri=...`**: O endereço onde o Nessie está ouvindo.
*   **`iceberg.nessie-catalog.default-warehouse-dir=s3://warehouse`**: Onde, dentro do MinIO, os dados "vivos" serão salvos.
*   **`fs.native-s3.enabled=true`**: Ativa o motor de alta performance do Trino para falar com o S3/MinIO.
*   **`s3.endpoint=http://minio:9000`**: O endereço do nosso servidor de arquivos.
*   **`s3.path-style-access=true`**: Essencial para o MinIO. Diz ao Trino para usar `minio/bucket` em vez de `bucket.minio`.
*   **`s3.region=us-east-1`**: Define uma região fictícia (exigida por versões modernas do Trino).

### 2. Automação do Storage (`entrypoint.sh`)
O "entrypoint" é o primeiro comando que o container `minio-init` roda ao nascer:
*   **`mc alias set local...`**: Cria uma conexão salva chamada `local` para o nosso servidor MinIO. É como salvar uma senha no navegador.
*   **`mc mb local/warehouse`**: Comando "Make Bucket". Cria a pasta raiz física onde os dados estarão.
*   **`mc anonymous set public...`**: Define que qualquer um pode ler os dados nesse bucket, facilitando testes de BI e ingestão.

### 3. Orquestração Avançada (`docker-compose.yml`)
O Docker Compose é o "maestro" que coordena os 4 serviços:

#### Configurações de "Saúde" (Healthchecks)
*   **`test: ["CMD", "curl", "-f", ...]`**: O Docker "pinga" o serviço a cada 5 segundos para ver se ele está respondendo.
*   **`condition: service_healthy`**: O Trino só começa a carregar quando o MinIO e o Nessie confirmam que estão 100% prontos. Isso evita falhas de boot!

#### Redes e Volumes
*   **`networks: lakehouse`**: Cria uma rede virtual privada. Nela, os containers se chamam pelo nome (ex: o Trino chama o `minio` pelo nome, não pelo IP).
*   **`volumes: ./trino/catalog:/etc/trino/catalog`**: Faz uma ponte entre a sua pasta na VM e o interior do container. Alterou o arquivo na VM? O Trino "lê" a mudança na hora.

---

## 🆘 Solução de Problemas

### Erro: `ICEBERG_FILESYSTEM_ERROR`
Se o Trino der este erro ao tentar criar uma tabela, geralmente significa que o bucket `warehouse` não foi criado.

**Como resolver manualmente:**
No terminal da VM, force a criação do bucket com este comando:
```bash
docker compose run --rm minio-init mc alias set local http://minio:9000 minioadmin minioadmin
docker compose run --rm minio-init mc mb local/warehouse
```

### Como sair do terminal do Trino?
Basta digitar `quit;` ou pressionar `Ctrl + D`.

### Trino demorando para subir (`SERVER_STARTING_UP`)
O Trino pode levar até 2 minutos para carregar todos os plugins na primeira vez. Tenha paciência!
