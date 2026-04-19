SELECT
  p.stock_code,
  p.description,
  SUM(fi.quantity) AS total_quantity_sold,
  COUNT(DISTINCT fi.invoice_id) AS num_invoices,
  SUM(fi.total_invoice_gbp) AS total_revenue_gbp,
  SUM(fi.total_invoice_usd) AS total_revenue_usd,
  SUM(fi.total_invoice_eur) AS total_revenue_eur
FROM `de-project-486617`.`online_business_online_business`.`fct_invoices` fi
JOIN `de-project-486617`.`online_business_online_business`.`dim_product` p ON fi.product_id = p.product_id
GROUP BY p.stock_code, p.description
ORDER BY total_revenue_gbp DESC