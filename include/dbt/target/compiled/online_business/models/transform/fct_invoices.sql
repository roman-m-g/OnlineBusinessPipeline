-- Create the fact table by joining the relevant keys from dimension table
WITH fct_invoices_cte AS (
    SELECT
        InvoiceNo AS invoice_id,
        InvoiceDate AS datetime_id,
        to_hex(md5(cast(coalesce(cast(StockCode as string), '_dbt_utils_surrogate_key_null_') || '-' || coalesce(cast(Description as string), '_dbt_utils_surrogate_key_null_') || '-' || coalesce(cast(UnitPrice as string), '_dbt_utils_surrogate_key_null_') as string))) as product_id,
        to_hex(md5(cast(coalesce(cast(CustomerID as string), '_dbt_utils_surrogate_key_null_') || '-' || coalesce(cast(Country as string), '_dbt_utils_surrogate_key_null_') as string))) as customer_id,
        Quantity AS quantity,
        Quantity * UnitPrice AS total
    FROM `de-project-486617`.`online_business`.`raw_invoices`
    WHERE Quantity > 0
)
SELECT
    invoice_id,
    dt.datetime_id,
    dp.product_id,
    dc.customer_id,
    quantity,
    round(fi.total) AS total_invoice_gbp,
    round(fi.total * cr.avg_rate_gpb_usd) AS total_invoice_usd,
    round(fi.total * cr.avg_rate_gpb_eur) AS total_invoice_eur
FROM fct_invoices_cte fi
INNER JOIN `de-project-486617`.`online_business_online_business`.`dim_datetime` dt ON fi.datetime_id = dt.datetime_id
INNER JOIN `de-project-486617`.`online_business_online_business`.`dim_product` dp ON fi.product_id = dp.product_id
INNER JOIN `de-project-486617`.`online_business_online_business`.`dim_customers` dc ON fi.customer_id = dc.customer_id
LEFT JOIN `de-project-486617`.`online_business`.`raw_currency_rates` cr
    ON FORMAT('%04d-%02d', dt.year, dt.month) = cr.year_month