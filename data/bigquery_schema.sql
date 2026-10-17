-- =====================================================================
-- JEWEL-AI: Google Cloud BigQuery Retail & Commerce Analytics Schema
-- Developed for Google Cloud AI Builder Hackathon
-- =====================================================================

-- 1. Create Dataset
CREATE SCHEMA IF NOT EXISTS `retail_jewel_ai`
OPTIONS(
  location="asia-south1",
  description="Jewel-AI Autonomous Jewellery Co-Creation & Demand Intelligence Warehouse"
);

-- 2. Telemetry Table: Bespoke Customer Design Requests
CREATE TABLE IF NOT EXISTS `retail_jewel_ai.design_requests` (
  request_id STRING NOT NULL OPTIONS(description="Unique 10-char transaction identifier"),
  created_at TIMESTAMP NOT NULL OPTIONS(description="UTC timestamp of customer design session"),
  category STRING NOT NULL OPTIONS(description="Jewellery silhouette: ring, necklace, earrings, bangle"),
  style STRING OPTIONS(description="Design style motif: temple, solitaire, polki, filigree, etc."),
  metal STRING NOT NULL OPTIONS(description="Precious alloy: gold_24k, gold_22k, gold_18k, platinum, rose_gold"),
  stone_type STRING OPTIONS(description="Gemstone: natural_diamond, lab_diamond, moissanite, cz, ruby, emerald, none"),
  stone_carat FLOAT64 OPTIONS(description="Total gem weight in carats"),
  budget_inr INT64 OPTIONS(description="Customer target budget in Indian Rupees"),
  occasion STRING OPTIONS(description="Occasion: Wedding, Engagement, Diwali/Dhanteras, Akshaya Tritiya, Daily wear"),
  customer_name STRING OPTIONS(description="Customer name if captured"),
  status STRING NOT NULL OPTIONS(description="State: designed, in_review, sent_to_workshop, completed")
)
PARTITION BY DATE(created_at)
CLUSTER BY category, metal, occasion;

-- 3. Telemetry Table: Circular Economy Old Gold Trade-In Vouchers
CREATE TABLE IF NOT EXISTS `retail_jewel_ai.tradein_vouchers` (
  voucher_id STRING NOT NULL OPTIONS(description="Unique voucher code EXCH-XXXXXX"),
  created_at TIMESTAMP NOT NULL,
  gross_weight_g FLOAT64 NOT NULL,
  declared_purity_kt INT64 NOT NULL,
  purity_factor FLOAT64 NOT NULL,
  refinery_melting_loss_g FLOAT64 NOT NULL,
  net_pure_gold_g FLOAT64 NOT NULL,
  bullion_spot_rate_per_g INT64 NOT NULL,
  gross_melt_value_inr FLOAT64 NOT NULL,
  assay_fee_inr FLOAT64 NOT NULL,
  net_credit_inr FLOAT64 NOT NULL,
  applied_to_request_id STRING
)
PARTITION BY DATE(created_at);

-- =====================================================================
-- SAMPLE BIGQUERY ANALYTICAL QUERIES (RUN IN BIGQUERY CONSOLE)
-- =====================================================================

-- QUERY 1: 30-Day Bullion Procurement & Festival Surge Forecast
-- Models expected grams of 22k vs 18k gold required prior to festival rushes.
SELECT 
  occasion,
  category,
  COUNT(1) AS total_requests,
  ROUND(AVG(budget_inr)) AS avg_customer_budget,
  ROUND(SUM(CASE WHEN metal = 'gold_22k' THEN 5.5 ELSE 0 END), 1) AS est_22k_gold_grams_needed,
  ROUND(SUM(CASE WHEN metal IN ('gold_18k', 'rose_gold') THEN 4.2 ELSE 0 END), 1) AS est_18k_gold_grams_needed,
  ROUND(SUM(COALESCE(stone_carat, 0)), 2) AS total_diamond_carats_needed
FROM `retail_jewel_ai.design_requests`
WHERE created_at >= TIMESTAMP_SUB(CURRENT_TIMESTAMP(), INTERVAL 30 DAY)
GROUP BY occasion, category
ORDER BY total_requests DESC;

-- QUERY 2: Customer Price Elasticity & Purity Segmentation
-- Segments shopper personas into Budget, Festive, and Royal Bridal cohorts.
SELECT
  CASE 
    WHEN budget_inr < 40000 THEN '1. Everyday / Budget (< ₹40k)'
    WHEN budget_inr BETWEEN 40000 AND 90000 THEN '2. Festive / Gifting (₹40k - ₹90k)'
    WHEN budget_inr BETWEEN 90000 AND 180000 THEN '3. Occasion / Engagement (₹90k - ₹1.8L)'
    ELSE '4. Royal Bridal & Heritage (> ₹1.8L)'
  END AS customer_segment,
  metal,
  COUNT(1) AS cohort_volume,
  ROUND(AVG(budget_inr), 2) AS cohort_avg_budget,
  COUNTIF(status = 'sent_to_workshop') AS karigar_conversions
FROM `retail_jewel_ai.design_requests`
GROUP BY customer_segment, metal
ORDER BY customer_segment, cohort_volume DESC;

-- QUERY 3: Circular Old Gold Margin Recovery
-- Measures recycled family gold funding against merchant inventory outflow.
SELECT 
  DATE_TRUNC(DATE(created_at), MONTH) AS month,
  COUNT(voucher_id) AS total_tradein_patrons,
  ROUND(SUM(gross_weight_g), 2) AS total_scrap_gold_received_grams,
  ROUND(SUM(net_pure_gold_g), 2) AS total_fine_gold_recovered_grams,
  ROUND(SUM(net_credit_inr), 2) AS total_customer_credit_issued_inr,
  ROUND(SUM(net_pure_gold_g * bullion_spot_rate_per_g) - SUM(net_credit_inr), 2) AS merchant_refinery_margin_inr
FROM `retail_jewel_ai.tradein_vouchers`
GROUP BY month
ORDER BY month DESC;
