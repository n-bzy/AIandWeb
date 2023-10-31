# %%
import requests
from bs4 import BeautifulSoup

server = requests.get("https://vm009.rz.uos.de/crawl/index.html")

def crawl():
    print(server.text)
# %%
