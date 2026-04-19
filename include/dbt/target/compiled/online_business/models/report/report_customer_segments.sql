SELECT
  c.country,
  c.iso,
  fi.customer_id,
  COUNT(DISTINCT fi.invoice_id) AS num_orders,
  SUM(fi.quantity) AS total_quantity,
  SUM(fi.total_invoice_gbp) AS total_revenue_gbp,
  SUM(fi.total_invoice_usd) AS total_revenue_usd,
  SUM(fi.total_invoice_eur) AS total_revenue_eur,
  ROUND(SUM(fi.total_invoice_gbp) / COUNT(DISTINCT fi.invoice_id), 2) AS avg_order_value_gbp
FROM `de-project-486617`.`online_business_online_business`.`fct_invoices` fi
JOIN `de-project-486617`.`online_business_online_business`.`dim_customers` c ON fi.customer_id = c.customer_id
GROUP BY fi.customer_id, c.country, c.iso
ORDER BY total_revenue_gbp DESC