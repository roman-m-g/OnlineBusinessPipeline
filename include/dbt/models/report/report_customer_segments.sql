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
FROM {{ ref('fct_invoices') }} fi
JOIN {{ ref('dim_customers') }} c ON fi.customer_id = c.customer_id
GROUP BY fi.customer_id, c.country, c.iso
ORDER BY total_revenue_gbp DESC
