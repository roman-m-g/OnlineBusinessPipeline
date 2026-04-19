SELECT
  dt.year,
  dt.month,
  COUNT(DISTINCT fi.invoice_id) AS num_invoices,
  SUM(fi.quantity) AS total_quantity,
  SUM(fi.total_invoice_gbp) AS total_revenue_gbp,
  SUM(fi.total_invoice_usd) AS total_revenue_usd,
  SUM(fi.total_invoice_eur) AS total_revenue_eur
FROM `de-project-486617`.`online_business_online_business`.`fct_invoices` fi
JOIN `de-project-486617`.`online_business_online_business`.`dim_datetime` dt ON fi.datetime_id = dt.datetime_id
GROUP BY dt.year, dt.month
ORDER BY dt.year, dt.month