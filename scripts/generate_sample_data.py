import pandas as pd
import random
from datetime import datetime, timedelta
import os

def generate_cnh_data(n=1000):
    categories = ['A', 'B', 'AB', 'C', 'D', 'E', 'AC', 'AD', 'AE']
    names = ['Joao', 'Maria', 'Jose', 'Ana', 'Carlos', 'Paulo', 'Adriana', 'Beatriz', 'Ricardo', 'Fernanda']
    surnames = ['Silva', 'Santos', 'Oliveira', 'Souza', 'Rodrigues', 'Ferreira', 'Alves', 'Pereira', 'Lima', 'Gomes']
    
    data = []
    start_date = datetime(2010, 1, 1)
    
    for i in range(n):
        first_name = random.choice(names)
        last_name = random.choice(surnames)
        full_name = f"{first_name} {last_name}"
        cpf = f"{random.randint(100, 999)}.{random.randint(100, 999)}.{random.randint(100, 999)}-{random.randint(10, 99)}"
        cnh_number = random.randint(100000000, 999999999)
        category = random.choice(categories)
        issue_date = start_date + timedelta(days=random.randint(0, 5000))
        expiry_date = issue_date + timedelta(days=3650) # 10 years validity
        
        data.append({
            'id_motorista': i + 1,
            'nome_completo': full_name,
            'cpf': cpf,
            'registro_cnh': cnh_number,
            'categoria': category,
            'data_emissao': issue_date,
            'data_vencimento': expiry_date,
            'snapshot_date': datetime.now()
        })
    
    return pd.DataFrame(data)

if __name__ == "__main__":
    print("Iniciando: Gerando dados de exemplo...")
    df = generate_cnh_data(1000)
    
    os.makedirs('data', exist_ok=True)
    df.to_csv('data/motoristas_fake.csv', index=False)
    
    print(f"Sucesso: Arquivo gerado em: data/motoristas_fake.csv")
    print(df.head())
