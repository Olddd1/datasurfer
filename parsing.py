import requests
import json

from selenium import webdriver

import time

categories = dict(json.load(open('categories.json', 'rb')))


def get_art(url):
    return url.split('/')[4]


def data_parse(art):
    try:
        r = requests.get(f'https://wbx-content-v2.wbstatic.net/ru/{art}.json').json()
        data = {"colors": r.get("colors"), "category": r.get("subj_root_name"), "name": r.get("subj_name"),
                "imt_name": r.get("imt_name")}
        r = requests.get(f"https://card.wb.ru/cards/detail?spp=19&regions=68,64,83,4,38,80,33,70,82,86,30,69,22,66,31,40,1,48&appType=1&locale=ru&lang=ru&curr=rub&dest=-1075831,-115100,-382776,-2383149&nm={art}").json()
        data["price"] = r.get('data').get('products')[0].get('salePriceU')
        data["feedbacks"] = r.get('data').get('products')[0].get("feedbacks")
        data["stocks"] = r.get('data').get('products')[0].get("sizes")[0].get("stocks")
        data["commission"] = categories[data["category"]][data["name"]]
        return data
    except Exception as e:
        return None


def init_driver():
    ff = "/usr/lib/chromium-browser/chromedriver"
    chrome_option = webdriver.ChromeOptions()
    chrome_option.add_argument('headless')
    driver = webdriver.Chrome(executable_path=ff, options=chrome_option)
    return driver


def get_keys(art):
    driver = init_driver()

    driver.get(f'https://www.wildberries.ru/catalog/{art}/detail.aspx')
    time.sleep(2)
    driver.get(f'https://www.wildberries.ru/webapi/product/{art}/searchtags')
    r = '}'.join('{'.join(driver.page_source.split('{')[1::]).split('}')[:-1:])

    driver.quit()

    data = json.loads('{' + r + '}')

    return [i["text"] for i in data['value']['tagsViewModels']]


def get_search_rating(key, art):
    r = requests.get(f'https://search.wb.ru/exactmatch/ru/common/v4/'
                     f'search?curr=rub&dest=-1029256,-102269,-2162196,-1257786&'
                     f'locale=ru&query={key}&resultset=catalog&sort=popular').json()["data"]["products"]

    data = [i['id'] for i in r]
    if art in data:
        return data.index(art)
    return None

