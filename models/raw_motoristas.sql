MODEL (
  name silver.raw_motoristas,
  kind SEED (
    path '../seeds/motoristas_fake.csv'
  ),
  columns (
    id_motorista INT,
    nome_completo VARCHAR,
    cpf VARCHAR,
    registro_cnh VARCHAR,
    categoria VARCHAR,
    data_emissao VARCHAR,
    data_vencimento VARCHAR,
    snapshot_date VARCHAR
  )
);
