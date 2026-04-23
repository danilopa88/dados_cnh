MODEL (
  name silver.motoristas_validados,
  kind FULL,
  cron '@daily'
);

SELECT
  id_motorista
  nome,
  cpf,
  categoria,
  registro_cnh,
  CAST(data_emissao AS DATE) AS data_emissao,
  CAST(data_vencimento AS DATE) AS data_vencimento,
  CAST(snapshot_date AS TIMESTAMP) AS snapshot_date
FROM silver.raw_motoristas


