WITH datetime_cte AS (
  SELECT DISTINCT
    InvoiceDate AS datetime_id,
    COALESCE(
      SAFE.PARSE_DATETIME('%m/%d/%y %H:%M', InvoiceDate),
      SAFE.PARSE_DATETIME('%m/%d/%Y %H:%M', InvoiceDate)
    ) AS date_part
  FROM {{ source('online_business', 'raw_invoices') }}
  WHERE InvoiceDate IS NOT NULL
)
SELECT
  datetime_id,
  date_part as datetime,
  EXTRACT(YEAR FROM date_part) AS year,
  EXTRACT(MONTH FROM date_part) AS month,
  EXTRACT(DAY FROM date_part) AS day,
  EXTRACT(HOUR FROM date_part) AS hour,
  EXTRACT(MINUTE FROM date_part) AS minute,
  EXTRACT(DAYOFWEEK FROM date_part) AS weekday
FROM datetime_cte