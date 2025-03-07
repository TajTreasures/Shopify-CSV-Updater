import os
import requests
import pandas as pd
import base64

# 🔹 Load secrets from environment variables
GITHUB_REPO = "TajTreasures/Shopify-CSV-Updater"
CSV_FILE_NAME = "Shopify_Product_Catalog_Modified.csv"
GITHUB_ACCESS_TOKEN = os.getenv("GH_ACCESS_TOKEN")  # ✅ Corrected GitHub Token Name
SHOPIFY_ACCESS_TOKEN = os.getenv("SHOPIFY_ACCESS_TOKEN")  # ✅ Shopify Token

# 🔹 Shopify API Details
SHOPIFY_STORE_URL = "https://b4ksa0-yv.myshopify.com"
SHOPIFY_API_VERSION = "2024-01"
SHOPIFY_API_URL = f"{SHOPIFY_STORE_URL}/admin/api/{SHOPIFY_API_VERSION}/products.json"

# 🔹 Step 1: Download CSV from GitHub
def download_csv_from_github():
    url = f"https://api.github.com/repos/{GITHUB_REPO}/contents/{CSV_FILE_NAME}"
    headers = {"Authorization": f"token {GITHUB_ACCESS_TOKEN}"}

    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        content = response.json()
        csv_data = base64.b64decode(content["content"]).decode("utf-8")

        with open(CSV_FILE_NAME, "w", encoding="utf-8") as f:
            f.write(csv_data)

        print(f"✅ CSV file '{CSV_FILE_NAME}' downloaded successfully from GitHub!")
        return CSV_FILE_NAME
    else:
        print(f"❌ Failed to download CSV. Response: {response.json()}")
        return None

# 🔹 Step 2: Process CSV
def process_csv(csv_path):
    df = pd.read_csv(csv_path)
    print("📌 CSV Data Preview:")
    print(df.head())  # Show first few rows

    products = []
    for _, row in df.iterrows():
        product = {
            "title": row["Title"],
            "body_html": row["Description"],
            "vendor": row["Vendor"],
            "product_type": row["Type"],
            "variants": [
                {
                    "price": row["Price"],
                    "sku": row["SKU"]
                }
            ]
        }
        products.append(product)

    return products

# 🔹 Step 3: Upload Products to Shopify
def upload_to_shopify(products):
    headers = {
        "X-Shopify-Access-Token": SHOPIFY_ACCESS_TOKEN,
        "Content-Type": "application/json"
    }

    for product in products:
        response = requests.post(SHOPIFY_API_URL, json={"product": product}, headers=headers)
        if response.status_code == 201:
            print(f"✅ Product '{product['title']}' uploaded successfully!")
        else:
            print(f"❌ Failed to upload product '{product['title']}'. Response: {response.json()}")

# 🔹 Run the Full Workflow
if __name__ == "__main__":
    csv_file = download_csv_from_github()
    if csv_file:
        products = process_csv(csv_file)
        upload_to_shopify(products)
