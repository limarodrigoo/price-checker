import time
import asyncio
import pandas as pd
from helper.scrapper import Scrapper
from helper.messager import Messager

PRODUCT_URL_CSV = "products.csv"
SAVE_TO_CSV = True
PRICES_CSV = "prices.csv"

scrapper = Scrapper()
messager = Messager()

def process_products(df):
    try:
        updated_products = []
        for product in df.to_dict("records"):
            price, site_name = scrapper.get_price(product["url"])
            product["price"]  = price
            product["site_name"] = site_name
            if product["price"] is None:
                continue
            product["alert"] = product["price"] < product["alert_price"]
            if product["alert"] is True:
                asyncio.run(messager.send_message(product=product["product"], url=product["url"], price=product["price"]))
            updated_products.append(product)
        return pd.DataFrame(updated_products)
    except Exception as error:
        print(error)


def main():
    t = time.localtime()
    current_time = time.strftime("%H:%M:%S", t)
    print(current_time)
    print("RUNNING SCRIPT!")
    df = scrapper.get_urls(csv_file=PRODUCT_URL_CSV)
    try:
        df_updated = process_products(df)
        if SAVE_TO_CSV:
            cols = list(df_updated)
            cols.remove('url')
            cols.append('url')
            df_updated = df_updated[cols]
            df_updated.to_csv(PRICES_CSV, index=False, mode="w")
            df_to_print = df_updated[['product','site_name', 'price']]
            print(df_to_print.to_string(index=False))
    except Exception as error:
        print(f"ERROR!{error}")

while True:
    main()
    
    time.sleep(15)
        