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

## 🚀 Como iniciar
1. **Pré-requisitos:** Docker e Docker Compose instalados.
2. **Setup da Infra:**
   ```bash
   cd infra/lakehouse
   docker compose up -d
   ```
3. **Validar:** Acesse o Trino UI em `http://localhost:8080`.

---
*Desenvolvido como parte do projeto de Modern DataStack.*
