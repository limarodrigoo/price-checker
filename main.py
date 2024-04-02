import time
import os
import asyncio
import pandas as pd
import requests
from bs4 import BeautifulSoup
from price_parser import Price
from telegram import Bot
from urllib.parse import urlparse
from dotenv import load_dotenv

load_dotenv()

PRODUCT_URL_CSV = "products.csv"
SAVE_TO_CSV = True
PRICES_CSV = "prices.csv"
SEND_MAIL = True
TELEGRAM_TOKEN = os.getenv('TELEGRAM_TOKEN')

def get_urls(csv_file):
    df = pd.read_csv(csv_file)
    return df

def get_site_name(url):
    parsed_url = urlparse(url)

    site_name = parsed_url.netloc

    if site_name.startswith('www.'):
        site_name = site_name[4:]

    site_name = site_name.replace('.com.br', '').replace('.com', '')

    if '/' in site_name:
        site_name = site_name.split('/')[0]

    return site_name

def get_response(url):
    site_name = get_site_name(url)
    headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }
    if site_name == 'amazon':
        headers = {"accept-language": "en-US,en;q=0.9","accept-encoding": "gzip, deflate, br","User-Agent":"Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/111.0.0.0 Safari/537.36","accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7"}
    response = requests.get(url, headers=headers)
    return response.text, site_name

def get_kabum_price(html):
    try:
        soup = BeautifulSoup(html, "lxml")
        price = soup.find("h4", {"class": "finalPrice"}).text
        return price
    except: 
        print(soup)
def get_terabyte_price(html):
    try:
        soup = BeautifulSoup(html, "lxml")
        price = soup.find(id="valVista").text
        return price
    except: 
        print(soup)

def get_pichau_price(html):
    try:
        soup = BeautifulSoup(html, "lxml")
        span_tag = soup.find('span', string='à vista')
        price = span_tag.find_next_sibling().text
        return price
    except:
        print(soup)

def get_amazon_price(html):
    try:
        soup = BeautifulSoup(html, "lxml")
        price = soup.find("span",{"class":"a-offscreen"}).text
        return price
    except:
        print(soup)

def get_price(html, site_name):
    price = 0
    try:
        if site_name == 'kabum':
            price = get_kabum_price(html)
        if site_name == 'terabyteshop':
            price = get_terabyte_price(html)
        if site_name == 'pichau':
            price = get_pichau_price(html)
        if site_name == 'amazon':
            price = get_amazon_price(html)
    except:
        print("ERROR", site_name)
    price = Price.fromstring(price)
    return price.amount_float

def process_products(df):
    try:
        updated_products = []
        for product in df.to_dict("records"):
            html, site_name = get_response(product["url"])
            product["price"] = get_price(html, site_name)
            product["alert"] = product["price"] < product["alert_price"]
            if product["alert"] is True:
                asyncio.run(send_message(product["product"], product["url"], product["price"]))
            updated_products.append(product)
        return pd.DataFrame(updated_products)
    except Exception as error:
        print(error)

async def send_message(product, url, price):
    bot = Bot(TELEGRAM_TOKEN)
    updates = await bot.get_updates()

    if updates:
        last_update = updates[-1]

        if last_update.message:
            chat_id = last_update.message.chat_id
    else:
        print("Nenhuma atualização recebida")

    message = f"Preço do produto {product} caiu! R${price} Acesse: {url}"
    print("PRICE FOUND!")
    await bot.send_message(chat_id=chat_id, text=message)

def main():
    print("RUNNING SCRIPT!")
    df = get_urls(PRODUCT_URL_CSV)
    try:
        df_updated = process_products(df)
        if SAVE_TO_CSV:
            df_updated.to_csv(PRICES_CSV, index=False, mode="w")
    except:
        print("DEU RUIM!")

while True:
    main()
    
    time.sleep(30)
        