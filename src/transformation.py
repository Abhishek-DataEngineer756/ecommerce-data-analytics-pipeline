import os
import pandas as pd

# Load the data
orders = pd.read_csv("data/processed/orders_clean.csv")
order_items = pd.read_csv("data/processed/order_items_clean.csv")
payments = pd.read_csv("data/processed/payments_clean.csv")
reviews = pd.read_csv("data/processed/reviews_clean.csv")
customers = pd.read_csv("data/processed/customers_clean.csv")
products = pd.read_csv("data/processed/products_clean.csv")
sellers = pd.read_csv("data/processed/sellers_clean.csv")
geolocation = pd.read_csv("data/processed/geolocation_clean.csv")
translation = pd.read_csv("data/processed/category_translation_clean.csv")

print("All cleaned tables loaded successfully.")

# Prepare date columns
order_date_columns = [
    "order_purchase_timestamp",
    "order_approved_at",
    "order_delivered_carrier_date",
    "order_delivered_customer_date",
    "order_estimated_delivery_date"
]

for column in order_date_columns:
    orders[column] = pd.to_datetime(
        orders[column],
        errors="coerce"
    )

review_date_columns = [
    "review_creation_date",
    "review_answer_timestamp"
]

for column in review_date_columns:
    reviews[column] = pd.to_datetime(
        reviews[column],
        errors="coerce"
    )

order_items["shipping_limit_date"] = pd.to_datetime(
    order_items["shipping_limit_date"],
    errors="coerce"
)

# Create order metrics
orders["delivery_days"] = (
    orders["order_delivered_customer_date"]
    - orders["order_purchase_timestamp"]
).dt.total_seconds() / 86400

orders["estimated_delivery_days"] = (
    orders["order_estimated_delivery_date"]
    - orders["order_purchase_timestamp"]
).dt.total_seconds() / 86400

orders["late_days"] = (
    orders["order_delivered_customer_date"]
    - orders["order_estimated_delivery_date"]
).dt.total_seconds() / 86400

orders["approval_delay_days"] = (
    orders["order_approved_at"]
    - orders["order_purchase_timestamp"]
).dt.total_seconds() / 86400

orders["is_late"] = (
    orders["late_days"] > 0
).astype("Int64")

# Create product dimension
dim_products = products.merge(
    translation,
    on="product_category_name",
    how="left",
    validate="many_to_one"
)

# Create category dimension
dim_category = translation.copy()

# Create customer dimension
dim_customers = customers.copy()

# Create seller dimension
dim_sellers = sellers.copy()

# Create order item fact
fact_order_items = order_items.merge(
    orders[
        [
            "order_id",
            "customer_id",
            "order_status",
            "order_purchase_timestamp",
            "order_approved_at",
            "order_delivered_carrier_date",
            "order_delivered_customer_date",
            "order_estimated_delivery_date"
        ]
    ],
    on="order_id",
    how="left",
    validate="many_to_one"
)

fact_order_items = fact_order_items.merge(
    dim_products[
        [
            "product_id",
            "product_category_name",
            "product_category_name_english"
        ]
    ],
    on="product_id",
    how="left",
    validate="many_to_one"
)

fact_order_items = fact_order_items.merge(
    dim_sellers[
        [
            "seller_id",
            "seller_zip_code_prefix",
            "seller_city",
            "seller_state"
        ]
    ],
    on="seller_id",
    how="left",
    validate="many_to_one"
)

fact_order_items["total_item_value"] = (
    fact_order_items["price"]
    + fact_order_items["freight_value"]
)

# Create payment summary
fact_payments = (
    payments
    .groupby("order_id")
    .agg(
        total_payment_value=("payment_value", "sum"),
        payment_count=("payment_sequential", "count"),
        max_installments=("payment_installments", "max"),
        payment_types=(
            "payment_type",
            lambda x: ", ".join(
                sorted(x.dropna().unique())
            )
        )
    )
    .reset_index()
)

# Create review summary
fact_reviews = (
    reviews
    .groupby("order_id")
    .agg(
        review_count=("review_id", "count"),
        average_review_score=("review_score", "mean"),
        minimum_review_score=("review_score", "min"),
        maximum_review_score=("review_score", "max")
    )
    .reset_index()
)

# Create order fact
fact_orders = orders.copy()

fact_orders = fact_orders.merge(
    fact_payments,
    on="order_id",
    how="left",
    validate="one_to_one"
)

fact_orders = fact_orders.merge(
    fact_reviews,
    on="order_id",
    how="left",
    validate="one_to_one"
)

# Create ZIP-level geolocation mapping
dim_geolocation = (
    geolocation
    .groupby("geolocation_zip_code_prefix")
    .agg(
        geolocation_lat=("geolocation_lat", "mean"),
        geolocation_lng=("geolocation_lng", "mean"),
        geolocation_city=(
            "geolocation_city",
            lambda x: (
                x.mode().iloc[0]
                if not x.mode().empty
                else x.iloc[0]
            )
        ),
        geolocation_state=(
            "geolocation_state",
            lambda x: (
                x.mode().iloc[0]
                if not x.mode().empty
                else x.iloc[0]
            )
        )
    )
    .reset_index()
)

# Validate tables
print()
print("Transformation completed successfully.")
print()

print("Table validation:")
print("fact_orders:", fact_orders.shape)
print("fact_order_items:", fact_order_items.shape)
print("fact_payments:", fact_payments.shape)
print("fact_reviews:", fact_reviews.shape)
print("dim_customers:", dim_customers.shape)
print("dim_products:", dim_products.shape)
print("dim_sellers:", dim_sellers.shape)
print("dim_category:", dim_category.shape)
print("dim_geolocation:", dim_geolocation.shape)

print()
print("Grain validation:")

print(
    "fact_orders duplicate order_id:",
    fact_orders["order_id"].duplicated().sum()
)

print(
    "fact_order_items duplicate order item:",
    fact_order_items[
        ["order_id", "order_item_id"]
    ].duplicated().sum()
)

print(
    "fact_payments duplicate order_id:",
    fact_payments["order_id"].duplicated().sum()
)

print(
    "fact_reviews duplicate order_id:",
    fact_reviews["order_id"].duplicated().sum()
)

print(
    "dim_customers duplicate customer_id:",
    dim_customers["customer_id"].duplicated().sum()
)

print(
    "dim_products duplicate product_id:",
    dim_products["product_id"].duplicated().sum()
)

print(
    "dim_sellers duplicate seller_id:",
    dim_sellers["seller_id"].duplicated().sum()
)

print(
    "dim_category duplicate category:",
    dim_category[
        "product_category_name"
    ].duplicated().sum()
)

print(
    "dim_geolocation duplicate zip:",
    dim_geolocation[
        "geolocation_zip_code_prefix"
    ].duplicated().sum()
)

# Save transformed data
output_path = "data/processed"
os.makedirs(output_path, exist_ok=True)

fact_orders.to_csv(
    f"{output_path}/fact_orders.csv",
    index=False
)

fact_order_items.to_csv(
    f"{output_path}/fact_order_items.csv",
    index=False
)

fact_payments.to_csv(
    f"{output_path}/fact_payments.csv",
    index=False
)

fact_reviews.to_csv(
    f"{output_path}/fact_reviews.csv",
    index=False
)

dim_customers.to_csv(
    f"{output_path}/dim_customers.csv",
    index=False
)

dim_products.to_csv(
    f"{output_path}/dim_products.csv",
    index=False
)

dim_sellers.to_csv(
    f"{output_path}/dim_sellers.csv",
    index=False
)

dim_category.to_csv(
    f"{output_path}/dim_category.csv",
    index=False
)

dim_geolocation.to_csv(
    f"{output_path}/dim_geolocation.csv",
    index=False
)

print()
print("All transformed tables saved successfully.")