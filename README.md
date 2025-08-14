# 🛍️ Ecommerce Multi Marketplace Analytics

The **Multi Marketplace Pipeline** is designed to analyze and process data from multiple e-commerce marketplaces — including **Amazon**, **Flipkart**, and **Meesho** — in one unified workflow.  
It fetches, cleans, aggregates, and visualizes sales and customer data to uncover trends, track performance, and assist in data-driven decision-making.

---

## ✨ Features

- 🔗 **Multi-source integration**: Process data from Amazon, Flipkart, Meesho, Olist, and more.
- 🧹 **Automated preprocessing**: Clean and transform raw marketplace data into analysis-ready format.
- 📊 **Sales analytics**: Generate monthly revenue reports, top categories, and top customers.
- ⚙️ **Scalable architecture**: Modular Python codebase with notebook support for data exploration.
- 🗄️ **Database support**: Load cleaned datasets into SQL databases for advanced querying.

---

## 🗂️ Project Structure

```markdown
multi_marketplace_pipeline
├── src
│   ├── app.py                  # 🚀 Main application entry point
│   ├── fetchData.py            # 📥 Module for fetching and preprocessing data
│   └── __init__.py             # 📦 Marks the directory as a Python package
├── data
│   ├── agg_monthly_revenue.csv       # 📈 Aggregated monthly revenue data
│   ├── agg_top_categories.csv        # 🏷️ Aggregated data on top product categories
│   ├── agg_top_customers.csv         # 🧑‍💼 Aggregated data on top customers
│   ├── amazon_orders_clean.csv       # 🛒 Cleaned order data from Amazon
│   ├── ecommerce_sales.csv           # 💰 Sales data from various e-commerce platforms
│   ├── flipkart_orders_clean.csv     # 🛍️ Cleaned order data from Flipkart
│   ├── meesho_orders_clean.csv       # 🧵 Cleaned order data from Meesho
│   ├── olist_customers_dataset.csv   # 👥 Customer data from Olist
│   ├── olist_geolocation_dataset.csv # 🌍 Geolocation data for Olist customers
│   ├── olist_order_items_dataset.csv # 📦 Order items data from Olist
│   ├── olist_order_payments_dataset.csv # 💳 Payment data for Olist orders
│   ├── olist_order_reviews_dataset.csv  # 📝 Reviews data from Olist orders
│   ├── olist_orders_dataset.csv      # 📃 Order data from Olist
│   ├── olist_products_dataset.csv    # 🧸 Product data from Olist
│   ├── olist_sellers_dataset.csv     # 🧑‍🔧 Seller data from Olist
│   ├── orders.csv                    # 📑 General order data
│   ├── product_category_name_translation.csv # 🌐 Category name translations
│   └── uk_ecommerce.csv              # 🇬🇧 UK-specific e-commerce data
├── notebooks
│   ├── load_to_db.ipynb               # 🗃️ Load data into a database
│   ├── preprocessing_all.ipynb        # 🔄 Preprocess data from all sources
│   ├── preprocessing_amazon.ipynb     # 🛒 Amazon-specific preprocessing
│   ├── preprocessing_flipkart.ipynb   # 🛍️ Flipkart-specific preprocessing
│   ├── preprocessing_meesho.ipynb     # 🧵 Meesho-specific preprocessing
│   └── Pyspark_sql_connection.ipynb   # 🔌 PySpark SQL connection
└── README.md                          # 📘 Documentation for the project
```

---

## ⚙️ Setup Instructions

1. 📥 **Clone the repository**:
   ```bash
   git clone https://github.com/PriyankaKhivsara/multi_marketplace_pipeline.git
   cd multi_marketplace_pipeline
   ```

2. 📦 **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

3. 🚀 **Run the main application**:
   ```bash
   python src/app.py
   ```

---

## 🧪 Usage

* ▶️ Run `fetchData.py` to retrieve and preprocess data from all marketplaces.
* 📓 Use the **Jupyter notebooks** in the `notebooks/` folder for interactive exploration and database loading.
* 📁 Use the pre-generated aggregated CSV files in `data/` for quick reporting and visualization.

---

## 🛠️ Technologies Used

* 🐍 **Python** — Core programming language  
* 🧮 **Pandas / NumPy** — Data processing  
* 📉 **Matplotlib / Seaborn** — Visualization  
* 🔥 **PySpark** — Big data processing  
* 🗄️ **MySQL** — Database storage  
* 📘 **Jupyter Notebook** — Interactive analysis  

---

## 📦 Data Sources

* 🛒 **Amazon** — E-commerce order dataset  
* 🛍️ **Flipkart** — Order & product dataset  
* 🧵 **Meesho** — Order dataset  

---

## 🚀 Future Improvements

* 🔄 Add **real-time ingestion** from APIs instead of static CSV files  
* 📊 Integrate **dashboarding tools** like Streamlit, Power BI, or Tableau  
* 🕒 Automate scheduled ETL pipelines using Apache Airflow  
* 🌍 Expand marketplace coverage to **eBay**, **Shopify**, and others  

---

## 🤝 Contributing

Contributions are welcome!  
If you find a bug or have an idea for improvement:

1. 🐞 Open an issue describing it  
2. 🍴 Fork the repo and submit a pull request  

---

## 📄 License

This project is licensed under the MIT License — see the [LICENSE](LICENSE) file for details.
