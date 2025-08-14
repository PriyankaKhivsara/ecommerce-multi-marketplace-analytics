import os
import time
import pandas as pd
import mysql.connector
from mysql.connector import pooling
from dotenv import load_dotenv
import streamlit as st
import plotly.express as px
import plotly.graph_objects as go

# -------------------- Config --------------------
# load_dotenv()  # reads .env if present

DB_CONFIG = {
    "host": os.getenv("MYSQL_HOST", "localhost"),
    "port": int(os.getenv("MYSQL_PORT", "3306")),
    "user": os.getenv("MYSQL_USER", "root"),
    "password": os.getenv("MYSQL_PASSWORD", "dbda"),
    "database": os.getenv("MYSQL_DB", "multi_marketplace"),
}

POOL = pooling.MySQLConnectionPool(
    pool_name="retail_pool",
    pool_size=5,
    pool_reset_session=True,
    **DB_CONFIG
)

st.set_page_config(page_title="E-commerce Sales Dashboard", layout="wide")

# -------------------- Helpers --------------------
def run_sql(query, params=None):
    conn = POOL.get_connection()
    try:
        print("SQL:", query)
        print("PARAMS:", params)
        df = pd.read_sql(query, conn, params=params)
    finally:
        conn.close()
    return df

@st.cache_data(ttl=300)
def load_base_table_name():
    """
    Determine whether you saved aggregates in MySQL already.
    If agg tables exist, we can use them; else compute from 'orders'.
    """
    try:
        q = "SHOW TABLES"
        df = run_sql(q)
        tables = set(df.iloc[:,0].str.lower())
        return {
            "has_monthly": "agg_monthly_revenue" in tables,
            "has_categories": "agg_top_categories" in tables,
            "has_customers": "agg_top_customers" in tables,
            "has_orders": "orders" in tables
        }
    except Exception:
        return {"has_monthly": False, "has_categories": False, "has_customers": False, "has_orders": True}

@st.cache_data(ttl=300)
def load_filter_values():
    """
    Pull filter values from raw orders (works whether or not agg tables exist).
    """
    q = """
    SELECT 
      MIN(order_date) AS min_dt,
      MAX(order_date) AS max_dt
    FROM orders
    """
    dt = run_sql(q).iloc[0]

    q2 = "SELECT DISTINCT marketplace FROM orders WHERE marketplace IS NOT NULL ORDER BY 1"
    marketplaces = run_sql(q2)["marketplace"].dropna().tolist()

    q3 = "SELECT DISTINCT product_category FROM orders WHERE product_category IS NOT NULL ORDER BY 1"
    categories = run_sql(q3)["product_category"].dropna().tolist()

    return pd.to_datetime(dt["min_dt"]), pd.to_datetime(dt["max_dt"]), marketplaces, categories

def build_where_clause(date_range, marketplaces, categories):
    clauses = []
    params = []

    if date_range:
        start, end = date_range
        clauses.append("order_date BETWEEN %s AND %s")
        params += [start.strftime("%Y-%m-%d"), end.strftime("%Y-%m-%d")]

    if marketplaces:
        if len(marketplaces) > 0:
            placeholders = ",".join(["%s"] * len(marketplaces))
            clauses.append(f"marketplace IN ({placeholders})")
            params += marketplaces

    if categories:
        if len(categories) > 0:
            placeholders = ",".join(["%s"] * len(categories))
            clauses.append(f"product_category IN ({placeholders})")
            params += categories

    where_sql = f"WHERE {' AND '.join(clauses)}" if clauses else ""
    return where_sql, params

# -------------------- UI: Sidebar Filters --------------------
st.title("🛒 E-commerce Sales Dashboard")
st.caption("Flipkart + Amazon + Meesho unified pipeline → MySQL → Streamlit")

table_info = load_base_table_name()
if not table_info.get("has_orders", False):
    st.error("Could not find `orders` table in MySQL. Please confirm your DB name and tables.")
    st.stop()

min_dt, max_dt, marketplaces_list, categories_list = load_filter_values()

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

    st.markdown("---")
    st.caption("Data refresh re-runs queries with your filters")

# -------------------- Build WHERE + Params --------------------
where_sql, where_params = build_where_clause(date_range, selected_marketplaces, selected_categories)

# -------------------- KPIs (computed from orders) --------------------
kpi_sql = f"""
SELECT
  COUNT(DISTINCT order_id) AS total_orders,
  ROUND(SUM(COALESCE(revenue,0)), 2) AS total_revenue,
  COUNT(DISTINCT customer_id) AS unique_customers
FROM orders
{where_sql}
"""
kpi_df = run_sql(kpi_sql, where_params)
kpi1, kpi2, kpi3 = st.columns(3)
kpi1.metric("Total Orders", f"{int(kpi_df['total_orders'].iloc[0] or 0):,}")
kpi2.metric("Total Revenue", f"{float(kpi_df['total_revenue'].iloc[0] or 0):,.2f}")
kpi3.metric("Unique Customers", f"{int(kpi_df['unique_customers'].iloc[0] or 0):,}")

st.markdown("---")

# -------------------- Monthly revenue trend --------------------
# If agg table exists, use it for speed; else compute on the fly with WHERE filters
if table_info["has_monthly"] and not selected_categories:
    # Use pre-aggregated and then filter by market/date if needed (join orders for filtering when necessary)
    # Simple path: recompute from orders to respect all filters consistently
    monthly_sql = f"""
    SELECT
      YEAR(order_date) AS order_year,
      MONTH(order_date) AS order_month,
      ROUND(SUM(COALESCE(revenue,0)), 2) AS total_revenue
    FROM orders
    {where_sql}
    GROUP BY 1,2
    ORDER BY 1,2
    """
else:
    # Compute from orders (respects all filters)
    monthly_sql = f"""
    SELECT
      YEAR(order_date) AS order_year,
      MONTH(order_date) AS order_month,
      ROUND(SUM(COALESCE(revenue,0)), 2) AS total_revenue
    FROM orders
    {where_sql}
    GROUP BY 1,2
    ORDER BY 1,2
    """

monthly_df = run_sql(monthly_sql, where_params)
monthly_df["year_month"] = monthly_df["order_year"].astype(str) + "-" + monthly_df["order_month"].astype(str).str.zfill(2)
st.subheader("Monthly Revenue Trend")
if len(monthly_df):
    fig_line = px.line(monthly_df, x="year_month", y="total_revenue", markers=True)
    fig_line.update_layout(xaxis_title="Year-Month", yaxis_title="Revenue")
    st.plotly_chart(fig_line, use_container_width=True)
else:
    st.info("No data for selected filters.")
    
# -------------------- Average Order Value (AOV) Trend --------------------
aov_sql = f"""
SELECT
    DATE_FORMAT(order_date, '%Y-%m') AS month,
    ROUND(SUM(COALESCE(revenue,0)) / NULLIF(COUNT(DISTINCT order_id), 0), 2) AS avg_order_value
FROM orders
{where_sql}
GROUP BY month
ORDER BY month
"""
aov_df = run_sql(aov_sql, where_params)

st.subheader("Average Order Value Over Time")
if len(aov_df):
    fig_aov = px.line(
        aov_df,
        x="month",
        y="avg_order_value",
        markers=True,
        title="Monthly Average Order Value"
    )
    fig_aov.update_layout(xaxis_title="Month", yaxis_title="Avg Order Value")
    st.plotly_chart(fig_aov, use_container_width=True)
else:
    st.info("No AOV data for selected filters.")
    
# -------------------- Top categories --------------------
cat_sql = f"""
SELECT
  product_category,
  ROUND(SUM(COALESCE(revenue,0)), 2) AS total_revenue
FROM orders
{where_sql}
GROUP BY 1
ORDER BY total_revenue DESC
LIMIT 15
"""
cat_df = run_sql(cat_sql, where_params)
left, right = st.columns([1.2, 1])

with left:
    st.subheader("Top Categories by Revenue")
    if len(cat_df):
        fig_bar = px.bar(cat_df, x="product_category", y="total_revenue")
        fig_bar.update_layout(xaxis_title="Category", yaxis_title="Revenue")
        st.plotly_chart(fig_bar, use_container_width=True)
    else:
        st.info("No category data for selected filters.")

# -------------------- Marketplace share --------------------
mkt_sql = f"""
SELECT
  marketplace,
  ROUND(SUM(COALESCE(revenue,0)), 2) AS total_revenue
FROM orders
{where_sql}
GROUP BY 1
ORDER BY total_revenue DESC
"""
mkt_df = run_sql(mkt_sql, where_params)

with right:
    st.subheader("Marketplace Revenue Share")
    if len(mkt_df):
        fig_pie = px.pie(mkt_df, names="marketplace", values="total_revenue", hole=0.4)
        st.plotly_chart(fig_pie, use_container_width=True)
    else:
        st.info("No marketplace data for selected filters.")

st.markdown("---")

# -------------------- Top products --------------------
prod_sql = f"""
SELECT
  product_id,
  product_category,
  ROUND(SUM(COALESCE(revenue,0)), 2) AS total_revenue,
  COUNT(DISTINCT order_id) AS total_orders
FROM orders
{where_sql}
GROUP BY 1, 2
ORDER BY total_revenue DESC
LIMIT 15
"""
prod_df = run_sql(prod_sql, where_params)

st.subheader("Top Products by Revenue")
if len(prod_df):
    fig_prod = px.bar(
        prod_df,
        x="product_id",
        y="total_revenue",
        color="product_category",
        hover_data=["total_orders"],
        title="Top 15 Products"
    )
    fig_prod.update_layout(xaxis_title="Product ID", yaxis_title="Revenue")
    st.plotly_chart(fig_prod, use_container_width=True)
else:
    st.info("No product data for selected filters.")


# -------------------- Top customers table --------------------
st.subheader("Top Customers")
cust_sql = f"""
SELECT
  customer_id,
  ROUND(SUM(COALESCE(revenue,0)), 2) AS total_spent,
  COUNT(DISTINCT order_id) AS orders_count
FROM orders
{where_sql}
GROUP BY 1
ORDER BY total_spent DESC
LIMIT 25
"""
cust_df = run_sql(cust_sql, where_params)
st.dataframe(cust_df, use_container_width=True)

# -------------------- Raw data preview (optional) --------------------
with st.expander("Peek raw data (sample 500 rows)"):
    sample_sql = f"""
    SELECT order_id, order_date, product_id, product_category, customer_id, product_price, revenue, marketplace
    FROM orders
    {where_sql}
    ORDER BY order_date DESC
    LIMIT 500
    """
    sample_df = run_sql(sample_sql, where_params)
    st.dataframe(sample_df, use_container_width=True)

st.caption("Tip: use the sidebar filters to slice by date, marketplace, and category.")

# -------------------- Top Categories by Revenue (Bar Chart) --------------------
cat_sql2 = f"""
SELECT
  product_category,
  ROUND(SUM(COALESCE(revenue,0)), 2) AS total_revenue,
  COUNT(DISTINCT order_id) AS total_orders
FROM orders
{where_sql}
GROUP BY product_category
ORDER BY total_revenue DESC
LIMIT 15
"""
cat_df2 = run_sql(cat_sql2, where_params)

st.subheader("Top Categories by Revenue (Bar Chart)")
if len(cat_df2):
    fig_cat2 = px.bar(
        cat_df2,
        x="product_category",
        y="total_revenue",
        hover_data=["total_orders"],
        title="Top 15 Categories"
    )
    fig_cat2.update_layout(xaxis_title="Product Category", yaxis_title="Revenue")
    st.plotly_chart(fig_cat2, use_container_width=True)
else:
    st.info("No category data for selected filters.")
