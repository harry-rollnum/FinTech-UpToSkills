

-- Table for companies
CREATE TABLE companies (
    company_id SERIAL PRIMARY KEY,
    name TEXT UNIQUE NOT NULL
);

-- Table for financial metrics
CREATE TABLE financial_metrics (
    metric_id SERIAL PRIMARY KEY,
    name TEXT NOT NULL,
    category TEXT NOT NULL,
    UNIQUE(name, category)
);

-- Table for metric values
CREATE TABLE metric_values (
    value_id SERIAL PRIMARY KEY,
    company_id INT REFERENCES companies(company_id),
    metric_id INT REFERENCES financial_metrics(metric_id),
    fiscal_year INT,
    value NUMERIC,
    source_file TEXT,
    UNIQUE(company_id, metric_id, fiscal_year)
);
