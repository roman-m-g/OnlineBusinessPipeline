SELECT DISTINCT
    year_month,
		avg_rate_gpb_usd,
    avg_rate_gpb_eur
FROM {{ source('online_business', 'raw_currency_rates') }}