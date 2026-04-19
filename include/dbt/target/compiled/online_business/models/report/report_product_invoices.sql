SELECT
  p.product_id,
  p.stock_code,
  p.description,
  SUM(fi.quantity) AS total_quantity_sold
FROM `de-project-486617`.`online_business_online_business`.`fct_invoices` fi
JOIN `de-project-486617`.`online_business_online_business`.`dim_product` p ON fi.product_id = p.product_id
GROUP BY p.product_id, p.stock_code, p.description
ORDER BY total_quantity_sold DESC