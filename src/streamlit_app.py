import os
import pandas as pd
import streamlit as st
import plotly.express as px

# -------------------- Config --------------------
DATA_DIR = "data"

# Load datasets
@st.cache_data
def load_data():
    orders = pd.read_csv(os.path.join(DATA_DIR, "orders.csv"), parse_dates=["order_date"])
    agg_monthly = pd.read_csv(os.path.join(DATA_DIR, "agg_monthly_revenue.csv")) if os.path.exists(os.path.join(DATA_DIR, "agg_monthly_revenue.csv")) else None
    agg_categories = pd.read_csv(os.path.join(DATA_DIR, "agg_top_categories.csv")) if os.path.exists(os.path.join(DATA_DIR, "agg_top_categories.csv")) else None
    agg_customers = pd.read_csv(os.path.join(DATA_DIR, "agg_top_customers.csv")) if os.path.exists(os.path.join(DATA_DIR, "agg_top_customers.csv")) else None
    return orders, agg_monthly, agg_categories, agg_customers

orders_df, monthly_df_agg, categories_df_agg, customers_df_agg = load_data()

st.set_page_config(page_title="E-commerce Sales Dashboard", layout="wide")
st.title("🛒 E-commerce Sales Dashboard")
st.caption("Flipkart + Amazon + Meesho unified pipeline → CSV → Streamlit")

# -------------------- Sidebar Filters --------------------
min_dt = orders_df["order_date"].min()
max_dt = orders_df["order_date"].max()
marketplaces_list = sorted(orders_df["marketplace"].dropna().unique())
categories_list = sorted(orders_df["product_category"].dropna().unique())

with st.sidebar:
    st.header("Filters")
    date_range = st.date_input(
        "Date range",
        value=(min_dt.date(), max_dt.date()),
        min_value=min_dt.date(),
        max_value=max_dt.date()
    )
    selected_marketplaces = st.multiselect("Marketplace", options=marketplaces_list, default=marketplaces_list)
    selected_categories = st.multiselect("Product category", options=categories_list, default=[])

# -------------------- Apply Filters --------------------
filtered_df = orders_df.copy()
filtered_df = filtered_df[(filtered_df["order_date"].dt.date >= date_range[0]) & (filtered_df["order_date"].dt.date <= date_range[1])]
if selected_marketplaces:
    filtered_df = filtered_df[filtered_df["marketplace"].isin(selected_marketplaces)]
if selected_categories:
    filtered_df = filtered_df[filtered_df["product_category"].isin(selected_categories)]

# -------------------- KPIs --------------------
kpi1, kpi2, kpi3 = st.columns(3)
kpi1.metric("Total Orders", f"{filtered_df['order_id'].nunique():,}")
kpi2.metric("Total Revenue", f"{filtered_df['revenue'].sum():,.2f}")
kpi3.metric("Unique Customers", f"{filtered_df['customer_id'].nunique():,}")

st.markdown("---")

# -------------------- Monthly Revenue Trend --------------------
monthly_df = filtered_df.groupby(filtered_df["order_date"].dt.to_period("M")).agg(total_revenue=("revenue", "sum")).reset_index()
monthly_df["year_month"] = monthly_df["order_date"].astype(str)
st.subheader("Monthly Revenue Trend")
if not monthly_df.empty:
    fig_line = px.line(monthly_df, x="year_month", y="total_revenue", markers=True)
    st.plotly_chart(fig_line, use_container_width=True)
else:
    st.info("No data for selected filters.")

# -------------------- Average Order Value --------------------
aov_df = filtered_df.groupby(filtered_df["order_date"].dt.to_period("M")).agg(
    avg_order_value=("revenue", lambda x: round(x.sum() / x.count(), 2))
).reset_index()
aov_df["month"] = aov_df["order_date"].astype(str)
st.subheader("Average Order Value Over Time")
if not aov_df.empty:
    fig_aov = px.line(aov_df, x="month", y="avg_order_value", markers=True)
    st.plotly_chart(fig_aov, use_container_width=True)
else:
    st.info("No AOV data for selected filters.")

# -------------------- Top Categories --------------------
cat_df = filtered_df.groupby("product_category").agg(total_revenue=("revenue", "sum")).reset_index().sort_values("total_revenue", ascending=False).head(15)
left, right = st.columns([1.2, 1])
with left:
    st.subheader("Top Categories by Revenue")
    if not cat_df.empty:
        st.plotly_chart(px.bar(cat_df, x="product_category", y="total_revenue"), use_container_width=True)
with right:
    st.subheader("Marketplace Revenue Share")
    mkt_df = filtered_df.groupby("marketplace").agg(total_revenue=("revenue", "sum")).reset_index()
    if not mkt_df.empty:
        st.plotly_chart(px.pie(mkt_df, names="marketplace", values="total_revenue", hole=0.4), use_container_width=True)

# -------------------- Top Products --------------------
prod_df = filtered_df.groupby(["product_id", "product_category"]).agg(
    total_revenue=("revenue", "sum"),
    total_orders=("order_id", "nunique")
).reset_index().sort_values("total_revenue", ascending=False).head(15)
st.subheader("Top Products by Revenue")
if not prod_df.empty:
    st.plotly_chart(px.bar(prod_df, x="product_id", y="total_revenue", color="product_category", hover_data=["total_orders"]), use_container_width=True)

# -------------------- Top Customers --------------------
cust_df = filtered_df.groupby("customer_id").agg(
    total_spent=("revenue", "sum"),
    orders_count=("order_id", "nunique")
).reset_index().sort_values("total_spent", ascending=False).head(25)
st.subheader("Top Customers")
st.dataframe(cust_df, use_container_width=True)

# -------------------- Raw Data --------------------
with st.expander("Peek raw data (sample 500 rows)"):
    st.dataframe(filtered_df.head(500), use_container_width=True)
