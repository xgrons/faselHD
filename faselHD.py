#! python
import requests
import os
import re
from bs4 import BeautifulSoup as bs
from youtube_dl.utils import random_user_agent


soup = lambda url : bs(requests.get(url).content,"html.parser")
dir_path = os.path.dirname(os.path.realpath(__file__))

def search(user_input):
    search_URL = "https://www.faselhd.pro/?s=" + user_input.strip()
    search_result = soup(search_URL)
    results = search_result.select(".postDiv")
    tit_url = [(i.select_one(".h1").text, i.a["href"]) for i in results]
    return dict(tit_url)

def display_results(lists):
    choises = list(lists.keys())
    for i in range(len(choises)):
        print(f"{i + 1}. \x1b[33m{choises[i]}\x1b[0m")
    choise = int(input("\n\x1b[41m\x1b[37mChoose one \x1b[0m : "))
    return choises[choise - 1]

def seasons(seasonList):
    seasons_num = dict([(i.select_one(".title").text,i.div["data-href"]) for i in seasonList])
    choise = display_results(seasons_num)
    return "https://www.faselhd.pro/?p=" + seasons_num[choise]

def select_episodes(media_url):
    media_htm = soup(media_url)
    seasons_list = media_htm.select("#seasonList > div")
    if seasons_list : media_htm = soup(seasons(seasons_list))
    episodes = [ i["href"] for i in media_htm.select(".epAll a") ]
    if not(episodes) : return [media_url]
    else :
        pattern = r"[%d8%a7%d9%84%d8%ad%d9%84%d9%82%d8%a9]-(\d+)"
        try : episodes_num = [int("".join(re.findall(pattern,i))) for i in episodes]
        except ValueError : episodes_num = list(range(1,len(episodes) + 1))
        print(f"Episodes : {episodes_num[0]}-{episodes_num[-1]}")
        start,end = [ input(f"\n {i} EP : ") for i in ["Start on","End in"] ]
        sel = lambda i,opt : opt if i == "" else episodes_num.index(int(i))
        return episodes[sel(start,0):sel(end,len(episodes))]

def getDirectLink(site) : 
    headers = {'User-Agent': f'{random_user_agent()}'}
    return requests.get(site,headers=headers).text
    
def CQuality(available,prefer) :
    all_qual = ["360","480","720","1080"]
    if prefer in all_qual : 
        return prefer if prefer in available else CQuality(available,all_qual[all_qual.index(prefer) - 1])
    else :
        return prefer

def download(links,folder,normal=True):
    if not(normal) : quality = input("Choose Your Preferde Resolution : [1080,720,480,360] ? ")
    for link in links:
        link = soup(link)
        title = link.select_one(".h3").text
        title = " ".join(re.findall(r"\d+|\w+",title)) + ".mp4"
        print(f"\n\x1b[41m\x1b[37mDownloading \x1b[0m ===> {title}")
        if normal :
            downloadLink = link.select_one(".downloadLinks").a["href"]
            down_page = soup(downloadLink)
            url = down_page.select_one(".dl-link").a["href"]
            os.system(f"wget '{url}' -O '{title}' --tries 10 -c --user-agent='{random_user_agent()}'")
        else : 
            link = getDirectLink(link.find("iframe")["src"])
            videoURL = re.findall("\"file\":\"(.*)\",\"hlshtml\"",link)[0].replace("\\","")
            available = re.findall(r",*(\d+)+,p*",videoURL)
            if available : newVideoURL = re.sub(r",(.*),",f",{CQuality(available,quality)}",videoURL)
            try : os.mkdir(folder)
            except FileExistsError : os.chdir(folder)
            os.system(f"downloadm3u8 -o '{folder}/{title}' '{newVideoURL or videoURL}'")

def main() :
    main_page = search(input("Search : "))
    while main_page == {} : 
        print("\n\n----- \x1b[41mNo Results\x1b[0m ----\n\n")
        main_page = search(input("Search : "))
    selected = display_results(main_page)
    episodes = select_episodes(main_page[selected])
    download(episodes,dir_path+selected,normal=False)

try : main()
except KeyboardInterrupt : print("\n\nExit .....")
