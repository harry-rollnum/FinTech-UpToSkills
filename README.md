# 📊 Financial Data ETL Pipeline — Supabase Integration

This project extracts financial data from Excel sheets and inserts it into a centralized PostgreSQL database hosted on **Supabase**, enabling collaborative access and updates.

---

## 🚀 Project Overview

- Reads `.xlsx` files with **multiple sheets (one per company)**
- Inserts data into Supabase PostgreSQL
- Supports:
  - ✅ Command-line file upload
  - 🔄 Dry-run mode (no DB insertion)
  - 📁 Logs each run with timestamp
  - 📊 Summary report after each run
  - Use Data Folder to store the xlsx 
---

## 🧱 Supabase Database Setup

Our team uses Supabase as a hosted PostgreSQL backend. To connect:

### 🧩 Required Environment Variables

Create a `.env` file in the project root:

```
DB_NAME=postgres
DB_USER=postgres
DB_PASSWORD=your_supabase_password
DB_HOST=db.sjddywpimurfgxylqmix.supabase.co
DB_PORT=5432
```

---

### 🔐 Accessing Supabase Dashboard

Only **authorized team members** can access:

1. Visit: [Supabase Dashboard](https://supabase.com/dashboard/project/sjddywpimurfgxylqmix/editor/17267?schema=public)
2. Log in with the email invited by the admin
3. Navigate to the `Editor` to explore tables and data

---

## ⚙️ Running the ETL Script

### ▶️ Basic Usage

```bash
python etl_runner.py --file path/to/your_file.xlsx
```

### 🧪 Dry Run (No DB Insertion)

```bash
python etl_runner.py --file path/to/your_file.xlsx --dry-run
```

---

## 📝 Logs

All logs are stored in the `logs/` folder with a timestamped filename.

Example:
```
logs/log_2025-05-25_16-45-12.txt
```

These logs include:
- Sheet names processed
- Company names inserted
- Metrics and values attempted
- Any skipped/invalid rows

---

## ✅ Final Notes

- The database schema is already created — no need to manually set it up.
- Logs provide transparency and error tracking.
- **DO NOT commit `.env` files** to version control (they contain secrets).
- For new teammates, contact the admin to:
  - Grant Supabase dashboard access
  - Share the latest `.env` credentials

---

## 👨‍💻 Contributors

- Sai Kumar Garlapati 
- Vaishnavi
- Kashesh

---

📬 For issues or onboarding help, reach out.
