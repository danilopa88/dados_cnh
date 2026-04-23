MODEL (
  name silver.raw_motoristas,
  kind SEED (
    path '../seeds/motoristas_fake.csv'
  ),
  columns (
    id INT,
    nome VARCHAR,
    cpf VARCHAR,
    categoria VARCHAR,
    data_emissao VARCHAR,
    data_vencimento VARCHAR,
    pontos INT,
    status VARCHAR,
    snapshot_date VARCHAR
  )
);
