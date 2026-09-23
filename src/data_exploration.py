
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





order_items = pd.read_csv(
    "data/raw/olist_order_items_dataset.csv"
)

print("\nOrder Items:")
print(order_items.head())

print("\nShape:", order_items.shape)

print("\nColumns:")
print(order_items.columns)

print("\nData Types:")
print(order_items.dtypes)