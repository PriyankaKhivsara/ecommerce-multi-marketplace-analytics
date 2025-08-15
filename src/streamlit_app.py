import os
import pandas as pd
import streamlit as st
import plotly.express as px

# -------------------- Config --------------------
st.set_page_config(page_title="E-commerce Sales Dashboard", layout="wide")

DATA_DIR = "data"

@st.cache_data
def load_data():
    # Load orders.csv with robust date parsing
    orders_df = pd.read_csv(os.path.join(DATA_DIR, "orders.csv"))
    if "order_date" in orders_df.columns:
        orders_df["order_date"] = pd.to_datetime(
            orders_df["order_date"], errors="coerce", infer_datetime_format=True
        )

    # Load aggregated monthly revenue, parse month column if exists
    agg_monthly_df = pd.read_csv(os.path.join(DATA_DIR, "agg_monthly_revenue.csv"))
    for col in ["order_month", "month", "date"]:
        if col in agg_monthly_df.columns:
            agg_monthly_df[col] = pd.to_datetime(
                agg_monthly_df[col], errors="coerce", infer_datetime_format=True
            )

    # Load other CSVs
    agg_top_cat_df = pd.read_csv(os.path.join(DATA_DIR, "agg_top_categories.csv"))
    agg_top_cust_df = pd.read_csv(os.path.join(DATA_DIR, "agg_top_customers.csv"))

    return orders_df, agg_monthly_df, agg_top_cat_df, agg_top_cust_df

# Load all data
orders_df, agg_monthly_df, agg_top_cat_df, agg_top_cust_df = load_data()

# -------------------- UI: Sidebar Filters --------------------
st.title("🛒 E-commerce Sales Dashboard")
st.caption("Flipkart + Amazon + Meesho unified pipeline → CSV → Streamlit")

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

    selected_marketplaces = st.multiselect(
        "Marketplace",
        options=marketplaces_list,
        default=marketplaces_list
    )

    selected_categories = st.multiselect(
        "Product category",
        options=categories_list,
        default=[]
    )

# -------------------- Apply Filters --------------------
mask = (
    (orders_df["order_date"].dt.date >= date_range[0]) &
    (orders_df["order_date"].dt.date <= date_range[1])
)
if selected_marketplaces:
    mask &= orders_df["marketplace"].isin(selected_marketplaces)
if selected_categories:
    mask &= orders_df["product_category"].isin(selected_categories)

filtered_df = orders_df.loc[mask]

# -------------------- KPIs --------------------
kpi1, kpi2, kpi3 = st.columns(3)
kpi1.metric("Total Orders", f"{filtered_df['order_id'].nunique():,}")
kpi2.metric("Total Revenue", f"{filtered_df['revenue'].sum():,.2f}")
kpi3.metric("Unique Customers", f"{filtered_df['customer_id'].nunique():,}")

st.markdown("---")

# -------------------- Monthly Revenue Trend --------------------
monthly_df = (
    filtered_df
    .groupby(filtered_df["order_date"].dt.to_period("M"))
    .agg(total_revenue=("revenue", "sum"))
    .reset_index()
)
monthly_df["year_month"] = monthly_df["order_date"].astype(str)

st.subheader("Monthly Revenue Trend")
if len(monthly_df):
    fig_line = px.line(monthly_df, x="year_month", y="total_revenue", markers=True)
    fig_line.update_layout(xaxis_title="Year-Month", yaxis_title="Revenue")
    st.plotly_chart(fig_line, use_container_width=True)
else:
    st.info("No data for selected filters.")

# -------------------- Average Order Value Trend --------------------
aov_df = (
    filtered_df
    .groupby(filtered_df["order_date"].dt.to_period("M"))
    .agg(
        avg_order_value=("revenue", lambda x: round(x.sum() / x.count(), 2) if x.count() else 0)
    )
    .reset_index()
)
aov_df["month"] = aov_df["order_date"].astype(str)

st.subheader("Average Order Value Over Time")
if len(aov_df):
    fig_aov = px.line(aov_df, x="month", y="avg_order_value", markers=True)
    fig_aov.update_layout(xaxis_title="Month", yaxis_title="Avg Order Value")
    st.plotly_chart(fig_aov, use_container_width=True)
else:
    st.info("No AOV data for selected filters.")

# -------------------- Top Categories --------------------
cat_df = (
    filtered_df
    .groupby("product_category")
    .agg(total_revenue=("revenue", "sum"))
    .reset_index()
    .sort_values("total_revenue", ascending=False)
    .head(15)
)

left, right = st.columns([1.2, 1])
with left:
    st.subheader("Top Categories by Revenue")
    if len(cat_df):
        fig_bar = px.bar(cat_df, x="product_category", y="total_revenue")
        fig_bar.update_layout(xaxis_title="Category", yaxis_title="Revenue")
        st.plotly_chart(fig_bar, use_container_width=True)
    else:
        st.info("No category data for selected filters.")

# -------------------- Marketplace Share --------------------
mkt_df = (
    filtered_df
    .groupby("marketplace")
    .agg(total_revenue=("revenue", "sum"))
    .reset_index()
)
with right:
    st.subheader("Marketplace Revenue Share")
    if len(mkt_df):
        fig_pie = px.pie(mkt_df, names="marketplace", values="total_revenue", hole=0.4)
        st.plotly_chart(fig_pie, use_container_width=True)
    else:
        st.info("No marketplace data for selected filters.")

st.markdown("---")

# -------------------- Top Products --------------------
prod_df = (
    filtered_df
    .groupby(["product_id", "product_category"])
    .agg(
        total_revenue=("revenue", "sum"),
        total_orders=("order_id", "nunique")
    )
    .reset_index()
    .sort_values("total_revenue", ascending=False)
    .head(15)
)

st.subheader("Top Products by Revenue")
if len(prod_df):
    fig_prod = px.bar(
        prod_df,
        x="product_id",
        y="total_revenue",
        color="product_category",
        hover_data=["total_orders"]
    )
    fig_prod.update_layout(xaxis_title="Product ID", yaxis_title="Revenue")
    st.plotly_chart(fig_prod, use_container_width=True)
else:
    st.info("No product data for selected filters.")

# -------------------- Top Customers --------------------
cust_df = (
    filtered_df
    .groupby("customer_id")
    .agg(
        total_spent=("revenue", "sum"),
        orders_count=("order_id", "nunique")
    )
    .reset_index()
    .sort_values("total_spent", ascending=False)
    .head(25)
)

st.subheader("Top Customers")
st.dataframe(cust_df, use_container_width=True)

# -------------------- Raw Data Preview --------------------
with st.expander("Peek raw data (sample 500 rows)"):
    st.dataframe(filtered_df.head(500), use_container_width=True)
