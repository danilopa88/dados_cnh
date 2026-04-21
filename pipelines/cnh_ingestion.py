import dlt
import pandas as pd
import os

# Correção para PyArrow no Windows
os.environ['PYARROW_IGNORE_TIMEZONE'] = '1'

# --- Configurações de Conectividade ---
# 1. Apontando para o MinIO (Filesystem)
os.environ['DESTINATION__FILESYSTEM__BUCKET_URL'] = 's3://warehouse/bronze_staged'
os.environ['DESTINATION__FILESYSTEM__CREDENTIALS__AWS_ACCESS_KEY_ID'] = 'minioadmin'
os.environ['DESTINATION__FILESYSTEM__CREDENTIALS__AWS_SECRET_ACCESS_KEY'] = 'minioadmin'
os.environ['DESTINATION__FILESYSTEM__CREDENTIALS__ENDPOINT_URL'] = 'http://localhost:9000'
os.environ['DESTINATION__FILESYSTEM__CREDENTIALS__REGION_NAME'] = 'us-east-1'

def load_cnh_to_bronze():
    print("Iniciando: Lendo dados do arquivo local...")
    df = pd.read_csv('data/motoristas_fake.csv')
    
    # Convertendo datas para STRING para evitar erros de timezone/sistema no Windows (Camada Bronze)
    df['data_emissao'] = pd.to_datetime(df['data_emissao']).dt.strftime('%Y-%m-%d')
    df['data_vencimento'] = pd.to_datetime(df['data_vencimento']).dt.strftime('%Y-%m-%d')
    df['snapshot_date'] = pd.to_datetime(df['snapshot_date']).dt.strftime('%Y-%m-%d %H:%M:%S')

    print("Iniciando: Pipeline dlt para Filesystem/Parquet (Bronze Isolation)...")
    
    pipeline = dlt.pipeline(
        pipeline_name='cnh_ingestion_staged',
        destination='filesystem',
        dataset_name='motoristas_staged'
    )

    # Executamos a carga como Parquet
    load_info = pipeline.run(
        df, 
        table_name="motoristas_raw", 
        write_disposition="append",
        loader_file_format="parquet"
    )

    print("Sucesso: Dados enviados para o Stage no MinIO!")
    print(load_info)

if __name__ == "__main__":
    try:
        load_cnh_to_bronze()
    except Exception as e:
        print(f"Erro durante a ingestao: {e}")
