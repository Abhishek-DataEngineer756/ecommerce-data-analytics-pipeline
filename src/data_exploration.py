
import pandas as pd
orders = pd.read_csv(r"data/raw/olist_orders_dataset.csv")
#print top 5 rows of the dataset
print(orders.head())
#print the information of the dataset 
print(orders.info())
#print last 5 rows of the dataset 
print(orders.tail())
#print the shape of the dataset 
print(orders.shape)
#print the column names of the dataset
print(orders.columns)
#print the summary statistics of the dataset
print(orders.describe())
#print data types of the dataset
print(orders.dtypes)

# missing values in the dataset
print(orders.isnull().sum())

#check duplicate rows in the dataset
print("Duplicate rows:", orders.duplicated().sum())

#check order status value counts
print(orders['order_status'].value_counts())

print("\nUnique Order Status:")
print(orders["order_status"].unique())

print("\nOrder Status Counts:")
print(orders["order_status"].value_counts())

print("\nOrder ID Unique Count:")
print(orders["order_id"].nunique())

print("\nCustomer ID Unique Count:")
print(orders["customer_id"].nunique())

print("\nOrder Purchase Date Range:")
print(orders["order_purchase_timestamp"].min())
print(orders["order_purchase_timestamp"].max())

# Convert purchase timestamp
orders["order_purchase_timestamp"] = pd.to_datetime(
    orders["order_purchase_timestamp"]
)

# Create year and month
orders["purchase_year"] = orders["order_purchase_timestamp"].dt.year
orders["purchase_month"] = orders["order_purchase_timestamp"].dt.month

# Yearly orders
print("\nOrders by year:")
print(orders["purchase_year"].value_counts().sort_index())

# Monthly orders
print("\nOrders by month:")
print(orders["purchase_month"].value_counts().sort_index())


date_columns = [
    "order_purchase_timestamp",
    "order_approved_at",
    "order_delivered_carrier_date",
    "order_delivered_customer_date",
    "order_estimated_delivery_date"
]

for column in date_columns:
    orders[column] = pd.to_datetime(orders[column])

print(orders.dtypes)




order_items = pd.read_csv("data/raw/olist_order_items_dataset.csv")

print("Shape:")
print(order_items.shape)

print("\nColumns:")
print(order_items.columns)

print("\nData Types:")
print(order_items.dtypes)

print("\nFirst 5 Rows:")
print(order_items.head())

print("\nMissing Values:")
print(order_items.isnull().sum())

print("\nDuplicate Rows:")
print(order_items.duplicated().sum())

print("\nUnique Orders:")
print(order_items["order_id"].nunique())

print("\nUnique Products:")
print(order_items["product_id"].nunique())

print("\nUnique Sellers:")
print(order_items["seller_id"].nunique())

print("\nTotal Product Value:")
print(order_items["price"].sum())

print("\nTotal Freight Value:")
print(order_items["freight_value"].sum())


order_items["shipping_limit_date"] = pd.to_datetime(
    order_items["shipping_limit_date"]
)

print(order_items.dtypes)



print("Orders table:")
print("Total rows:", len(orders))
print("Unique order_id:", orders["order_id"].nunique())

print("\nOrder Items table:")
print("Total rows:", len(order_items))
print("Unique order_id:", order_items["order_id"].nunique())

print("\nOrders per order_id in order_items:")
print(order_items["order_id"].value_counts().head(10))

print("\nOrders from orders table missing in order_items:")
missing_orders = ~orders["order_id"].isin(order_items["order_id"])
print(missing_orders.sum())

print("\nOrder_items with order_id not found in orders:")
missing_parent_orders = ~order_items["order_id"].isin(orders["order_id"])
print(missing_parent_orders.sum())


# using merge function we join the order table and order_items table on order_id column using left join
merged_orders = orders.merge(
    order_items,
    on="order_id",
    how="left"
)

print(merged_orders.shape)
print(merged_orders.head())


print("Merged shape:")
print(merged_orders.shape)

print("\nMerged columns:")
print(merged_orders.columns)

print("\nMissing values after LEFT JOIN:")
print(merged_orders.isnull().sum())

print("\nOrders with missing item information:")
print(merged_orders["product_id"].isnull().sum())


# ---------------------------------------------------------
# Basic business metrics
# Yahan hum raw data se kuch simple numbers nikal rahe hain
# taaki hume business ka overall picture mil sake.
# ---------------------------------------------------------

# Har item ki price ko add karke total product value nikal rahe hain.
# Price order_items table mein item level par stored hai.
total_product_value = order_items["price"].sum()

# Har item ka freight/shipping charge add kar rahe hain.
# Isse pata chalega ki total freight cost/value kitni hai.
total_freight_value = order_items["freight_value"].sum()

# orders table se unique order_id count kar rahe hain.
# Ek order ko ek hi baar count karna hai, isliye unique count use kar rahe hain.
total_orders = orders["order_id"].nunique()

# order_items mein kitne different orders ke items available hain,
# ye check kar rahe hain.
orders_with_items = order_items["order_id"].nunique()

# Sirf delivered status wale orders count kar rahe hain.
# Isse pata chalega kitne orders successfully delivered hue.
delivered_orders = (orders["order_status"] == "delivered").sum()

# Sirf canceled status wale orders count kar rahe hain.
# Isse pata chalega kitne orders cancel hue.
cancelled_orders = (orders["order_status"] == "canceled").sum()


# Ab saare results ek saath dekhte hain.
print("Total product value:", total_product_value)
print("Total freight value:", total_freight_value)
print("Total orders:", total_orders)
print("Orders with items:", orders_with_items)
print("Delivered orders:", delivered_orders)
print("Cancelled orders:", cancelled_orders)


# Delivery time calculate karne ke liye hume purchase date
# aur actual delivery date ke beech ka difference chahiye.
# Dono columns ko hum pehle hi datetime mein convert kar chuke hain.

# Sirf un orders ko le rahe hain jinki actual delivery date available hai.
# Missing delivery date wale orders ka delivery time calculate nahi kar sakte.
delivered_data = orders.dropna(
    subset=["order_delivered_customer_date"]
).copy()

# Actual delivery time nikal rahe hain.
# Delivery date - purchase date = order ko deliver hone mein laga time.
delivered_data["delivery_days"] = (
    delivered_data["order_delivered_customer_date"]
    - delivered_data["order_purchase_timestamp"]
).dt.total_seconds() / (24 * 60 * 60)

# Ab basic delivery statistics dekhte hain.
print("Orders with delivery date:", len(delivered_data))
print("Average delivery days:", delivered_data["delivery_days"].mean())
print("Minimum delivery days:", delivered_data["delivery_days"].min())
print("Maximum delivery days:", delivered_data["delivery_days"].max())

# Delivery time ko small se large order mein dekh rahe hain
# Isse pata chalega ki unusually high delivery days wale orders kaunse hain.

print(
    delivered_data[
        ["order_id", "order_purchase_timestamp",
         "order_delivered_customer_date", "delivery_days"]
    ]
    .sort_values("delivery_days", ascending=False)
    .head(10)
)


# Sabse late delivered orders ka status check kar rahe hain
# Isse pata chalega ki ye orders actually delivered status mein hain ya nahi.

long_delivery_orders = delivered_data.sort_values(
    "delivery_days",
    ascending=False
).head(10)

print(
    long_delivery_orders[
        ["order_id", "order_status", "delivery_days"]
    ]
)

# Ab actual delivery date ko estimated delivery date ke saath compare kar rahe hain.
# Isse pata chalega ki order expected date ke comparison mein kitna late hua.

print(
    long_delivery_orders[
        [
            "order_id",
            "order_purchase_timestamp",
            "order_delivered_customer_date",
            "order_estimated_delivery_date",
            "delivery_days"
        ]
    ]
)

# Actual delivery aur estimated delivery ke beech kitne din ka difference hai,
# ye calculate kar rahe hain.
# Positive value ka matlab actual delivery estimated date ke baad hui.

long_delivery_orders["late_days"] = (
    long_delivery_orders["order_delivered_customer_date"]
    - long_delivery_orders["order_estimated_delivery_date"]
).dt.total_seconds() / (24 * 60 * 60)

print(
    long_delivery_orders[
        ["order_id", "delivery_days", "late_days"]
    ]
)

# Ab poore delivered orders ka delivery-time distribution dekh rahe hain.
# Isse hume pata chalega ki normal delivery range kya hai
# aur bahut long deliveries kitni unusual hain.

print(delivered_data["delivery_days"].describe())

# Delivery days ko different ranges mein divide kar rahe hain
# taaki hume overall delivery pattern clearly samajh aaye.

delivery_ranges = pd.cut(
    delivered_data["delivery_days"],
    bins=[0, 5, 10, 20, 30, float("inf")],
    labels=["0-5 days", "5-10 days", "10-20 days", "20-30 days", "30+ days"],
    include_lowest=True
)

print(delivery_ranges.value_counts().sort_index())

# Ab sabhi delivered orders ke liye actual delivery
# aur estimated delivery ka difference nikal rahe hain.
# Positive value ka matlab order estimated date ke baad deliver hua.

delivered_data["late_days"] = (
    delivered_data["order_delivered_customer_date"]
    - delivered_data["order_estimated_delivery_date"]
).dt.total_seconds() / (24 * 60 * 60)

print(delivered_data["late_days"].describe())


# Positive late_days ka matlab order estimated date ke baad deliver hua.
# Isliye ab late aur not-late orders ka count nikal rahe hain.

late_orders = (delivered_data["late_days"] > 0).sum()
not_late_orders = (delivered_data["late_days"] <= 0).sum()

print("Late orders:", late_orders)
print("Not-late orders:", not_late_orders)
print("Total delivered orders:", len(delivered_data))


# Ab late aur not-late orders ka percentage nikal rahe hain
# taaki delivery performance ko percentage mein samajh sakein.

late_percentage = (late_orders / len(delivered_data)) * 100
not_late_percentage = (not_late_orders / len(delivered_data)) * 100

print("Late orders percentage:", late_percentage)
print("Not-late orders percentage:", not_late_percentage)

# Customers ki CSV file load kar rahe hain
# taaki hum customer table ko samajh sakein.

customers = pd.read_csv(
    "data/raw/olist_customers_dataset.csv"
)

# Pehle table ka size aur columns dekh rahe hain
# taaki hume pata chale kitna data aur kya information available hai.

print("Customers shape:", customers.shape)
print("\nCustomers columns:")
print(customers.columns)

print("\nCustomers first 5 rows:")
print(customers.head())

print("\nCustomers data types:")
print(customers.dtypes)


# Ab customers table ki basic data quality check kar rahe hain.
# Isse missing values aur duplicate records ka idea milega.

print("Missing values:")
print(customers.isnull().sum())

print("\nDuplicate rows:")
print(customers.duplicated().sum())

print("\nUnique customer_id:")
print(customers["customer_id"].nunique())

print("\nUnique customer_unique_id:")
print(customers["customer_unique_id"].nunique())

# Dekh rahe hain ki kaunse unique customers
# customers table mein multiple records ke saath present hain.

repeat_customer_records = (
    customers["customer_unique_id"]
    .value_counts()
)

print(repeat_customer_records.head(10))

# Customers table ko orders table ke saath connect kar rahe hain.
# customer_id common column hai, isliye usi par join karenge.

customer_orders = customers.merge(
    orders[["order_id", "customer_id"]],
    on="customer_id",
    how="inner"
)

# Ab dekh rahe hain ki har unique customer ne kitne orders kiye.
orders_per_customer = (
    customer_orders["customer_unique_id"]
    .value_counts()
)

print("Total customers with orders:", orders_per_customer.size)

print("\nTop customers by number of orders:")
print(orders_per_customer.head(10))

# Ab check kar rahe hain ki kitne unique customers ne
# ek se zyada orders place kiye hain.

repeat_customers = (orders_per_customer > 1).sum()
one_time_customers = (orders_per_customer == 1).sum()

print("Repeat customers:", repeat_customers)
print("One-time customers:", one_time_customers)
print("Total unique customers:", orders_per_customer.size)

# Ab dekh rahe hain ki total unique customers mein
# repeat customers ka percentage kitna hai.

repeat_percentage = (
    repeat_customers / orders_per_customer.size
) * 100

one_time_percentage = (
    one_time_customers / orders_per_customer.size
) * 100

print("Repeat customer percentage:", repeat_percentage)
print("One-time customer percentage:", one_time_percentage)

# Ab dekh rahe hain ki customers ka distribution
# different states mein kaisa hai.

customers_per_state = (
    customers["customer_state"]
    .value_counts()
)

print("Customers per state:")
print(customers_per_state)

# Ab sirf top 10 states dekh rahe hain
# taaki customer distribution ko easily compare kar sakein.

top_states = customers_per_state.head(10)

print("Top 10 states by customer count:")
print(top_states)

# We already analyzed customers by state.
# Now we want to know which cities have the highest
# number of customer records in the dataset.

customers_per_city = (
    customers["customer_city"]
    .value_counts()
)

# Take only the top 10 cities so the result is easy to analyze.
top_cities = customers_per_city.head(10)

print("Top 10 cities by customer count:")
print(top_cities)

# We already have the number of customer records for each state.
# Now we want to understand each state's share of the total
# customer records.

state_percentage = (
    customers_per_state
    / customers_per_state.sum()
    * 100
)

# Show the top 10 states with their percentage contribution.
top_state_percentage = state_percentage.head(10)

print("Top 10 states and their percentage of customer records:")
print(top_state_percentage.round(2))


# We want to connect customer location with their orders.
# The customers table tells us WHERE the customer is.
# The orders table tells us WHICH order belongs to that customer.
#
# customer_id is the common key between the two tables.

customer_orders = customers.merge(
    orders[["order_id", "customer_id", "order_status"]],
    on="customer_id",
    how="inner"
)

# Now count orders for each state.
orders_per_state = (
    customer_orders["customer_state"]
    .value_counts()
)

print("Top 10 states by number of orders:")
print(orders_per_state.head(10))


# We already connected customers with orders.
# Now we want to understand order status by state.
#
# This helps us see whether different states have
# different numbers of delivered, canceled, shipped, etc. orders.

orders_status_by_state = pd.crosstab(
    customer_orders["customer_state"],
    customer_orders["order_status"]
)

# Display the top 10 states based on total orders.
top_10_states = orders_per_state.head(10).index

print("Order status by top 10 customer states:")
print(orders_status_by_state.loc[top_10_states])

# We already have order-status counts for every state.
# Now we calculate the percentage of orders that were canceled
# in each state.
#
# Formula:
# canceled orders / total orders × 100

canceled_orders_by_state = orders_status_by_state["canceled"]

total_orders_by_state = orders_status_by_state.sum(axis=1)

cancellation_rate_by_state = (
    canceled_orders_by_state
    / total_orders_by_state
    * 100
)

# Sort states from highest cancellation rate to lowest.
cancellation_rate_by_state = (
    cancellation_rate_by_state
    .sort_values(ascending=False)
)

print("Cancellation rate by state:")
print(cancellation_rate_by_state.round(2))


# Cancellation rate alone is not enough.
# We also need to see how many total orders each state had.
# This helps us understand whether a high rate comes from
# a large number of orders or a very small sample.

cancellation_analysis = pd.DataFrame({
    "total_orders": total_orders_by_state,
    "canceled_orders": canceled_orders_by_state,
    "cancellation_rate": cancellation_rate_by_state
})

# Sort by cancellation rate so the highest-rate states appear first.
cancellation_analysis = cancellation_analysis.sort_values(
    "cancellation_rate",
    ascending=False
)

print("Cancellation analysis by state:")
print(cancellation_analysis.round(2))



# The payments table contains information about how orders
# were paid and how much was paid.
#
# We first inspect the raw table before doing any analysis.
# This is important because a Data Engineer should understand
# the structure and grain of a table before transforming it.

payments = pd.read_csv(
    "data/raw/olist_order_payments_dataset.csv"
)

print("Shape:")
print(payments.shape)

print("\nColumns:")
print(payments.columns.tolist())

print("\nFirst 5 rows:")
print(payments.head())

print("\nData types:")
print(payments.dtypes)

print("\nMissing values:")
print(payments.isnull().sum())

print("\nDuplicate rows:")
print(payments.duplicated().sum())


# We want to understand which payment methods are present
# in the dataset and how frequently each one appears.
#
# value_counts() counts how many payment records belong
# to each payment type.

payment_type_counts = (
    payments["payment_type"]
    .value_counts()
)

print("Payment type counts:")
print(payment_type_counts)

# We already know how many payment records exist for each
# payment type.
#
# Now we want to calculate the total payment value associated
# with each payment method.
#
# sum() adds all payment_value values within each payment type.

payment_value_by_type = (
    payments.groupby("payment_type")["payment_value"]
    .sum()
    .sort_values(ascending=False)
)

print("Total payment value by payment type:")
print(payment_value_by_type.round(2))


# We already calculated the total payment value for each
# payment method.
#
# Now we want to understand each payment method's share
# of the overall payment value.

total_payment_value = payment_value_by_type.sum()

payment_value_percentage = (
    payment_value_by_type
    / total_payment_value
    * 100
)

print("Payment value percentage by payment type:")
print(payment_value_percentage.round(2))

# payment_installments tells us how many installments
# were used for a payment record.
#
# We count how frequently each installment value appears
# in the payments table.

installment_counts = (
    payments["payment_installments"]
    .value_counts()
    .sort_index()
)

print("Payment installment distribution:")
print(installment_counts)


# We already counted how many payment records use each
# installment value.
#
# Now we convert those counts into percentages so we can
# understand the relative distribution.

installment_percentage = (
    installment_counts
    / installment_counts.sum()
    * 100
)

print("Installment percentage distribution:")
print(installment_percentage.round(2))


# One order can potentially have more than one payment record.
# We want to count how many payment records belong to each order.
#
# This helps us understand the relationship between:
# orders → payments

payments_per_order = (
    payments["order_id"]
    .value_counts()
)

print("Payment records per order:")
print(payments_per_order.value_counts().sort_index())

# We want to know how many orders have multiple payment records.
#
# payments_per_order contains:
# order_id → number of payment records for that order.
#
# So > 1 means the order has more than one payment record.

multiple_payment_orders = (
    payments_per_order > 1
).sum()

single_payment_orders = (
    payments_per_order == 1
).sum()

print("Orders with exactly one payment record:", single_payment_orders)
print("Orders with multiple payment records:", multiple_payment_orders)
print("Total orders with payment records:", len(payments_per_order))


# We know there are 99,441 orders in the orders table,
# but only 99,440 order_ids appear in the payments table.
#
# So we find the order_id that exists in orders
# but does not exist in payments.

orders_without_payment = orders[
    ~orders["order_id"].isin(payments["order_id"])
]

print("Orders without a payment record:")
print(orders_without_payment)


# We found one order that exists in the orders table
# but does not have a matching payment record.
#
# Now we check whether this order has any item records.
# This helps us understand whether the order itself contains
# normal order-item information.

missing_payment_order_id = orders_without_payment["order_id"].iloc[0]

order_items_for_missing_payment = order_items[
    order_items["order_id"] == missing_payment_order_id
]

print("Order ID:")
print(missing_payment_order_id)

print("\nOrder items for this order:")
print(order_items_for_missing_payment)

print("\nNumber of item records:")
print(len(order_items_for_missing_payment))


# We found an unusual order:
# it has order items and is marked as delivered,
# but it has no payment record.
#
# Now we inspect all available order information
# to understand its timeline.

print("Complete order information:")
print(
    orders[
        orders["order_id"] == missing_payment_order_id
    ].T
)

# This order has no payment record, so we are investigating
# whether anything else unusual happened with its timeline.
#
# Here we calculate how many days late the order was compared
# with its estimated delivery date.

missing_order_data = orders[
    orders["order_id"] == missing_payment_order_id
].copy()

missing_order_data["late_days"] = (
    missing_order_data["order_delivered_customer_date"]
    - missing_order_data["order_estimated_delivery_date"]
).dt.total_seconds() / (24 * 60 * 60)

print("Delivery delay for this order:")
print(missing_order_data["late_days"])


# The order_reviews table contains customer review information.
# First, we inspect its structure before doing any analysis.
#
# We want to know:
# 1. How many rows and columns it has
# 2. What columns are available
# 3. What the first few records look like
# 4. What data types the columns have
# 5. Whether any values are missing
# 6. Whether there are completely duplicated rows

reviews = pd.read_csv(
    "data/raw/olist_order_reviews_dataset.csv"
)

print("Shape:")
print(reviews.shape)

print("\nColumns:")
print(reviews.columns.tolist())

print("\nFirst 5 rows:")
print(reviews.head())

print("\nData types:")
print(reviews.dtypes)

print("\nMissing values:")
print(reviews.isnull().sum())

print("\nDuplicate rows:")
print(reviews.duplicated().sum())

# review_score tells us the rating given by the customer.
#
# We count how many review records belong to each score.
# This helps us understand the overall distribution
# of customer ratings.

review_score_counts = (
    reviews["review_score"]
    .value_counts()
    .sort_index()
)

print("Review score distribution:")
print(review_score_counts)

# We already counted the number of reviews for each score.
# Now we convert those counts into percentages.
#
# This tells us what percentage of all review records
# belongs to each rating score.

review_score_percentage = (
    review_score_counts
    / review_score_counts.sum()
    * 100
)

print("Review score percentage distribution:")
print(review_score_percentage.round(2))


# The mean gives us the average review score across
# all review records.
#
# Since review_score is numeric, Pandas calculates the
# arithmetic average automatically.

average_review_score = reviews["review_score"].mean()

print("Average review score:")
print(round(average_review_score, 2))

# WHY:
# Before using reviews in joins or analysis, we need to understand
# how review records relate to orders.

# 1. Check whether every review_id is unique
unique_review_ids = reviews["review_id"].nunique()

# 2. Count how many different orders have reviews
unique_review_orders = reviews["order_id"].nunique()

# 3. Find orders that have more than one review record
reviews_per_order = reviews["order_id"].value_counts()

multiple_review_orders = reviews_per_order[
    reviews_per_order > 1
]

print("Total review rows:", len(reviews))
print("Unique review IDs:", unique_review_ids)
print("Unique orders with reviews:", unique_review_orders)

print("\nOrders having multiple review records:")
print(len(multiple_review_orders))

print("\nTop orders by number of review records:")
print(multiple_review_orders.head(10))


# WHY:
# We found that review_id is not unique.
# Now we want to see whether duplicate review_ids
# represent completely identical records or different records.

duplicate_review_ids = reviews[
    reviews["review_id"].duplicated(keep=False)
].sort_values("review_id")

print("Rows belonging to duplicated review_ids:")
print(len(duplicate_review_ids))

print("\nNumber of duplicated review_ids:")
print(duplicate_review_ids["review_id"].nunique())

print("\nSample duplicated review records:")
print(duplicate_review_ids.head(10))


# WHY:
# We found that the same review_id can appear with different order_ids.
# Now we want to know how many orders are associated with each review_id.

orders_per_review_id = reviews.groupby("review_id")["order_id"].nunique()

print("Review IDs linked to more than one order:")
print((orders_per_review_id > 1).sum())

print("\nMaximum number of different orders linked to one review_id:")
print(orders_per_review_id.max())

print("\nTop review IDs by number of different orders:")
print(orders_per_review_id.sort_values(ascending=False).head(10))


# WHY:
# We have checked the relationship from review_id to order_id.
# Now we check the reverse relationship:
# how many review records can belong to one order?

reviews_per_order = reviews.groupby("order_id")["review_id"].count()

print("Orders with more than one review record:")
print((reviews_per_order > 1).sum())

print("\nMaximum review records for one order:")
print(reviews_per_order.max())

print("\nTop orders by number of review records:")
print(reviews_per_order.sort_values(ascending=False).head(10))

# WHY:
# Review dates are currently stored as text.
# We need to convert them into real datetime values so later
# we can calculate things like review response time.

date_columns_reviews = [
    "review_creation_date",
    "review_answer_timestamp"
]

for column in date_columns_reviews:
    reviews[column] = pd.to_datetime(reviews[column])

print("Review date columns converted successfully.")

print("\nData types:")
print(reviews[date_columns_reviews].dtypes)

print("\nDate range:")
print("Review creation:",
      reviews["review_creation_date"].min(),
      "to",
      reviews["review_creation_date"].max())

print("Review answer:",
      reviews["review_answer_timestamp"].min(),
      "to",
      reviews["review_answer_timestamp"].max())

print("\nMissing values:")
print(reviews[date_columns_reviews].isna().sum())


# WHY:
# We want to measure how quickly reviews are answered.
# Subtracting two datetime columns gives us the time difference.

reviews["response_time"] = (
    reviews["review_answer_timestamp"]
    - reviews["review_creation_date"]
)

# Convert the time difference into hours
reviews["response_hours"] = (
    reviews["response_time"].dt.total_seconds() / 3600
)

print("Response time statistics (hours):")
print(reviews["response_hours"].describe())

print("\nAverage response time:",
      round(reviews["response_hours"].mean(), 2), "hours")

print("Median response time:",
      round(reviews["response_hours"].median(), 2), "hours")

print("Minimum response time:",
      round(reviews["response_hours"].min(), 2), "hours")

print("Maximum response time:",
      round(reviews["response_hours"].max(), 2), "hours")



# WHY:
# The maximum response time is extremely high.
# Before deciding whether these are valid or problematic,
# we need to inspect the actual records.

longest_response_reviews = reviews[
    [
        "review_id",
        "order_id",
        "review_score",
        "review_creation_date",
        "review_answer_timestamp",
        "response_hours"
    ]
].sort_values(
    "response_hours",
    ascending=False
)

print("Top 10 longest review response times:")
print(longest_response_reviews.head(10))

# WHY:
# A review answer should normally happen after the review was created.
# We check for records where the answer timestamp is earlier
# than the creation timestamp.

invalid_response_times = reviews[
    reviews["response_hours"] < 0
]

print("Reviews with negative response time:")
print(len(invalid_response_times))

print("\nMinimum response time:")
print(reviews["response_hours"].min())

# WHY:
# Missing comments are not automatically bad data.
# A customer can give a rating without writing a comment.
# We want to see the relationship between review score
# and whether a comment was provided.

reviews["has_comment"] = (
    reviews["review_comment_message"].notna()
)

comment_by_score = pd.crosstab(
    reviews["review_score"],
    reviews["has_comment"],
    normalize="index"
) * 100

print("Comment availability by review score (%):")
print(comment_by_score.round(2))

# WHY:
# We want to compare customer rating with the time taken
# to answer the review.

response_by_score = reviews.groupby("review_score")[
    "response_hours"
].agg(["count", "mean", "median"])

print("Response time by review score:")
print(response_by_score.round(2))


# ============================================================
# PRODUCTS TABLE - COMPLETE RAW DATA EXPLORATION
# ============================================================

import pandas as pd


# ------------------------------------------------------------
# 1. LOAD THE RAW DATA
# ------------------------------------------------------------

# Load the original products CSV file.
# We are only exploring the data; we are not modifying the raw file.

products = pd.read_csv(
    "data/raw/olist_products_dataset.csv"
)


# ------------------------------------------------------------
# 2. BASIC STRUCTURE
# ------------------------------------------------------------

print("=" * 60)
print("1. BASIC STRUCTURE")
print("=" * 60)

print("Shape:")
print(products.shape)

print("\nColumns:")
print(products.columns.tolist())


# ------------------------------------------------------------
# 3. DATA TYPES
# ------------------------------------------------------------

print("\n" + "=" * 60)
print("2. DATA TYPES")
print("=" * 60)

print(products.dtypes)


# ------------------------------------------------------------
# 4. MISSING VALUES
# ------------------------------------------------------------

print("\n" + "=" * 60)
print("3. MISSING VALUES")
print("=" * 60)

print(products.isna().sum())


# ------------------------------------------------------------
# 5. DUPLICATE ROWS
# ------------------------------------------------------------

print("\n" + "=" * 60)
print("4. DUPLICATE ROWS")
print("=" * 60)

print("Duplicate rows:", products.duplicated().sum())


# ------------------------------------------------------------
# 6. PRODUCT ID CHECK
# ------------------------------------------------------------

# Check whether product_id uniquely identifies each product.

print("\n" + "=" * 60)
print("5. PRODUCT ID CHECK")
print("=" * 60)

print("Total rows:", len(products))
print("Unique product IDs:", products["product_id"].nunique())


# ------------------------------------------------------------
# 7. NUMERIC COLUMN STATISTICS
# ------------------------------------------------------------

# These columns describe product size, weight, photos,
# name length, and description length.

print("\n" + "=" * 60)
print("6. NUMERIC COLUMN STATISTICS")
print("=" * 60)

numeric_columns = [
    "product_name_lenght",
    "product_description_lenght",
    "product_photos_qty",
    "product_weight_g",
    "product_length_cm",
    "product_height_cm",
    "product_width_cm"
]

print(
    products[numeric_columns]
    .describe()
    .round(2)
)


# ------------------------------------------------------------
# 8. PRODUCT CATEGORY ANALYSIS
# ------------------------------------------------------------

# Check how many different product categories exist
# and which categories appear most frequently.

print("\n" + "=" * 60)
print("7. PRODUCT CATEGORY CHECK")
print("=" * 60)

print(
    "Unique categories:",
    products["product_category_name"].nunique()
)

print("\nTop 15 categories:")

print(
    products["product_category_name"]
    .value_counts()
    .head(15)
)


# ------------------------------------------------------------
# 9. PRODUCT -> ORDER ITEMS RELATIONSHIP
# ------------------------------------------------------------

# Check whether every product that appears in order_items
# also exists in the products table.

print("\n" + "=" * 60)
print("8. PRODUCT -> ORDER ITEMS RELATIONSHIP")
print("=" * 60)

order_item_product_ids = set(
    order_items["product_id"].unique()
)

product_table_ids = set(
    products["product_id"].unique()
)

missing_products = (
    order_item_product_ids - product_table_ids
)

print(
    "Unique products found in order_items:",
    len(order_item_product_ids)
)

print(
    "Unique products in products table:",
    len(product_table_ids)
)

print(
    "Sold product IDs missing from products table:",
    len(missing_products)
)


# ------------------------------------------------------------
# 10. PRODUCTS NEVER FOUND IN ORDER ITEMS
# ------------------------------------------------------------

# Find products that exist in the products table
# but never appear in order_items.

print("\n" + "=" * 60)
print("9. PRODUCTS NEVER FOUND IN ORDER ITEMS")
print("=" * 60)

never_sold_products = products[
    ~products["product_id"].isin(
        order_item_product_ids
    )
]

print(
    "Products in products table:",
    len(products)
)

print(
    "Products never found in order_items:",
    len(never_sold_products)
)


# ------------------------------------------------------------
# 11. SAMPLE DATA
# ------------------------------------------------------------

# Display a few rows so we can visually understand
# what a product record looks like.

print("\n" + "=" * 60)
print("10. SAMPLE PRODUCTS")
print("=" * 60)

print(products.head())



# ============================================================
# SELLERS TABLE - COMPLETE RAW DATA EXPLORATION
# ============================================================



# ------------------------------------------------------------
# 1. LOAD THE RAW DATA
# ------------------------------------------------------------

# Load the original sellers CSV file.
# We are only exploring the data and will not modify the raw file.

sellers = pd.read_csv(
    "data/raw/olist_sellers_dataset.csv"
)


# ------------------------------------------------------------
# 2. BASIC STRUCTURE
# ------------------------------------------------------------

print("=" * 60)
print("1. BASIC STRUCTURE")
print("=" * 60)

print("Shape:")
print(sellers.shape)

print("\nColumns:")
print(sellers.columns.tolist())


# ------------------------------------------------------------
# 3. DATA TYPES
# ------------------------------------------------------------

print("\n" + "=" * 60)
print("2. DATA TYPES")
print("=" * 60)

print(sellers.dtypes)


# ------------------------------------------------------------
# 4. MISSING VALUES
# ------------------------------------------------------------

print("\n" + "=" * 60)
print("3. MISSING VALUES")
print("=" * 60)

print(sellers.isna().sum())


# ------------------------------------------------------------
# 5. DUPLICATE ROWS
# ------------------------------------------------------------

print("\n" + "=" * 60)
print("4. DUPLICATE ROWS")
print("=" * 60)

print("Duplicate rows:", sellers.duplicated().sum())


# ------------------------------------------------------------
# 6. SELLER ID CHECK
# ------------------------------------------------------------

# Check whether seller_id uniquely identifies each seller.

print("\n" + "=" * 60)
print("5. SELLER ID CHECK")
print("=" * 60)

print("Total rows:", len(sellers))
print("Unique seller IDs:", sellers["seller_id"].nunique())


# ------------------------------------------------------------
# 7. SELLER LOCATION ANALYSIS
# ------------------------------------------------------------

# Check how many unique cities and states sellers belong to.

print("\n" + "=" * 60)
print("6. SELLER LOCATION CHECK")
print("=" * 60)

print(
    "Unique seller cities:",
    sellers["seller_city"].nunique()
)

print(
    "Unique seller states:",
    sellers["seller_state"].nunique()
)

print("\nTop 15 seller states:")

print(
    sellers["seller_state"]
    .value_counts()
    .head(15)
)


# ------------------------------------------------------------
# 8. SELLER -> ORDER ITEMS RELATIONSHIP
# ------------------------------------------------------------

# Check whether every seller found in order_items
# also exists in the sellers table.

print("\n" + "=" * 60)
print("7. SELLER -> ORDER ITEMS RELATIONSHIP")
print("=" * 60)

order_item_seller_ids = set(
    order_items["seller_id"].unique()
)

seller_table_ids = set(
    sellers["seller_id"].unique()
)

missing_sellers = (
    order_item_seller_ids - seller_table_ids
)

print(
    "Unique sellers found in order_items:",
    len(order_item_seller_ids)
)

print(
    "Unique sellers in sellers table:",
    len(seller_table_ids)
)

print(
    "Seller IDs in order_items missing from sellers table:",
    len(missing_sellers)
)


# ------------------------------------------------------------
# 9. SELLERS NEVER FOUND IN ORDER ITEMS
# ------------------------------------------------------------

# Find sellers that exist in the sellers table
# but never appear in order_items.

print("\n" + "=" * 60)
print("8. SELLERS NEVER FOUND IN ORDER ITEMS")
print("=" * 60)

never_used_sellers = sellers[
    ~sellers["seller_id"].isin(
        order_item_seller_ids
    )
]

print(
    "Sellers in sellers table:",
    len(sellers)
)

print(
    "Sellers never found in order_items:",
    len(never_used_sellers)
)


# ------------------------------------------------------------
# 10. SAMPLE DATA
# ------------------------------------------------------------

# Display a few rows to understand what one seller record looks like.

print("\n" + "=" * 60)
print("9. SAMPLE SELLERS")
print("=" * 60)

print(sellers.head())

# ============================================================
# GEOLOCATION TABLE - COMPLETE RAW DATA EXPLORATION
# ============================================================




# ------------------------------------------------------------
# 1. LOAD THE RAW DATA
# ------------------------------------------------------------

# Load the original geolocation CSV file.
# We are only exploring the data and will not modify the raw file.

geolocation = pd.read_csv(
    "data/raw/olist_geolocation_dataset.csv"
)


# ------------------------------------------------------------
# 2. BASIC STRUCTURE
# ------------------------------------------------------------

print("=" * 60)
print("1. BASIC STRUCTURE")
print("=" * 60)

print("Shape:")
print(geolocation.shape)

print("\nColumns:")
print(geolocation.columns.tolist())


# ------------------------------------------------------------
# 3. DATA TYPES
# ------------------------------------------------------------

print("\n" + "=" * 60)
print("2. DATA TYPES")
print("=" * 60)

print(geolocation.dtypes)


# ------------------------------------------------------------
# 4. MISSING VALUES
# ------------------------------------------------------------

print("\n" + "=" * 60)
print("3. MISSING VALUES")
print("=" * 60)

print(geolocation.isna().sum())


# ------------------------------------------------------------
# 5. DUPLICATE ROWS
# ------------------------------------------------------------

print("\n" + "=" * 60)
print("4. DUPLICATE ROWS")
print("=" * 60)

print("Duplicate rows:", geolocation.duplicated().sum())


# ------------------------------------------------------------
# 6. ZIP CODE PREFIX CHECK
# ------------------------------------------------------------

# Check how many unique zip code prefixes exist.
# A zip code prefix may appear in multiple rows.

print("\n" + "=" * 60)
print("5. ZIP CODE PREFIX CHECK")
print("=" * 60)

print(
    "Total rows:",
    len(geolocation)
)

print(
    "Unique zip code prefixes:",
    geolocation["geolocation_zip_code_prefix"].nunique()
)


# ------------------------------------------------------------
# 7. CITY AND STATE CHECK
# ------------------------------------------------------------

# Check how many cities and states are represented
# in the geolocation data.

print("\n" + "=" * 60)
print("6. LOCATION CHECK")
print("=" * 60)

print(
    "Unique cities:",
    geolocation["geolocation_city"].nunique()
)

print(
    "Unique states:",
    geolocation["geolocation_state"].nunique()
)

print("\nTop 15 states:")

print(
    geolocation["geolocation_state"]
    .value_counts()
    .head(15)
)


# ------------------------------------------------------------
# 8. ZIP CODE PREFIX REPETITION
# ------------------------------------------------------------

# Check how many rows exist for each zip code prefix.
# This helps us understand the grain of the table.

print("\n" + "=" * 60)
print("7. ZIP CODE PREFIX REPETITION")
print("=" * 60)

rows_per_zip = (
    geolocation
    .groupby("geolocation_zip_code_prefix")
    .size()
)

print("Average rows per zip code prefix:",
      round(rows_per_zip.mean(), 2))

print("Maximum rows for one zip code prefix:",
      rows_per_zip.max())

print("\nTop 10 zip code prefixes by number of rows:")

print(
    rows_per_zip
    .sort_values(ascending=False)
    .head(10)
)


# ------------------------------------------------------------
# 9. COORDINATE RANGE
# ------------------------------------------------------------

# Check the minimum and maximum latitude and longitude values.
# This helps us understand the geographic coverage.

print("\n" + "=" * 60)
print("8. COORDINATE RANGE")
print("=" * 60)

print("Latitude:")
print(
    geolocation["geolocation_lat"]
    .agg(["min", "max"])
)

print("\nLongitude:")
print(
    geolocation["geolocation_lng"]
    .agg(["min", "max"])
)


# ------------------------------------------------------------
# 10. DUPLICATE ZIP + LOCATION COMBINATIONS
# ------------------------------------------------------------

# Check whether the same zip code, city, and state combination
# appears multiple times.

location_columns = [
    "geolocation_zip_code_prefix",
    "geolocation_city",
    "geolocation_state"
]

unique_location_combinations = (
    geolocation[location_columns]
    .drop_duplicates()
)

print("\n" + "=" * 60)
print("9. UNIQUE ZIP + CITY + STATE COMBINATIONS")
print("=" * 60)

print(
    "Unique zip/city/state combinations:",
    len(unique_location_combinations)
)


# ------------------------------------------------------------
# 11. SAMPLE DATA
# ------------------------------------------------------------

# Display a few rows to understand what one geolocation
# record looks like.

print("\n" + "=" * 60)
print("10. SAMPLE GEOLOCATION RECORDS")
print("=" * 60)

print(geolocation.head())

# PRODUCT CATEGORY TRANSLATION TABLE
# - COMPLETE RAW DATA EXPLORATION
# 1. LOAD THE RAW DATA
# Load the original category translation CSV file.
# We are only exploring the data and will not modify the raw file.

category_translation = pd.read_csv(
    "data/raw/product_category_name_translation.csv"
)

#Basic Structure

print("=" * 60)
print("1. BASIC STRUCTURE")
print("=" * 60)

print("Shape:")
print(category_translation.shape)

print("\nColumns:")
print(category_translation.columns.tolist())

#Data Types
print("\n" + "=" * 60)
print("2. DATA TYPES")
print("=" * 60)

print(category_translation.dtypes)

# 4. MISSING VALUES
print("\n" + "=" * 60)
print("3. MISSING VALUES")
print("=" * 60)

print(category_translation.isna().sum())

# 5. DUPLICATE ROWS

print("\n" + "=" * 60)
print("4. DUPLICATE ROWS")
print("=" * 60)

print(
    "Duplicate rows:",
    category_translation.duplicated().sum()
)
# 6. CATEGORY NAME UNIQUENESS
# Check whether each Portuguese category has one translation.

print("\n" + "=" * 60)
print("5. CATEGORY UNIQUENESS CHECK")
print("=" * 60)

print(
    "Total rows:",
    len(category_translation)
)

print(
    "Unique Portuguese categories:",
    category_translation["product_category_name"]
    .nunique()
)

print(
    "Unique English categories:",
    category_translation["product_category_name_english"]
    .nunique()
)
# 7. CHECK FOR MULTIPLE TRANSLATIONS
# Check whether one Portuguese category maps to
# more than one English category.

translations_per_category = (
    category_translation
    .groupby("product_category_name")
    ["product_category_name_english"]
    .nunique()
)

print("\n" + "=" * 60)
print("6. TRANSLATION RELATIONSHIP CHECK")
print("=" * 60)

print(
    "Portuguese categories with multiple English translations:",
    (translations_per_category > 1).sum()
)

print(
    "Maximum translations for one Portuguese category:",
    translations_per_category.max()
)
# 8. CHECK WHETHER ALL PRODUCT CATEGORIES HAVE TRANSLATIONS
# Compare the categories in the products table with
# the categories available in the translation table.

print("\n" + "=" * 60)
print("7. PRODUCTS -> TRANSLATION RELATIONSHIP")
print("=" * 60)

product_categories = set(
    products["product_category_name"]
    .dropna()
    .unique()
)

translated_categories = set(
    category_translation["product_category_name"]
    .unique()
)

missing_translations = (
    product_categories - translated_categories
)

print(
    "Unique categories in products:",
    len(product_categories)
)

print(
    "Categories in translation table:",
    len(translated_categories)
)

print(
    "Product categories without translation:",
    len(missing_translations)
)


# ------------------------------------------------------------
# 9. EXTRA TRANSLATIONS
# ------------------------------------------------------------

# Check whether the translation table contains categories
# that do not appear in the products table.

extra_translations = (
    translated_categories - product_categories
)

print(
    "Translations without matching product category:",
    len(extra_translations)
)


# ------------------------------------------------------------
# 10. SAMPLE DATA
# ------------------------------------------------------------

# Display sample rows to understand the translation mapping.

print("\n" + "=" * 60)
print("8. SAMPLE TRANSLATIONS")
print("=" * 60)

print(
    category_translation.head(15)
)

