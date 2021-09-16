#! python
import requests
import os
import re
from bs4 import BeautifulSoup as bs

def search(user_input):
    search_URL = "https://www.faselhd.pro/?s=" + user_input.strip()
    search_result = bs(requests.get(search_URL).content, "html.parser")
    results = search_result.select(".postDiv")
    tit_url = [(i.select_one(".h1").text, i.a["href"]) for i in results]
    return {k: v for k, v in tit_url}

def display_results(lists):
    choises = list(lists.keys())
    for i in range(len(choises)):
        print(f"{i}. \x1b[33m{choises[i]}\x1b[0m")
    choise = int(input("\n\x1b[41m\x1b[37mChoose one \x1b[0m : "))
    return choises[choise]

def select_episodes(media_url):
    media_htm = bs(requests.get(media_url).text,'html.parser')
    episodes = [ i["href"] for i in media_htm.select(".epAll a") ]
    pattern = r"[%d8%a7%d9%84%d8%ad%d9%84%d9%82%d8%a9]-(\d+)"
    episodes_num = [int("".join(re.findall(pattern,i))) for i in episodes]
    start,end = [ input(f"\n {i} EP : ") for i in ["Start on","End in"] ]
    sel = lambda i,opt : opt if i == "" else episodes_num.index(int(i))
    return episodes[sel(start,0):sel(end,-2) + 1]

def download(links,series=True):
    for link in links:
        link = bs(requests.get(link).text,"html.parser")
        downloadLink = link.select_one(".downloadLinks").a["href"]
        down_page = bs(requests.get(downloadLink).text,'html.parser')
        title = down_page.find("p",{"class":"info-item"}).span.text
        url = down_page.select_one(".dl-link").a["href"]
        print(f"\n\x1b[41m\x1b[37mDownloading \x1b[0m ===> {title}")
        os.system(f"wget '{url}' -O '{title}' --tries 10 -c --user-agent='Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/90.0.4430.212 Safari/537.36'")

def main() :
    main_page = search(input("Search : "))
    selected = display_results(main_page)
    try : 
        os.mkdir(selected)
        os.chdir(selected)
    except FileExistsError : os.chdir(selected)
    episodes = select_episodes(main_page[selected])
    download(episodes)

main()
