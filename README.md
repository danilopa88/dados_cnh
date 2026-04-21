# Projeto Dados CNH - Modern Data Lakehouse 🚛💨

Este repositório contém a implementação de um **Modern Data Lakehouse** para processamento e análise de dados relacionados a condutores (CNH), utilizando uma arquitetura baseada em **Apache Iceberg**.

## 🏗️ Arquitetura
A stack tecnológica é composta por:
- **Storage:** MinIO (S3-compatible)
- **Table Format:** Apache Iceberg
- **Catalog:** Project Nessie (Git-like catalog)
- **Engine:** Trino (Distributed SQL)
- **Ingestion:** dlt (Data Load Tool)
- **Transformation:** SQLMesh

## 📂 Estrutura do Projeto
- `/infra`: Arquivos de orquestração de containers e setup de infraestrutura.
- `/pipelines`: Código fonte das ferramentas de ingestão e transformação de dados.
- `/docs`: Documentação técnica e diagramas de arquitetura.
- `/scripts`: Utilitários para configuração do ambiente de desenvolvimento.

## 🚀 Como Iniciar

### 1. Infraestrutura (VM)
1. Garanta que o Docker esteja rodando.
2. Acesse a pasta de infra: `cd infra/lakehouse`
3. Suba o stack: `docker-compose up -d`

### 2. Ambiente de Dados (Local)
Para rodar a ingestão a partir do seu host, instale as dependências Python:
```bash
pip install pandas dlt "dlt[pyiceberg]" s3fs tzdata
```

### 3. Fluxo de Ingestão (Bronze Layer)
1. **Gerar Dados:** Crie 1.000 registros de teste:
   ```bash
   python scripts/generate_sample_data.py
   ```
2. **Executar Ingestão:** Envie os dados para o MinIO/Iceberg:
   ```bash
   python pipelines/cnh_ingestion.py
   ```

## 🛠️ Solução de Problemas
- **Windows Timezone:** Caso receba erro de `tzdata` no PyArrow, o script já contém o fix `PYARROW_IGNORE_TIMEZONE`.
- **Port Forwarding:** Se estiver usando VM, certifique-se de que as portas `9000` (MinIO) e `19120` (Nessie) estão redirecionadas no VirtualBox.

---
*Desenvolvido como parte do projeto de Modern DataStack.*
