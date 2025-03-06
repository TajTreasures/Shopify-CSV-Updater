import pandas as pd
import requests
import time
import os
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

# Shopify API credentials
SHOPIFY_STORE_URL = "https://www.tajtreasures.com"
ACCESS_TOKEN = "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"
CSV_FILE_PATH = "/mnt/data/Shopify_Product_Catalog_Modified.csv"

# Shopify API endpoint
HEADERS = {
    "Content-Type": "application/json",
    "X-Shopify-Access-Token": ACCESS_TOKEN,
}

# Function to update products in Shopify
def update_shopify_product(product_id, data):
    url = f"{SHOPIFY_STORE_URL}/admin/api/2023-04/products/{product_id}.json"
    response = requests.put(url, json=data, headers=HEADERS)
    if response.status_code == 200:
        print(f"Updated product {product_id} successfully.")
    else:
        print(f"Failed to update product {product_id}: {response.text}")

# Function to process CSV and update Shopify
def process_csv():
    df = pd.read_csv(CSV_FILE_PATH)
    for _, row in df.iterrows():
        product_id = row.get("Product ID")
        if pd.notna(product_id):
            data = {
                "product": {
                    "id": int(product_id),
                    "title": row.get("Title"),
                    "variants": [{
                        "price": row.get("Price"),
                        "inventory_quantity": row.get("Stock")
                    }]
                }
            }
            update_shopify_product(product_id, data)

# Watchdog event handler to monitor CSV changes
class CSVHandler(FileSystemEventHandler):
    def on_modified(self, event):
        if event.src_path == CSV_FILE_PATH:
            print("CSV file changed. Updating Shopify...")
            process_csv()

if __name__ == "__main__":
    # Initial CSV processing
    print("Starting initial CSV processing...")
    process_csv()
    
    # Set up file watcher for automatic updates
    event_handler = CSVHandler()
    observer = Observer()
    observer.schedule(event_handler, path=os.path.dirname(CSV_FILE_PATH), recursive=False)
    observer.start()
    
    try:
        while True:
            time.sleep(10)
    except KeyboardInterrupt:
        observer.stop()
    observer.join()
