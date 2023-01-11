from selenium import webdriver
from bs4 import BeautifulSoup
import time
import requests
import pandas as pd
import concurrent.futures
import math

products_dict = dict()

req_batch = 20


def get_desc(url):
    response = requests.get(url=url)
    soup = BeautifulSoup(response.text, "html.parser")
    span = soup.find("span", id="desc")
    try:
        span_text = list(span.stripped_strings)
    except:
        print("Couldn't find desc'")
    return [url, span_text]


# define the url of the website to scrape
url = "https://www.tradeinn.com/goalinn/en/equipment-goalkeeper-gloves/11027/s#pf=id_subfamilia=11027&start=480"

chrome_options = webdriver.ChromeOptions()
chrome_options.add_argument("--headless")
chrome_options.add_argument("window-size=1920x1080")
driver = webdriver.Chrome(options=chrome_options)
driver.get(url)
time.sleep(60)
page = driver.page_source

# parse the html
soup = BeautifulSoup(page, "html.parser")

# getting the products ul
products_ul = soup.find("ul", class_="productos items_listado")

products = products_ul.findChildren("li", recursive=False)


for product in products:
    product_a = product.find("a", class_="prod_list")
    product_url = "http://www.tradeinn.com" + product_a.get("href")
    product_name = product_a.get("data-ta-product-name")
    product_image = product.find("img", class_="imagen_buscador")
    product_image_url = "http://www.tradeinn.com" + product_image.get("src")
    product_price = product.find("p", class_="BoxPriceValor").get_text()[2:]
    products_dict[product_url] = [
        product_url,
        product_name,
        product_image_url,
        product_price,
    ]

tm1 = time.perf_counter()

product_keys = list(products_dict.keys())
print(len(products))
print(len(product_keys))

batch_groups_count = math.ceil(len(product_keys) / req_batch)
for i in range(0, batch_groups_count):
    with concurrent.futures.ThreadPoolExecutor() as executor:
        futures = []
        for product_url in product_keys[i * req_batch : (i + 1) * req_batch]:
            futures.append(executor.submit(get_desc, url=product_url))
        for future in concurrent.futures.as_completed(futures):
            [url, desc] = future.result()
            products_dict[url].append(desc)
    print("Finshed Scrapping ..." + str(i) + "/" + str(batch_groups_count))
    time.sleep(5)


tm2 = time.perf_counter()
print(f"Total time elapsed: {tm2-tm1:0.2f} seconds")
print("Done Scrapping")

columns = [
    "product_url",
    "product_name",
    "product_image",
    "product_price",
    "product_description",
]


products_negative_cut_dict = dict()
for product_url in product_keys:
    product_desc = products_dict[product_url][4]
    str_desc = ""
    str_desc = " ".join(product_desc)
    if (
        str_desc.lower().find("negative") > -1
        and str_desc.lower().find("cut") > -1
        and str_desc.lower().find("half") == -1
        and str_desc.lower().find("roll") == -1
        and str_desc.lower().find("hybrid") == -1
    ):
        products_negative_cut_dict[product_url] = [
            product_url,
            products_dict[product_url][1],
            products_dict[product_url][2],
            products_dict[product_url][3],
            str_desc,
        ]


df = pd.DataFrame(products_negative_cut_dict.values(), columns=columns)
writer = pd.ExcelWriter("products_negative_cut.xlsx", engine="xlsxwriter")
df.to_excel(writer, sheet_name="products", index=False)
writer.save()


products_backhand_dict = dict()
for product_url in product_keys:
    product_desc = products_dict[product_url][4]
    str_desc = ""
    str_desc = " ".join(product_desc)
    if (
        str_desc.lower().find("backhand") > -1
        and str_desc.lower().find("latex") > -1
        and str_desc.lower().find("neoprene") > -1
    ):
        products_backhand_dict[product_url] = [
            product_url,
            products_dict[product_url][1],
            products_dict[product_url][2],
            products_dict[product_url][3],
            str_desc,
        ]


df = pd.DataFrame(products_backhand_dict.values(), columns=columns)
writer = pd.ExcelWriter("products_backhand_latex_neoprene.xlsx", engine="xlsxwriter")
df.to_excel(writer, sheet_name="products", index=False)
writer.save()

products_wrist_closure_dict = dict()
for product_url in product_keys:
    product_desc = products_dict[product_url][4]
    str_desc = ""
    str_desc = " ".join(product_desc)
    if (
        str_desc.lower().find("around") > -1
        and str_desc.lower().find("closure") > -1
        and str_desc.lower().find("wrap") > -1
    ):
        products_wrist_closure_dict[product_url] = [
            product_url,
            products_dict[product_url][1],
            products_dict[product_url][2],
            products_dict[product_url][3],
            str_desc,
        ]


df = pd.DataFrame(products_wrist_closure_dict.values(), columns=columns)
writer = pd.ExcelWriter("products_wrist_closure_wraparound.xlsx", engine="xlsxwriter")
df.to_excel(writer, sheet_name="products", index=False)
writer.save()
