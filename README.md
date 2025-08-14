# Multi Marketplace Pipeline

This project is designed to analyze and process data from multiple e-commerce marketplaces, including Amazon, Flipkart, Meesho, and Olist. The pipeline fetches, cleans, and aggregates data to provide insights into sales, customer behavior, and product performance.

## Project Structure

```
multi_marketplace_pipeline
├── src
│   ├── app.py                  # Main application entry point
│   ├── fetchData.py            # Module for fetching and preprocessing data
│   └── __init__.py             # Marks the directory as a Python package
├── data
│   ├── agg_monthly_revenue.csv  # Aggregated monthly revenue data
│   ├── agg_top_categories.csv    # Aggregated data on top product categories
│   ├── agg_top_customers.csv     # Aggregated data on top customers
│   ├── amazon_orders_clean.csv    # Cleaned order data from Amazon
│   ├── ecommerce_sales.csv        # Sales data from various e-commerce platforms
│   ├── flipkart_orders_clean.csv   # Cleaned order data from Flipkart
│   ├── meesho_orders_clean.csv     # Cleaned order data from Meesho
│   ├── olist_customers_dataset.csv  # Customer data from Olist
│   ├── olist_geolocation_dataset.csv # Geolocation data for Olist customers
│   ├── olist_order_items_dataset.csv  # Order items data from Olist
│   ├── olist_order_payments_dataset.csv # Payment data for Olist orders
│   ├── olist_order_reviews_dataset.csv  # Reviews data for Olist orders
│   ├── olist_orders_dataset.csv       # Order data from Olist
│   ├── olist_products_dataset.csv      # Product data from Olist
│   ├── olist_sellers_dataset.csv       # Seller data from Olist
│   ├── orders.csv                      # General order data
│   ├── product_category_name_translation.csv # Translations for product category names
│   └── uk_ecommerce.csv                # E-commerce data specific to the UK
├── notebooks
│   ├── load_to_db.ipynb               # Code for loading data into a database
│   ├── preprocessing_all.ipynb         # Code for preprocessing data from all sources
│   ├── preprocessing_amazon.ipynb      # Code for preprocessing Amazon-specific data
│   ├── preprocessing_flipkart.ipynb     # Code for preprocessing Flipkart-specific data
│   ├── preprocessing_meesho.ipynb       # Code for preprocessing Meesho-specific data
│   └── Pyspark_sql_connection.ipynb     # Code for establishing a SQL connection using PySpark
└── README.md                          # Documentation for the project
```

## Setup Instructions

1. Clone the repository to your local machine.
2. Navigate to the project directory.
3. Install the required dependencies using:
   ```
   pip install -r requirements.txt
   ```
4. Run the main application using:
   ```
   python src/app.py
   ```

## Usage

- Use the `fetchData.py` module to retrieve and preprocess data from various sources.
- The Jupyter notebooks in the `notebooks` directory provide additional functionality for data preprocessing and loading into databases.
- The aggregated data files in the `data` directory can be used for analysis and reporting.

## Contributing

Contributions are welcome! Please open an issue or submit a pull request for any improvements or bug fixes.

## License

This project is licensed under the MIT License. See the LICENSE file for more details.