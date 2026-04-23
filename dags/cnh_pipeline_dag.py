from airflow import DAG
from airflow.operators.bash import BashOperator
from datetime import datetime, timedelta

# Definições base do nosso cronograma
default_args = {
    'owner': 'engenharia_dados',
    'depends_on_past': False,
    'start_date': datetime(2024, 1, 1),
    'email_on_failure': False,
    'email_on_retry': False,
    'retries': 1,
    'retry_delay': timedelta(minutes=5),
}

# Criamos nossa DAG
with DAG(
    'Datalakehouse_CNH_Dag',
    default_args=default_args,
    description='Orquestração ponta a ponta do Datalakehouse CNH',
    schedule_interval=None, # Deixamos MANUAL por enquanto para você testar no botão Play!
    catchup=False,
    tags=['lakehouse', 'cnh', 'sqlmesh'],
) as dag:

    # Tarefa 1: Gerar os dados crus usando nosso script Python
    gerar_dados = BashOperator(
        task_id='gerar_dados_sistema_origem',
        # Como mapeamos a raiz do projeto para o Airflow, ele enxerga a pasta scripts/
        bash_command='cd /opt/airflow && python3 scripts/generate_sample_data.py',
    )

    # Tarefa 2: Mover os dados recém-gerados para a pasta seeds/ do SQLMesh
    preparar_sementes = BashOperator(
        task_id='preparar_sementes_lakehouse',
        bash_command='mv /opt/airflow/data/motoristas_fake.csv /opt/airflow/seeds/ || true',
    )

    # Tarefa 3: Disparar o SQLMesh!
    # No SQLMesh, "plan --auto-apply" roda tudo automaticamente sem perguntar [y/n] pro usuário!
    rodar_sqlmesh = BashOperator(
        task_id='processar_camada_silver_sqlmesh',
        bash_command='cd /opt/airflow && sqlmesh plan --auto-apply',
    )

    # Aqui nós dizemos ao Airflow a ordem das setinhas (A -> B -> C)
    gerar_dados >> preparar_sementes >> rodar_sqlmesh
