import pandas as pd
from urllib.request import urlopen
from bs4 import BeautifulSoup
import requests
import random

def GET_UA():
    uastrings = ["Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/38.0.2125.111 Safari/537.36",\
                "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/28.0.1500.72 Safari/537.36",\
                "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10) AppleWebKit/600.1.25 (KHTML, like Gecko) Version/8.0 Safari/600.1.25",\
                "Mozilla/5.0 (Windows NT 6.1; WOW64; rv:33.0) Gecko/20100101 Firefox/33.0",\
                "Mozilla/5.0 (Windows NT 6.3; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/38.0.2125.111 Safari/537.36",\
                "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/38.0.2125.111 Safari/537.36",\
                "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_9_5) AppleWebKit/600.1.17 (KHTML, like Gecko) Version/7.1 Safari/537.85.10",\
                "Mozilla/5.0 (Windows NT 6.1; WOW64; Trident/7.0; rv:11.0) like Gecko",\
                "Mozilla/5.0 (Windows NT 6.3; WOW64; rv:33.0) Gecko/20100101 Firefox/33.0",\
                "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/38.0.2125.104 Safari/537.36"\
                ]
 
    return random.choice(uastrings)

def parse_url(url):
 
    headers = {'User-Agent': GET_UA()}
    content = None
 
    try:
        response = requests.get(url, headers=headers)
        ct = response.headers['Content-Type'].lower().strip()
 
        if 'text/html' in ct:
            content = response.content
            soup = BeautifulSoup(content)
        else:
            content = response.content
            soup = None
 
    except Exception as e:
        print('Error:', str(e))
 
    return content, soup, ct

acronyms = pd.read_csv('acronyms.csv',index_col=0)
acr_dict = {}
for i in range(len(acronyms)):
    acr_dict[acronyms.Team[i]] = acronyms.Acr[i]


url = 'https://www.basketball-reference.com/leagues/NBA_2024_standings.html'
html = urlopen(url)
soup = BeautifulSoup(html,features='lxml')

# use findALL() to get the column headers
soup.findAll('tr', limit=40)
# use getText()to extract the text we need into a list
i = 0
header_list = []
length = 35
while i < length:
    headers = [th.getText() for th in soup.findAll('tr', limit=length)[i].findAll('th')]
    i = i +1
    if headers:
        header_list.append(headers[0])
        idx = i

east,west = [],[]
for team in header_list:
    team = team.replace('*','')
    if team =='Eastern Conference':
        flag = 0
    if team =='Western Conference':
        flag = 1
    if flag == 0 and team !='Eastern Conference':
        east.append(acr_dict[team])
    if flag == 1 and team !='Western Conference':
        west.append(acr_dict[team])



df = pd.DataFrame([east,west]).T
df.columns = ['East','West']
print(df.columns)

df.to_csv('data/current_standings.csv',index=False)