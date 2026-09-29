


    
from pathlib import Path

import pandas as pd
import psycopg2
from dotenv import dotenv_values


BASE_DIR = Path(__file__).resolve().parent.parent
ENV_FILE = BASE_DIR / ".env"
DATA_PATH = BASE_DIR / "data" / "processed"

config = dotenv_values(ENV_FILE)

DB_CONFIG = {
    "host": config["POSTGRES_HOST"],
    "port": config["POSTGRES_PORT"],
    "database": config["POSTGRES_DB"],
    "user": config["POSTGRES_USER"],
    "password": config["POSTGRES_PASSWORD"]
}


TABLES = [
    ("dim_customers", "dim_customers.csv"),
    ("dim_products", "dim_products.csv"),
    ("dim_sellers", "dim_sellers.csv"),
    ("dim_category", "dim_category.csv"),
    ("dim_geolocation", "dim_geolocation.csv"),
    ("fact_orders", "fact_orders.csv"),
    ("fact_order_items", "fact_order_items.csv"),
    ("fact_payments", "fact_payments.csv"),
    ("fact_reviews", "fact_reviews.csv")
]


def get_connection():
    return psycopg2.connect(**DB_CONFIG)


def load_table(connection, table_name, file_name):
    file_path = DATA_PATH / file_name

    df = pd.read_csv(file_path)

    columns = list(df.columns)
    column_names = ", ".join(columns)
    placeholders = ", ".join(["%s"] * len(columns))

    query = f"""
        INSERT INTO {table_name} ({column_names})
        VALUES ({placeholders})
    """

    records = [
        tuple(None if pd.isna(value) else value for value in row)
        for row in df.itertuples(index=False, name=None)
    ]

    cursor = connection.cursor()

    cursor.executemany(query, records)

    connection.commit()
    cursor.close()

    return len(df)


def main():
    connection = get_connection()

    print("PostgreSQL connection successful!")

    try:
        for table_name, file_name in TABLES:
            row_count = load_table(
                connection,
                table_name,
                file_name
            )

            print(f"{table_name}: {row_count} rows loaded")

        print("All tables loaded successfully!")

    except Exception as error:
        connection.rollback()
        print("Loading failed!")
        print(error)

    finally:
        connection.close()
        print("PostgreSQL connection closed.")


if __name__ == "__main__":
    main()