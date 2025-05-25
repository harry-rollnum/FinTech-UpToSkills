import os
import re
import argparse
import psycopg2
import pandas as pd
from dotenv import load_dotenv
from datetime import datetime

# Load .env variables
load_dotenv()

DB_NAME = os.getenv("DB_NAME")
DB_USER = os.getenv("DB_USER")
DB_PASSWORD = os.getenv("DB_PASSWORD")
DB_HOST = os.getenv("DB_HOST", "localhost")
DB_PORT = os.getenv("DB_PORT", "5432")

# Create logs folder
os.makedirs("logs", exist_ok=True)
log_filename = datetime.now().strftime("logs/etl_log_%Y%m%d_%H%M%S.txt")
log_file = open(log_filename, "w", encoding="utf-8")

def log(msg):
    print(msg)
    log_file.write(f"{msg}\n")

def extract_unit(name):
    match = re.search(r'\(([^)]+)\)', name)
    return match.group(1) if match else ''

def clean_metric_name(name):
    return re.sub(r'\s*\(.*?\)\s*', '', name).strip()

def insert_data_from_excel(xlsx_path, dry_run=False):
    summary = {
        "sheets": 0, "companies": 0, "metrics": 0, "values": 0, "skipped": 0
    }

    if not dry_run:
        conn = psycopg2.connect(
            dbname=DB_NAME, user=DB_USER, password=DB_PASSWORD,
            host=DB_HOST, port=DB_PORT, sslmode='require'  # Supabase requires SSL
        )
        cur = conn.cursor()
    else:
        conn = cur = None
        log("[DRY-RUN MODE ENABLED]")

    xls = pd.ExcelFile(xlsx_path)

    for sheet_name in xls.sheet_names:
        summary["sheets"] += 1
        log(f"\n[INFO] Processing sheet: {sheet_name}")
        df_raw = pd.read_excel(xls, sheet_name=sheet_name, header=None)
        company_name = str(df_raw.iat[0, 0]).strip()
        log(f"[DEBUG] Company: {company_name}")

        df = pd.read_excel(xls, sheet_name=sheet_name, header=1)

        if not dry_run:
            cur.execute("INSERT INTO companies (name) VALUES (%s) ON CONFLICT (name) DO NOTHING", (company_name,))
            conn.commit()
            cur.execute("SELECT company_id FROM companies WHERE name = %s", (company_name,))
            res = cur.fetchone()
            if res:
                company_id = res[0]
                summary["companies"] += 1
            else:
                log(f"[WARN] Could not retrieve company_id for {company_name}")
                summary["skipped"] += 1
                continue
        else:
            company_id = 0  # Dummy
            summary["companies"] += 1

        year_cols = [col for col in df.columns if re.match(r'^\d{4}$', str(col))]
        log(f"[DEBUG] Years detected: {year_cols}")

        for idx, row in df.iterrows():
            category = row[df.columns[0]]
            metric_raw = row[df.columns[1]]
            if pd.isna(category) or pd.isna(metric_raw):
                summary["skipped"] += 1
                continue

            category = str(category).strip()
            metric_name = clean_metric_name(str(metric_raw).strip())

            if not dry_run:
                cur.execute("""INSERT INTO financial_metrics (name, category)
                               VALUES (%s, %s) ON CONFLICT (name, category) DO NOTHING""",
                            (metric_name, category))
                conn.commit()
                cur.execute("""SELECT metric_id FROM financial_metrics
                               WHERE name=%s AND category=%s""",
                            (metric_name, category))
                res = cur.fetchone()
                if res:
                    metric_id = res[0]
                    summary["metrics"] += 1
                else:
                    log(f"[WARN] Metric {metric_name} not inserted/found.")
                    summary["skipped"] += 1
                    continue
            else:
                metric_id = 0  # Dummy
                summary["metrics"] += 1

            for year in year_cols:
                val = row[year]
                if pd.isna(val):
                    continue
                try:
                    val_float = float(val)
                except ValueError:
                    log(f"[WARN] Invalid value {val} for year {year} in metric {metric_name}")
                    summary["skipped"] += 1
                    continue

                summary["values"] += 1
                log(f"[DEBUG] Value {val_float} for {year} | Metric: {metric_name}")

                if not dry_run:
                    cur.execute('''INSERT INTO metric_values
                                   (company_id, metric_id, fiscal_year, value, source_file)
                                   VALUES (%s, %s, %s, %s, %s)
                                   ON CONFLICT DO NOTHING''',
                                (company_id, metric_id, int(year), val_float, xlsx_path))

        if not dry_run:
            conn.commit()
            log(f"[INFO] ✅ Sheet {sheet_name} processed")

    if conn:
        conn.close()

    # Summary
    log("\n[SUMMARY]")
    for key, value in summary.items():
        log(f"{key.capitalize()}: {value}")
    log("[INFO] 🎉 ETL Process Completed\n")
    log_file.close()

# CLI entry point
if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="ETL tool for financial Excel data")
    parser.add_argument("--file", required=True, help="Path to Excel file")
    parser.add_argument("--dry-run", action="store_true", help="Run without inserting to DB")
    args = parser.parse_args()

    insert_data_from_excel(args.file, dry_run=args.dry_run)
