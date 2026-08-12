"""
CropCare MySQL to Neon PostgreSQL Data Migration Script

Migrates existing records from local XAMPP MySQL to Cloud Neon PostgreSQL while:
- Preserving primary keys and foreign key relationships
- Preserving password hashes byte-for-byte
- Converting MySQL tinyint(1) integers (0/1) to PostgreSQL booleans (True/False)
- Adjusting PostgreSQL serial sequences post-import
- Performing row count validation and reporting
"""
import os
import sys
import logging
from sqlalchemy import create_engine, text, inspect, Boolean
from sqlalchemy.orm import sessionmaker

# Setup logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger("migration")

# Add project root to sys.path
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
if project_root not in sys.path:
    sys.path.insert(0, project_root)


from backend.config.settings import settings
from backend.database.database import Base
import backend.models  # Register all 8 model classes in Base.metadata

MYSQL_URL = os.environ.get("MYSQL_SOURCE_URL", "mysql+pymysql://root:@localhost:3307/cropcare_db")
NEON_URL = settings.DATABASE_URL

TABLE_ORDER = [
    "users",
    "admins",
    "ads",
    "schemes",
    "crop_plans",
    "mandi_prices",
    "district_rainfall",
    "ai_usage_history",
]

BOOLEAN_COLUMNS = {"is_approved", "is_active"}

def run_migration():
    logger.info("Starting CropCare MySQL -> Neon PostgreSQL migration...")
    logger.info("Source MySQL: %s", MYSQL_URL.split("@")[-1] if "@" in MYSQL_URL else MYSQL_URL)
    logger.info("Target Neon: %s", NEON_URL.split("@")[-1] if "@" in NEON_URL else NEON_URL)

    # 1. Create Target Tables in Neon
    logger.info("Creating schema tables in Neon PostgreSQL if not present...")
    neon_engine = create_engine(NEON_URL, pool_pre_ping=True)
    Base.metadata.create_all(bind=neon_engine)

    # 2. Setup Source Engine
    try:
        mysql_engine = create_engine(MYSQL_URL)
        mysql_conn = mysql_engine.connect()
    except Exception as exc:
        logger.error("Failed to connect to source MySQL database: %s", exc)
        logger.info("If MySQL is running on a different port or password, set MYSQL_SOURCE_URL environment variable.")
        sys.exit(1)

    neon_conn = neon_engine.connect()
    inspector_mysql = inspect(mysql_engine)
    inspector_neon = inspect(neon_engine)

    mysql_tables = inspector_mysql.get_table_names()
    neon_tables = inspector_neon.get_table_names()
    logger.info("MySQL tables found: %s", mysql_tables)
    logger.info("Neon tables found: %s", neon_tables)

    validation_report = []

    for table in TABLE_ORDER:
        if table not in mysql_tables:
            logger.warning("Table '%s' not present in MySQL source. Skipping.", table)
            validation_report.append((table, 0, 0, "SKIPPED (No MySQL table)"))
            continue

        # Get source records
        res_mysql = mysql_conn.execute(text(f"SELECT * FROM `{table}`"))
        mysql_columns = res_mysql.keys()
        rows = [dict(zip(mysql_columns, row)) for row in res_mysql.fetchall()]
        mysql_count = len(rows)

        # Check existing Neon target count
        res_neon_cnt = neon_conn.execute(text(f'SELECT COUNT(*) FROM "{table}"'))
        neon_initial_cnt = res_neon_cnt.scalar()

        if mysql_count == 0:
            logger.info("Table '%s': 0 rows in MySQL. Skipping data copy.", table)
            validation_report.append((table, 0, neon_initial_cnt, "OK (Empty in MySQL)"))
            continue

        logger.info("Migrating table '%s': %d records from MySQL...", table, mysql_count)

        # Target column inspection
        neon_cols = {c["name"]: c for c in inspector_neon.get_columns(table)}

        inserted = 0
        for row in rows:
            # Filter row to matching columns and cast types if needed
            filtered_row = {}
            for k, v in row.items():
                if k in neon_cols:
                    # Convert MySQL integer 0/1 to True/False for boolean columns
                    if k in BOOLEAN_COLUMNS or isinstance(neon_cols[k].get("type"), Boolean):
                        if v is not None:
                            v = bool(v)
                    filtered_row[k] = v

            col_names = ", ".join([f'"{k}"' for k in filtered_row.keys()])
            param_names = ", ".join([f":{k}" for k in filtered_row.keys()])
            
            sql = f'INSERT INTO "{table}" ({col_names}) VALUES ({param_names}) ON CONFLICT DO NOTHING'
            try:
                neon_conn.execute(text(sql), filtered_row)
                inserted += 1
            except Exception as exc:
                logger.warning("Insert exception on %s row %s: %s", table, filtered_row.get("id"), exc)

        neon_conn.commit()

        # Update PostgreSQL sequence to match max(id)
        if "id" in neon_cols:
            try:
                seq_sql = f"SELECT setval(pg_get_serial_sequence('{table}', 'id'), COALESCE((SELECT MAX(id) FROM \"{table}\"), 1));"
                neon_conn.execute(text(seq_sql))
                neon_conn.commit()
            except Exception as exc:
                logger.warning("Sequence reset for %s: %s", table, exc)

        # Final count check
        res_final = neon_conn.execute(text(f'SELECT COUNT(*) FROM "{table}"'))
        final_neon_cnt = res_final.scalar()
        status = "SUCCESS" if final_neon_cnt >= mysql_count else "WARN (Count mismatch)"
        validation_report.append((table, mysql_count, final_neon_cnt, status))

    mysql_conn.close()
    neon_conn.close()

    print("\n" + "=" * 65)
    print("MIGRATION VALIDATION REPORT")
    print("=" * 65)
    print(f"{'Table':<20} | {'MySQL Rows':<12} | {'Neon Rows':<12} | {'Status'}")
    print("-" * 65)
    for t_name, m_cnt, n_cnt, stat in validation_report:
        print(f"{t_name:<20} | {m_cnt:<12} | {n_cnt:<12} | {stat}")
    print("=" * 65 + "\n")

if __name__ == "__main__":
    run_migration()
