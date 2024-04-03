import pandas as pd
import requests
from urllib.parse import urlparse
from fake_useragent import UserAgent
from bs4 import BeautifulSoup
from price_parser import Price


class Scrapper:
    def get_urls(self, csv_file):
        df = pd.read_csv(csv_file)
        return df
    
    def get_site_name(self, url):
        parsed_url = urlparse(url)

        site_name = parsed_url.netloc

        if site_name.startswith('www.'):
            site_name = site_name[4:]

        site_name = site_name.replace('.com.br', '').replace('.com', '')

        if '/' in site_name:
            site_name = site_name.split('/')[0]

        return site_name
    
    def get_response(self, url):
        site_name = self.get_site_name(url)
        headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        if site_name == 'amazon':
            headers = {"accept-language": "en-US,en;q=0.9","accept-encoding": "gzip, deflate, br","User-Agent":"Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/111.0.0.0 Safari/537.36","accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7"}
        ua = UserAgent(browsers=['edge', 'chrome'], platforms=['pc'])
        user_agent_random = ua.random
        headers["User-Agent"] = user_agent_random
        response = requests.get(url, headers=headers)
        return response.text, site_name

    def get_kabum_price(self, html):
        try:
            soup = BeautifulSoup(html, "lxml")
            price = soup.find("h4", {"class": "finalPrice"}).text
            return price
        except: 
            print("Error while scrapping!")
    
    def get_terabyte_price(self, html):
        try:
            soup = BeautifulSoup(html, "lxml")
            price = soup.find(id="valVista").text
            return price
        except: 
            print("Error while scrapping!")

    def get_pichau_price(self, html):
        try:
            soup = BeautifulSoup(html, "lxml")
            span_tag = soup.find('span', string='à vista')
            price = span_tag.find_next_sibling().text
            return price
        except:
            print("Error while scrapping!")

    def get_amazon_price(self, html):
        try:
            soup = BeautifulSoup(html, "lxml")
            price = soup.find("span",{"class":"a-offscreen"}).text
            return price
        except:
            print("Error while scrapping!")
    
    def get_price(self, url):
        html, site_name = self.get_response(url)
        try:
            if site_name == 'kabum':
                price = self.get_kabum_price(html)
            if site_name == 'terabyteshop':
                price = self.get_terabyte_price(html)
            if site_name == 'pichau':
                price = self.get_pichau_price(html)
            if site_name == 'amazon':
                price = self.get_amazon_price(html)
            price = Price.fromstring(price)
            if price == 0.00:
                return None
            return price.amount_float, site_name
        except:
            print("ERROR", site_name)
    
