import pandas as pd


# ============================================================
# ORDERS TABLE - DATA CLEANING
# ============================================================

# ------------------------------------------------------------
# 1. LOAD RAW DATA
# ------------------------------------------------------------

# Load the original orders CSV.
# The raw file will not be modified.
orders = pd.read_csv(
    "data/raw/olist_orders_dataset.csv"
)

print("=" * 60)
print("ORDERS CLEANING - START")
print("=" * 60)

print("Original shape:", orders.shape)


# ------------------------------------------------------------
# 2. REMOVE EXACT DUPLICATE ROWS
# ------------------------------------------------------------

# Check the number of duplicate rows before removing them.
duplicate_count = orders.duplicated().sum()

print("\nDuplicate rows before cleaning:", duplicate_count)

# Remove only completely identical rows.
# In our exploration we found zero duplicates,
# but keeping this validation step makes the pipeline robust.
orders = orders.drop_duplicates().copy()

print("Shape after duplicate removal:", orders.shape)


# ------------------------------------------------------------
# 3. CONVERT DATE COLUMNS
# ------------------------------------------------------------

# These columns represent different stages of the order lifecycle.
date_columns = [
    "order_purchase_timestamp",
    "order_approved_at",
    "order_delivered_carrier_date",
    "order_delivered_customer_date",
    "order_estimated_delivery_date"
]

# Convert text timestamps into real datetime values.
for column in date_columns:
    orders[column] = pd.to_datetime(
        orders[column],
        errors="coerce"
    )


# ------------------------------------------------------------
# 4. CHECK DATE CONVERSION
# ------------------------------------------------------------

print("\nDate column data types:")
print(orders[date_columns].dtypes)


# ------------------------------------------------------------
# 5. CHECK MISSING VALUES
# ------------------------------------------------------------

# Missing values are reported first.
# We are not dropping them blindly because missing dates
# can be valid depending on the order status.
print("\nMissing values:")
print(orders.isna().sum())


# ------------------------------------------------------------
# 6. CHECK ORDER ID UNIQUENESS
# ------------------------------------------------------------

# order_id should uniquely identify an order.
duplicate_order_ids = (
    orders["order_id"].duplicated().sum()
)

print("\nDuplicate order IDs:", duplicate_order_ids)


# ------------------------------------------------------------
# 7. VALIDATE ORDER STATUS
# ------------------------------------------------------------

print("\nOrder status values:")
print(
    orders["order_status"]
    .value_counts()
    .sort_index()
)


# ------------------------------------------------------------
# 8. VALIDATE ORDER TIMELINE
# ------------------------------------------------------------

# Check whether approval happened before purchase.
invalid_approval_time = (
    orders["order_approved_at"].notna()
    & (
        orders["order_approved_at"]
        < orders["order_purchase_timestamp"]
    )
)

# Check whether carrier handover happened before purchase.
invalid_carrier_time = (
    orders["order_delivered_carrier_date"].notna()
    & (
        orders["order_delivered_carrier_date"]
        < orders["order_purchase_timestamp"]
    )
)

# Check whether customer delivery happened before purchase.
invalid_delivery_time = (
    orders["order_delivered_customer_date"].notna()
    & (
        orders["order_delivered_customer_date"]
        < orders["order_purchase_timestamp"]
    )
)

print("\nInvalid approval timestamps:", invalid_approval_time.sum())
print("Invalid carrier timestamps:", invalid_carrier_time.sum())
print("Invalid delivery timestamps:", invalid_delivery_time.sum())


# ------------------------------------------------------------
# 9. CHECK DELIVERY STATUS CONSISTENCY
# ------------------------------------------------------------

# Delivered orders should normally have a customer delivery date.
delivered_without_date = (
    (orders["order_status"] == "delivered")
    & orders["order_delivered_customer_date"].isna()
)

print(
    "\nDelivered orders without delivery date:",
    delivered_without_date.sum()
)


# ------------------------------------------------------------
# 10. SAVE CLEANED DATA
# ------------------------------------------------------------

# Save the cleaned orders table into the processed layer.
orders.to_csv(
    "data/processed/orders_clean.csv",
    index=False
)

print("\nCleaned orders shape:", orders.shape)
print("Saved file: data/processed/orders_clean.csv")

print("\n" + "=" * 60)
print("ORDERS CLEANING - COMPLETE")
print("=" * 60)

# ------------------------------------------------------------
# 9. INVESTIGATE INVALID CARRIER TIMESTAMPS
# ------------------------------------------------------------

# Select orders where the carrier date occurs before purchase.
invalid_carrier_orders = orders[
    invalid_carrier_time
].copy()

print("\n" + "=" * 60)
print("INVALID CARRIER TIMESTAMP RECORDS")
print("=" * 60)

print("Number of invalid records:", len(invalid_carrier_orders))

print(
    invalid_carrier_orders[
        [
            "order_id",
            "order_status",
            "order_purchase_timestamp",
            "order_approved_at",
            "order_delivered_carrier_date",
            "order_delivered_customer_date"
        ]
    ].head(20)
)


# ------------------------------------------------------------
# 10. CHECK STATUS OF INVALID CARRIER RECORDS
# ------------------------------------------------------------

print("\nOrder status distribution for invalid carrier records:")

print(
    invalid_carrier_orders["order_status"]
    .value_counts()
)


# ------------------------------------------------------------
# 11. CHECK WHETHER CARRIER DATE IS ALSO BEFORE APPROVAL
# ------------------------------------------------------------

invalid_carrier_before_approval = (
    invalid_carrier_orders["order_approved_at"].notna()
    & (
        invalid_carrier_orders["order_delivered_carrier_date"]
        < invalid_carrier_orders["order_approved_at"]
    )
)

print(
    "\nCarrier date before approval:",
    invalid_carrier_before_approval.sum()
)


# ------------------------------------------------------------
# 12. INVESTIGATE DELIVERED ORDERS WITHOUT DELIVERY DATE
# ------------------------------------------------------------

delivered_without_date_orders = orders[
    delivered_without_date
].copy()

print("\n" + "=" * 60)
print("DELIVERED ORDERS WITHOUT DELIVERY DATE")
print("=" * 60)

print(
    delivered_without_date_orders[
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
    ]
)

# ------------------------------------------------------------
# 13. FIX INVALID CARRIER TIMESTAMPS
# ------------------------------------------------------------

# The carrier timestamp occurs before the purchase/approval
# timestamp for these records, so the value is logically invalid.
#
# We do not delete the complete order.
# We only replace the invalid carrier timestamp with NaT.

orders.loc[
    invalid_carrier_time,
    "order_delivered_carrier_date"
] = pd.NaT

print("\nInvalid carrier timestamps replaced with NaT:")
print(
    orders["order_delivered_carrier_date"].isna().sum()
)


# ------------------------------------------------------------
# 14. VERIFY INVALID CARRIER TIMESTAMPS ARE FIXED
# ------------------------------------------------------------

remaining_invalid_carrier = (
    orders["order_delivered_carrier_date"].notna()
    & (
        orders["order_delivered_carrier_date"]
        < orders["order_approved_at"]
    )
)

print(
    "Remaining invalid carrier timestamps:",
    remaining_invalid_carrier.sum()
)


# ------------------------------------------------------------
# 15. VERIFY DELIVERED ORDERS WITH MISSING DELIVERY DATE
# ------------------------------------------------------------

# We keep these records because the actual delivery date
# is unavailable and should not be invented.

print(
    "Delivered orders with missing delivery date:",
    (
        (orders["order_status"] == "delivered")
        & orders["order_delivered_customer_date"].isna()
    ).sum()
)


# ------------------------------------------------------------
# 16. FINAL DATA QUALITY CHECK
# ------------------------------------------------------------

print("\n" + "=" * 60)
print("FINAL ORDERS DATA QUALITY CHECK")
print("=" * 60)

print("Final shape:", orders.shape)
print(
    "Duplicate rows:",
    orders.duplicated().sum()
)
print(
    "Duplicate order IDs:",
    orders["order_id"].duplicated().sum()
)

print("\nMissing values:")
print(orders.isna().sum())


# ------------------------------------------------------------
# 17. SAVE FINAL CLEANED ORDERS DATA
# ------------------------------------------------------------

orders.to_csv(
    "data/processed/orders_clean.csv",
    index=False
)

print("\nFinal cleaned file saved:")
print("data/processed/orders_clean.csv")


# ------------------------------------------------------------
# 18. FIX CARRIER TIMESTAMPS BEFORE APPROVAL
# ------------------------------------------------------------

# A carrier handover cannot logically happen before
# the order has been approved.
#
# We keep the order record but remove the invalid
# carrier timestamp.

invalid_carrier_before_approval = (
    orders["order_delivered_carrier_date"].notna()
    & orders["order_approved_at"].notna()
    & (
        orders["order_delivered_carrier_date"]
        < orders["order_approved_at"]
    )
)

print(
    "Carrier timestamps before approval:",
    invalid_carrier_before_approval.sum()
)

orders.loc[
    invalid_carrier_before_approval,
    "order_delivered_carrier_date"
] = pd.NaT


# ------------------------------------------------------------
# 19. RECHECK CARRIER TIMESTAMPS
# ------------------------------------------------------------

remaining_invalid_carrier = (
    orders["order_delivered_carrier_date"].notna()
    & (
        orders["order_delivered_carrier_date"]
        < orders["order_approved_at"]
    )
)

print(
    "Remaining carrier timestamps before approval:",
    remaining_invalid_carrier.sum()
)


# ------------------------------------------------------------
# 20. CHECK DELIVERY AFTER CARRIER
# ------------------------------------------------------------

# If both dates exist, customer delivery should not happen
# before the order reaches the carrier.

invalid_delivery_after_carrier = (
    orders["order_delivered_customer_date"].notna()
    & orders["order_delivered_carrier_date"].notna()
    & (
        orders["order_delivered_customer_date"]
        < orders["order_delivered_carrier_date"]
    )
)

print(
    "Delivery timestamps before carrier timestamps:",
    invalid_delivery_after_carrier.sum()
)


# ------------------------------------------------------------
# 21. FINAL ORDERS VALIDATION
# ------------------------------------------------------------

print("\n" + "=" * 60)
print("FINAL ORDERS VALIDATION")
print("=" * 60)

print("Final shape:", orders.shape)
print("Duplicate rows:", orders.duplicated().sum())
print("Duplicate order IDs:", orders["order_id"].duplicated().sum())

print("\nMissing values:")
print(orders.isna().sum())


# ------------------------------------------------------------
# 22. SAVE FINAL ORDERS DATA
# ------------------------------------------------------------

orders.to_csv(
    "data/processed/orders_clean.csv",
    index=False
)

print("\nFinal orders file saved:")
print("data/processed/orders_clean.csv")


# ------------------------------------------------------------
# 23. INVESTIGATE DELIVERY BEFORE CARRIER
# ------------------------------------------------------------

invalid_delivery_orders = orders[
    invalid_delivery_after_carrier
].copy()

print("\n" + "=" * 60)
print("DELIVERY BEFORE CARRIER INVESTIGATION")
print("=" * 60)

print(
    "Number of records:",
    len(invalid_delivery_orders)
)

print(
    invalid_delivery_orders[
        [
            "order_id",
            "order_status",
            "order_purchase_timestamp",
            "order_approved_at",
            "order_delivered_carrier_date",
            "order_delivered_customer_date",
            "order_estimated_delivery_date"
        ]
    ]
)


# ------------------------------------------------------------
# 24. CHECK ORDER STATUS
# ------------------------------------------------------------

print("\nOrder status distribution:")

print(
    invalid_delivery_orders["order_status"]
    .value_counts()
)


# ------------------------------------------------------------
# 25. CALCULATE DELIVERY-CARRIER DIFFERENCE
# ------------------------------------------------------------

invalid_delivery_orders["delivery_before_carrier_days"] = (
    invalid_delivery_orders["order_delivered_customer_date"]
    - invalid_delivery_orders["order_delivered_carrier_date"]
).dt.total_seconds() / (24 * 60 * 60)

print("\nDifference between delivery and carrier timestamps:")

print(
    invalid_delivery_orders[
        [
            "order_id",
            "delivery_before_carrier_days"
        ]
    ]
)


# ------------------------------------------------------------
# 26. FIX DELIVERY BEFORE CARRIER ANOMALIES
# ------------------------------------------------------------

# The customer delivery timestamp occurs before the carrier
# timestamp for these records.
#
# Since the carrier timestamp is logically invalid, we remove
# only that timestamp and keep the complete order record.

orders.loc[
    invalid_delivery_after_carrier,
    "order_delivered_carrier_date"
] = pd.NaT


# ------------------------------------------------------------
# 27. FINAL ORDER TIMELINE VALIDATION
# ------------------------------------------------------------

remaining_delivery_before_carrier = (
    orders["order_delivered_customer_date"].notna()
    & orders["order_delivered_carrier_date"].notna()
    & (
        orders["order_delivered_customer_date"]
        < orders["order_delivered_carrier_date"]
    )
)

print(
    "Remaining delivery-before-carrier records:",
    remaining_delivery_before_carrier.sum()
)


# ------------------------------------------------------------
# 28. FINAL ORDERS VALIDATION
# ------------------------------------------------------------

print("\n" + "=" * 60)
print("ORDERS CLEANING - FINAL VALIDATION")
print("=" * 60)

print("Final shape:", orders.shape)

print(
    "Duplicate rows:",
    orders.duplicated().sum()
)

print(
    "Duplicate order IDs:",
    orders["order_id"].duplicated().sum()
)

print("\nMissing values:")
print(orders.isna().sum())


# ------------------------------------------------------------
# 29. SAVE FINAL CLEANED ORDERS
# ------------------------------------------------------------

orders.to_csv(
    "data/processed/orders_clean.csv",
    index=False
)

print("\nFinal cleaned orders saved:")
print("data/processed/orders_clean.csv")


import pandas as pd

# Load the data

order_items = pd.read_csv("data/raw/olist_order_items_dataset.csv")

print("Order items shape:", order_items.shape)

print("\nColumns:")
print(order_items.columns.tolist())


# Basic checks

print("\nData types:")
print(order_items.dtypes)

print("\nMissing values:")
print(order_items.isna().sum())

print("\nDuplicate rows:", order_items.duplicated().sum())


# Check unique values

print("\nUnique values:")
print("Orders:", order_items["order_id"].nunique())
print("Products:", order_items["product_id"].nunique())
print("Sellers:", order_items["seller_id"].nunique())

print("\nOrder item ID range:")
print(
    order_items["order_item_id"].min(),
    "to",
    order_items["order_item_id"].max()
)


# Check order item grain

print("\nDuplicate order-item combinations:")
print(
    order_items.duplicated(
        subset=["order_id", "order_item_id"]
    ).sum()
)


# Check shipping date

order_items["shipping_limit_date"] = pd.to_datetime(
    order_items["shipping_limit_date"],
    errors="coerce"
)

print("\nShipping limit date range:")
print(
    order_items["shipping_limit_date"].min(),
    "to",
    order_items["shipping_limit_date"].max()
)


# Check price and freight values

print("\nPrice statistics:")
print(order_items["price"].describe())

print("\nFreight value statistics:")
print(order_items["freight_value"].describe())

print("\nNegative price records:")
print((order_items["price"] < 0).sum())

print("\nZero price records:")
print((order_items["price"] == 0).sum())

print("\nNegative freight records:")
print((order_items["freight_value"] < 0).sum())

print("\nZero freight records:")
print((order_items["freight_value"] == 0).sum())


# Check relationships

orders = pd.read_csv("data/processed/orders_clean.csv")
products = pd.read_csv("data/raw/olist_products_dataset.csv")
sellers = pd.read_csv("data/raw/olist_sellers_dataset.csv")

missing_orders = ~order_items["order_id"].isin(orders["order_id"])
missing_products = ~order_items["product_id"].isin(products["product_id"])
missing_sellers = ~order_items["seller_id"].isin(sellers["seller_id"])

print("\nForeign key checks:")
print("Order IDs not found in orders:", missing_orders.sum())
print("Product IDs not found in products:", missing_products.sum())
print("Seller IDs not found in sellers:", missing_sellers.sum())


# Check date consistency

order_purchase = orders[
    ["order_id", "order_purchase_timestamp"]
].copy()

order_purchase["order_purchase_timestamp"] = pd.to_datetime(
    order_purchase["order_purchase_timestamp"],
    errors="coerce"
)

order_items_check = order_items.merge(
    order_purchase,
    on="order_id",
    how="left"
)

invalid_shipping_dates = (
    order_items_check["shipping_limit_date"].notna()
    & order_items_check["order_purchase_timestamp"].notna()
    & (
        order_items_check["shipping_limit_date"]
        < order_items_check["order_purchase_timestamp"]
    )
)

print("\nShipping limit date before purchase date:")
print(invalid_shipping_dates.sum())


# Preview the data

print("\nOrder items preview:")
print(order_items.head())


# Investigate zero freight values

zero_freight = order_items[
    order_items["freight_value"] == 0
]

print("Zero freight records:", len(zero_freight))

print("\nZero freight by product:")
print(zero_freight["product_id"].nunique())

print("\nZero freight by seller:")
print(zero_freight["seller_id"].nunique())

print("\nSample zero freight records:")
print(zero_freight.head(10))


# Investigate unusual shipping dates

print("\nShipping records after 2018:")

late_shipping = order_items[
    order_items["shipping_limit_date"] > "2018-12-31"
]

print("Records:", len(late_shipping))

print("\nLatest shipping records:")
print(
    late_shipping[
        [
            "order_id",
            "product_id",
            "seller_id",
            "shipping_limit_date",
            "price",
            "freight_value"
        ]
    ].sort_values("shipping_limit_date", ascending=False).head(10)
)


# Compare unusual shipping dates with orders

late_shipping_check = late_shipping.merge(
    orders[
        [
            "order_id",
            "order_purchase_timestamp",
            "order_status"
        ]
    ],
    on="order_id",
    how="left"
)

print("\nUnusual shipping records with order information:")
print(late_shipping_check.head(10))

print("\nOrder status of unusual shipping records:")
print(late_shipping_check["order_status"].value_counts(dropna=False))

# Inspect the unusual shipping dates

print(
    late_shipping_check[
        [
            "order_id",
            "order_item_id",
            "shipping_limit_date",
            "order_purchase_timestamp",
            "order_status"
        ]
    ].sort_values("shipping_limit_date")
)


# Check the complete order timeline

print(
    orders[
        orders["order_id"].isin(late_shipping["order_id"])
    ][
        [
            "order_id",
            "order_status",
            "order_purchase_timestamp",
            "order_approved_at",
            "order_delivered_carrier_date",
            "order_delivered_customer_date",
            "order_estimated_delivery_date"
        ]
    ]
)

# Clean invalid shipping dates

invalid_shipping_dates = (
    order_items["shipping_limit_date"] > "2018-12-31"
)

order_items.loc[
    invalid_shipping_dates,
    "shipping_limit_date"
] = pd.NaT


# Final checks

print("Rows:", len(order_items))
print("Duplicate rows:", order_items.duplicated().sum())

print(
    "Duplicate order-item combinations:",
    order_items.duplicated(
        subset=["order_id", "order_item_id"]
    ).sum()
)

print("\nMissing values:")
print(order_items.isna().sum())

print(
    "\nInvalid shipping dates after cleaning:",
    (
        order_items["shipping_limit_date"] > "2018-12-31"
    ).sum()
)


# Save the cleaned data

order_items.to_csv(
    "data/processed/order_items_clean.csv",
    index=False
)

print("\nCleaned order items saved:")
print("data/processed/order_items_clean.csv")




# Load the data

customers = pd.read_csv(
    "data/raw/olist_customers_dataset.csv"
)

print("Customers shape:", customers.shape)

print("\nColumns:")
print(customers.columns.tolist())


# Basic checks

print("\nData types:")
print(customers.dtypes)

print("\nMissing values:")
print(customers.isna().sum())

print("\nDuplicate rows:")
print(customers.duplicated().sum())


# Check customer IDs

print("\nUnique customer IDs:")
print(customers["customer_id"].nunique())

print("\nUnique customer identities:")
print(customers["customer_unique_id"].nunique())

print("\nDuplicate customer IDs:")
print(customers["customer_id"].duplicated().sum())


# Check location information

print("\nUnique zip code prefixes:")
print(customers["customer_zip_code_prefix"].nunique())

print("\nUnique cities:")
print(customers["customer_city"].nunique())

print("\nUnique states:")
print(customers["customer_state"].nunique())

print("\nTop states:")
print(customers["customer_state"].value_counts().head(10))

print("\nTop cities:")
print(customers["customer_city"].value_counts().head(10))


# Check customer relationships

orders = pd.read_csv(
    "data/processed/orders_clean.csv"
)

missing_customer_ids = ~orders["customer_id"].isin(
    customers["customer_id"]
)

print("\nCustomer IDs in orders but not in customers:")
print(missing_customer_ids.sum())

customer_ids_not_in_orders = ~customers["customer_id"].isin(
    orders["customer_id"]
)

print("\nCustomer IDs not used in orders:")
print(customer_ids_not_in_orders.sum())


# Check repeat customers

customer_order_counts = (
    orders.merge(
        customers[
            ["customer_id", "customer_unique_id"]
        ],
        on="customer_id",
        how="left"
    )
    .groupby("customer_unique_id")["order_id"]
    .nunique()
)

print("\nCustomers with more than one order:")
print((customer_order_counts > 1).sum())

print("\nMaximum orders by one customer:")
print(customer_order_counts.max())


# Check location values

print("\nBlank city values:")
print(
    customers["customer_city"]
    .astype(str)
    .str.strip()
    .eq("")
    .sum()
)

print("\nBlank state values:")
print(
    customers["customer_state"]
    .astype(str)
    .str.strip()
    .eq("")
    .sum()
)


# Preview the data

print("\nCustomer preview:")
print(customers.head())


# Investigate customer identities

identity_counts = (
    customers
    .groupby("customer_unique_id")["customer_id"]
    .nunique()
)

print("Customer identities linked to multiple customer IDs:")
print((identity_counts > 1).sum())

print("\nMaximum customer IDs for one identity:")
print(identity_counts.max())

print("\nCustomer identity examples:")
print(
    identity_counts[
        identity_counts > 1
    ].sort_values(ascending=False).head(10)
)

# Save the validated customer data

customers.to_csv(
    "data/processed/customers_clean.csv",
    index=False
)

print("Customers data saved:")
print("data/processed/customers_clean.csv")


import pandas as pd

# Load the data

payments = pd.read_csv(
    "data/raw/olist_order_payments_dataset.csv"
)

print("Payments shape:", payments.shape)

print("\nColumns:")
print(payments.columns.tolist())


# Basic checks

print("\nData types:")
print(payments.dtypes)

print("\nMissing values:")
print(payments.isna().sum())

print("\nDuplicate rows:")
print(payments.duplicated().sum())


# Check payment records

print("\nUnique orders:")
print(payments["order_id"].nunique())

print("\nPayment types:")
print(payments["payment_type"].value_counts())

print("\nPayment sequential range:")
print(
    payments["payment_sequential"].min(),
    "to",
    payments["payment_sequential"].max()
)


# Check payment values

print("\nPayment value statistics:")
print(payments["payment_value"].describe())

print("\nNegative payment values:")
print((payments["payment_value"] < 0).sum())

print("\nZero payment values:")
print((payments["payment_value"] == 0).sum())


# Check installments

print("\nInstallment statistics:")
print(payments["payment_installments"].describe())

print("\nZero installments:")
print((payments["payment_installments"] == 0).sum())

print("\nNegative installments:")
print((payments["payment_installments"] < 0).sum())


# Check payment relationships

orders = pd.read_csv(
    "data/processed/orders_clean.csv"
)

missing_order_ids = ~payments["order_id"].isin(
    orders["order_id"]
)

print("\nPayment records with missing order:")
print(missing_order_ids.sum())


# Check orders with multiple payments

payments_per_order = (
    payments
    .groupby("order_id")
    .size()
)

print("\nOrders with multiple payment records:")
print((payments_per_order > 1).sum())

print("\nMaximum payment records for one order:")
print(payments_per_order.max())


# Check payment sequence

duplicate_payment_sequences = payments.duplicated(
    subset=["order_id", "payment_sequential"]
)

print("\nDuplicate order-payment sequences:")
print(duplicate_payment_sequences.sum())


# Check payment types and installments

print("\nInstallments by payment type:")
print(
    payments.groupby("payment_type")["payment_installments"]
    .describe()
)


# Preview the data

print("\nPayment preview:")
print(payments.head())


# Investigate zero payment values

zero_payment = payments[
    payments["payment_value"] == 0
]

print("Zero payment records:")
print(zero_payment)


# Investigate zero installments

zero_installments = payments[
    payments["payment_installments"] == 0
]

print("\nZero installment records:")
print(zero_installments)


# Check payment types

print("\nPayment types with zero installments:")
print(
    zero_installments["payment_type"].value_counts()
)


# Check the related orders

zero_payment_orders = orders[
    orders["order_id"].isin(
        zero_payment["order_id"]
    )
]

print("\nOrders related to zero payment values:")
print(
    zero_payment_orders[
        [
            "order_id",
            "order_status",
            "order_purchase_timestamp",
            "order_approved_at"
        ]
    ]
)


# Check whether these orders have other payment records

print("\nAll payments for zero-payment orders:")
print(
    payments[
        payments["order_id"].isin(
            zero_payment["order_id"]
        )
    ].sort_values(
        ["order_id", "payment_sequential"]
    )
)


# Clean invalid installment values

invalid_installments = (
    payments["payment_installments"] == 0
)

payments.loc[
    invalid_installments,
    "payment_installments"
] = pd.NA


# Final checks

print("Rows:", len(payments))

print("Duplicate rows:", payments.duplicated().sum())

print(
    "Duplicate order-payment sequences:",
    payments.duplicated(
        subset=["order_id", "payment_sequential"]
    ).sum()
)

print("\nMissing values:")
print(payments.isna().sum())

print(
    "\nInvalid installment values:",
    (payments["payment_installments"] <= 0).sum()
)

print(
    "\nNegative payment values:",
    (payments["payment_value"] < 0).sum()
)


# Save the cleaned data

payments.to_csv(
    "data/processed/payments_clean.csv",
    index=False
)

print("\nCleaned payments data saved:")
print("data/processed/payments_clean.csv")



import pandas as pd

# Load the data

reviews = pd.read_csv(
    "data/raw/olist_order_reviews_dataset.csv"
)

print("Reviews shape:", reviews.shape)

print("\nColumns:")
print(reviews.columns.tolist())


# Basic checks

print("\nData types:")
print(reviews.dtypes)

print("\nMissing values:")
print(reviews.isna().sum())

print("\nDuplicate rows:")
print(reviews.duplicated().sum())


# Check review IDs

print("\nUnique review IDs:")
print(reviews["review_id"].nunique())

print("\nDuplicate review IDs:")
print(reviews["review_id"].duplicated().sum())

print("\nUnique orders with reviews:")
print(reviews["order_id"].nunique())


# Check review scores

print("\nReview score distribution:")
print(
    reviews["review_score"]
    .value_counts()
    .sort_index()
)

print("\nReview score statistics:")
print(reviews["review_score"].describe())


# Check review relationships

orders = pd.read_csv(
    "data/processed/orders_clean.csv"
)

missing_order_ids = ~reviews["order_id"].isin(
    orders["order_id"]
)

print("\nReview orders not found in orders:")
print(missing_order_ids.sum())


# Check multiple reviews for one order

reviews_per_order = (
    reviews
    .groupby("order_id")
    .size()
)

print("\nOrders with multiple reviews:")
print((reviews_per_order > 1).sum())

print("\nMaximum reviews for one order:")
print(reviews_per_order.max())


# Check review dates

reviews["review_creation_date"] = pd.to_datetime(
    reviews["review_creation_date"],
    errors="coerce"
)

reviews["review_answer_timestamp"] = pd.to_datetime(
    reviews["review_answer_timestamp"],
    errors="coerce"
)

print("\nReview creation date range:")
print(
    reviews["review_creation_date"].min(),
    "to",
    reviews["review_creation_date"].max()
)

print("\nReview answer date range:")
print(
    reviews["review_answer_timestamp"].min(),
    "to",
    reviews["review_answer_timestamp"].max()
)


# Check review timeline

invalid_review_dates = (
    reviews["review_answer_timestamp"].notna()
    & reviews["review_creation_date"].notna()
    & (
        reviews["review_answer_timestamp"]
        < reviews["review_creation_date"]
    )
)

print("\nAnswer before review creation:")
print(invalid_review_dates.sum())


# Check review comments

print("\nReviews with titles:")
print(
    reviews["review_comment_title"].notna().sum()
)

print("\nReviews with messages:")
print(
    reviews["review_comment_message"].notna().sum()
)

print("\nReviews without title and message:")
print(
    (
        reviews["review_comment_title"].isna()
        & reviews["review_comment_message"].isna()
    ).sum()
)


# Preview the data

print("\nReview preview:")
print(reviews.head())


# Investigate duplicate review IDs

review_id_counts = (
    reviews
    .groupby("review_id")["order_id"]
    .nunique()
)

print("Review IDs linked to multiple orders:")
print((review_id_counts > 1).sum())

print("\nMaximum orders for one review ID:")
print(review_id_counts.max())


# Check repeated review IDs

duplicate_review_ids = review_id_counts[
    review_id_counts > 1
]

print("\nExamples of review IDs linked to multiple orders:")
print(
    duplicate_review_ids
    .sort_values(ascending=False)
    .head(10)
)


# Check duplicate review rows

repeated_review_ids = reviews[
    reviews["review_id"].duplicated(keep=False)
].sort_values("review_id")

print("\nSample repeated review IDs:")
print(
    repeated_review_ids[
        [
            "review_id",
            "order_id",
            "review_score",
            "review_creation_date",
            "review_answer_timestamp"
        ]
    ].head(20)
)


# Check review score validity

invalid_scores = ~reviews["review_score"].between(1, 5)

print("\nInvalid review scores:")
print(invalid_scores.sum())

# Save the validated review data

reviews.to_csv(
    "data/processed/reviews_clean.csv",
    index=False
)

print("Reviews data saved:")
print("data/processed/reviews_clean.csv")


import pandas as pd

# Load the raw products data
products = pd.read_csv(
    "data/raw/olist_products_dataset.csv"
)

print("Products shape:", products.shape)
print("\nColumns:")
print(products.columns.tolist())

print("\nData types:")
print(products.dtypes)

print("\nMissing values:")
print(products.isna().sum())

print("\nDuplicate rows:", products.duplicated().sum())

print("\nUnique product IDs:", products["product_id"].nunique())
print(
    "Duplicate product IDs:",
    products["product_id"].duplicated().sum()
)

# Check product categories
print("\nUnique product categories:")
print(products["product_category_name"].nunique())

print("\nTop product categories:")
print(
    products["product_category_name"]
    .value_counts(dropna=False)
    .head(15)
)

# Check numeric columns
numeric_columns = [
    "product_name_lenght",
    "product_description_lenght",
    "product_photos_qty",
    "product_weight_g",
    "product_length_cm",
    "product_height_cm",
    "product_width_cm"
]

print("\nNumeric summary:")
print(products[numeric_columns].describe())

# Check invalid negative values
print("\nNegative values:")
for column in numeric_columns:
    print(
        column,
        ":",
        (products[column] < 0).sum()
    )

# Check zero values
print("\nZero values:")
for column in numeric_columns:
    print(
        column,
        ":",
        (products[column] == 0).sum()
    )

# Check products used in order items
order_items = pd.read_csv(
    "data/processed/order_items_clean.csv"
)

missing_products = (
    ~order_items["product_id"].isin(products["product_id"])
).sum()

unused_products = (
    ~products["product_id"].isin(order_items["product_id"])
).sum()

print("\nProduct IDs missing from products table:")
print(missing_products)

print("\nProducts never used in order items:")
print(unused_products)

# Check category translation relationship
translation = pd.read_csv(
    "data/raw/product_category_name_translation.csv"
)

missing_translations = (
    products["product_category_name"].notna()
    & ~products["product_category_name"].isin(
        translation["product_category_name"]
    )
).sum()

extra_translations = (
    ~translation["product_category_name"].isin(
        products["product_category_name"].dropna()
    )
).sum()

print("\nProduct categories without translation:")
print(missing_translations)

print("\nTranslation categories not found in products:")
print(extra_translations)

print("\nProducts with missing values:")
print(
    products[products.isna().any(axis=1)].head(20)
)


# Inspect unusual product records

print("Products with zero weight:")
print(
    products[
        products["product_weight_g"] == 0
    ]
)

print("\nProducts with missing physical dimensions:")
print(
    products[
        products[
            [
                "product_weight_g",
                "product_length_cm",
                "product_height_cm",
                "product_width_cm"
            ]
        ].isna().any(axis=1)
    ]
)

print("\nCategories without translation:")

untranslated_categories = (
    products.loc[
        products["product_category_name"].notna()
        & ~products["product_category_name"].isin(
            translation["product_category_name"]
        ),
        "product_category_name"
    ]
    .drop_duplicates()
    .sort_values()
)

print(untranslated_categories.tolist())



import pandas as pd

# Load the raw products data
products = pd.read_csv(
    "data/raw/olist_products_dataset.csv"
)

# Check and remove exact duplicate rows if any
products = products.drop_duplicates()

# Make sure product IDs are unique
products = products.drop_duplicates(
    subset=["product_id"]
)

# Validate numeric columns
numeric_columns = [
    "product_name_lenght",
    "product_description_lenght",
    "product_photos_qty",
    "product_weight_g",
    "product_length_cm",
    "product_height_cm",
    "product_width_cm"
]

for column in numeric_columns:
    products[column] = pd.to_numeric(
        products[column],
        errors="coerce"
    )

# Final validation
print("Products shape:", products.shape)

print("\nDuplicate rows:")
print(products.duplicated().sum())

print("\nDuplicate product IDs:")
print(products["product_id"].duplicated().sum())

print("\nMissing values:")
print(products.isna().sum())

print("\nNegative values:")
for column in numeric_columns:
    print(
        column,
        ":",
        (products[column] < 0).sum()
    )

print("\nZero weight values:")
print(
    (products["product_weight_g"] == 0).sum()
)

# Save the cleaned products data
products.to_csv(
    "data/processed/products_clean.csv",
    index=False
)

print("\nCleaned products data saved:")
print("data/processed/products_clean.csv")


import pandas as pd

# Load the raw sellers data
sellers = pd.read_csv(
    "data/raw/olist_sellers_dataset.csv"
)

print("Sellers shape:", sellers.shape)

print("\nColumns:")
print(sellers.columns.tolist())

print("\nData types:")
print(sellers.dtypes)

print("\nMissing values:")
print(sellers.isna().sum())

print("\nDuplicate rows:")
print(sellers.duplicated().sum())

print("\nUnique seller IDs:")
print(sellers["seller_id"].nunique())

print("\nDuplicate seller IDs:")
print(sellers["seller_id"].duplicated().sum())

print("\nUnique seller cities:")
print(sellers["seller_city"].nunique())

print("\nUnique seller states:")
print(sellers["seller_state"].nunique())

print("\nTop seller states:")
print(
    sellers["seller_state"]
    .value_counts()
    .head(15)
)

print("\nTop seller cities:")
print(
    sellers["seller_city"]
    .value_counts()
    .head(15)
)

# Check relationship with order items
order_items = pd.read_csv(
    "data/processed/order_items_clean.csv"
)

missing_sellers = (
    ~order_items["seller_id"].isin(
        sellers["seller_id"]
    )
).sum()

unused_sellers = (
    ~sellers["seller_id"].isin(
        order_items["seller_id"]
    )
).sum()

print("\nSeller IDs missing from sellers table:")
print(missing_sellers)

print("\nSellers never used in order items:")
print(unused_sellers)

print("\nBlank city values:")
print(
    sellers["seller_city"].isna().sum()
)

print("\nBlank state values:")
print(
    sellers["seller_state"].isna().sum()
)

print("\nSample sellers:")
print(sellers.head(10))



# Load the raw sellers data
sellers = pd.read_csv(
    "data/raw/olist_sellers_dataset.csv"
)

# Remove exact duplicate rows
sellers = sellers.drop_duplicates()

# Keep one record per seller
sellers = sellers.drop_duplicates(
    subset=["seller_id"]
)

# Final validation
print("Sellers shape:", sellers.shape)

print("\nDuplicate rows:")
print(sellers.duplicated().sum())

print("\nDuplicate seller IDs:")
print(sellers["seller_id"].duplicated().sum())

print("\nMissing values:")
print(sellers.isna().sum())

# Save the cleaned sellers data
sellers.to_csv(
    "data/processed/sellers_clean.csv",
    index=False
)

print("\nCleaned sellers data saved:")
print("data/processed/sellers_clean.csv")



# Load the raw geolocation data
geolocation = pd.read_csv(
    "data/raw/olist_geolocation_dataset.csv"
)

print("Geolocation shape:", geolocation.shape)

print("\nColumns:")
print(geolocation.columns.tolist())

print("\nData types:")
print(geolocation.dtypes)

print("\nMissing values:")
print(geolocation.isna().sum())

print("\nDuplicate rows:")
print(geolocation.duplicated().sum())

print("\nUnique ZIP prefixes:")
print(
    geolocation["geolocation_zip_code_prefix"].nunique()
)

print("\nUnique cities:")
print(
    geolocation["geolocation_city"].nunique()
)

print("\nUnique states:")
print(
    geolocation["geolocation_state"].nunique()
)

# Check ZIP prefix frequency
print("\nMost common ZIP prefixes:")
print(
    geolocation["geolocation_zip_code_prefix"]
    .value_counts()
    .head(15)
)

# Check coordinate ranges
print("\nCoordinate summary:")
print(
    geolocation[
        [
            "geolocation_lat",
            "geolocation_lng"
        ]
    ].describe()
)

# Check invalid coordinate values
print("\nZero latitude values:")
print(
    (geolocation["geolocation_lat"] == 0).sum()
)

print("\nZero longitude values:")
print(
    (geolocation["geolocation_lng"] == 0).sum()
)

# Check negative coordinate values
print("\nNegative latitude values:")
print(
    (geolocation["geolocation_lat"] < 0).sum()
)

print("\nNegative longitude values:")
print(
    (geolocation["geolocation_lng"] < 0).sum()
)

# Check ZIP prefixes mapped to multiple cities
zip_city_counts = (
    geolocation
    .groupby("geolocation_zip_code_prefix")[
        "geolocation_city"
    ]
    .nunique()
)

print("\nZIP prefixes mapped to multiple cities:")
print(
    (zip_city_counts > 1).sum()
)

# Check ZIP prefixes mapped to multiple states
zip_state_counts = (
    geolocation
    .groupby("geolocation_zip_code_prefix")[
        "geolocation_state"
    ]
    .nunique()
)

print("\nZIP prefixes mapped to multiple states:")
print(
    (zip_state_counts > 1).sum()
)

# Compare ZIP prefixes with customers and sellers
customers = pd.read_csv(
    "data/processed/customers_clean.csv"
)

sellers = pd.read_csv(
    "data/processed/sellers_clean.csv"
)

customer_zips = set(
    customers["customer_zip_code_prefix"]
)

seller_zips = set(
    sellers["seller_zip_code_prefix"]
)

geo_zips = set(
    geolocation["geolocation_zip_code_prefix"]
)

print("\nCustomer ZIP prefixes missing from geolocation:")
print(
    len(customer_zips - geo_zips)
)

print("\nSeller ZIP prefixes missing from geolocation:")
print(
    len(seller_zips - geo_zips)
)

print("\nCustomer ZIP prefixes found in geolocation:")
print(
    len(customer_zips & geo_zips)
)

print("\nSeller ZIP prefixes found in geolocation:")
print(
    len(seller_zips & geo_zips)
)

# Investigate ZIP prefixes mapped to multiple states

multi_state_zips = (
    zip_state_counts[
        zip_state_counts > 1
    ]
    .index
)

print("ZIP prefixes mapped to multiple states:")
print(multi_state_zips.tolist())

print("\nDetails for these ZIP prefixes:")
print(
    geolocation[
        geolocation["geolocation_zip_code_prefix"].isin(
            multi_state_zips
        )
    ]
    .sort_values("geolocation_zip_code_prefix")
    .drop_duplicates()
)

# Check unusual coordinate values

print("\nLatitude values above 0:")
print(
    geolocation[
        geolocation["geolocation_lat"] > 0
    ][
        [
            "geolocation_zip_code_prefix",
            "geolocation_lat",
            "geolocation_lng",
            "geolocation_city",
            "geolocation_state"
        ]
    ].head(20)
)

print("\nLongitude values above 0:")
print(
    geolocation[
        geolocation["geolocation_lng"] > 0
    ][
        [
            "geolocation_zip_code_prefix",
            "geolocation_lat",
            "geolocation_lng",
            "geolocation_city",
            "geolocation_state"
        ]
    ].head(20)
)

print("\nExact duplicate percentage:")
print(
    round(
        geolocation.duplicated().mean() * 100,
        2
    ),
    "%"
)


# Load the raw geolocation data
geolocation = pd.read_csv(
    "data/raw/olist_geolocation_dataset.csv"
)

# Remove exact duplicate rows
geolocation = geolocation.drop_duplicates()

# Final validation
print("Geolocation shape:", geolocation.shape)

print("\nDuplicate rows:")
print(geolocation.duplicated().sum())

print("\nMissing values:")
print(geolocation.isna().sum())

print("\nUnique ZIP prefixes:")
print(
    geolocation["geolocation_zip_code_prefix"].nunique()
)

print("\nUnique cities:")
print(
    geolocation["geolocation_city"].nunique()
)

print("\nUnique states:")
print(
    geolocation["geolocation_state"].nunique()
)

# Save the cleaned geolocation data
geolocation.to_csv(
    "data/processed/geolocation_clean.csv",
    index=False
)

print("\nCleaned geolocation data saved:")
print("data/processed/geolocation_clean.csv")



# Load the raw category translation data
translation = pd.read_csv(
    "data/raw/product_category_name_translation.csv"
)

print("Translation shape:", translation.shape)

print("\nColumns:")
print(translation.columns.tolist())

print("\nData types:")
print(translation.dtypes)

print("\nMissing values:")
print(translation.isna().sum())

print("\nDuplicate rows:")
print(translation.duplicated().sum())

print("\nDuplicate category names:")
print(
    translation["product_category_name"].duplicated().sum()
)

print("\nDuplicate English names:")
print(
    translation["product_category_name_english"].duplicated().sum()
)

print("\nUnique Portuguese categories:")
print(
    translation["product_category_name"].nunique()
)

print("\nUnique English categories:")
print(
    translation["product_category_name_english"].nunique()
)

print("\nSample translations:")
print(translation.head(15))

# Check relationship with products
products = pd.read_csv(
    "data/processed/products_clean.csv"
)

product_categories = set(
    products["product_category_name"].dropna()
)

translation_categories = set(
    translation["product_category_name"]
)

missing_from_translation = (
    product_categories - translation_categories
)

unused_translations = (
    translation_categories - product_categories
)

print("\nProduct categories without translation:")
print(len(missing_from_translation))

print(sorted(missing_from_translation))

print("\nTranslation categories not used by products:")
print(len(unused_translations))

print(sorted(unused_translations))


# Load the raw category translation data
translation = pd.read_csv(
    "data/raw/product_category_name_translation.csv"
)

# Remove exact duplicate rows
translation = translation.drop_duplicates()

# Keep one record per Portuguese category
translation = translation.drop_duplicates(
    subset=["product_category_name"]
)

# Final validation
print("Translation shape:", translation.shape)

print("\nDuplicate rows:")
print(translation.duplicated().sum())

print("\nDuplicate Portuguese categories:")
print(
    translation["product_category_name"].duplicated().sum()
)

print("\nDuplicate English categories:")
print(
    translation["product_category_name_english"].duplicated().sum()
)

print("\nMissing values:")
print(translation.isna().sum())

# Save the cleaned translation data
translation.to_csv(
    "data/processed/category_translation_clean.csv",
    index=False
)

print("\nCleaned translation data saved:")
print(
    "data/processed/category_translation_clean.csv"
)